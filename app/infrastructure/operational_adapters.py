import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports import AuditPort, IdempotencyClaim
from app.domain.enums import AgentKind
from app.domain.errors import IdempotencyConflict
from app.domain.types import Principal


async def _set_workspace(session: AsyncSession, workspace_id: UUID) -> None:
    await session.execute(
        text("select set_config('app.workspace_id', :value, true)"),
        {"value": str(workspace_id)},
    )


class SqlAlchemyIdempotencyAdapter:
    def __init__(
        self,
        factory: async_sessionmaker[AsyncSession],
        *,
        lease_duration: timedelta = timedelta(minutes=2),
    ) -> None:
        self._factory = factory
        self._lease_duration = lease_duration

    async def acquire(self, workspace_id: UUID, key: str, request_hash: str) -> IdempotencyClaim:
        if not key.strip():
            raise IdempotencyConflict("Idempotency-Key is required.")
        owner_token = uuid4()
        now = datetime.now(UTC)
        lease_expires_at = now + self._lease_duration
        async with self._factory() as session, session.begin():
            await _set_workspace(session, workspace_id)
            inserted = (
                await session.execute(
                    text(
                        """
                        INSERT INTO idempotency_records (
                            workspace_id, idempotency_key, request_hash, status,
                            owner_token, lease_expires_at
                        ) VALUES (
                            :workspace_id, :key, :request_hash, 'processing',
                            :owner_token, :lease_expires_at
                        )
                        ON CONFLICT (workspace_id, idempotency_key) DO NOTHING
                        RETURNING idempotency_key
                        """
                    ),
                    {
                        "workspace_id": str(workspace_id),
                        "key": key,
                        "request_hash": request_hash,
                        "owner_token": str(owner_token),
                        "lease_expires_at": lease_expires_at,
                    },
                )
            ).scalar_one_or_none()
            if inserted is not None:
                return IdempotencyClaim("acquired")

            row = (
                (
                    await session.execute(
                        text(
                            """
                        SELECT request_hash, status, response, lease_expires_at
                        FROM idempotency_records
                        WHERE workspace_id = :workspace_id AND idempotency_key = :key
                        FOR UPDATE
                        """
                        ),
                        {"workspace_id": str(workspace_id), "key": key},
                    )
                )
                .mappings()
                .one()
            )
            if row["request_hash"] != request_hash:
                raise IdempotencyConflict(
                    "Idempotency key was already used for a different request."
                )
            if row["status"] == "completed":
                return IdempotencyClaim("completed", row["response"])
            if row["status"] == "processing" and row["lease_expires_at"] > now:
                raise IdempotencyConflict("An identical request is already processing.")
            await session.execute(
                text(
                    """
                    UPDATE idempotency_records
                    SET status = 'processing', owner_token = :owner_token,
                        lease_expires_at = :lease_expires_at, error_code = NULL,
                        updated_at = now()
                    WHERE workspace_id = :workspace_id AND idempotency_key = :key
                    """
                ),
                {
                    "workspace_id": str(workspace_id),
                    "key": key,
                    "owner_token": str(owner_token),
                    "lease_expires_at": lease_expires_at,
                },
            )
            return IdempotencyClaim("acquired")

    async def complete(self, workspace_id: UUID, key: str, response: dict[str, Any]) -> None:
        async with self._factory() as session, session.begin():
            await _set_workspace(session, workspace_id)
            await session.execute(
                text(
                    """
                    UPDATE idempotency_records
                    SET status = 'completed', response = CAST(:response AS jsonb),
                        error_code = NULL, updated_at = now()
                    WHERE workspace_id = :workspace_id AND idempotency_key = :key
                    """
                ),
                {
                    "workspace_id": str(workspace_id),
                    "key": key,
                    "response": json.dumps(response, sort_keys=True),
                },
            )

    async def fail(self, workspace_id: UUID, key: str, error_code: str) -> None:
        async with self._factory() as session, session.begin():
            await _set_workspace(session, workspace_id)
            await session.execute(
                text(
                    """
                    UPDATE idempotency_records
                    SET status = 'failed', error_code = :error_code, updated_at = now()
                    WHERE workspace_id = :workspace_id AND idempotency_key = :key
                    """
                ),
                {
                    "workspace_id": str(workspace_id),
                    "key": key,
                    "error_code": error_code,
                },
            )


