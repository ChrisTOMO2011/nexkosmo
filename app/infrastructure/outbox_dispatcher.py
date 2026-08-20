from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class OutboxEnvelopeError(ValueError):
    pass


class TransientOutboxError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class EventEnvelope:
    event_id: UUID
    workspace_id: UUID
    aggregate_id: UUID
    aggregate_sequence: int
    event_type: str
    event_version: int
    payload: dict[str, Any]
    occurred_at: datetime
    attempts: int

    @classmethod
    def from_row(cls, row: Any) -> EventEnvelope:
        payload = row["payload"]
        if not isinstance(payload, dict):
            raise OutboxEnvelopeError("Outbox payload must be a JSON object.")
        if not str(row["event_type"]).strip():
            raise OutboxEnvelopeError("Outbox event_type is required.")
        if int(row["event_version"]) < 1 or int(row["aggregate_sequence"]) < 1:
            raise OutboxEnvelopeError("Outbox versions and sequences must be positive.")
        return cls(
            event_id=row["id"],
            workspace_id=row["workspace_id"],
            aggregate_id=row["aggregate_id"],
            aggregate_sequence=int(row["aggregate_sequence"]),
            event_type=str(row["event_type"]),
            event_version=int(row["event_version"]),
            payload=dict(payload),
            occurred_at=row["occurred_at"],
            attempts=int(row["attempts"]),
        )


EventHandler = Callable[[EventEnvelope], Awaitable[None]]
DatabaseConsumerHandler = Callable[[AsyncSession, EventEnvelope], Awaitable[None]]


class EventHandlerRegistry:
    def __init__(self) -> None:
        self._handlers: dict[tuple[str, int], EventHandler] = {}

    def register(self, event_type: str, event_version: int, handler: EventHandler) -> None:
        key = (event_type.strip(), event_version)
        if not key[0] or event_version < 1:
            raise ValueError("Handlers require an event type and positive version.")
        if key in self._handlers:
            raise ValueError(f"A handler is already registered for {key!r}.")
        self._handlers[key] = handler

    async def dispatch(self, envelope: EventEnvelope) -> None:
        handler = self._handlers.get((envelope.event_type, envelope.event_version))
        if handler is None:
            raise OutboxEnvelopeError(
                f"No handler for {envelope.event_type} v{envelope.event_version}."
            )
        await handler(envelope)


@dataclass(slots=True)
class OutboxMetrics:
    claimed: int = 0
    delivered: int = 0
    retried: int = 0
    dead_lettered: int = 0
    lease_conflicts: int = 0
    last_poll_at: datetime | None = None
    last_success_at: datetime | None = None
    last_error: str | None = None

    def snapshot(self) -> dict[str, Any]:
        return {
            "claimed": self.claimed,
            "delivered": self.delivered,
            "retried": self.retried,
            "dead_lettered": self.dead_lettered,
            "lease_conflicts": self.lease_conflicts,
            "last_poll_at": self.last_poll_at.isoformat() if self.last_poll_at else None,
            "last_success_at": (self.last_success_at.isoformat() if self.last_success_at else None),
            "last_error": self.last_error,
        }


async def _set_workspace(session: AsyncSession, workspace_id: UUID) -> None:
    await session.execute(
        text("select set_config('app.workspace_id', :workspace_id, true)"),
        {"workspace_id": str(workspace_id)},
    )


