from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any, Literal, Self, cast
from uuid import UUID, uuid4

from app.domain.errors import InvariantViolation

CharacterRole = Literal["Lead", "Co-Lead", "Supporting", "Background", "Creature", "Custom"]
PipelineStatus = Literal["draft", "validating", "preview-pending", "ready", "blocked", "archived"]
DownstreamState = Literal["valid", "stale", "blocked", "pending"]
AssetCategory = Literal[
    "type",
    "style-profile",
    "identity",
    "face",
    "hair",
    "skin",
    "eyes",
    "beard",
    "body",
    "age-preset",
    "expression",
    "wardrobe",
    "accessory",
    "rig",
    "skeleton",
    "material",
    "texture",
    "animation",
    "voice",
    "preview",
    "uploaded-source",
    "generated-output",
]

SCALAR_SELECTION_FIELDS: dict[str, str] = {
    "type": "type_id",
    "style-profile": "style_profile_id",
    "identity": "identity_id",
    "face": "face_id",
    "hair": "hair_id",
    "skin": "skin_id",
    "eyes": "eyes_id",
    "beard": "beard_id",
    "body": "body_id",
    "age-preset": "age_preset_id",
    "expression": "expression_id",
    "rig": "rig_id",
    "skeleton": "skeleton_id",
    "voice": "voice_id",
}
CHARACTER_ROLES = frozenset({"Lead", "Co-Lead", "Supporting", "Background", "Creature", "Custom"})
PIPELINE_STATUSES = frozenset(
    {"draft", "validating", "preview-pending", "ready", "blocked", "archived"}
)


@dataclass(frozen=True, slots=True)
class DownstreamDependency:
    stage: str
    status: DownstreamState
    invalidated_at: datetime | None = None
    reason: str | None = None

    def __post_init__(self) -> None:
        if not self.stage.strip():
            raise InvariantViolation("Downstream dependency stage is required.")
        if self.status == "stale" and self.invalidated_at is None:
            raise InvariantViolation("Stale downstream dependencies require an invalidation time.")


