from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.characters import Character
from app.domain.errors import ConcurrencyConflict, InvariantViolation

NOW = datetime(2026, 8, 20, tzinfo=UTC)


def _character() -> Character:
    return Character.create(
        character_id=uuid4(),
        workspace_id=uuid4(),
        project_id=uuid4(),
        created_by_principal_id=uuid4(),
        display_name="  Christopher  ",
        role_label="  Lead  ",
        now=NOW,
    )


def test_character_creation_uses_one_stable_identity_and_normalizes_metadata() -> None:
    character = _character()
    assert character.id == character.identity_id
    assert character.display_name == "Christopher"
    assert character.role_label == "Lead"
    assert character.version == 1
    assert character.created_at == character.updated_at == NOW


def test_character_ownership_and_provenance_are_immutable() -> None:
    character = _character()
    with pytest.raises(FrozenInstanceError):
        character.project_id = uuid4()  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        character.created_by_principal_id = uuid4()  # type: ignore[misc]


def test_character_metadata_update_increments_exactly_once_and_can_clear_role() -> None:
    character = _character()
    updated = character.update_metadata(
        display_name="Christopher Vale",
        role_label=None,
        replace_role_label=True,
        expected_version=1,
        now=NOW + timedelta(seconds=1),
    )
    assert updated.display_name == "Christopher Vale"
    assert updated.role_label is None
    assert updated.version == 2
    assert updated.project_id == character.project_id
    assert updated.identity_id == character.identity_id


def test_character_update_rejects_stale_version_and_no_op() -> None:
    character = _character()
    with pytest.raises(ConcurrencyConflict):
        character.update_metadata(
            display_name="Changed",
            expected_version=2,
            now=NOW,
        )
    with pytest.raises(InvariantViolation):
        character.update_metadata(
            display_name="Christopher",
            expected_version=1,
            now=NOW,
        )


@pytest.mark.parametrize("name", ["", "   ", "x" * 161])
def test_character_display_name_is_bounded(name: str) -> None:
    with pytest.raises(InvariantViolation):
        Character.create(
            character_id=uuid4(),
            workspace_id=uuid4(),
            project_id=uuid4(),
            created_by_principal_id=uuid4(),
            display_name=name,
            role_label=None,
            now=NOW,
        )
