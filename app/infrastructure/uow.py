from types import TracebackType
from typing import Self

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.types import Principal
from app.infrastructure.audit_delivery import SqlAuditDeliveryQueueRepository
from app.infrastructure.character_repositories import SqlCharacterRepository
from app.infrastructure.idempotency import SqlTransactionalIdempotencyRepository
from app.infrastructure.project_repositories import (
    SqlOutboxRepository,
    SqlProductionRepository,
    SqlProjectMembershipRepository,
    SqlProjectRepository,
)
from app.infrastructure.semantic_repositories import SqlSemanticProjectRepository
from app.infrastructure.workspace_repositories import SqlWorkspaceAuthorityRepository


class SqlAlchemyUnitOfWork:
    def __init__(self, factory: async_sessionmaker[AsyncSession], principal: Principal) -> None:
        self._factory = factory
        self._principal = principal
        self.session: AsyncSession | None = None
        self.semantic_projects: SqlSemanticProjectRepository
        self.workspace_authority: SqlWorkspaceAuthorityRepository
        self.projects: SqlProjectRepository
        self.project_memberships: SqlProjectMembershipRepository
        self.productions: SqlProductionRepository
        self.characters: SqlCharacterRepository
        self.transactional_idempotency: SqlTransactionalIdempotencyRepository
        self.audit_delivery_queue: SqlAuditDeliveryQueueRepository
        self.outbox: SqlOutboxRepository

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
        self.semantic_projects = SqlSemanticProjectRepository(self.session)
        self.workspace_authority = SqlWorkspaceAuthorityRepository(self.session)
        self.projects = SqlProjectRepository(self.session)
        self.project_memberships = SqlProjectMembershipRepository(self.session)
        self.productions = SqlProductionRepository(self.session)
        self.characters = SqlCharacterRepository(self.session)
        self.transactional_idempotency = SqlTransactionalIdempotencyRepository(self.session)
        self.audit_delivery_queue = SqlAuditDeliveryQueueRepository(self.session)
        self.outbox = SqlOutboxRepository(self.session, self._principal.workspace_id)
        return self

    def _require_session(self) -> AsyncSession:
        if self.session is None:
            raise RuntimeError("unit of work session is not active")
        return self.session

    async def commit(self) -> None:
        session = self._require_session()
        await session.commit()

    async def rollback(self) -> None:
        session = self._require_session()
        await session.rollback()

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
