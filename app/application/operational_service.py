from datetime import UTC, datetime
from typing import Any

from app.application.ports import UnitOfWorkFactory
from app.domain.enums import AgentKind
from app.domain.errors import AuthorizationDenied
from app.domain.types import Principal


class OperationalStatusService:
    def __init__(self, uow_factory: UnitOfWorkFactory) -> None:
        self._uow_factory = uow_factory

    async def get_delivery_status(self, principal: Principal) -> dict[str, Any]:
        if principal.agent_kind is not AgentKind.HUMAN:
            raise AuthorizationDenied("A human actor is required for operational status.")
        now = datetime.now(UTC)
        async with self._uow_factory(principal) as uow:
            await uow.workspace_authority.require_current_human_role(
                workspace_id=principal.workspace_id,
                principal_id=principal.principal_id,
                agent_id=principal.agent_id,
                at=now,
            )
            return await uow.operational_status.delivery_status(
                workspace_id=principal.workspace_id
            )