@dataclass(frozen=True, slots=True)
class Character:
    character_id: UUID
    workspace_id: UUID
    project_id: UUID
    production_id: UUID
    display_name: str
    role: CharacterRole
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
    pipeline_status: PipelineStatus
    readiness_status: str
    validation_issues: tuple[dict[str, object], ...]
    validated_version: int | None
    validated_at: datetime | None
    downstream_status: tuple[DownstreamDependency, ...]
    version: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.display_name.strip():
            raise InvariantViolation("Character display name is required.")
        if self.display_name != self.display_name.strip():
            raise InvariantViolation("Character display name must be trimmed.")
        if self.role not in CHARACTER_ROLES:
            raise InvariantViolation("Character role is not supported.")
        if self.pipeline_status not in PIPELINE_STATUSES:
            raise InvariantViolation("Character pipeline status is not supported.")
        if self.readiness_status not in {
            "incomplete",
            "invalid",
            "processing-required",
            "ready-for-set",
        }:
            raise InvariantViolation("Character readiness status is not supported.")
        if not self.identity_type.strip():
            raise InvariantViolation("Character identity type is required.")
        if not 0 <= self.age <= 2000 or not 0 <= self.apparent_age <= 2000:
            raise InvariantViolation("Character age must be between 0 and 2000.")
        if not 30 <= self.height_cm <= 400:
            raise InvariantViolation("Character height must be between 30 and 400 cm.")
        if not self.body_type.strip():
            raise InvariantViolation("Character body type is required.")
        if not 0 <= self.skin_tone <= 100:
            raise InvariantViolation("Character skin tone must be between 0 and 100.")
        if self.physical_profile_version < 1:
            raise InvariantViolation("Physical profile version must be positive.")
        if self.version < 1:
            raise InvariantViolation("Character version must be positive.")
        if self.updated_at < self.created_at:
            raise InvariantViolation("Character updated_at cannot precede created_at.")
        for field_name in (
            "wardrobe_ids",
            "accessory_ids",
            "material_ids",
            "texture_ids",
            "animation_ids",
            "uploaded_asset_ids",
            "generated_asset_ids",
        ):
            values = getattr(self, field_name)
            if len(values) != len(set(values)):
                raise InvariantViolation(f"{field_name} cannot contain duplicate asset IDs.")
        stages = [dependency.stage for dependency in self.downstream_status]
        if len(stages) != len(set(stages)):
            raise InvariantViolation("Downstream dependency stages must be unique.")

    @classmethod
    def create(
        cls,
        *,
        workspace_id: UUID,
        project_id: UUID,
        production_id: UUID,
        display_name: str,
        role: CharacterRole,
        species_id: UUID,
        compatibility_profile_id: UUID,
        character_id: UUID | None = None,
        type_id: UUID | None = None,
        style_profile_id: UUID | None = None,
        identity_id: UUID | None = None,
        identity_type: str = "Human Male",
        age: int = 35,
        apparent_age: int = 35,
        height_cm: int = 180,
        body_type: str = "Athletic",
        skin_tone: int = 89,
        gender_presentation: str | None = None,
        body_id: UUID | None = None,
        rig_id: UUID | None = None,
        skeleton_id: UUID | None = None,
        material_ids: tuple[UUID, ...] = (),
        preview_asset_id: UUID | None = None,
        now: datetime | None = None,
    ) -> Self:
        timestamp = now or datetime.now(UTC)
        return cls(
            character_id=character_id or uuid4(),
            workspace_id=workspace_id,
            project_id=project_id,
            production_id=production_id,
            display_name=display_name.strip(),
            role=role,
            identity_type=identity_type.strip(),
            age=age,
            apparent_age=apparent_age,
            height_cm=height_cm,
            body_type=body_type.strip(),
            skin_tone=skin_tone,
            gender_presentation=gender_presentation,
            physical_profile_version=1,
            species_id=species_id,
            type_id=type_id,
            style_profile_id=style_profile_id,
            identity_id=identity_id,
            face_id=None,
            hair_id=None,
            skin_id=None,
            eyes_id=None,
            beard_id=None,
            body_id=body_id,
            age_preset_id=None,
            expression_id=None,
            wardrobe_ids=(),
            accessory_ids=(),
            rig_id=rig_id,
            skeleton_id=skeleton_id,
            material_ids=material_ids,
            texture_ids=(),
            animation_ids=(),
            voice_id=None,
            uploaded_asset_ids=(),
            generated_asset_ids=(),
            preview_asset_id=preview_asset_id,
            compatibility_profile_id=compatibility_profile_id,
            pipeline_status="draft",
            readiness_status="incomplete",
            validation_issues=(),
            validated_version=None,
            validated_at=None,
            downstream_status=(),
            version=1,
            created_at=timestamp,
            updated_at=timestamp,
        )

    def _evolve(self, *, now: datetime | None = None, **changes: object) -> Self:
        if "readiness_status" not in changes and any(
            getattr(self, key) != value for key, value in changes.items()
        ):
            changes = {
                **changes,
                "readiness_status": "incomplete",
                "validation_issues": (),
                "validated_version": None,
                "validated_at": None,
            }
        effective = {key: value for key, value in changes.items() if getattr(self, key) != value}
        if not effective:
            return self
        return replace(
            self,
            **cast(Any, effective),
            version=self.version + 1,
            updated_at=now or datetime.now(UTC),
        )

    def rename(self, display_name: str, *, now: datetime | None = None) -> Self:
        name = display_name.strip()
        if not name:
            raise InvariantViolation("Character display name is required.")
        return self._evolve(display_name=name, now=now)

    def update_metadata(
        self,
        *,
        display_name: str | None = None,
        role: CharacterRole | None = None,
        now: datetime | None = None,
    ) -> Self:
        changes: dict[str, object] = {}
        if display_name is not None:
            name = display_name.strip()
            if not name:
                raise InvariantViolation("Character display name is required.")
            changes["display_name"] = name
        if role is not None:
            changes["role"] = role
        if not changes:
            return self
        return self._evolve(now=now, **changes)

    def update_identity_properties(
        self,
        *,
        identity_type: str | None = None,
        gender_presentation: str | None = None,
        now: datetime | None = None,
    ) -> Self:
        changes: dict[str, object] = {}
        if identity_type is not None:
            value = identity_type.strip()
            if not value:
                raise InvariantViolation("Character identity type is required.")
            changes["identity_type"] = value
        if gender_presentation is not None:
            changes["gender_presentation"] = gender_presentation.strip() or None
        return self._evolve(now=now, **changes)

    def update_physical_properties(
        self,
        *,
        age: int | None = None,
        apparent_age: int | None = None,
        height_cm: int | None = None,
        body_type: str | None = None,
        skin_tone: int | None = None,
        now: datetime | None = None,
    ) -> Self:
        changes: dict[str, object] = {}
        for field_name, value in {
            "age": age,
            "apparent_age": apparent_age,
            "height_cm": height_cm,
            "skin_tone": skin_tone,
        }.items():
            if value is not None:
                changes[field_name] = value
        if body_type is not None:
            body_value = body_type.strip()
            if not body_value:
                raise InvariantViolation("Character body type is required.")
            changes["body_type"] = body_value
        if changes and any(getattr(self, key) != value for key, value in changes.items()):
            changes["physical_profile_version"] = self.physical_profile_version + 1
        return self._evolve(now=now, **changes)

    def update_readiness(
        self,
        *,
        status: str,
        issues: tuple[dict[str, object], ...],
        now: datetime | None = None,
    ) -> Self:
        timestamp = now or datetime.now(UTC)
        if (
            self.readiness_status == status
            and self.validation_issues == issues
            and self.validated_version == self.version
        ):
            return self
        return self._evolve(
            readiness_status=status,
            validation_issues=issues,
            validated_version=self.version + 1,
            validated_at=timestamp,
            now=timestamp,
        )

    def change_species(
        self,
        *,
        species_id: UUID,
        compatibility_profile_id: UUID,
        rig_id: UUID | None,
        skeleton_id: UUID | None,
        body_id: UUID | None,
        material_ids: tuple[UUID, ...],
        cleared_fields: frozenset[str],
        preserved_collections: Mapping[str, tuple[UUID, ...]] | None = None,
        downstream_stages: tuple[str, ...] = ("set", "studio", "review", "render"),
        now: datetime | None = None,
    ) -> Self:
        timestamp = now or datetime.now(UTC)
        downstream = {item.stage: item for item in self.downstream_status}
        for stage in downstream_stages:
            downstream[stage] = DownstreamDependency(
                stage=stage,
                status="stale",
                invalidated_at=timestamp,
                reason="character species changed",
            )
        changes: dict[str, object] = {
            "species_id": species_id,
            "compatibility_profile_id": compatibility_profile_id,
            "rig_id": rig_id,
            "skeleton_id": skeleton_id,
            "body_id": body_id,
            "material_ids": material_ids,
            "downstream_status": tuple(downstream[key] for key in sorted(downstream)),
        }
        retained = preserved_collections or {}
        for field_name in cleared_fields:
            if field_name in {"rig_id", "skeleton_id", "body_id", "material_ids"}:
                continue
            if field_name in SCALAR_SELECTION_FIELDS.values():
                changes[field_name] = None
            elif field_name in {
                "wardrobe_ids",
                "accessory_ids",
                "material_ids",
                "texture_ids",
                "animation_ids",
            }:
                changes[field_name] = retained.get(field_name, ())
        return self._evolve(now=timestamp, **changes)

    def update_selection(
        self, category: str, asset_id: UUID, *, now: datetime | None = None
    ) -> Self:
        field_name = SCALAR_SELECTION_FIELDS.get(category)
        if field_name is None:
            raise InvariantViolation(f"Unsupported scalar selection category: {category}")
        return self._evolve(now=now, **{field_name: asset_id})

    def remove_selection(self, category: str, *, now: datetime | None = None) -> Self:
        field_name = SCALAR_SELECTION_FIELDS.get(category)
        if field_name is None:
            raise InvariantViolation(f"Unsupported scalar selection category: {category}")
        return self._evolve(now=now, **{field_name: None})

    def replace_accessories(
        self, asset_ids: tuple[UUID, ...], *, now: datetime | None = None
    ) -> Self:
        return self._evolve(accessory_ids=tuple(dict.fromkeys(asset_ids)), now=now)

    def replace_wardrobe(self, asset_ids: tuple[UUID, ...], *, now: datetime | None = None) -> Self:
        return self._evolve(wardrobe_ids=tuple(dict.fromkeys(asset_ids)), now=now)

    def update_pipeline_status(
        self, status: PipelineStatus, *, now: datetime | None = None
    ) -> Self:
        return self._evolve(pipeline_status=status, now=now)

    def update_preview_reference(
        self, asset_id: UUID | None, *, now: datetime | None = None
    ) -> Self:
        return self._evolve(preview_asset_id=asset_id, now=now)

    def register_generated_assets(
        self, asset_ids: tuple[UUID, ...], *, now: datetime | None = None
    ) -> Self:
        combined = tuple(dict.fromkeys((*self.generated_asset_ids, *asset_ids)))
        return self._evolve(generated_asset_ids=combined, now=now)

    def register_uploaded_assets(
        self, asset_ids: tuple[UUID, ...], *, now: datetime | None = None
    ) -> Self:
        combined = tuple(dict.fromkeys((*self.uploaded_asset_ids, *asset_ids)))
        return self._evolve(uploaded_asset_ids=combined, now=now)

    def invalidate_downstream(
        self,
        *,
        reason: str,
        stages: tuple[str, ...],
        now: datetime | None = None,
        increment_version: bool = True,
    ) -> Self:
        timestamp = now or datetime.now(UTC)
        current = {item.stage: item for item in self.downstream_status}
        for stage in stages:
            current[stage] = DownstreamDependency(
                stage=stage,
                status="stale",
                invalidated_at=timestamp,
                reason=reason,
            )
        updated = tuple(current[key] for key in sorted(current))
        if increment_version:
            return self._evolve(downstream_status=updated, now=timestamp)
        return replace(self, downstream_status=updated, updated_at=timestamp)


