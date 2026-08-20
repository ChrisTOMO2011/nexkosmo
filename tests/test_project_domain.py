from dataclasses import FrozenInstanceError
from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.domain.errors import InvariantViolation
from app.domain.projects import Production, ProductionType, Project

WORKSPACE_ID = UUID("60000000-0000-4000-8000-000000000001")
OWNER_ID = UUID("60000000-0000-4000-8000-000000000002")
MEMBER_ID = UUID("60000000-0000-4000-8000-000000000003")
PROJECT_ID = UUID("60000000-0000-4000-8000-000000000004")
PRODUCTION_ID = UUID("60000000-0000-4000-8000-000000000005")
NOW = datetime(2026, 7, 28, tzinfo=UTC)


def test_project_is_immutable_versioned_and_owns_membership():
    project = Project.create(
        project_id=PROJECT_ID,
        workspace_id=WORKSPACE_ID,
        name="The Last Dawn",
        description="Feature production.",
        owner_id=OWNER_ID,
        now=NOW,
    )
    member_added = project.add_member(MEMBER_ID, now=NOW)
    renamed = member_added.rename("The Last Dawn II", now=NOW)
    archived = renamed.archive(now=NOW)
    restored = archived.restore(now=NOW)

    assert project.member_ids == (OWNER_ID,)
    assert member_added.member_ids == (OWNER_ID, MEMBER_ID)
    assert restored.status == "active"
    assert restored.version == 5
    with pytest.raises(FrozenInstanceError):
        project.name = "Mutable"  # type: ignore[misc]
    with pytest.raises(InvariantViolation):
        project.remove_member(OWNER_ID)


def test_project_owner_change_preserves_owner_membership_invariant():
    project = Project.create(
        project_id=PROJECT_ID,
        workspace_id=WORKSPACE_ID,
        name="The Last Dawn",
        description="Feature production.",
        owner_id=OWNER_ID,
        now=NOW,
    )
    transferred = project.change_owner(MEMBER_ID)
    assert transferred.owner_id == MEMBER_ID
    assert transferred.member_ids == (OWNER_ID, MEMBER_ID)


@pytest.mark.parametrize(
    "production_type",
    [
        "Feature Film",
        "Short Film",
        "TV",
        "Commercial",
        "Music Video",
        "Social",
        "Animation",
        "Documentary",
        "Custom",
    ],
)
def test_production_supports_canonical_types_and_statuses(
    production_type: ProductionType,
):
    production = Production.create(
        production_id=PRODUCTION_ID,
        project_id=PROJECT_ID,
        workspace_id=WORKSPACE_ID,
        name="Principal Photography",
        production_type=production_type,
        owner_id=OWNER_ID,
        now=NOW,
    )
    renamed = production.rename("The Last Dawn Production", now=NOW)
    active = renamed.change_status("production", now=NOW)
    archived = active.archive(now=NOW)

    assert production.status == "pre-production"
    assert archived.status == "archived"
    assert archived.version == 4
    with pytest.raises(InvariantViolation):
        Production.create(
            project_id=PROJECT_ID,
            workspace_id=WORKSPACE_ID,
            name="Invalid",
            production_type="Unsupported",  # type: ignore[arg-type]
            owner_id=OWNER_ID,
        )
