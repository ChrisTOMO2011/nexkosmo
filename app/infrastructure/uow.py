from types import TracebackType

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.domain.types import Principal


class SqlAlchemyUnitOfWork:
    def __init__(self, factory: async_sessionmaker[AsyncSession], principal: Principal) -> None:
        self._factory = factory
        self._principal = principal
        self.session: AsyncSession | None = None

    async def __aenter__(self) -> "SqlAlchemyUnitOfWork":
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
        return self

    async def commit(self) -> None:
        session = self._require_session()
        await session.commit()

    async def rollback(self) -> None:
        session = self._require_session()
        await session.rollback()

    def _require_session(self) -> AsyncSession:
        if self.session is None:
            raise RuntimeError("Unit of work has not been entered.")
        return self.session

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
