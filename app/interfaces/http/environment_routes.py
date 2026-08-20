from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.application.environment_service import EnvironmentMutationResult
from app.interfaces.http.dependencies import (
    EnvironmentServiceDependency,
    IdempotencyKey,
    PrincipalDependency,
)
from app.interfaces.http.environment_schemas import (
    ChangeEnvironmentTypeRequest,
    CreateEnvironmentRequest,
    CreateProductionEnvironmentRequest,
    EnvironmentAssetListResponse,
    EnvironmentAssetResponse,
    EnvironmentAssetSelectionRequest,
    EnvironmentListResponse,
    EnvironmentMutationResponse,
    EnvironmentReadinessResponse,
    EnvironmentResponse,
    EnvironmentSupportedTabsResponse,
    EnvironmentTypeResponse,
    RemoveEnvironmentAssetRequest,
    ReplaceEnvironmentAssetsRequest,
    UpdateEnvironmentIdentityRequest,
    UpdateEnvironmentPropertiesRequest,
    ValidateEnvironmentPackageRequest,
)

router = APIRouter(prefix="/api/v1", tags=["environments"])
PageLimit = Annotated[int, Query(ge=1, le=500)]
PageOffset = Annotated[int, Query(ge=0)]


def mutation_response(result: EnvironmentMutationResult) -> EnvironmentMutationResponse:
    if result.replayed_response is not None:
        return EnvironmentMutationResponse.model_validate(result.replayed_response)
    return EnvironmentMutationResponse(
        environment=EnvironmentResponse.from_domain(result.environment),
        change_summary=result.change_summary,
    )


@router.get("/environment-types")
async def list_environment_types(
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
) -> tuple[EnvironmentTypeResponse, ...]:
    return tuple(
        EnvironmentTypeResponse.from_domain(item)
        for item in await service.list_environment_types(principal)
    )


@router.post("/projects/{project_id}/environments", status_code=201)
async def create_environment(
    project_id: UUID,
    body: CreateEnvironmentRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return mutation_response(
        await service.create_environment(
            principal,
            project_id=project_id,
            production_id=body.production_id,
            display_name=body.display_name,
            environment_type_id=body.environment_type_id,
            description=body.description,
            idempotency_key=idempotency_key,
        )
    )


@router.get("/projects/{project_id}/environments")
async def list_project_environments(
    project_id: UUID,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    limit: PageLimit = 50,
    offset: PageOffset = 0,
) -> EnvironmentListResponse:
    items = await service.list_project_environments(
        principal, project_id, limit=limit, offset=offset
    )
    return EnvironmentListResponse(
        items=tuple(EnvironmentResponse.from_domain(item) for item in items),
        limit=limit,
        offset=offset,
    )


@router.get("/productions/{production_id}/environments")
async def list_production_environments(
    production_id: UUID,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    limit: PageLimit = 50,
    offset: PageOffset = 0,
) -> EnvironmentListResponse:
    items = await service.list_production_environments(
        principal, production_id, limit=limit, offset=offset
    )
    return EnvironmentListResponse(
        items=tuple(EnvironmentResponse.from_domain(item) for item in items),
        limit=limit,
        offset=offset,
    )


@router.post("/productions/{production_id}/environments", status_code=201)
async def create_production_environment(
    production_id: UUID,
    body: CreateProductionEnvironmentRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return mutation_response(
        await service.create_production_environment(
            principal,
            production_id=production_id,
            display_name=body.display_name,
            environment_type_id=body.environment_type_id,
            description=body.description,
            idempotency_key=idempotency_key,
        )
    )


@router.get("/environments/{environment_id}")
async def get_environment(
    environment_id: UUID,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
) -> EnvironmentResponse:
    return EnvironmentResponse.from_domain(await service.get_environment(principal, environment_id))


@router.patch("/environments/{environment_id}/properties")
async def update_environment_properties(
    environment_id: UUID,
    body: UpdateEnvironmentPropertiesRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    payload = body.model_dump(exclude={"expected_version"}, exclude_none=True)
    return mutation_response(
        await service.update_properties(
            principal,
            environment_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
            **payload,
        )
    )


@router.patch("/environments/{environment_id}/identity")
async def update_environment_identity(
    environment_id: UUID,
    body: UpdateEnvironmentIdentityRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return mutation_response(
        await service.update_identity(
            principal,
            environment_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
            display_name=body.display_name,
            description=body.description,
        )
    )


@router.post("/environments/{environment_id}/change-type")
async def change_environment_type(
    environment_id: UUID,
    body: ChangeEnvironmentTypeRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return mutation_response(
        await service.change_type(
            principal,
            environment_id,
            environment_type_id=body.environment_type_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.put("/environments/{environment_id}/selections/{category}")
async def select_environment_asset(
    environment_id: UUID,
    category: str,
    body: EnvironmentAssetSelectionRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return mutation_response(
        await service.select_asset(
            principal,
            environment_id,
            category=category,
            asset_id=body.asset_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.put("/environments/{environment_id}/collections/{category}")
async def replace_environment_assets(
    environment_id: UUID,
    category: str,
    body: ReplaceEnvironmentAssetsRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return mutation_response(
        await service.replace_assets(
            principal,
            environment_id,
            category=category,
            asset_ids=body.asset_ids,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.delete("/environments/{environment_id}/selections/{category}")
async def remove_environment_asset(
    environment_id: UUID,
    category: str,
    body: RemoveEnvironmentAssetRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return mutation_response(
        await service.remove_asset(
            principal,
            environment_id,
            category=category,
            asset_id=body.asset_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.post("/environments/{environment_id}/validate-package")
async def validate_environment_package(
    environment_id: UUID,
    body: ValidateEnvironmentPackageRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return mutation_response(
        await service.validate_package(
            principal,
            environment_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.post("/environments/{environment_id}/validate")
async def validate_environment(
    environment_id: UUID,
    body: ValidateEnvironmentPackageRequest,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    idempotency_key: IdempotencyKey,
) -> EnvironmentMutationResponse:
    return await validate_environment_package(
        environment_id, body, principal, service, idempotency_key
    )


@router.get("/environments/{environment_id}/readiness")
async def environment_readiness(
    environment_id: UUID,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
) -> EnvironmentReadinessResponse:
    return EnvironmentReadinessResponse.from_domain(
        await service.get_readiness(principal, environment_id)
    )


@router.get("/environments/{environment_id}/compatible-assets")
async def compatible_environment_assets(
    environment_id: UUID,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
    category: str | None = None,
    subcategory: str | None = None,
    limit: PageLimit = 100,
    offset: PageOffset = 0,
) -> EnvironmentAssetListResponse:
    items = await service.get_compatible_assets(
        principal,
        environment_id,
        category=category,
        subcategory=subcategory,
        limit=limit,
        offset=offset,
    )
    return EnvironmentAssetListResponse(
        items=tuple(EnvironmentAssetResponse.from_domain(item) for item in items),
        limit=limit,
        offset=offset,
    )


@router.get("/environments/{environment_id}/supported-tabs")
async def supported_environment_tabs(
    environment_id: UUID,
    principal: PrincipalDependency,
    service: EnvironmentServiceDependency,
) -> EnvironmentSupportedTabsResponse:
    return EnvironmentSupportedTabsResponse(
        items=await service.get_supported_tabs(principal, environment_id)
    )
