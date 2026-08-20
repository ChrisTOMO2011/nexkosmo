from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.application.environment_compatibility import EnvironmentCompatibilityService
from app.domain.environments import Environment, EnvironmentAssetManifest, EnvironmentType
from app.domain.errors import InvariantViolation

NOW = datetime(2026, 8, 7, tzinfo=UTC)
WORKSPACE_ID = UUID("52000000-0000-4000-8000-000000000001")
PROJECT_ID = UUID("52000000-0000-4000-8000-000000000002")
PRODUCTION_ID = UUID("52000000-0000-4000-8000-000000000003")
CITY_ID = UUID("22000000-0000-4000-8000-000000000001")
FOREST_ID = UUID("22000000-0000-4000-8000-000000000002")
WEATHER_ID = UUID("52000000-0000-4000-8000-000000000010")
STYLE_ID = UUID("52000000-0000-4000-8000-000000000011")


class FakeAssets:
    def __init__(self, items: list[EnvironmentAssetManifest]) -> None:
        self.items = {item.asset_id: item for item in items}

    async def get_by_id(self, asset_id: UUID) -> EnvironmentAssetManifest | None:
        return self.items.get(asset_id)

    async def get_many(self, asset_ids):
        return [self.items[item] for item in asset_ids if item in self.items]

    async def list_compatible(self, **_kwargs):
        return list(self.items.values())

    async def batch_load_dependencies(self, asset_ids):
        direct = await self.get_many(asset_ids)
        dependency_ids = tuple(
            dependency for item in direct for dependency in item.dependent_asset_ids
        )
        return [*direct, *(await self.get_many(dependency_ids))]


def environment(type_id: UUID = CITY_ID, **values: str) -> Environment:
    return Environment.create(
        workspace_id=WORKSPACE_ID,
        project_id=PROJECT_ID,
        production_id=PRODUCTION_ID,
        display_name="Environment",
        environment_type_id=type_id,
        now=NOW,
        **values,
    )


def environment_type(type_id: UUID, *capabilities: str) -> EnvironmentType:
    return EnvironmentType(
        environment_type_id=type_id,
        key="city" if type_id == CITY_ID else "forest",
        name="City" if type_id == CITY_ID else "Forest",
        enabled=True,
        capabilities=frozenset(capabilities),
        supported_tabs=("Identity", "Terrain"),
        version=1,
        created_at=NOW,
        updated_at=NOW,
    )


def asset(
    suffix: int,
    *,
    types: tuple[UUID, ...] = (),
    locations: tuple[str, ...] = (),
    times: tuple[str, ...] = (),
    weather: tuple[UUID, ...] = (),
    styles: tuple[UUID, ...] = (),
    capabilities: frozenset[str] = frozenset(),
    dependencies: tuple[UUID, ...] = (),
    conflicts: tuple[UUID, ...] = (),
    status: str = "available",
) -> EnvironmentAssetManifest:
    asset_id = UUID(f"52000000-0000-4000-8000-{suffix:012d}")
    return EnvironmentAssetManifest(
        asset_id=asset_id,
        workspace_id=None,
        name=f"Asset {suffix}",
        category="terrain",
        subcategory="ground",
        compatible_environment_type_ids=types,
        compatible_location_types=locations,
        compatible_biomes=(),
        compatible_climates=(),
        compatible_times_of_day=times,
        compatible_weather_profile_ids=weather,
        compatible_style_profile_ids=styles,
        compatible_lighting_profile_ids=(),
        compatible_camera_profile_ids=(),
        required_capabilities=capabilities,
        incompatible_asset_ids=conflicts,
        dependent_asset_ids=dependencies,
        material_references=(),
        texture_references=(),
        preview_reference="preview",
        thumbnail_reference="thumbnail",
        visibility="global",
        status=status,
        source="seed",
        uploaded=False,
        generated=False,
        placeholder=False,
        version=1,
        created_at=NOW,
        updated_at=NOW,
    )


async def test_environment_type_and_interior_filters_are_authoritative() -> None:
    city = asset(20, types=(CITY_ID,), locations=("street",))
    forest = asset(21, types=(FOREST_ID,), locations=("landscape",))
    service = EnvironmentCompatibilityService(FakeAssets([city, forest]))
    city_items = await service.get_compatible_assets(
        environment=environment(location_type="street"),
        environment_type=environment_type(CITY_ID, "urban-layout"),
        category="terrain",
        limit=100,
        offset=0,
    )
    forest_items = await service.get_compatible_assets(
        environment=environment(FOREST_ID, location_type="landscape"),
        environment_type=environment_type(FOREST_ID, "terrain"),
        category="terrain",
        limit=100,
        offset=0,
    )
    interior_items = await service.get_compatible_assets(
        environment=environment(location_type="room"),
        environment_type=environment_type(CITY_ID, "urban-layout"),
        category="terrain",
        limit=100,
        offset=0,
    )
    assert [item.asset_id for item in city_items] == [city.asset_id]
    assert [item.asset_id for item in forest_items] == [forest.asset_id]
    assert interior_items == []


async def test_weather_time_style_capability_and_status_filters() -> None:
    compatible = asset(
        30,
        times=("night",),
        weather=(WEATHER_ID,),
        styles=(STYLE_ID,),
        capabilities=frozenset({"weather"}),
    )
    disabled = asset(31, status="disabled")
    service = EnvironmentCompatibilityService(FakeAssets([compatible, disabled]))
    current = environment(time_of_day="night")
    current = current.select_asset("weather-profile", WEATHER_ID, now=NOW)
    current = current.select_asset("style-profile", STYLE_ID, now=NOW)
    items = await service.get_compatible_assets(
        environment=current,
        environment_type=environment_type(CITY_ID, "weather"),
        category="terrain",
        limit=100,
        offset=0,
    )
    assert [item.asset_id for item in items] == [compatible.asset_id]


async def test_missing_dependencies_and_explicit_incompatibilities_are_rejected() -> None:
    dependency = asset(40)
    dependent = asset(41, dependencies=(dependency.asset_id,))
    conflict = asset(42, conflicts=(dependency.asset_id,))
    service = EnvironmentCompatibilityService(FakeAssets([dependency, dependent, conflict]))
    current = environment().select_asset("terrain", dependency.asset_id, now=NOW)
    with pytest.raises(InvariantViolation, match="conflicts"):
        await service.validate_selection(
            environment=current,
            environment_type=environment_type(CITY_ID),
            asset_id=conflict.asset_id,
        )
    with pytest.raises(InvariantViolation, match="dependencies"):
        await service.validate_selection(
            environment=environment(),
            environment_type=environment_type(CITY_ID),
            asset_id=dependent.asset_id,
        )


async def test_readiness_reports_missing_requirements_and_processing() -> None:
    service = EnvironmentCompatibilityService(FakeAssets([]))
    assessment = await service.validate_environment_package(
        environment=environment(),
        environment_type=environment_type(CITY_ID, "urban-layout", "buildings", "weather"),
    )
    assert assessment.missing_requirements == (
        "terrain-or-ground",
        "structure-or-building",
        "material-package",
    )
    assert assessment.required_processing_jobs == ("environment-preview",)
    assert assessment.warnings[0]["code"] == "weather-not-selected"
