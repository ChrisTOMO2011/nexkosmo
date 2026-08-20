from dataclasses import FrozenInstanceError, replace

import pytest

from app.domain.characters import Character
from app.domain.errors import InvariantViolation
from tests.character_fakes import (
    HUMAN_ID,
    HUMAN_MATERIAL_ID,
    HUMAN_PROFILE_ID,
    HUMAN_RIG_ID,
    HUMAN_SKELETON_ID,
    NOW,
    PRODUCTION_ID,
    PROJECT_ID,
    WORKSPACE_ID,
)


def make_character() -> Character:
    return Character.create(
        workspace_id=WORKSPACE_ID,
        project_id=PROJECT_ID,
        production_id=PRODUCTION_ID,
        display_name="Christopher",
        role="Lead",
        species_id=HUMAN_ID,
        compatibility_profile_id=HUMAN_PROFILE_ID,
        rig_id=HUMAN_RIG_ID,
        skeleton_id=HUMAN_SKELETON_ID,
        material_ids=(HUMAN_MATERIAL_ID,),
        now=NOW,
    )


def test_character_is_immutable_and_uses_uuid_identity():
    character = make_character()
    assert character.character_id.version == 4
    with pytest.raises(FrozenInstanceError):
        character.display_name = "Changed"  # type: ignore[misc]


def test_character_mutations_increment_version_without_erasing_history_fields():
    original = make_character()
    renamed = original.rename("Christopher Vale")
    selected = renamed.update_selection("hair", HUMAN_RIG_ID)
    assert original.display_name == "Christopher"
    assert renamed.version == 2
    assert selected.version == 3
    assert selected.created_at == original.created_at


def test_character_rejects_duplicate_relationship_assets():
    with pytest.raises(InvariantViolation):
        replace(
            make_character(),
            accessory_ids=(HUMAN_RIG_ID, HUMAN_RIG_ID),
        )