class SqlAlchemyAuditAdapter:
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
        deduplication_key: str | None = None,
    ) -> None:
        workspace_id = principal.workspace_id if principal else None
        stream_key = f"workspace:{workspace_id}" if workspace_id else "system"
        async with self._factory() as session, session.begin():
            await session.execute(
                text("SELECT pg_advisory_xact_lock(hashtext(:stream_key))"),
                {"stream_key": stream_key},
            )
            if deduplication_key is not None:
                existing = await session.scalar(
                    text(
                        """
                        SELECT 1 FROM audit_log
                        WHERE stream_key = :stream_key
                          AND deduplication_key = :deduplication_key
                        """
                    ),
                    {
                        "stream_key": stream_key,
                        "deduplication_key": deduplication_key,
                    },
                )
                if existing is not None:
                    return
            head = (
                (
                    await session.execute(
                        text(
                            """
                        SELECT last_sequence, last_hash FROM audit_stream_heads
                        WHERE stream_key = :stream_key FOR UPDATE
                        """
                        ),
                        {"stream_key": stream_key},
                    )
                )
                .mappings()
                .first()
            )
            sequence = int(head["last_sequence"]) + 1 if head else 1
            previous_hash = str(head["last_hash"]) if head else "0" * 64
            recorded_at = datetime.now(UTC)
            canonical = json.dumps(
                {
                    "stream_key": stream_key,
                    "sequence": sequence,
                    "recorded_at": recorded_at.isoformat(),
                    "workspace_id": str(workspace_id) if workspace_id else None,
                    "principal_id": (str(principal.principal_id) if principal else None),
                    "agent_id": str(principal.agent_id) if principal else None,
                    "action": action,
                    "outcome": outcome,
                    "resource_id": str(resource_id) if resource_id else None,
                    "details": details,
                    "previous_hash": previous_hash,
                },
                sort_keys=True,
                separators=(",", ":"),
            ).encode()
            entry_hash = hashlib.sha256(canonical).hexdigest()
            await session.execute(
                text(
                    """
                    INSERT INTO audit_log (
                        stream_key, sequence, recorded_at, workspace_id, principal_id,
                        agent_id, action, outcome, resource_id, details,
                        previous_hash, entry_hash, deduplication_key
                    ) VALUES (
                        :stream_key, :sequence, :recorded_at, :workspace_id, :principal_id,
                        :agent_id, :action, :outcome, :resource_id,
                        CAST(:details AS jsonb), :previous_hash, :entry_hash,
                        :deduplication_key
                    )
                    """
                ),
                {
                    "stream_key": stream_key,
                    "sequence": sequence,
                    "recorded_at": recorded_at,
                    "workspace_id": str(workspace_id) if workspace_id else None,
                    "principal_id": (str(principal.principal_id) if principal else None),
                    "agent_id": str(principal.agent_id) if principal else None,
                    "action": action,
                    "outcome": outcome,
                    "resource_id": str(resource_id) if resource_id else None,
                    "details": json.dumps(details, sort_keys=True),
                    "previous_hash": previous_hash,
                    "entry_hash": entry_hash,
                    "deduplication_key": deduplication_key,
                },
            )
            await session.execute(
                text(
                    """
                    INSERT INTO audit_stream_heads (stream_key, last_sequence, last_hash)
                    VALUES (:stream_key, :sequence, :entry_hash)
                    ON CONFLICT (stream_key) DO UPDATE SET
                        last_sequence = EXCLUDED.last_sequence,
                        last_hash = EXCLUDED.last_hash
                    """
                ),
                {
                    "stream_key": stream_key,
                    "sequence": sequence,
                    "entry_hash": entry_hash,
                },
            )


