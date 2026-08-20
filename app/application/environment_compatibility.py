from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from app.application.ports import EnvironmentAssetManifestRepository
from app.domain.environments import (
    ENVIRONMENT_COLLECTION_SELECTIONS,
    ENVIRONMENT_SINGLE_SELECTIONS,
    Environment,
    EnvironmentAssetManifest,
    EnvironmentType,
)
from app.domain.errors import InvariantViolation, NotFound


@dataclass(frozen=True, slots=True)
class EnvironmentCompatibilityIssue:
    field: str
    asset_id: UUID
    reason: str


@dataclass(frozen=True, slots=True)
class EnvironmentCompatibilityResolution:
    cleared_fields: tuple[str, ...]
    cleared_asset_ids: tuple[UUID, ...]
    preserved_asset_ids: tuple[UUID, ...]
    preserved_collections: dict[str, tuple[UUID, ...]]


@dataclass(frozen=True, slots=True)
class EnvironmentReadinessAssessment:
    blocking_issues: tuple[dict[str, object], ...]
    warnings: tuple[dict[str, object], ...]
    missing_requirements: tuple[str, ...]
    invalid_asset_ids: tuple[UUID, ...]
    required_processing_jobs: tuple[str, ...]


def environment_selections(environment: Environment) -> dict[str, tuple[UUID, ...]]:
    selections: dict[str, tuple[UUID, ...]] = {}
    for field_name in ENVIRONMENT_SINGLE_SELECTIONS.values():
        asset_id = getattr(environment, field_name)
        if asset_id is not None:
            selections[field_name] = (asset_id,)
    for field_name in ENVIRONMENT_COLLECTION_SELECTIONS.values():
        selections[field_name] = getattr(environment, field_name)
    return selections


