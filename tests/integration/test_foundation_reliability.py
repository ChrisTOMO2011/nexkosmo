import asyncio
import os
from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from app.domain.errors import IdempotencyConflict
from app.infrastructure.config import settings
from app.infrastructure.operational_adapters import (
    AuditDeliveryCoordinator,
    SqlAlchemyAuditAdapter,
    SqlAlchemyIdempotencyAdapter,
)
from app.infrastructure.outbox_dispatcher import (
    EventEnvelope,
    EventHandlerRegistry,
    SqlAlchemyConsumerInbox,
    SqlAlchemyOutboxDispatcher,
)

_config = settings()
_app_engine = create_async_engine(_config.database_url, poolclass=NullPool)
_audit_engine = create_async_engine(_config.audit_database_url, poolclass=NullPool)
app_sessions = async_sessionmaker(_app_engine, expire_on_commit=False)
audit_sessions = async_sessionmaker(_audit_engine, expire_on_commit=False)


def owner_execute(statement: str, values: dict[str, object] | None = None) -> None:
    engine = create_engine(os.environ["MIGRATION_DATABASE_URL"])
    try:
        with engine.begin() as connection:
            connection.execute(text(statement), values or {})
    finally:
        engine.dispose()


def create_workspace(workspace_id: UUID) -> None:
    owner_execute(
        "INSERT INTO workspaces (id, canonical_key) VALUES (:id, :key)",
        {"id": str(workspace_id), "key": f"reliability-{workspace_id}"},
    )


def insert_event(workspace_id: UUID, aggregate_id: UUID, sequence: int = 1) -> UUID:
    event_id = uuid4()
    owner_execute(
        """
        INSERT INTO outbox_events (
            id, workspace_id, aggregate_id, aggregate_sequence,
            event_type, event_version, payload
        ) VALUES (
            :id, :workspace_id, :aggregate_id, :sequence,
            'foundation.test', 1, '{"valid": true}'::jsonb
        )
        """,
        {
            "id": str(event_id),
            "workspace_id": str(workspace_id),
            "aggregate_id": str(aggregate_id),
            "sequence": sequence,
        },
    )
    return event_id


async def test_idempotency_lease_recovery_and_fingerprint_conflict() -> None:
    workspace_id = uuid4()
    create_workspace(workspace_id)
    adapter = SqlAlchemyIdempotencyAdapter(app_sessions)

    assert (await adapter.acquire(workspace_id, "command", "fingerprint")).state == "acquired"
    with pytest.raises(IdempotencyConflict, match="already processing"):
        await adapter.acquire(workspace_id, "command", "fingerprint")
    with pytest.raises(IdempotencyConflict, match="different request"):
        await adapter.acquire(workspace_id, "command", "different")

    owner_execute(
        """
        UPDATE idempotency_records SET lease_expires_at = now() - interval '1 second'
        WHERE workspace_id = :workspace_id AND idempotency_key = 'command'
        """,
        {"workspace_id": str(workspace_id)},
    )
    assert (await adapter.acquire(workspace_id, "command", "fingerprint")).state == "acquired"


async def test_dispatch_success_competing_workers_and_duplicate_consumer() -> None:
    workspace_id = uuid4()
    aggregate_id = uuid4()
    create_workspace(workspace_id)
    event_id = insert_event(workspace_id, aggregate_id)
    delivered: list[UUID] = []
    registry = EventHandlerRegistry()

    async def handler(envelope: EventEnvelope) -> None:
        delivered.append(envelope.event_id)

    registry.register("foundation.test", 1, handler)
    workers = [
        SqlAlchemyOutboxDispatcher(app_sessions, registry, batch_size=1),
        SqlAlchemyOutboxDispatcher(app_sessions, registry, batch_size=1),
    ]
    counts = await asyncio.gather(*(worker.dispatch_once(workspace_id) for worker in workers))
    assert sum(counts) == 1
    assert delivered == [event_id]

    envelope = EventEnvelope(
        event_id=event_id,
        workspace_id=workspace_id,
        aggregate_id=aggregate_id,
        aggregate_sequence=1,
        event_type="foundation.test",
        event_version=1,
        payload={"valid": True},
        occurred_at=datetime.now(UTC),
        attempts=1,
    )
    inbox = SqlAlchemyConsumerInbox(app_sessions)
    handled = 0

    async def consumer(_session: object, _envelope: EventEnvelope) -> None:
        nonlocal handled
        handled += 1

    assert await inbox.process_once("foundation-test", envelope, consumer) is True  # type: ignore[arg-type]
    assert await inbox.process_once("foundation-test", envelope, consumer) is False  # type: ignore[arg-type]
    assert handled == 1


