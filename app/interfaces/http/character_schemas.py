from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.characters import Character, CharacterAssetManifest, Species


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DownstreamDependencyResponse(StrictModel):
    stage: str
    status: str
    invalidated_at: datetime | None
    reason: str | None


class CharacterResponse(StrictModel):
    character_id: UUID
    project_id: UUID
    production_id: UUID
    display_name: str
    role: str
    identity_type: str
    age: int
    apparent_age: int
    height_cm: int
    body_type: str
    skin_tone: int
    gender_presentation: str | None
    physical_profile_version: int
    species_id: UUID
    type_id: UUID | None
    style_profile_id: UUID | None
    identity_id: UUID | None
    face_id: UUID | None
    hair_id: UUID | None
    skin_id: UUID | None
    eyes_id: UUID | None
    beard_id: UUID | None
    body_id: UUID | None
    age_preset_id: UUID | None
    expression_id: UUID | None
    wardrobe_ids: tuple[UUID, ...]
    accessory_ids: tuple[UUID, ...]
    rig_id: UUID | None
    skeleton_id: UUID | None
    material_ids: tuple[UUID, ...]
    texture_ids: tuple[UUID, ...]
    animation_ids: tuple[UUID, ...]
    voice_id: UUID | None
    uploaded_asset_ids: tuple[UUID, ...]
    generated_asset_ids: tuple[UUID, ...]
    preview_asset_id: UUID | None
    compatibility_profile_id: UUID
    pipeline_status: str
    readiness_status: str
    validation_issues: tuple[dict[str, Any], ...]
    validated_version: int | None
    validated_at: datetime | None
    downstream_status: tuple[DownstreamDependencyResponse, ...]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, character: Character) -> Self:
        return cls(
            **{
                field: getattr(character, field)
                for field in cls.model_fields
                if field != "downstream_status"
            },
            downstream_status=tuple(
                DownstreamDependencyResponse(
                    stage=item.stage,
                    status=item.status,
                    invalidated_at=item.invalidated_at,
                    reason=item.reason,
                )
                for item in character.downstream_status
            ),
        )


class CharacterMutationResponse(StrictModel):
    character: CharacterResponse
    change_summary: dict[str, Any] = Field(default_factory=dict)


class CharacterListResponse(StrictModel):
    items: tuple[CharacterResponse, ...]
    limit: int
    offset: int


class CreateCharacterRequest(StrictModel):
    production_id: UUID
    display_name: str = Field(min_length=1, max_length=160)
    role: str = Field(pattern="^(Lead|Co-Lead|Supporting|Background|Creature|Custom)$")
    species_id: UUID


class UpdateCharacterRequest(StrictModel):
    expected_version: int = Field(ge=1)
    display_name: str | None = Field(default=None, min_length=1, max_length=160)
    role: str | None = Field(
        default=None,
        pattern="^(Lead|Co-Lead|Supporting|Background|Creature|Custom)$",
    )

    @model_validator(mode="after")
    def require_update(self) -> Self:
        if self.display_name is None and self.role is None:
            raise ValueError("At least one character metadata field is required.")
        return self


class ChangeSpeciesRequest(StrictModel):
    species_id: UUID
    expected_version: int = Field(ge=1)


class UpdateIdentityPropertiesRequest(StrictModel):
    expected_version: int = Field(ge=1)
    identity_type: str | None = Field(default=None, min_length=1, max_length=80)
    gender_presentation: str | None = Field(default=None, max_length=80)

    @model_validator(mode="after")
    def require_update(self) -> Self:
        if self.identity_type is None and self.gender_presentation is None:
            raise ValueError("At least one identity property is required.")
        return self


class UpdatePhysicalPropertiesRequest(StrictModel):
    expected_version: int = Field(ge=1)
    age: int | None = Field(default=None, ge=0, le=2000)
    apparent_age: int | None = Field(default=None, ge=0, le=2000)
    height_cm: int | None = Field(default=None, ge=30, le=400)
    body_type: str | None = Field(default=None, min_length=1, max_length=80)
    skin_tone: int | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def require_update(self) -> Self:
        if all(
            value is None
            for value in (
                self.age,
                self.apparent_age,
                self.height_cm,
                self.body_type,
                self.skin_tone,
            )
        ):
            raise ValueError("At least one physical property is required.")
        return self


class ValidateCharacterPackageRequest(StrictModel):
    expected_version: int = Field(ge=1)


class AssetSelectionRequest(StrictModel):
    asset_id: UUID
    expected_version: int = Field(ge=1)


class RemoveSelectionRequest(StrictModel):
    expected_version: int = Field(ge=1)


class ReplaceAssetCollectionRequest(StrictModel):
    asset_ids: tuple[UUID, ...]
    expected_version: int = Field(ge=1)


class UpdatePipelineStatusRequest(StrictModel):
    status: str = Field(pattern="^(draft|validating|preview-pending|ready|blocked|archived)$")
    expected_version: int = Field(ge=1)


class SpeciesResponse(StrictModel):
    species_id: UUID
    key: str
    name: str
    category: str
    enabled: bool
    capabilities: frozenset[str]
    supported_tabs: tuple[str, ...]
    compatibility_profile_id: UUID
    default_rig_id: UUID | None
    default_skeleton_id: UUID | None
    default_material_profile_id: UUID | None
    default_body_id: UUID | None
    min_age: int
    max_age: int
    min_height_cm: int
    max_height_cm: int
    surface_control_label: str
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, species: Species) -> Self:
        return cls(**{field: getattr(species, field) for field in cls.model_fields})


class AssetManifestResponse(StrictModel):
    asset_id: UUID
    name: str
    species_ids: tuple[UUID, ...]
    type_ids: tuple[UUID, ...]
    category: str
    subcategory: str
    thumbnail_reference: str | None
    preview_reference: str | None
    source: str
    status: str
    tags: frozenset[str]
    gender_compatibility: tuple[str, ...]
    age_compatibility: tuple[str, ...]
    body_compatibility: tuple[UUID, ...]
    rig_compatibility: tuple[UUID, ...]
    skeleton_compatibility: tuple[UUID, ...]
    material_compatibility: tuple[UUID, ...]
    required_capabilities: frozenset[str]
    incompatible_asset_ids: tuple[UUID, ...]
    dependent_asset_ids: tuple[UUID, ...]
    generated: bool
    uploaded: bool
    visibility: str
    attachment_point: str | None
    compatible_body_regions: tuple[str, ...]
    profile_metadata: dict[str, Any]
    version: int
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, asset: CharacterAssetManifest) -> Self:
        # file_references and provenance are deliberately not exposed.
        return cls(**{field: getattr(asset, field) for field in cls.model_fields})


class AssetListResponse(StrictModel):
    items: tuple[AssetManifestResponse, ...]
    limit: int
    offset: int


class SupportedTabsResponse(StrictModel):
    items: tuple[str, ...]


class DownstreamStatusResponse(StrictModel):
    items: tuple[DownstreamDependencyResponse, ...]
