import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports import AuditPort
from app.domain.enums import AgentKind
from app.domain.types import Principal


class SqlIndependentAuditPort:
    """Append-only hash-chained audit store, independent of business transactions."""

    def __init__(self, factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = factory

    async def record_independent(
        self,
        *,
        principal: Principal | None,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
        delivery_key: str | None = None,
    ) -> None:
        workspace_id = principal.workspace_id if principal is not None else None
        stream_key = f"workspace:{workspace_id}" if workspace_id else "system"
        async with self._factory() as session, session.begin():
            await session.execute(
                text("select pg_advisory_xact_lock(hashtextextended(:stream_key, 0))"),
                {"stream_key": stream_key},
            )
            if delivery_key is not None:
                existing = await session.scalar(
                    text(
                        """
                        select 1 from audit_log
                        where stream_key = :stream_key and delivery_key = :delivery_key
                        """
                    ),
                    {"stream_key": stream_key, "delivery_key": delivery_key},
                )
                if existing is not None:
                    return
            head = (
                await session.execute(
                    text(
                        """
                        select last_sequence, last_hash from audit_stream_heads
                        where stream_key = :stream_key for update
                        """
                    ),
                    {"stream_key": stream_key},
                )
            ).mappings().one_or_none()
            sequence = 1 if head is None else int(head["last_sequence"]) + 1
            previous_hash = "0" * 64 if head is None else str(head["last_hash"])
            recorded_at = datetime.now(UTC)
            payload = {
                "stream_key": stream_key,
                "sequence": sequence,
                "recorded_at": recorded_at.isoformat(),
                "workspace_id": str(workspace_id) if workspace_id else None,
                "principal_id": str(principal.principal_id) if principal else None,
                "agent_id": str(principal.agent_id) if principal else None,
                "action": action,
                "outcome": outcome,
                "resource_id": str(resource_id) if resource_id else None,
                "details": details,
                "delivery_key": delivery_key,
                "previous_hash": previous_hash,
            }
            entry_hash = hashlib.sha256(
                json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
            ).hexdigest()
            await session.execute(
                text(
                    """
                    insert into audit_log (
                        stream_key, sequence, recorded_at, workspace_id,
                        principal_id, agent_id, action, outcome, resource_id,
                        details, delivery_key, previous_hash, entry_hash
                    ) values (
                        :stream_key, :sequence, :recorded_at, :workspace_id,
                        :principal_id, :agent_id, :action, :outcome, :resource_id,
                        cast(:details as jsonb), :delivery_key, :previous_hash, :entry_hash
                    )
                    """
                ),
                {
                    **payload,
                    "recorded_at": recorded_at,
                    "workspace_id": workspace_id,
                    "principal_id": principal.principal_id if principal else None,
                    "agent_id": principal.agent_id if principal else None,
                    "resource_id": resource_id,
                    "details": json.dumps(details),
                    "entry_hash": entry_hash,
                },
            )
            await session.execute(
                text(
                    """
                    insert into audit_stream_heads (stream_key, last_sequence, last_hash)
                    values (:stream_key, :sequence, :entry_hash)
                    on conflict (stream_key) do update
                    set last_sequence = excluded.last_sequence,
                        last_hash = excluded.last_hash
                    """
                ),
                {
                    "stream_key": stream_key,
                    "sequence": sequence,
                    "entry_hash": entry_hash,
                },
            )


class SqlAuditDeliveryQueueRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def append(
        self,
        *,
        workspace_id: UUID,
        deduplication_key: str,
        principal_id: UUID,
        agent_id: UUID,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None:
        await self._session.execute(
            text(
                """
                insert into audit_delivery_queue (
                    workspace_id, deduplication_key, principal_id, agent_id,
                    action, outcome, resource_id, details
                ) values (
                    :workspace_id, :deduplication_key, :principal_id, :agent_id,
                    :action, :outcome, :resource_id, cast(:details as jsonb)
                )
                on conflict (workspace_id, deduplication_key) do nothing
                """
            ),
            {
                "workspace_id": workspace_id,
                "deduplication_key": deduplication_key,
                "principal_id": principal_id,
                "agent_id": agent_id,
                "action": action,
                "outcome": outcome,
                "resource_id": resource_id,
                "details": json.dumps(details),
            },
        )


class SqlAuditDeliveryDispatcher:
    """Best-effort delivery; durable queue state survives independent audit outages."""

    def __init__(
        self,
        factory: async_sessionmaker[AsyncSession],
        audit: AuditPort,
        *,
        max_attempts: int = 8,
        base_delay_seconds: int = 30,
        max_delay_seconds: int = 3600,
    ) -> None:
        self._factory = factory
        self._audit = audit
        self._max_attempts = max_attempts
        self._base_delay_seconds = base_delay_seconds
        self._max_delay_seconds = max_delay_seconds

    async def deliver_pending(self, *, principal: Principal) -> int:
        delivered = 0
        while True:
            async with self._factory() as session, session.begin():
                await _set_actor_context(session, principal)
                row = (
                    await session.execute(
                        text(
                            """
                            select id, principal_id, agent_id, action, outcome,
                                   resource_id, details, deduplication_key, attempts
                            from audit_delivery_queue
                            where workspace_id = :workspace_id
                              and delivered_at is null
                              and failed_at is null
                              and attempts < :max_attempts
                              and available_at <= now()
                              and (lease_expires_at is null or lease_expires_at <= now())
                            order by created_at, id
                            for update skip locked
                            limit 1
                            """
                        ),
                        {
                            "workspace_id": principal.workspace_id,
                            "max_attempts": self._max_attempts,
                        },
                    )
                ).mappings().one_or_none()
                if row is None:
                    return delivered
                await session.execute(
                    text(
                        """
                        update audit_delivery_queue
                        set lease_owner = :agent_id,
                            lease_expires_at = now() + interval '30 seconds',
                            attempts = attempts + 1
                        where id = :id
                        """
                    ),
                    {"agent_id": principal.agent_id, "id": row["id"]},
                )

            try:
                authority_principal = Principal(
                    principal_id=row["principal_id"],
                    workspace_id=principal.workspace_id,
                    agent_id=row["agent_id"],
                    agent_kind=AgentKind.HUMAN,
                )
                await self._audit.record_independent(
                    principal=authority_principal,
                    action=row["action"],
                    outcome=row["outcome"],
                    resource_id=row["resource_id"],
                    details={
                        **dict(row["details"]),
                        "audit_delivery_key": row["deduplication_key"],
                        "authority_principal_id": str(row["principal_id"]),
                        "acting_agent_id": str(row["agent_id"]),
                    },
                    delivery_key=row["deduplication_key"],
                )
            except Exception as exc:
                attempt = int(row["attempts"]) + 1
                exhausted = attempt >= self._max_attempts
                delay = retry_delay_seconds(
                    attempt,
                    base_seconds=self._base_delay_seconds,
                    max_seconds=self._max_delay_seconds,
                )
                async with self._factory() as session, session.begin():
                    await _set_actor_context(session, principal)
                    await session.execute(
                        text(
                            """
                            update audit_delivery_queue
                            set lease_owner = null, lease_expires_at = null,
                                available_at = :available_at,
                                failed_at = case when :exhausted then now() else null end,
                                last_error = :error
                            where id = :id and delivered_at is null
                            """
                        ),
                        {
                            "id": row["id"],
                            "error": type(exc).__name__,
                            "exhausted": exhausted,
                            "available_at": datetime.now(UTC) + timedelta(seconds=delay),
                        },
                    )
                return delivered

            async with self._factory() as session, session.begin():
                await _set_actor_context(session, principal)
                await session.execute(
                    text(
                        """
                        update audit_delivery_queue
                            set delivered_at = now(), lease_owner = null,
                            lease_expires_at = null, last_error = null, failed_at = null
                        where id = :id and delivered_at is null
                        """
                    ),
                    {"id": row["id"]},
                )
            delivered += 1

    async def requeue_failed(self, *, principal: Principal, delivery_id: UUID) -> bool:
        async with self._factory() as session, session.begin():
            await _set_actor_context(session, principal)
            result = await session.execute(
                text(
                    """
                    update audit_delivery_queue
                    set attempts = 0, failed_at = null, available_at = now(),
                        lease_owner = null, lease_expires_at = null, last_error = null
                    where id = :id and workspace_id = :workspace_id
                      and delivered_at is null and failed_at is not null
                    returning id
                    """
                ),
                {"id": delivery_id, "workspace_id": principal.workspace_id},
            )
            return result.scalar_one_or_none() is not None


def retry_delay_seconds(attempt: int, *, base_seconds: int, max_seconds: int) -> int:
    exponent = max(attempt - 1, 0)
    delay = base_seconds * pow(2, exponent)
    return delay if delay < max_seconds else max_seconds


async def _set_actor_context(session: AsyncSession, principal: Principal) -> None:
    for setting, value in (
        ("app.workspace_id", principal.workspace_id),
        ("app.principal_id", principal.principal_id),
        ("app.agent_id", principal.agent_id),
    ):
        await session.execute(
            text("select set_config(:setting, :value, true)"),
            {"setting": setting, "value": str(value)},
        )