async def test_transient_failure_retries_and_poison_message_dead_letters() -> None:
    workspace_id = uuid4()
    create_workspace(workspace_id)
    retried_id = insert_event(workspace_id, uuid4())
    attempts = 0
    registry = EventHandlerRegistry()

    async def transient(envelope: EventEnvelope) -> None:
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("temporary")
        assert envelope.event_id == retried_id

    registry.register("foundation.test", 1, transient)
    dispatcher = SqlAlchemyOutboxDispatcher(app_sessions, registry, batch_size=1, max_attempts=3)
    assert await dispatcher.dispatch_once(workspace_id) == 1
    owner_execute(
        "UPDATE outbox_events SET available_at = now() WHERE id = :id",
        {"id": str(retried_id)},
    )
    assert await dispatcher.dispatch_once(workspace_id) == 1
    assert attempts == 2

    poison_id = insert_event(workspace_id, uuid4())
    poison_registry = EventHandlerRegistry()

    async def poison(_envelope: EventEnvelope) -> None:
        raise ValueError("poison")

    poison_registry.register("foundation.test", 1, poison)
    poison_dispatcher = SqlAlchemyOutboxDispatcher(
        app_sessions, poison_registry, batch_size=1, max_attempts=1
    )
    assert await poison_dispatcher.dispatch_once(workspace_id) == 1
    state = None
    engine = create_engine(os.environ["MIGRATION_DATABASE_URL"])
    try:
        with engine.connect() as connection:
            state = connection.execute(
                text(
                    "SELECT delivered_at, dead_lettered_at, attempts "
                    "FROM outbox_events WHERE id = :id"
                ),
                {"id": str(poison_id)},
            ).one()
    finally:
        engine.dispose()
    assert state.delivered_at is None
    assert state.dead_lettered_at is not None
    assert state.attempts == 1


async def test_audit_failure_is_queued_and_retry_is_deduplicated() -> None:
    workspace_id = uuid4()
    principal_id = uuid4()
    agent_id = uuid4()
    create_workspace(workspace_id)
    from app.domain.enums import AgentKind
    from app.domain.types import Principal

    principal = Principal(
        principal_id=principal_id,
        workspace_id=workspace_id,
        agent_id=agent_id,
        agent_kind=AgentKind.HUMAN,
    )

    class FailingAudit:
        async def record_independent(self, **_values: object) -> None:
            raise RuntimeError("audit unavailable")

    failed = AuditDeliveryCoordinator(
        app_sessions,
        FailingAudit(),  # type: ignore[arg-type]
    )
    await failed.record_or_queue(
        deduplication_key="foundation-audit",
        principal=principal,
        action="foundation.test",
        outcome="success",
        resource_id=None,
        details={"test": True},
    )
    owner_execute(
        """
        UPDATE audit_delivery_queue SET available_at = now()
        WHERE workspace_id = :workspace_id AND deduplication_key = 'foundation-audit'
        """,
        {"workspace_id": str(workspace_id)},
    )
    recovered = AuditDeliveryCoordinator(app_sessions, SqlAlchemyAuditAdapter(audit_sessions))
    assert await recovered.deliver(workspace_id, "foundation-audit") is True
    assert await recovered.deliver(workspace_id, "foundation-audit") is False
    engine = create_engine(os.environ["MIGRATION_DATABASE_URL"])
    try:
        with engine.connect() as connection:
            count = connection.scalar(
                text(
                    "SELECT count(*) FROM audit_log "
                    "WHERE workspace_id = :workspace_id "
                    "AND deduplication_key = 'foundation-audit'"
                ),
                {"workspace_id": str(workspace_id)},
            )
    finally:
        engine.dispose()
    assert count == 1
