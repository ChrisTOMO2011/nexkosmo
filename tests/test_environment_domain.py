from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.domain.environments import Environment, EnvironmentType
from app.domain.errors import InvariantViolation

NOW = datetime(2026, 8, 3, tzinfo=UTC)
WORKSPACE_ID = UUID("50000000-0000-4000-8000-000000000001")
PROJECT_ID = UUID("50000000-0000-4000-8000-000000000002")
PRODUCTION_ID = UUID("50000000-0000-4000-8000-000000000003")
CITY_ID = UUID("22000000-0000-4000-8000-000000000001")
FOREST_ID = UUID("22000000-0000-4000-8000-000000000002")
TERRAIN_ID = UUID("44000000-0000-4000-8000-000000000002")
BUILDING_ID = UUID("44000000-0000-4000-8000-000000000008")


def environment() -> Environment:
    return Environment.create(
        workspace_id=WORKSPACE_ID,
        project_id=PROJECT_ID,
        production_id=PRODUCTION_ID,
        display_name="City Street",
        environment_type_id=CITY_ID,
        now=NOW,
    )


def test_environment_is_immutable_versioned_and_owns_canonical_ids() -> None:
    original = environment()
    updated = original.update_properties(
        biome="metropolitan", location_type="street", scale=125, now=NOW
    )
    assert original.biome == "urban"
    assert updated.biome == "metropolitan"
    assert updated.location_type == "street"
    assert updated.version == 2
    assert (updated.workspace_id, updated.project_id, updated.production_id) == (
        WORKSPACE_ID,
        PROJECT_ID,
        PRODUCTION_ID,
    )
    assert isinstance(updated.environment_id, UUID)


def test_environment_no_op_does_not_increment_and_collections_are_immutable() -> None:
    original = environment()
    assert original.update_properties(biome="urban", now=NOW) is original
    selected = original.replace_assets("nature", (TERRAIN_ID,), now=NOW)
    assert selected.nature_asset_ids == (TERRAIN_ID,)
    assert isinstance(selected.nature_asset_ids, tuple)
    assert selected.version == original.version + 1


def test_environment_single_and_multi_selection_semantics() -> None:
    selected = environment().select_asset("terrain-profile", TERRAIN_ID, now=NOW)
    selected = selected.select_asset("building", BUILDING_ID, now=NOW)
    no_op = selected.select_asset("building", BUILDING_ID, now=NOW)
    assert selected.terrain_profile_id == TERRAIN_ID
    assert selected.building_asset_ids == (BUILDING_ID,)
    assert no_op is selected
    assert selected.selected_asset_ids == (TERRAIN_ID, BUILDING_ID)
    removed = selected.remove_asset("building", BUILDING_ID, now=NOW)
    assert removed.building_asset_ids == ()
    assert removed.version == selected.version + 1


def test_environment_type_change_clears_only_incompatible_selections() -> None:
    current = environment().select_asset("terrain-profile", TERRAIN_ID, now=NOW)
    current = current.select_asset("building", BUILDING_ID, now=NOW)
    changed = current.change_type(
        FOREST_ID,
        cleared_scalar_fields=frozenset({"terrain_profile_id"}),
        preserved_collections={"building_asset_ids": ()},
        now=NOW,
    )
    assert changed.environment_type_id == FOREST_ID
    assert changed.terrain_profile_id is None
    assert changed.building_asset_ids == ()
    assert changed.version == current.version + 1


def test_environment_rejects_invalid_package_values() -> None:
    with pytest.raises(InvariantViolation):
        environment().update_properties(scale=0)
    with pytest.raises(InvariantViolation):
        EnvironmentType(
            environment_type_id=CITY_ID,
            key="City",
            name="City",
            enabled=True,
            capabilities=frozenset(),
            supported_tabs=("Identity",),
            version=1,
            created_at=NOW,
            updated_at=NOW,
        )


def test_environment_readiness_is_structured_honest_and_invalidated_by_change() -> None:
    current = environment().validate_readiness(
        blocking_issues=(),
        warnings=(),
        missing_requirements=("material-package",),
        invalid_asset_ids=(),
        required_processing_jobs=("environment-preview",),
        now=NOW,
    )
    assert current.readiness_status == "incomplete"
    assert current.missing_requirements == ("material-package",)
    assert current.required_processing_jobs == ("environment-preview",)
    assert current.readiness.validated_version == current.version
    changed = current.update_properties(time_of_day="night", now=NOW)
    assert changed.readiness_status == "incomplete"
    assert changed.readiness_validated_version is None
    assert changed.required_processing_jobs == ()
