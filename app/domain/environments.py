from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import UTC, datetime
from typing import Any, Literal, Self, cast
from uuid import UUID, uuid4

from app.domain.errors import InvariantViolation

EnvironmentLocationType = Literal[
    "room",
    "corridor",
    "street",
    "plaza",
    "building",
    "landscape",
    "vehicle-interior",
    "spacecraft-interior",
    "abstract-environment",
    "custom",
]
InteriorExterior = Literal["interior", "exterior", "mixed", "virtual", "studio-stage"]
EnvironmentPackageStatus = Literal["draft", "active", "archived"]
EnvironmentReadinessStatus = Literal[
    "incomplete",
    "valid",
    "processing_required",
    "ready_for_scene",
    "blocked",
]

LOCATION_TYPES = frozenset(
    {
        "room",
        "corridor",
        "street",
        "plaza",
        "building",
        "landscape",
        "vehicle-interior",
        "spacecraft-interior",
        "abstract-environment",
        "custom",
    }
)
INTERIOR_EXTERIOR_VALUES = frozenset({"interior", "exterior", "mixed", "virtual", "studio-stage"})
ENVIRONMENT_PACKAGE_STATUSES = frozenset({"draft", "active", "archived"})
ENVIRONMENT_READINESS_STATUSES = frozenset(
    {"incomplete", "valid", "processing_required", "ready_for_scene", "blocked"}
)

ENVIRONMENT_SINGLE_SELECTIONS = {
    "terrain-profile": "terrain_profile_id",
    "weather-profile": "weather_profile_id",
    "atmosphere-profile": "atmosphere_profile_id",
    "style-profile": "style_profile_id",
}
ENVIRONMENT_COLLECTION_SELECTIONS = {
    "background": "background_asset_ids",
    "terrain": "terrain_asset_ids",
    "building": "building_asset_ids",
    "nature": "nature_asset_ids",
    "practical": "practical_asset_ids",
    "material": "material_profile_ids",
    "texture": "texture_profile_ids",
    "detail": "detail_asset_ids",
}


@dataclass(frozen=True, slots=True)
class EnvironmentType:
    environment_type_id: UUID
    key: str
    name: str
    enabled: bool
    capabilities: frozenset[str]
    supported_tabs: tuple[str, ...]
    version: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.key or self.key != self.key.strip().lower():
            raise InvariantViolation("Environment type key must be a lowercase stable key.")
        if not self.name.strip():
            raise InvariantViolation("Environment type name is required.")
        if not self.supported_tabs or self.supported_tabs[0] != "Identity":
            raise InvariantViolation("Environment types must support Identity as the first tab.")
        if self.version < 1:
            raise InvariantViolation("Environment type version must be positive.")


@dataclass(frozen=True, slots=True)
class EnvironmentAssetManifest:
    asset_id: UUID
    workspace_id: UUID | None
    name: str
    category: str
    subcategory: str
    compatible_environment_type_ids: tuple[UUID, ...]
    compatible_location_types: tuple[str, ...]
    compatible_biomes: tuple[str, ...]
    compatible_climates: tuple[str, ...]
    compatible_times_of_day: tuple[str, ...]
    compatible_weather_profile_ids: tuple[UUID, ...]
    compatible_style_profile_ids: tuple[UUID, ...]
    compatible_lighting_profile_ids: tuple[UUID, ...]
    compatible_camera_profile_ids: tuple[UUID, ...]
    required_capabilities: frozenset[str]
    incompatible_asset_ids: tuple[UUID, ...]
    dependent_asset_ids: tuple[UUID, ...]
    material_references: tuple[UUID, ...]
    texture_references: tuple[UUID, ...]
    preview_reference: str
    thumbnail_reference: str
    visibility: str
    status: str
    source: str
    uploaded: bool
    generated: bool
    placeholder: bool
    version: int
    created_at: datetime
    updated_at: datetime

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.category.strip():
            raise InvariantViolation("Environment asset name and category are required.")
        if self.version < 1:
            raise InvariantViolation("Environment asset version must be positive.")


