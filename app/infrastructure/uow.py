from types import TracebackType
from typing import Any, Self, cast
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.application.ports import UnitOfWork
from app.domain.types import Principal
from app.infrastructure.character_repositories import (
    SqlAlchemyCharacterAssetManifestRepository,
    SqlAlchemyCharacterRepository,
    SqlAlchemySpeciesRepository,
)
from app.infrastructure.environment_repositories import (
    SqlAlchemyEnvironmentAssetManifestRepository,
    SqlAlchemyEnvironmentRepository,
    SqlAlchemyEnvironmentTypeRepository,
)
from app.infrastructure.project_repositories import (
    SqlAlchemyProductionRepository,
    SqlAlchemyProjectRepository,
)
from app.infrastructure.semantic_kernel_boundary import (
    DEFERRED_SEMANTIC_KERNEL_REPOSITORY,
)


class SqlAlchemyOutboxPort:
    def __init__(self, session: AsyncSession, workspace_id: UUID) -> None:
        self._session = session
        self._workspace_id = workspace_id

    async def append(
        self,
        event_type: str,
        version: int,
        payload: dict[str, Any],
        *,
        aggregate_id: UUID | None = None,
        aggregate_sequence: int | None = None,
    ) -> None:
        import json

        resolved_aggregate_id = aggregate_id
        if resolved_aggregate_id is None:
            for key in (
                "project_id",
                "production_id",
                "character_id",
                "environment_id",
                "assertion_id",
                "decision_id",
            ):
                if key in payload:
                    resolved_aggregate_id = UUID(str(payload[key]))
                    break
        if resolved_aggregate_id is None:
            raise ValueError("Outbox events require an aggregate identifier.")
        resolved_sequence = aggregate_sequence or int(payload.get("version", 1))
        await self._session.execute(
            text(
                """
                INSERT INTO outbox_events (
                    workspace_id, aggregate_id, aggregate_sequence,
                    event_type, event_version, payload
                ) VALUES (
                    :workspace_id, :aggregate_id, :aggregate_sequence,
                    :event_type, :event_version, CAST(:payload AS jsonb)
                )
                """
            ),
            {
                "workspace_id": str(self._workspace_id),
                "aggregate_id": str(resolved_aggregate_id),
                "aggregate_sequence": resolved_sequence,
                "event_type": event_type,
                "event_version": version,
                "payload": json.dumps(payload, sort_keys=True),
            },
        )


class SqlAlchemyTransactionalIdempotencyPort:
    def __init__(self, session: AsyncSession, workspace_id: UUID) -> None:
        self._session = session
        self._workspace_id = workspace_id

    async def complete(self, key: str, response: dict[str, Any]) -> None:
        import json

        result = await self._session.execute(
            text(
                """
                UPDATE idempotency_records
                SET status = 'completed', response = CAST(:response AS jsonb),
                    error_code = NULL, updated_at = now()
                WHERE workspace_id = :workspace_id
                  AND idempotency_key = :key
                  AND status = 'processing'
                """
            ),
            {
                "workspace_id": str(self._workspace_id),
                "key": key,
                "response": json.dumps(response, sort_keys=True),
            },
        )
        if getattr(result, "rowcount", 0) != 1:
            raise RuntimeError(
                "The idempotency lease was not available for transactional completion."
            )


class SqlAlchemyAuditDeliveryQueuePort:
    def __init__(self, session: AsyncSession, workspace_id: UUID) -> None:
        self._session = session
        self._workspace_id = workspace_id

    async def enqueue(
        self,
        *,
        deduplication_key: str,
        principal: Principal,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None:
        import json

        await self._session.execute(
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
                "workspace_id": str(self._workspace_id),
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


class SqlAlchemyUnitOfWork:
    def __init__(self, factory: async_sessionmaker[AsyncSession], principal: Principal) -> None:
        self._factory = factory
        self._principal = principal
        self.session: AsyncSession | None = None
        self.projects: SqlAlchemyProjectRepository
        self.productions: SqlAlchemyProductionRepository
        self.characters: SqlAlchemyCharacterRepository
        self.species: SqlAlchemySpeciesRepository
        self.character_assets: SqlAlchemyCharacterAssetManifestRepository
        self.environments: SqlAlchemyEnvironmentRepository
        self.environment_types: SqlAlchemyEnvironmentTypeRepository
        self.environment_assets: SqlAlchemyEnvironmentAssetManifestRepository
        self.outbox: SqlAlchemyOutboxPort
        self.idempotency: SqlAlchemyTransactionalIdempotencyPort
        self.audit_queue: SqlAlchemyAuditDeliveryQueuePort
        # Existing semantic-kernel repositories have ports but no concrete
        # adapters in this checkout. They remain explicit until that slice is wired.
        self.identities: Any = DEFERRED_SEMANTIC_KERNEL_REPOSITORY
        self.assertions: Any = DEFERRED_SEMANTIC_KERNEL_REPOSITORY
        self.decisions: Any = DEFERRED_SEMANTIC_KERNEL_REPOSITORY
        self.policies: Any = DEFERRED_SEMANTIC_KERNEL_REPOSITORY
        self.registry: Any = DEFERRED_SEMANTIC_KERNEL_REPOSITORY

    async def __aenter__(self) -> Self:
        self.session = self._factory()
        await self.session.begin()
        await self.session.execute(
            text("select set_config('app.workspace_id', :value, true)"),
            {"value": str(self._principal.workspace_id)},
        )
        await self.session.execute(
            text("select set_config('app.principal_id', :value, true)"),
            {"value": str(self._principal.principal_id)},
        )
        await self.session.execute(
            text("select set_config('app.agent_id', :value, true)"),
            {"value": str(self._principal.agent_id)},
        )
        self.projects = SqlAlchemyProjectRepository(self.session)
        self.productions = SqlAlchemyProductionRepository(self.session)
        self.characters = SqlAlchemyCharacterRepository(self.session)
        self.species = SqlAlchemySpeciesRepository(self.session)
        self.character_assets = SqlAlchemyCharacterAssetManifestRepository(self.session)
        self.environments = SqlAlchemyEnvironmentRepository(self.session)
        self.environment_types = SqlAlchemyEnvironmentTypeRepository(self.session)
        self.environment_assets = SqlAlchemyEnvironmentAssetManifestRepository(self.session)
        self.outbox = SqlAlchemyOutboxPort(self.session, self._principal.workspace_id)
        self.idempotency = SqlAlchemyTransactionalIdempotencyPort(
            self.session, self._principal.workspace_id
        )
        self.audit_queue = SqlAlchemyAuditDeliveryQueuePort(
            self.session, self._principal.workspace_id
        )
        return self

    async def commit(self) -> None:
        assert self.session is not None
        await self.session.commit()

    async def rollback(self) -> None:
        assert self.session is not None
        await self.session.rollback()

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self.session is not None:
            if exc is not None and self.session.in_transaction():
                await self.session.rollback()
            await self.session.close()


class SqlAlchemyUnitOfWorkFactory:
    def __init__(self, factory: async_sessionmaker[AsyncSession]) -> None:
        self._factory = factory

    def __call__(self, principal: Principal) -> UnitOfWork:
        return cast(UnitOfWork, SqlAlchemyUnitOfWork(self._factory, principal))