@dataclass(frozen=True, slots=True)
class Species:
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

    def __post_init__(self) -> None:
        if not self.key or self.key != self.key.lower():
            raise InvariantViolation("Species key must be a non-empty lowercase value.")
        if not self.name.strip():
            raise InvariantViolation("Species name is required.")
        if self.version < 1:
            raise InvariantViolation("Species version must be positive.")
        if self.min_age < 0 or self.max_age < self.min_age:
            raise InvariantViolation("Species age range is invalid.")
        if self.min_height_cm < 30 or self.max_height_cm < self.min_height_cm:
            raise InvariantViolation("Species height range is invalid.")


@dataclass(frozen=True, slots=True)
class CompatibilityProfile:
    compatibility_profile_id: UUID
    key: str
    name: str
    required_capabilities: frozenset[str]
    supported_categories: tuple[str, ...]
    version: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.key.strip() or not self.name.strip():
            raise InvariantViolation("Compatibility profile key and name are required.")
        if self.version < 1:
            raise InvariantViolation("Compatibility profile version must be positive.")


@dataclass(frozen=True, slots=True)
class CharacterAssetManifest:
    asset_id: UUID
    workspace_id: UUID | None
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
    file_references: tuple[str, ...]
    generated: bool
    uploaded: bool
    provenance: dict[str, object]
    visibility: str
    attachment_point: str | None
    compatible_body_regions: tuple[str, ...]
    profile_metadata: dict[str, object]
    version: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise InvariantViolation("Asset manifest name is required.")
        if not self.category.strip():
            raise InvariantViolation("Asset manifest category is required.")
        if self.version < 1:
            raise InvariantViolation("Asset manifest version must be positive.")
        if len(self.species_ids) != len(set(self.species_ids)):
            raise InvariantViolation("Asset manifest species IDs must be unique.")
        if any(reference.strip() == "" for reference in self.file_references):
            raise InvariantViolation("Asset file references cannot be blank.")
