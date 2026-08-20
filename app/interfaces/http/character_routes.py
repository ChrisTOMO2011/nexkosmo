from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, status

from app.domain.errors import AuthorizationDenied
from app.interfaces.http.character_schemas import (
    CharacterResponse,
    CreateCharacterRequest,
    UpdateCharacterRequest,
)
from app.interfaces.http.dependencies import CharacterServiceDependency, PrincipalDependency

router = APIRouter(
    prefix="/v1/workspaces/{workspace_id}/projects/{project_id}/characters",
    tags=["characters"],
)
IdempotencyKey = Annotated[str, Header(alias="Idempotency-Key", min_length=1, max_length=200)]


def _require_path_workspace(workspace_id: UUID, principal_workspace_id: UUID) -> None:
    if workspace_id != principal_workspace_id:
        raise AuthorizationDenied(
            "The requested Workspace does not match the authenticated context."
        )


@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
async def create_character(
    workspace_id: UUID,
    project_id: UUID,
    body: CreateCharacterRequest,
    idempotency_key: IdempotencyKey,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.create_character(
        principal,
        project_id=project_id,
        display_name=body.display_name,
        role_label=body.role_label,
        idempotency_key=idempotency_key,
    )


@router.get("", response_model=list[CharacterResponse])
async def list_characters(
    workspace_id: UUID,
    project_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> list[dict[str, object]]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.list_characters(principal, project_id=project_id)


@router.get("/{character_id}", response_model=CharacterResponse)
async def get_character(
    workspace_id: UUID,
    project_id: UUID,
    character_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.get_character(
        principal,
        project_id=project_id,
        character_id=character_id,
    )


@router.patch("/{character_id}", response_model=CharacterResponse)
async def update_character(
    workspace_id: UUID,
    project_id: UUID,
    character_id: UUID,
    body: UpdateCharacterRequest,
    idempotency_key: IdempotencyKey,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> dict[str, object]:
    _require_path_workspace(workspace_id, principal.workspace_id)
    return await service.update_character(
        principal,
        project_id=project_id,
        character_id=character_id,
        expected_version=body.expected_version,
        display_name=body.display_name,
        role_label=body.role_label,
        replace_role_label="role_label" in body.model_fields_set,
        idempotency_key=idempotency_key,
    )