@dataclass(frozen=True, slots=True)
class EnvironmentReadiness:
    readiness_status: EnvironmentReadinessStatus
    blocking_issues: tuple[dict[str, object], ...]
    warnings: tuple[dict[str, object], ...]
    missing_requirements: tuple[str, ...]
    invalid_asset_ids: tuple[UUID, ...]
    required_processing_jobs: tuple[str, ...]
    validated_version: int | None
    validated_at: datetime | None


@dataclass(frozen=True, slots=True)
class Environment:
    environment_id: UUID
    workspace_id: UUID
    project_id: UUID
    production_id: UUID
    display_name: str
    description: str
    environment_type_id: UUID
    location_type: EnvironmentLocationType
    interior_exterior: InteriorExterior
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
    package_status: EnvironmentPackageStatus
    readiness_status: EnvironmentReadinessStatus
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

    def __post_init__(self) -> None:
        if not self.display_name.strip() or self.display_name != self.display_name.strip():
            raise InvariantViolation("Environment display name is required and must be trimmed.")
        if self.description != self.description.strip():
            raise InvariantViolation("Environment description must be trimmed.")
        if self.location_type not in LOCATION_TYPES:
            raise InvariantViolation("Environment location type is not supported.")
        if self.interior_exterior not in INTERIOR_EXTERIOR_VALUES:
            raise InvariantViolation("Environment interior/exterior value is not supported.")
        if self.package_status not in ENVIRONMENT_PACKAGE_STATUSES:
            raise InvariantViolation("Environment package status is not supported.")
        if self.readiness_status not in ENVIRONMENT_READINESS_STATUSES:
            raise InvariantViolation("Environment readiness status is not supported.")
        if not 1 <= self.scale <= 1000:
            raise InvariantViolation("Environment scale must be between 1 and 1000.")
        if self.version < 1:
            raise InvariantViolation("Environment version must be positive.")
        if self.updated_at < self.created_at:
            raise InvariantViolation("Environment updated_at cannot precede created_at.")
        for field_name in ENVIRONMENT_COLLECTION_SELECTIONS.values():
            values = getattr(self, field_name)
            if len(values) != len(set(values)):
                raise InvariantViolation(f"{field_name} cannot contain duplicate asset IDs.")

    @classmethod
    def create(
        cls,
        *,
        workspace_id: UUID,
        project_id: UUID,
        production_id: UUID,
        display_name: str,
        environment_type_id: UUID,
        environment_id: UUID | None = None,
        description: str = "",
        location_type: EnvironmentLocationType = "landscape",
        interior_exterior: InteriorExterior = "exterior",
        biome: str = "urban",
        climate_profile: str = "temperate",
        time_of_day: str = "day",
        now: datetime | None = None,
    ) -> Self:
        timestamp = now or datetime.now(UTC)
        return cls(
            environment_id=environment_id or uuid4(),
            workspace_id=workspace_id,
            project_id=project_id,
            production_id=production_id,
            display_name=display_name.strip(),
            description=description.strip(),
            environment_type_id=environment_type_id,
            location_type=location_type,
            interior_exterior=interior_exterior,
            biome=biome.strip().lower(),
            climate_profile=climate_profile.strip().lower(),
            terrain_profile_id=None,
            weather_profile_id=None,
            time_of_day=time_of_day.strip().lower(),
            atmosphere_profile_id=None,
            background_asset_ids=(),
            terrain_asset_ids=(),
            building_asset_ids=(),
            nature_asset_ids=(),
            practical_asset_ids=(),
            material_profile_ids=(),
            texture_profile_ids=(),
            detail_asset_ids=(),
            style_profile_id=None,
            lighting_compatibility_profile_id=None,
            camera_compatibility_profile_id=None,
            audio_compatibility_profile_id=None,
            vfx_compatibility_profile_id=None,
            preview_asset_id=None,
            scale=100,
            navigation_constraints="Standard character navigation",
            camera_access_constraints="Standard camera access",
            package_status="draft",
            readiness_status="incomplete",
            validation_issues=(),
            readiness_warnings=(),
            missing_requirements=(),
            invalid_asset_ids=(),
            required_processing_jobs=(),
            readiness_validated_version=None,
            readiness_validated_at=None,
            version=1,
            created_at=timestamp,
            updated_at=timestamp,
        )

    @property
    def selected_asset_ids(self) -> tuple[UUID, ...]:
        values = [
            self.terrain_profile_id,
            self.weather_profile_id,
            self.atmosphere_profile_id,
            self.style_profile_id,
            *self.background_asset_ids,
            *self.terrain_asset_ids,
            *self.building_asset_ids,
            *self.nature_asset_ids,
            *self.practical_asset_ids,
            *self.material_profile_ids,
            *self.texture_profile_ids,
            *self.detail_asset_ids,
        ]
        return tuple(dict.fromkeys(item for item in values if item is not None))

    def _evolve(self, *, now: datetime | None = None, **changes: object) -> Self:
        if "readiness_status" not in changes:
            changes = {
                **changes,
                "readiness_status": "incomplete",
                "validation_issues": (),
                "readiness_warnings": (),
                "missing_requirements": (),
                "invalid_asset_ids": (),
                "required_processing_jobs": (),
                "readiness_validated_version": None,
                "readiness_validated_at": None,
            }
        return replace(
            self,
            **cast(Any, changes),
            version=self.version + 1,
            updated_at=now or datetime.now(UTC),
        )

    def update_properties(
        self,
        *,
        display_name: str | None = None,
        description: str | None = None,
        location_type: EnvironmentLocationType | None = None,
        interior_exterior: InteriorExterior | None = None,
        biome: str | None = None,
        climate_profile: str | None = None,
        time_of_day: str | None = None,
        scale: int | None = None,
        navigation_constraints: str | None = None,
        camera_access_constraints: str | None = None,
        weather_profile_id: UUID | None = None,
        atmosphere_profile_id: UUID | None = None,
        style_profile_id: UUID | None = None,
        lighting_compatibility_profile_id: UUID | None = None,
        camera_compatibility_profile_id: UUID | None = None,
        audio_compatibility_profile_id: UUID | None = None,
        vfx_compatibility_profile_id: UUID | None = None,
        now: datetime | None = None,
    ) -> Self:
        changes: dict[str, object] = {}
        for field_name, value in {
            "display_name": display_name,
            "description": description,
            "biome": biome,
            "climate_profile": climate_profile,
            "time_of_day": time_of_day,
            "navigation_constraints": navigation_constraints,
            "camera_access_constraints": camera_access_constraints,
        }.items():
            if value is not None:
                normalized = value.strip()
                if field_name == "display_name" and not normalized:
                    raise InvariantViolation("Environment display name is required.")
                changes[field_name] = (
                    normalized.lower()
                    if field_name in {"biome", "climate_profile", "time_of_day"}
                    else normalized
                )
        if location_type is not None:
            changes["location_type"] = location_type
        if interior_exterior is not None:
            changes["interior_exterior"] = interior_exterior
        if scale is not None:
            changes["scale"] = scale
        for field_name, profile_value in {
            "weather_profile_id": weather_profile_id,
            "atmosphere_profile_id": atmosphere_profile_id,
            "style_profile_id": style_profile_id,
            "lighting_compatibility_profile_id": lighting_compatibility_profile_id,
            "camera_compatibility_profile_id": camera_compatibility_profile_id,
            "audio_compatibility_profile_id": audio_compatibility_profile_id,
            "vfx_compatibility_profile_id": vfx_compatibility_profile_id,
        }.items():
            if profile_value is not None:
                changes[field_name] = profile_value
        if not changes or all(getattr(self, key) == value for key, value in changes.items()):
            return self
        return self._evolve(now=now, **changes)

    def change_type(
        self,
        environment_type_id: UUID,
        *,
        cleared_scalar_fields: frozenset[str] = frozenset(),
        preserved_collections: dict[str, tuple[UUID, ...]] | None = None,
        now: datetime | None = None,
    ) -> Self:
        if self.environment_type_id == environment_type_id:
            return self
        changes: dict[str, object] = {"environment_type_id": environment_type_id}
        for field_name in cleared_scalar_fields:
            if field_name in ENVIRONMENT_SINGLE_SELECTIONS.values():
                changes[field_name] = None
        changes.update(preserved_collections or {})
        return self._evolve(now=now, **changes)

    def select_asset(self, category: str, asset_id: UUID, *, now: datetime | None = None) -> Self:
        scalar_field = ENVIRONMENT_SINGLE_SELECTIONS.get(category)
        if scalar_field:
            if getattr(self, scalar_field) == asset_id:
                return self
            return self._evolve(now=now, **{scalar_field: asset_id})
        collection_field = ENVIRONMENT_COLLECTION_SELECTIONS.get(category)
        if collection_field:
            current: tuple[UUID, ...] = getattr(self, collection_field)
            if asset_id in current:
                return self
            return self._evolve(now=now, **{collection_field: (*current, asset_id)})
        raise InvariantViolation(f"Unsupported Environment asset category: {category}")

    def replace_assets(
        self, category: str, asset_ids: tuple[UUID, ...], *, now: datetime | None = None
    ) -> Self:
        field_name = ENVIRONMENT_COLLECTION_SELECTIONS.get(category)
        if field_name is None:
            raise InvariantViolation(f"Unsupported Environment collection category: {category}")
        unique = tuple(dict.fromkeys(asset_ids))
        if getattr(self, field_name) == unique:
            return self
        return self._evolve(now=now, **{field_name: unique})

    def remove_asset(
        self, category: str, asset_id: UUID | None = None, *, now: datetime | None = None
    ) -> Self:
        scalar_field = ENVIRONMENT_SINGLE_SELECTIONS.get(category)
        if scalar_field:
            selected_id = getattr(self, scalar_field)
            if selected_id is None or (asset_id is not None and selected_id != asset_id):
                return self
            return self._evolve(now=now, **{scalar_field: None})
        collection_field = ENVIRONMENT_COLLECTION_SELECTIONS.get(category)
        if collection_field:
            collection: tuple[UUID, ...] = getattr(self, collection_field)
            if asset_id is None:
                replacement: tuple[UUID, ...] = ()
            else:
                replacement = tuple(item for item in collection if item != asset_id)
            if replacement == collection:
                return self
            return self._evolve(now=now, **{collection_field: replacement})
        raise InvariantViolation(f"Unsupported Environment asset category: {category}")

    def archive(self, *, now: datetime | None = None) -> Self:
        if self.package_status == "archived":
            return self
        return self._evolve(now=now, package_status="archived")

    def validate_readiness(
        self,
        blocking_issues: tuple[dict[str, object], ...],
        *,
        warnings: tuple[dict[str, object], ...] = (),
        missing_requirements: tuple[str, ...] = (),
        invalid_asset_ids: tuple[UUID, ...] = (),
        required_processing_jobs: tuple[str, ...] = (),
        now: datetime | None = None,
    ) -> Self:
        timestamp = now or datetime.now(UTC)
        status: EnvironmentReadinessStatus
        if blocking_issues or invalid_asset_ids:
            status = "blocked"
        elif missing_requirements:
            status = "incomplete"
        elif required_processing_jobs or self.preview_asset_id is None:
            status = "processing_required"
            if (
                self.preview_asset_id is None
                and "environment-preview" not in required_processing_jobs
            ):
                required_processing_jobs = (*required_processing_jobs, "environment-preview")
        elif warnings:
            status = "valid"
        else:
            status = "ready_for_scene"
        return self._evolve(
            readiness_status=status,
            validation_issues=blocking_issues,
            readiness_warnings=warnings,
            missing_requirements=missing_requirements,
            invalid_asset_ids=tuple(dict.fromkeys(invalid_asset_ids)),
            required_processing_jobs=tuple(dict.fromkeys(required_processing_jobs)),
            readiness_validated_version=self.version + 1,
            readiness_validated_at=timestamp,
            now=timestamp,
        )

    @property
    def readiness(self) -> EnvironmentReadiness:
        return EnvironmentReadiness(
            readiness_status=self.readiness_status,
            blocking_issues=self.validation_issues,
            warnings=self.readiness_warnings,
            missing_requirements=self.missing_requirements,
            invalid_asset_ids=self.invalid_asset_ids,
            required_processing_jobs=self.required_processing_jobs,
            validated_version=self.readiness_validated_version,
            validated_at=self.readiness_validated_at,
        )
