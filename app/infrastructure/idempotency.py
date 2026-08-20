import json
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports import IdempotencyClaim
from app.domain.errors import (
    IdempotencyConflict,
    IdempotencyInProgress,
    IdempotencyLeaseLost,
)
from app.domain.types import Principal


class SqlTransactionalIdempotency:
    """Claims outside a business UoW; completion is written inside that UoW."""

    def __init__(
        self,
        factory: async_sessionmaker[AsyncSession],
        *,
        lease_seconds: int = 60,
    ) -> None:
        self._factory = factory
        self._lease_seconds = lease_seconds

    async def claim(
        self,
        *,
        principal: Principal,
        key: str,
        request_hash: str,
    ) -> IdempotencyClaim:
        if not key.strip():
            raise IdempotencyConflict("An idempotency key is required.")
        owner_token = uuid4()
        async with self._factory() as session, session.begin():
            await _set_actor_context(session, principal)
            inserted = cast(
                CursorResult[Any],
                await session.execute(
                    text(
                        """
                        insert into idempotency_records (
                            workspace_id, idempotency_key, request_hash, status,
                            owner_token, lease_expires_at
                        ) values (
                            :workspace_id, :key, :request_hash, 'processing',
                            :owner_token, now() + make_interval(secs => :lease_seconds)
                        ) on conflict (workspace_id, idempotency_key) do nothing
                        """
                    ),
                    {
                        "workspace_id": principal.workspace_id,
                        "key": key,
                        "request_hash": request_hash,
                        "owner_token": owner_token,
                        "lease_seconds": self._lease_seconds,
                    },
                ),
            )
            if inserted.rowcount == 1:
                return IdempotencyClaim(owner_token=owner_token)

            record = (
                await session.execute(
                    text(
                        """
                        select request_hash, status, owner_token, lease_expires_at, response
                        from idempotency_records
                        where workspace_id = :workspace_id and idempotency_key = :key
                        for update
                        """
                    ),
                    {"workspace_id": principal.workspace_id, "key": key},
                )
            ).mappings().one()
            if record["request_hash"] != request_hash:
                raise IdempotencyConflict(
                    "The idempotency key was already used for a different request."
                )
            if record["status"] == "completed":
                response = record["response"]
                return IdempotencyClaim(
                    owner_token=None,
                    response=dict(response) if response is not None else {},
                )
            reclaimed = cast(
                CursorResult[Any],
                await session.execute(
                    text(
                        """
                        update idempotency_records
                        set status = 'processing', owner_token = :owner_token,
                            lease_expires_at = now() + make_interval(secs => :lease_seconds),
                            error_code = null, updated_at = now()
                        where workspace_id = :workspace_id
                          and idempotency_key = :key
                          and (status = 'failed' or lease_expires_at <= now())
                        """
                    ),
                    {
                        "owner_token": owner_token,
                        "lease_seconds": self._lease_seconds,
                        "workspace_id": principal.workspace_id,
                        "key": key,
                    },
                ),
            )
            if reclaimed.rowcount != 1:
                raise IdempotencyInProgress("An identical request is already in progress.")
            return IdempotencyClaim(owner_token=owner_token)


class SqlTransactionalIdempotencyRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def require_lease(
        self,
        *,
        workspace_id: UUID,
        key: str,
        request_hash: str,
        owner_token: UUID,
    ) -> None:
        present = await self._session.scalar(
            text(
                """
                select exists(
                    select 1 from idempotency_records
                    where workspace_id = :workspace_id
                      and idempotency_key = :key
                      and request_hash = :request_hash
                      and status = 'processing'
                      and owner_token = :owner_token
                      and lease_expires_at > now()
                    for update
                )
                """
            ),
            {
                "workspace_id": workspace_id,
                "key": key,
                "request_hash": request_hash,
                "owner_token": owner_token,
            },
        )
        if not present:
            raise IdempotencyLeaseLost("Idempotency ownership or lease was lost.")

    async def complete(
        self,
        *,
        workspace_id: UUID,
        key: str,
        request_hash: str,
        owner_token: UUID,
        response: dict[str, object],
    ) -> None:
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    """
                    update idempotency_records
                    set status = 'completed', response = cast(:response as jsonb),
                        error_code = null, updated_at = now()
                    where workspace_id = :workspace_id
                      and idempotency_key = :key
                      and request_hash = :request_hash
                      and status = 'processing'
                      and owner_token = :owner_token
                      and lease_expires_at > now()
                    """
                ),
                {
                    "workspace_id": workspace_id,
                    "key": key,
                    "request_hash": request_hash,
                    "owner_token": owner_token,
                    "response": json.dumps(response),
                },
            ),
        )
        if result.rowcount != 1:
            raise IdempotencyLeaseLost("Idempotency completion no longer owns a valid lease.")


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