class AuditDeliveryCoordinator:
    """Durably queues audit intent and delivers it through the separate audit role.

    Business services enqueue success records inside their Unit of Work, then call
    ``deliver`` after commit. Delivery failures remain pending for reconciliation
    and never change the already-committed business response.
    """

    def __init__(
        self,
        factory: async_sessionmaker[AsyncSession],
        audit: AuditPort,
        *,
        lease_duration: timedelta = timedelta(minutes=2),
    ) -> None:
        self._factory = factory
        self._audit = audit
        self._lease_duration = lease_duration

    async def record_or_queue(
        self,
        *,
        deduplication_key: str,
        principal: Principal,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None:
        async with self._factory() as session, session.begin():
            await _set_workspace(session, principal.workspace_id)
            await session.execute(
                text(
                    """
                    INSERT INTO audit_delivery_queue (
                        workspace_id, deduplication_key, principal_id, agent_id,
                        agent_kind, action, outcome, resource_id, details
                    ) VALUES (
                        :workspace_id, :deduplication_key, :principal_id, :agent_id,
                        :agent_kind, :action, :outcome, :resource_id,
                        CAST(:details AS jsonb)
                    )
                    ON CONFLICT (workspace_id, deduplication_key) DO NOTHING
                    """
                ),
                {
                    "workspace_id": str(principal.workspace_id),
                    "deduplication_key": deduplication_key,
                    "principal_id": str(principal.principal_id),
                    "agent_id": str(principal.agent_id),
                    "agent_kind": principal.agent_kind.value,
                    "action": action,
                    "outcome": outcome,
                    "resource_id": str(resource_id) if resource_id else None,
                    "details": json.dumps(details, sort_keys=True),
                },
            )
        await self.deliver(principal.workspace_id, deduplication_key)

    async def deliver(self, workspace_id: UUID, deduplication_key: str) -> bool:
        owner = uuid4()
        now = datetime.now(UTC)
        lease_expires_at = now + self._lease_duration
        async with self._factory() as session, session.begin():
            await _set_workspace(session, workspace_id)
            row = (
                (
                    await session.execute(
                        text(
                            """
                        UPDATE audit_delivery_queue
                        SET lease_owner = :owner, lease_expires_at = :lease_expires_at,
                            attempts = attempts + 1, updated_at = now()
                        WHERE workspace_id = :workspace_id
                          AND deduplication_key = :deduplication_key
                          AND status = 'pending'
                          AND available_at <= now()
                          AND (lease_expires_at IS NULL OR lease_expires_at <= now())
                        RETURNING *
                        """
                        ),
                        {
                            "workspace_id": str(workspace_id),
                            "deduplication_key": deduplication_key,
                            "owner": str(owner),
                            "lease_expires_at": lease_expires_at,
                        },
                    )
                )
                .mappings()
                .first()
            )
        if row is None:
            return False

        principal = Principal(
            principal_id=row["principal_id"],
            workspace_id=row["workspace_id"],
            agent_id=row["agent_id"],
            agent_kind=AgentKind(row["agent_kind"]),
        )
        try:
            await self._audit.record_independent(
                principal=principal,
                action=row["action"],
                outcome=row["outcome"],
                resource_id=row["resource_id"],
                details=dict(row["details"]),
                deduplication_key=deduplication_key,
            )
        except Exception as exc:
            await self._record_failure(
                workspace_id,
                deduplication_key,
                owner,
                int(row["attempts"]),
                int(row["max_attempts"]),
                exc,
            )
            return False

        async with self._factory() as session, session.begin():
            await _set_workspace(session, workspace_id)
            await session.execute(
                text(
                    """
                    UPDATE audit_delivery_queue
                    SET status = 'delivered', delivered_at = now(),
                        lease_owner = NULL, lease_expires_at = NULL,
                        last_error = NULL, updated_at = now()
                    WHERE workspace_id = :workspace_id
                      AND deduplication_key = :deduplication_key
                      AND lease_owner = :owner
                    """
                ),
                {
                    "workspace_id": str(workspace_id),
                    "deduplication_key": deduplication_key,
                    "owner": str(owner),
                },
            )
        return True

    async def _record_failure(
        self,
        workspace_id: UUID,
        deduplication_key: str,
        owner: UUID,
        attempts: int,
        max_attempts: int,
        exc: Exception,
    ) -> None:
        exhausted = attempts >= max_attempts
        delay_seconds = min(3600, 2 ** min(attempts, 12))
        async with self._factory() as session, session.begin():
            await _set_workspace(session, workspace_id)
            await session.execute(
                text(
                    """
                    UPDATE audit_delivery_queue
                    SET status = :status,
                        dead_lettered_at = CASE WHEN :exhausted THEN now() ELSE NULL END,
                        available_at = CASE
                            WHEN :exhausted THEN available_at
                            ELSE now() + make_interval(secs => :delay_seconds)
                        END,
                        lease_owner = NULL, lease_expires_at = NULL,
                        last_error = :last_error, updated_at = now()
                    WHERE workspace_id = :workspace_id
                      AND deduplication_key = :deduplication_key
                      AND lease_owner = :owner
                    """
                ),
                {
                    "status": "dead-letter" if exhausted else "pending",
                    "exhausted": exhausted,
                    "delay_seconds": delay_seconds,
                    "last_error": f"{type(exc).__name__}: {exc}"[:2000],
                    "workspace_id": str(workspace_id),
                    "deduplication_key": deduplication_key,
                    "owner": str(owner),
                },
            )

    async def reconcile_pending(self, workspace_id: UUID, *, limit: int = 100) -> int:
        async with self._factory() as session, session.begin():
            await _set_workspace(session, workspace_id)
            keys = (
                (
                    await session.execute(
                        text(
                            """
                        SELECT deduplication_key FROM audit_delivery_queue
                        WHERE workspace_id = :workspace_id
                          AND status = 'pending'
                          AND available_at <= now()
                          AND (lease_expires_at IS NULL OR lease_expires_at <= now())
                        ORDER BY available_at, created_at
                        LIMIT :limit
                        """
                        ),
                        {"workspace_id": str(workspace_id), "limit": limit},
                    )
                )
                .scalars()
                .all()
            )
        delivered = 0
        for key in keys:
            delivered += int(await self.deliver(workspace_id, str(key)))
        return delivered
