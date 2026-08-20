from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query

from app.application.character_service import CharacterMutationResult
from app.interfaces.http.character_schemas import (
    AssetListResponse,
    AssetManifestResponse,
    AssetSelectionRequest,
    ChangeSpeciesRequest,
    CharacterListResponse,
    CharacterMutationResponse,
    CharacterResponse,
    CreateCharacterRequest,
    DownstreamDependencyResponse,
    DownstreamStatusResponse,
    RemoveSelectionRequest,
    ReplaceAssetCollectionRequest,
    SpeciesResponse,
    SupportedTabsResponse,
    UpdateCharacterRequest,
    UpdateIdentityPropertiesRequest,
    UpdatePhysicalPropertiesRequest,
    UpdatePipelineStatusRequest,
    ValidateCharacterPackageRequest,
)
from app.interfaces.http.dependencies import (
    CharacterServiceDependency,
    IdempotencyKey,
    PrincipalDependency,
)

router = APIRouter(prefix="/api/v1", tags=["characters"])
PageLimit = Annotated[int, Query(ge=1, le=200)]
PageOffset = Annotated[int, Query(ge=0)]


def mutation_response(result: CharacterMutationResult) -> CharacterMutationResponse:
    replayed = result.replayed_response
    if replayed is not None:
        return CharacterMutationResponse.model_validate(replayed)
    return CharacterMutationResponse(
        character=CharacterResponse.from_domain(result.character),
        change_summary=result.change_summary,
    )


@router.get("/projects/{project_id}/characters")
async def list_project_characters(
    project_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    limit: PageLimit = 50,
    offset: PageOffset = 0,
) -> CharacterListResponse:
    characters = await service.list_project_characters(
        principal, project_id, limit=limit, offset=offset
    )
    return CharacterListResponse(
        items=tuple(CharacterResponse.from_domain(item) for item in characters),
        limit=limit,
        offset=offset,
    )


@router.get("/productions/{production_id}/characters")
async def list_production_characters(
    production_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    limit: PageLimit = 50,
    offset: PageOffset = 0,
) -> CharacterListResponse:
    characters = await service.list_production_characters(
        principal, production_id, limit=limit, offset=offset
    )
    return CharacterListResponse(
        items=tuple(CharacterResponse.from_domain(item) for item in characters),
        limit=limit,
        offset=offset,
    )


@router.post("/projects/{project_id}/characters", status_code=201)
async def create_character(
    project_id: UUID,
    body: CreateCharacterRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.create_character(
            principal,
            project_id=project_id,
            production_id=body.production_id,
            display_name=body.display_name,
            role=body.role,
            species_id=body.species_id,
            idempotency_key=idempotency_key,
        )
    )