class EnvironmentCompatibilityService:
    def __init__(self, assets: EnvironmentAssetManifestRepository) -> None:
        self._assets = assets

    @staticmethod
    def validate_manifest(
        *,
        environment: Environment,
        environment_type: EnvironmentType,
        manifest: EnvironmentAssetManifest,
        selected_ids: frozenset[UUID],
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if (
            manifest.compatible_environment_type_ids
            and environment_type.environment_type_id not in manifest.compatible_environment_type_ids
        ):
            reasons.append("asset is not declared for the selected Environment type")
        if (
            manifest.compatible_location_types
            and environment.location_type not in manifest.compatible_location_types
        ):
            reasons.append("location type is incompatible")
        if manifest.compatible_biomes and environment.biome not in manifest.compatible_biomes:
            reasons.append("biome is incompatible")
        if (
            manifest.compatible_climates
            and environment.climate_profile not in manifest.compatible_climates
        ):
            reasons.append("climate is incompatible")
        if (
            manifest.compatible_times_of_day
            and environment.time_of_day not in manifest.compatible_times_of_day
        ):
            reasons.append("time of day is incompatible")
        if (
            manifest.compatible_weather_profile_ids
            and environment.weather_profile_id not in manifest.compatible_weather_profile_ids
        ):
            reasons.append("weather profile is incompatible")
        if (
            manifest.compatible_style_profile_ids
            and environment.style_profile_id not in manifest.compatible_style_profile_ids
        ):
            reasons.append("style profile is incompatible")
        if not manifest.required_capabilities.issubset(environment_type.capabilities):
            reasons.append("Environment type lacks required capabilities")
        conflicts = selected_ids.intersection(manifest.incompatible_asset_ids)
        if conflicts:
            reasons.append("asset conflicts with another selected Environment asset")
        missing = set(manifest.dependent_asset_ids).difference(selected_ids)
        if missing:
            reasons.append("asset dependencies are not selected")
        if manifest.status not in {"development-placeholder", "available", "approved"}:
            reasons.append("asset is not available")
        if manifest.visibility not in {"global", "workspace", "project"}:
            reasons.append("asset is not visible")
        return tuple(reasons)

    async def get_compatible_assets(
        self,
        *,
        environment: Environment,
        environment_type: EnvironmentType,
        category: str | None,
        limit: int,
        offset: int,
        subcategory: str | None = None,
    ) -> list[EnvironmentAssetManifest]:
        candidates = await self._assets.list_compatible(
            environment_type_id=environment_type.environment_type_id,
            category=category,
            limit=limit,
            offset=offset,
        )
        selected_ids = frozenset(environment.selected_asset_ids)
        return [
            item
            for item in candidates
            if (subcategory is None or item.subcategory == subcategory)
            if not self.validate_manifest(
                environment=environment,
                environment_type=environment_type,
                manifest=item,
                selected_ids=selected_ids,
            )
        ]

    async def validate_selection(
        self,
        *,
        environment: Environment,
        environment_type: EnvironmentType,
        asset_id: UUID,
    ) -> EnvironmentAssetManifest:
        manifest = await self._assets.get_by_id(asset_id)
        if manifest is None:
            raise NotFound("Environment asset does not exist.")
        selected_manifests = await self._assets.get_many(environment.selected_asset_ids)
        if any(asset_id in selected.incompatible_asset_ids for selected in selected_manifests):
            raise InvariantViolation("asset conflicts with another selected Environment asset")
        reasons = self.validate_manifest(
            environment=environment,
            environment_type=environment_type,
            manifest=manifest,
            selected_ids=frozenset((*environment.selected_asset_ids, asset_id)),
        )
        if reasons:
            raise InvariantViolation("; ".join(reasons))
        return manifest

    async def validate_environment_selection(
        self,
        *,
        environment: Environment,
        environment_type: EnvironmentType,
        asset_id: UUID,
    ) -> EnvironmentAssetManifest:
        return await self.validate_selection(
            environment=environment,
            environment_type=environment_type,
            asset_id=asset_id,
        )

    @staticmethod
    def resolve_environment_defaults(environment_type: EnvironmentType) -> dict[str, str]:
        capabilities = environment_type.capabilities
        return {
            "location_type": "room" if "interior" in capabilities else "landscape",
            "interior_exterior": "interior" if "interior" in capabilities else "exterior",
            "time_of_day": "day",
        }

    @staticmethod
    def resolve_supported_environment_tabs(
        environment_type: EnvironmentType,
    ) -> tuple[str, ...]:
        return environment_type.supported_tabs

    async def validate_environment_package(
        self,
        *,
        environment: Environment,
        environment_type: EnvironmentType,
    ) -> EnvironmentReadinessAssessment:
        manifests = {
            item.asset_id: item
            for item in await self._assets.batch_load_dependencies(environment.selected_asset_ids)
        }
        selected_ids = frozenset(environment.selected_asset_ids)
        blocking: list[dict[str, object]] = []
        invalid_ids: list[UUID] = []
        for asset_id in environment.selected_asset_ids:
            manifest = manifests.get(asset_id)
            reasons = (
                ("asset does not exist",)
                if manifest is None
                else self.validate_manifest(
                    environment=environment,
                    environment_type=environment_type,
                    manifest=manifest,
                    selected_ids=selected_ids,
                )
            )
            if reasons:
                invalid_ids.append(asset_id)
                blocking.extend(
                    {
                        "code": "incompatible-selection",
                        "asset_id": str(asset_id),
                        "message": reason,
                        "blocking": True,
                    }
                    for reason in reasons
                )

        missing: list[str] = []
        capabilities = environment_type.capabilities
        if ("terrain" in capabilities or "urban-layout" in capabilities) and not (
            environment.terrain_profile_id or environment.terrain_asset_ids
        ):
            missing.append("terrain-or-ground")
        if "buildings" in capabilities and not environment.building_asset_ids:
            missing.append("structure-or-building")
        if not environment.material_profile_ids:
            missing.append("material-package")

        warnings: list[dict[str, object]] = []
        if "weather" in capabilities and environment.weather_profile_id is None:
            warnings.append(
                {
                    "code": "weather-not-selected",
                    "message": "No canonical weather profile is selected.",
                    "blocking": False,
                }
            )
        jobs = () if environment.preview_asset_id else ("environment-preview",)
        return EnvironmentReadinessAssessment(
            blocking_issues=tuple(blocking),
            warnings=tuple(warnings),
            missing_requirements=tuple(missing),
            invalid_asset_ids=tuple(dict.fromkeys(invalid_ids)),
            required_processing_jobs=jobs,
        )

    async def clear_invalid_environment_selections(
        self, *, environment: Environment, environment_type: EnvironmentType
    ) -> EnvironmentCompatibilityResolution:
        return await self.resolve_type_change(
            environment=environment, environment_type=environment_type
        )

    async def resolve_type_change(
        self, *, environment: Environment, environment_type: EnvironmentType
    ) -> EnvironmentCompatibilityResolution:
        selections = environment_selections(environment)
        all_ids = tuple(asset_id for values in selections.values() for asset_id in values)
        manifests = {item.asset_id: item for item in await self._assets.get_many(all_ids)}
        selected_ids = frozenset(all_ids)
        issues: list[EnvironmentCompatibilityIssue] = []
        for field_name, asset_ids in selections.items():
            for asset_id in asset_ids:
                manifest = manifests.get(asset_id)
                reasons = (
                    ("asset does not exist",)
                    if manifest is None
                    else self.validate_manifest(
                        environment=environment,
                        environment_type=environment_type,
                        manifest=manifest,
                        selected_ids=selected_ids,
                    )
                )
                issues.extend(
                    EnvironmentCompatibilityIssue(field_name, asset_id, reason)
                    for reason in reasons
                )
        cleared_ids = tuple(dict.fromkeys(issue.asset_id for issue in issues))
        invalid = frozenset(cleared_ids)
        cleared_fields = tuple(sorted({issue.field for issue in issues}))
        preserved_collections = {
            field_name: tuple(asset_id for asset_id in asset_ids if asset_id not in invalid)
            for field_name, asset_ids in selections.items()
            if field_name in ENVIRONMENT_COLLECTION_SELECTIONS.values()
            and field_name in cleared_fields
        }
        return EnvironmentCompatibilityResolution(
            cleared_fields=cleared_fields,
            cleared_asset_ids=cleared_ids,
            preserved_asset_ids=tuple(asset_id for asset_id in all_ids if asset_id not in invalid),
            preserved_collections=preserved_collections,
        )