class SqlAlchemyOutboxDispatcher:
    """At-least-once dispatcher with leases, aggregate ordering, and dead letters."""

    def __init__(
        self,
        factory: async_sessionmaker[AsyncSession],
        registry: EventHandlerRegistry,
        *,
        worker_id: UUID | None = None,
        lease_duration: timedelta = timedelta(seconds=30),
        max_attempts: int = 8,
        batch_size: int = 25,
        poll_interval: float = 1.0,
    ) -> None:
        if max_attempts < 1 or batch_size < 1 or poll_interval <= 0:
            raise ValueError("Dispatcher limits must be positive.")
        self._factory = factory
        self._registry = registry
        self._worker_id = worker_id or uuid4()
        self._lease_duration = lease_duration
        self._max_attempts = max_attempts
        self._batch_size = batch_size
        self._poll_interval = poll_interval
        self.metrics = OutboxMetrics()

    async def claim(self, workspace_id: UUID) -> tuple[EventEnvelope, ...]:
        lease_expires_at = datetime.now(UTC) + self._lease_duration
        async with self._factory() as session, session.begin():
            await _set_workspace(session, workspace_id)
            rows = (
                (
                    await session.execute(
                        text(
                            """
                        WITH candidates AS (
                            SELECT candidate.id
                            FROM outbox_events candidate
                            WHERE candidate.workspace_id = :workspace_id
                              AND candidate.delivered_at IS NULL
                              AND candidate.dead_lettered_at IS NULL
                              AND candidate.available_at <= now()
                              AND (
                                  candidate.lease_expires_at IS NULL
                                  OR candidate.lease_expires_at <= now()
                              )
                              AND NOT EXISTS (
                                  SELECT 1 FROM outbox_events earlier
                                  WHERE earlier.workspace_id = candidate.workspace_id
                                    AND earlier.aggregate_id = candidate.aggregate_id
                                    AND earlier.aggregate_sequence < candidate.aggregate_sequence
                                    AND earlier.delivered_at IS NULL
                                    AND earlier.dead_lettered_at IS NULL
                              )
                            ORDER BY candidate.occurred_at, candidate.id
                            LIMIT :limit
                            FOR UPDATE SKIP LOCKED
                        )
                        UPDATE outbox_events event
                        SET lease_owner = :worker_id,
                            lease_expires_at = :lease_expires_at,
                            attempts = event.attempts + 1
                        FROM candidates
                        WHERE event.id = candidates.id
                        RETURNING event.*
                        """
                        ),
                        {
                            "workspace_id": str(workspace_id),
                            "worker_id": str(self._worker_id),
                            "lease_expires_at": lease_expires_at,
                            "limit": self._batch_size,
                        },
                    )
                )
                .mappings()
                .all()
            )
        envelopes = tuple(EventEnvelope.from_row(row) for row in rows)
        self.metrics.claimed += len(envelopes)
        self.metrics.last_poll_at = datetime.now(UTC)
        return envelopes

    async def dispatch_once(self, workspace_id: UUID) -> int:
        envelopes = await self.claim(workspace_id)
        for envelope in envelopes:
            try:
                await self._registry.dispatch(envelope)
            except Exception as exc:
                await self._fail(envelope, exc)
            else:
                await self._mark_delivered(envelope)
        return len(envelopes)

    async def _mark_delivered(self, envelope: EventEnvelope) -> None:
        async with self._factory() as session, session.begin():
            await _set_workspace(session, envelope.workspace_id)
            result = await session.execute(
                text(
                    """
                    UPDATE outbox_events
                    SET delivered_at = now(), lease_owner = NULL,
                        lease_expires_at = NULL, last_error = NULL
                    WHERE workspace_id = :workspace_id AND id = :event_id
                      AND lease_owner = :worker_id
                      AND delivered_at IS NULL AND dead_lettered_at IS NULL
                    """
                ),
                {
                    "workspace_id": str(envelope.workspace_id),
                    "event_id": str(envelope.event_id),
                    "worker_id": str(self._worker_id),
                },
            )
        if getattr(result, "rowcount", 0) == 1:
            self.metrics.delivered += 1
            self.metrics.last_success_at = datetime.now(UTC)
            self.metrics.last_error = None
        else:
            self.metrics.lease_conflicts += 1

    async def _fail(self, envelope: EventEnvelope, exc: Exception) -> None:
        exhausted = envelope.attempts >= self._max_attempts
        delay_seconds = min(3600, 2 ** min(envelope.attempts, 12))
        async with self._factory() as session, session.begin():
            await _set_workspace(session, envelope.workspace_id)
            result = await session.execute(
                text(
                    """
                    UPDATE outbox_events
                    SET dead_lettered_at = CASE WHEN :exhausted THEN now() ELSE NULL END,
                        available_at = CASE
                            WHEN :exhausted THEN available_at
                            ELSE now() + make_interval(secs => :delay_seconds)
                        END,
                        lease_owner = NULL, lease_expires_at = NULL,
                        last_error = :last_error
                    WHERE workspace_id = :workspace_id AND id = :event_id
                      AND lease_owner = :worker_id
                      AND delivered_at IS NULL AND dead_lettered_at IS NULL
                    """
                ),
                {
                    "exhausted": exhausted,
                    "delay_seconds": delay_seconds,
                    "last_error": f"{type(exc).__name__}: {exc}"[:2000],
                    "workspace_id": str(envelope.workspace_id),
                    "event_id": str(envelope.event_id),
                    "worker_id": str(self._worker_id),
                },
            )
        if getattr(result, "rowcount", 0) != 1:
            self.metrics.lease_conflicts += 1
            return
        self.metrics.last_error = f"{type(exc).__name__}: {exc}"[:2000]
        if exhausted:
            self.metrics.dead_lettered += 1
        else:
            self.metrics.retried += 1

    async def run(self, workspace_id: UUID, stop: asyncio.Event) -> None:
        while not stop.is_set():
            await self.dispatch_once(workspace_id)
            try:
                await asyncio.wait_for(stop.wait(), timeout=self._poll_interval)
            except TimeoutError:
                continue


class SqlAlchemyConsumerInbox:
    def __init__(self, factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = factory

    async def process_once(
        self,
        consumer_name: str,
        envelope: EventEnvelope,
        handler: DatabaseConsumerHandler,
    ) -> bool:
        async with self._factory() as session, session.begin():
            await _set_workspace(session, envelope.workspace_id)
            inserted = await session.scalar(
                text(
                    """
                    INSERT INTO consumer_inbox (
                        consumer_name, event_id, event_type, event_version
                    ) VALUES (
                        :consumer_name, :event_id, :event_type, :event_version
                    )
                    ON CONFLICT (consumer_name, event_id) DO NOTHING
                    RETURNING event_id
                    """
                ),
                {
                    "consumer_name": consumer_name,
                    "event_id": str(envelope.event_id),
                    "event_type": envelope.event_type,
                    "event_version": envelope.event_version,
                },
            )
            if inserted is None:
                return False
            await handler(session, envelope)
            await session.execute(
                text(
                    """
                    UPDATE consumer_inbox
                    SET processed_at = now()
                    WHERE consumer_name = :consumer_name AND event_id = :event_id
                    """
                ),
                {
                    "consumer_name": consumer_name,
                    "event_id": str(envelope.event_id),
                },
            )
        return True


async def noop_handler(_envelope: EventEnvelope) -> None:
    """Test-only handler. It is deliberately not registered by application startup."""