@router.get("/characters/{character_id}")
async def get_character(
    character_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> CharacterResponse:
    return CharacterResponse.from_domain(await service.get_character(principal, character_id))


@router.patch("/characters/{character_id}")
async def update_character(
    character_id: UUID,
    body: UpdateCharacterRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.update_metadata(
            principal,
            character_id,
            expected_version=body.expected_version,
            display_name=body.display_name,
            role=body.role,
            idempotency_key=idempotency_key,
        )
    )


@router.post("/characters/{character_id}/change-species")
async def change_species(
    character_id: UUID,
    body: ChangeSpeciesRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.change_species(
            principal,
            character_id,
            species_id=body.species_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.patch("/characters/{character_id}/identity-properties")
async def update_identity_properties(
    character_id: UUID,
    body: UpdateIdentityPropertiesRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.update_identity_properties(
            principal,
            character_id,
            expected_version=body.expected_version,
            identity_type=body.identity_type,
            gender_presentation=body.gender_presentation,
            idempotency_key=idempotency_key,
        )
    )


@router.patch("/characters/{character_id}/physical-properties")
async def update_physical_properties(
    character_id: UUID,
    body: UpdatePhysicalPropertiesRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.update_physical_properties(
            principal,
            character_id,
            expected_version=body.expected_version,
            age=body.age,
            apparent_age=body.apparent_age,
            height_cm=body.height_cm,
            body_type=body.body_type,
            skin_tone=body.skin_tone,
            idempotency_key=idempotency_key,
        )
    )


@router.post("/characters/{character_id}/validate-package")
async def validate_character_package(
    character_id: UUID,
    body: ValidateCharacterPackageRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.validate_character_package(
            principal,
            character_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.put("/characters/{character_id}/selections/{category}")
async def select_asset(
    character_id: UUID,
    category: str,
    body: AssetSelectionRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.select_asset(
            principal,
            character_id,
            category=category,
            asset_id=body.asset_id,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.delete("/characters/{character_id}/selections/{category}")
async def remove_asset(
    character_id: UUID,
    category: str,
    body: RemoveSelectionRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.remove_asset_selection(
            principal,
            character_id,
            category=category,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.put("/characters/{character_id}/accessories")
async def replace_accessories(
    character_id: UUID,
    body: ReplaceAssetCollectionRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.replace_accessories(
            principal,
            character_id,
            asset_ids=body.asset_ids,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.put("/characters/{character_id}/wardrobe")
async def replace_wardrobe(
    character_id: UUID,
    body: ReplaceAssetCollectionRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.replace_wardrobe(
            principal,
            character_id,
            asset_ids=body.asset_ids,
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.put("/characters/{character_id}/pipeline-status")
async def update_pipeline_status(
    character_id: UUID,
    body: UpdatePipelineStatusRequest,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    idempotency_key: IdempotencyKey,
) -> CharacterMutationResponse:
    return mutation_response(
        await service.update_pipeline_status(
            principal,
            character_id,
            status=body.status,  # type: ignore[arg-type]
            expected_version=body.expected_version,
            idempotency_key=idempotency_key,
        )
    )


@router.get("/characters/{character_id}/compatible-assets")
async def compatible_assets(
    character_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    category: str | None = None,
    limit: PageLimit = 100,
    offset: PageOffset = 0,
) -> AssetListResponse:
    assets = await service.get_compatible_assets(
        principal,
        character_id,
        category=category,
        limit=limit,
        offset=offset,
    )
    return AssetListResponse(
        items=tuple(AssetManifestResponse.from_domain(item) for item in assets),
        limit=limit,
        offset=offset,
    )


@router.get("/characters/{character_id}/supported-tabs")
async def supported_tabs(
    character_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> SupportedTabsResponse:
    return SupportedTabsResponse(items=await service.get_supported_tabs(principal, character_id))


@router.get("/characters/{character_id}/downstream-status")
async def downstream_status(
    character_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> DownstreamStatusResponse:
    items = await service.get_downstream_status(principal, character_id)
    return DownstreamStatusResponse(
        items=tuple(
            DownstreamDependencyResponse(
                stage=item.stage,
                status=item.status,
                invalidated_at=item.invalidated_at,
                reason=item.reason,
            )
            for item in items
        )
    )


@router.get("/species")
async def list_species(
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> tuple[SpeciesResponse, ...]:
    return tuple(
        SpeciesResponse.from_domain(item) for item in await service.get_species_registry(principal)
    )


@router.get("/species/{species_id}")
async def get_species(
    species_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> SpeciesResponse:
    return SpeciesResponse.from_domain(await service.get_species(principal, species_id))


@router.get("/species/{species_id}/assets")
async def species_assets(
    species_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
    category: str | None = None,
    limit: PageLimit = 100,
    offset: PageOffset = 0,
) -> AssetListResponse:
    assets = await service.get_species_assets(
        principal,
        species_id,
        category=category,
        limit=limit,
        offset=offset,
    )
    return AssetListResponse(
        items=tuple(AssetManifestResponse.from_domain(item) for item in assets),
        limit=limit,
        offset=offset,
    )


@router.get("/assets/{asset_id}")
async def get_asset(
    asset_id: UUID,
    principal: PrincipalDependency,
    service: CharacterServiceDependency,
) -> AssetManifestResponse:
    return AssetManifestResponse.from_domain(await service.get_asset_manifest(principal, asset_id))
