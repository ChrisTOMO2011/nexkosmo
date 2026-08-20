from uuid import UUID

from fastapi import APIRouter

from app.domain.errors import AuthorizationDenied
from app.interfaces.http.dependencies import (
    OperationalStatusServiceDependency,
    PrincipalDependency,
)

router = APIRouter(prefix="/v1/workspaces/{workspace_id}/operations", tags=["operations"])


@router.get("/delivery-status")
async def delivery_status(
    workspace_id: UUID,
    principal: PrincipalDependency,
    service: OperationalStatusServiceDependency,
) -> dict[str, object]:
    if workspace_id != principal.workspace_id:
        raise AuthorizationDenied(
            "The requested Workspace does not match the authenticated context."
        )
    return await service.get_delivery_status(principal)
