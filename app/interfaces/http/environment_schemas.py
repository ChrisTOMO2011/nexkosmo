from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import Field, model_validator

from app.domain.environments import (
    Environment,
    EnvironmentAssetManifest,
    EnvironmentReadiness,
    EnvironmentType,
)
from app.interfaces.http.character_schemas import StrictModel


class EnvironmentResponse(StrictModel):
    environment_id: UUID
    workspace_id: UUID
    project_id: UUID
    production_id: UUID
    display_name: str
    description: str
    environment_type_id: UUID
    location_type: str
    interior_exterior: str
    biome: str
    climate_profile: str
    terrain_profile_id: UUID | None
    weather_profile_id: UUID | None
    time_of_day: str
    atmosphere_profile_id: UUID | None
    background_asset_ids: tuple[UUID, ...]
    terrain_asset_ids: tuple[UUID, ...]
    building_asset_ids: tuple[UUID, ...]
    nature_asset_ids: tuple[UUID, ...]
    practical_asset_ids: tuple[UUID, ...]
    material_profile_ids: tuple[UUID, ...]
    texture_profile_ids: tuple[UUID, ...]
    detail_asset_ids: tuple[UUID, ...]
    style_profile_id: UUID | None
    lighting_compatibility_profile_id: UUID | None
    camera_compatibility_profile_id: UUID | None
    audio_compatibility_profile_id: UUID | None
    vfx_compatibility_profile_id: UUID | None
    preview_asset_id: UUID | None
    scale: int
    navigation_constraints: str
    camera_access_constraints: str
    package_status: str
    readiness_status: str
    validation_issues: tuple[dict[str, object], ...]
    readiness_warnings: tuple[dict[str, object], ...]
    missing_requirements: tuple[str, ...]
    invalid_asset_ids: tuple[UUID, ...]
    required_processing_jobs: tuple[str, ...]
    readiness_validated_version: int | None
    readiness_validated_at: datetime | None
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, environment: Environment) -> Self:
        return cls(**{field: getattr(environment, field) for field in cls.model_fields})


class EnvironmentMutationResponse(StrictModel):
    environment: EnvironmentResponse
    change_summary: dict[str, Any] = Field(default_factory=dict)


class EnvironmentListResponse(StrictModel):
    items: tuple[EnvironmentResponse, ...]
    limit: int
    offset: int


class CreateEnvironmentRequest(StrictModel):
    production_id: UUID
    display_name: str = Field(min_length=1, max_length=160)
    environment_type_id: UUID
    description: str = Field(default="", max_length=2000)


class CreateProductionEnvironmentRequest(StrictModel):
    display_name: str = Field(min_length=1, max_length=160)
    environment_type_id: UUID
    description: str = Field(default="", max_length=2000)


class UpdateEnvironmentIdentityRequest(StrictModel):
    expected_version: int = Field(ge=1)
    display_name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)

    @model_validator(mode="after")
    def require_identity_update(self) -> Self:
        if self.display_name is None and self.description is None:
            raise ValueError("At least one Environment identity field is required.")
        return self


class UpdateEnvironmentPropertiesRequest(StrictModel):
    expected_version: int = Field(ge=1)
    display_name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=2000)
    location_type: str | None = Field(
        default=None,
        pattern=(
            "^(room|corridor|street|plaza|building|landscape|vehicle-interior|"
            "spacecraft-interior|abstract-environment|custom)$"
        ),
    )
    interior_exterior: str | None = Field(
        default=None, pattern="^(interior|exterior|mixed|virtual|studio-stage)$"
    )
    biome: str | None = Field(default=None, min_length=1, max_length=80)
    climate_profile: str | None = Field(default=None, min_length=1, max_length=80)
    time_of_day: str | None = Field(default=None, min_length=1, max_length=80)
    scale: int | None = Field(default=None, ge=1, le=1000)
    navigation_constraints: str | None = Field(default=None, max_length=1000)
    camera_access_constraints: str | None = Field(default=None, max_length=1000)
    weather_profile_id: UUID | None = None
    atmosphere_profile_id: UUID | None = None
    style_profile_id: UUID | None = None
    lighting_compatibility_profile_id: UUID | None = None
    camera_compatibility_profile_id: UUID | None = None
    audio_compatibility_profile_id: UUID | None = None
    vfx_compatibility_profile_id: UUID | None = None

    @model_validator(mode="after")
    def require_update(self) -> Self:
        if all(
            getattr(self, field) is None
            for field in type(self).model_fields
            if field != "expected_version"
        ):
            raise ValueError("At least one Environment property is required.")
        return self


class ChangeEnvironmentTypeRequest(StrictModel):
    environment_type_id: UUID
    expected_version: int = Field(ge=1)


class EnvironmentAssetSelectionRequest(StrictModel):
    asset_id: UUID
    expected_version: int = Field(ge=1)


class ReplaceEnvironmentAssetsRequest(StrictModel):
    asset_ids: tuple[UUID, ...]
    expected_version: int = Field(ge=1)


class RemoveEnvironmentAssetRequest(StrictModel):
    expected_version: int = Field(ge=1)
    asset_id: UUID | None = None


class ValidateEnvironmentPackageRequest(StrictModel):
    expected_version: int = Field(ge=1)


class EnvironmentTypeResponse(StrictModel):
    environment_type_id: UUID
    key: str
    name: str
    enabled: bool
    capabilities: frozenset[str]
    supported_tabs: tuple[str, ...]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, environment_type: EnvironmentType) -> Self:
        return cls(**{field: getattr(environment_type, field) for field in cls.model_fields})


class EnvironmentAssetResponse(StrictModel):
    asset_id: UUID
    name: str
    category: str
    subcategory: str
    thumbnail_reference: str
    preview_reference: str
    visibility: str
    status: str
    source: str
    uploaded: bool
    generated: bool
    placeholder: bool
    version: int

    @classmethod
    def from_domain(cls, asset: EnvironmentAssetManifest) -> Self:
        # Storage references, provenance, dependencies, and internal profiles are not exposed.
        return cls(**{field: getattr(asset, field) for field in cls.model_fields})


class EnvironmentAssetListResponse(StrictModel):
    items: tuple[EnvironmentAssetResponse, ...]
    limit: int
    offset: int


class EnvironmentSupportedTabsResponse(StrictModel):
    items: tuple[str, ...]


class EnvironmentReadinessResponse(StrictModel):
    readiness_status: str
    blocking_issues: tuple[dict[str, object], ...]
    warnings: tuple[dict[str, object], ...]
    missing_requirements: tuple[str, ...]
    invalid_asset_ids: tuple[UUID, ...]
    required_processing_jobs: tuple[str, ...]
    validated_version: int | None
    validated_at: datetime | None

    @classmethod
    def from_domain(cls, readiness: EnvironmentReadiness) -> Self:
        return cls(**{field: getattr(readiness, field) for field in cls.model_fields})
