from typing import Annotated, cast
from uuid import UUID

from fastapi import APIRouter, Query

from app.application.project_service import (
    ProductionMutationResult,
    ProjectMutationResult,
)
from app.domain.projects import ProductionStatus, ProductionType, ProjectMemberRole
from app.interfaces.http.dependencies import (
    IdempotencyKey,
    PrincipalDependency,
    ProjectServiceDependency,
)
from app.interfaces.http.project_schemas import (
    CreateProductionRequest,
    CreateProjectRequest,
    ProductionListResponse,
    ProductionMutationResponse,
    ProductionResponse,
    ProjectListResponse,
    ProjectMutationResponse,
    ProjectResponse,
    RemoveProjectMemberRequest,
    SetProjectMemberRequest,
    UpdateProductionRequest,
    UpdateProjectRequest,
)

router = APIRouter(prefix="/api/v1", tags=["projects", "productions"])
PageLimit = Annotated[int, Query(ge=1, le=200)]
PageOffset = Annotated[int, Query(ge=0)]


def project_mutation_response(
    result: ProjectMutationResult,
) -> ProjectMutationResponse:
    if result.replayed_response is not None:
        return ProjectMutationResponse.model_validate(result.replayed_response)
    return ProjectMutationResponse(
        project=ProjectResponse.from_domain(result.project),
        change_summary=result.change_summary,
    )


def production_mutation_response(
    result: ProductionMutationResult,
) -> ProductionMutationResponse:
    if result.replayed_response is not None:
        return ProductionMutationResponse.model_validate(result.replayed_response)
    return ProductionMutationResponse(
        production=ProductionResponse.from_domain(result.production),
        change_summary=result.change_summary,
    )


@router.get("/projects")
async def list_projects(
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
    limit: PageLimit = 50,
    offset: PageOffset = 0,
) -> ProjectListResponse:
    projects = await service.list_workspace_projects(principal, limit=limit, offset=offset)
    return ProjectListResponse(
        items=tuple(ProjectResponse.from_domain(item) for item in projects),
        limit=limit,
        offset=offset,
    )


@router.post("/projects", status_code=201)
async def create_project(
    body: CreateProjectRequest,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
    idempotency_key: IdempotencyKey,
) -> ProjectMutationResponse:
    return project_mutation_response(
        await service.create_project(
            principal,
            name=body.name,
            description=body.description,
            idempotency_key=idempotency_key,
        )
    )


@router.get("/projects/{project_id}")
async def get_project(
    project_id: UUID,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> ProjectResponse:
    return ProjectResponse.from_domain(await service.get_project(principal, project_id))


@router.patch("/projects/{project_id}")
async def update_project(
    project_id: UUID,
    body: UpdateProjectRequest,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
    idempotency_key: IdempotencyKey,
) -> ProjectMutationResponse:
    return project_mutation_response(
        await service.update_project(
            principal,
            project_id,
            expected_version=body.expected_version,
            name=body.name,
            description=body.description,
            status=body.status,
            idempotency_key=idempotency_key,
        )
    )


@router.put("/projects/{project_id}/members/{member_id}")
async def set_project_member(
    project_id: UUID,
    member_id: UUID,
    body: SetProjectMemberRequest,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
    idempotency_key: IdempotencyKey,
) -> ProjectMutationResponse:
    return project_mutation_response(
        await service.set_project_member_role(
            principal,
            project_id,
            member_id,
            role=cast(ProjectMemberRole, body.role),
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.delete("/projects/{project_id}/members/{member_id}")
async def remove_project_member(
    project_id: UUID,
    member_id: UUID,
    body: RemoveProjectMemberRequest,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
    idempotency_key: IdempotencyKey,
) -> ProjectMutationResponse:
    return project_mutation_response(
        await service.remove_project_member(
            principal,
            project_id,
            member_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.get("/projects/{project_id}/productions")
async def list_project_productions(
    project_id: UUID,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
    limit: PageLimit = 50,
    offset: PageOffset = 0,
) -> ProductionListResponse:
    productions = await service.list_project_productions(
        principal, project_id, limit=limit, offset=offset
    )
    return ProductionListResponse(
        items=tuple(ProductionResponse.from_domain(item) for item in productions),
        limit=limit,
        offset=offset,
    )


@router.post("/projects/{project_id}/productions", status_code=201)
async def create_production(
    project_id: UUID,
    body: CreateProductionRequest,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
    idempotency_key: IdempotencyKey,
) -> ProductionMutationResponse:
    return production_mutation_response(
        await service.create_production(
            principal,
            project_id,
            name=body.name,
            production_type=cast(ProductionType, body.production_type),
            idempotency_key=idempotency_key,
        )
    )


@router.get("/productions/{production_id}")
async def get_production(
    production_id: UUID,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
) -> ProductionResponse:
    return ProductionResponse.from_domain(await service.get_production(principal, production_id))


@router.patch("/productions/{production_id}")
async def update_production(
    production_id: UUID,
    body: UpdateProductionRequest,
    principal: PrincipalDependency,
    service: ProjectServiceDependency,
    idempotency_key: IdempotencyKey,
) -> ProductionMutationResponse:
    return production_mutation_response(
        await service.update_production(
            principal,
            production_id,
            expected_version=body.expected_version,
            name=body.name,
            status=cast(ProductionStatus | None, body.status),
            idempotency_key=idempotency_key,
        )
    )
