from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, status

from app.domain.errors import AuthorizationDenied
from app.interfaces.http.dependencies import PrincipalDependency, ProjectServiceDependency
from app.interfaces.http.project_schemas import (
    CreateProductionRequest,
    CreateProjectRequest,
    ProductionResponse,
    ProjectResponse,
    ProjectVersionRequest,
    TransferOwnershipRequest,
    TransitionProductionRequest,
)

router = APIRouter(prefix="/v1/workspaces/{workspace_id}", tags=["projects"])
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=200)]


def _require_path_workspace(workspace_id: UUID, principal_workspace_id: UUID) -> None:
    if workspace_id != principal_workspace_id:
        raise AuthorizationDenied(
            "The requested Workspace does not match the authenticated context."
        )


@router.post("/projects", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: UUID,
    body: CreateProjectRequest,
    idempotency_key: IdempotencyKey,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.create_project(
        principal,
        name=body.name,
        idempotency_key=idempotency_key,
    )


@router.get("/projects", response_model=list[ProjectResponse])
async def list_projects(
    workspace_id: UUID,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> list[dict[str, object]]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.list_projects(principal)


@router.get("/projects/{project_id}", response_model=ProjectResponse)
async def get_project(
    workspace_id: UUID,
    project_id: UUID,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.get_project(principal, project_id=project_id)


@router.post("/projects/{project_id}/ownership", response_model=ProjectResponse)
async def transfer_project_ownership(
    workspace_id: UUID,
    project_id: UUID,
    body: TransferOwnershipRequest,
    idempotency_key: IdempotencyKey,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.transfer_ownership(
        principal,
        project_id=project_id,
        target_principal_id=body.target_principal_id,
        expected_version=body.expected_version,
        idempotency_key=idempotency_key,
    )


@router.post("/projects/{project_id}/archive", response_model=ProjectResponse)
async def archive_project(
    workspace_id: UUID,
    project_id: UUID,
    body: ProjectVersionRequest,
    idempotency_key: IdempotencyKey,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.set_project_archived(
        principal,
        project_id=project_id,
        archived=True,
        expected_version=body.expected_version,
        idempotency_key=idempotency_key,
    )


@router.post("/projects/{project_id}/restore", response_model=ProjectResponse)
async def restore_project(
    workspace_id: UUID,
    project_id: UUID,
    body: ProjectVersionRequest,
    idempotency_key: IdempotencyKey,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.set_project_archived(
        principal,
        project_id=project_id,
        archived=False,
        expected_version=body.expected_version,
        idempotency_key=idempotency_key,
    )


@router.post(
    "/projects/{project_id}/productions",
    response_model=ProductionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_production(
    workspace_id: UUID,
    project_id: UUID,
    body: CreateProductionRequest,
    idempotency_key: IdempotencyKey,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.create_production(
        principal,
        project_id=project_id,
        name=body.name,
        idempotency_key=idempotency_key,
    )


@router.post(
    "/projects/{project_id}/productions/{production_id}/state",
    response_model=ProductionResponse,
)
async def transition_production(
    workspace_id: UUID,
    project_id: UUID,
    production_id: UUID,
    body: TransitionProductionRequest,
    idempotency_key: IdempotencyKey,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    result = await service.transition_production(
        principal,
        project_id=project_id,
        production_id=production_id,
        target_state=body.target_state,
        expected_version=body.expected_version,
        idempotency_key=idempotency_key,
    )
    return result
