from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from app.domain.errors import AuthorizationDenied, ConcurrencyConflict, InvariantViolation
from app.domain.projects import Production, ProductionState, Project, ProjectLifecycle
from app.domain.workspaces import (
    WorkspaceRole,
    require_project_create_authority,
    require_project_role_compatible,
)

NOW = datetime(2026, 8, 20, tzinfo=UTC)


def _project() -> Project:
    return Project.create(
        project_id=uuid4(),
        workspace_id=uuid4(),
        context_id=uuid4(),
        owner_principal_id=uuid4(),
        name="The Lost Star",
        now=NOW,
    )


def test_project_create_authority_is_owner_or_admin_only() -> None:
    require_project_create_authority(WorkspaceRole.OWNER)
    require_project_create_authority(WorkspaceRole.ADMIN)
    with pytest.raises(AuthorizationDenied):
        require_project_create_authority(WorkspaceRole.MEMBER)
    with pytest.raises(AuthorizationDenied):
        require_project_create_authority(WorkspaceRole.VIEWER)


def test_workspace_viewer_may_only_receive_project_viewer() -> None:
    require_project_role_compatible(WorkspaceRole.VIEWER, "viewer")
    with pytest.raises(InvariantViolation):
        require_project_role_compatible(WorkspaceRole.VIEWER, "editor")


def test_ownership_transfer_requires_owner_and_increments_once() -> None:
    project = _project()
    target = uuid4()
    updated = project.transfer_ownership(
        current_principal_id=project.owner_principal_id,
        target_principal_id=target,
        expected_version=1,
        now=NOW + timedelta(seconds=1),
    )
    assert updated.owner_principal_id == target
    assert updated.version == 2
    with pytest.raises(ConcurrencyConflict):
        project.transfer_ownership(
            current_principal_id=project.owner_principal_id,
            target_principal_id=target,
            expected_version=2,
            now=NOW,
        )


def test_project_archive_and_owner_only_restore() -> None:
    project = _project()
    archived = project.archive(expected_version=1, now=NOW + timedelta(seconds=1))
    assert archived.lifecycle is ProjectLifecycle.ARCHIVED
    assert archived.version == 2
    with pytest.raises(AuthorizationDenied):
        archived.restore(
            principal_id=uuid4(), expected_version=2, now=NOW + timedelta(seconds=2)
        )
    restored = archived.restore(
        principal_id=project.owner_principal_id,
        expected_version=2,
        now=NOW + timedelta(seconds=2),
    )
    assert restored.lifecycle is ProjectLifecycle.ACTIVE
    assert restored.version == 3


@pytest.mark.parametrize(
    ("source", "target"),
    [
        (ProductionState.PLANNED, ProductionState.ACTIVE),
        (ProductionState.PLANNED, ProductionState.ARCHIVED),
        (ProductionState.ACTIVE, ProductionState.PAUSED),
        (ProductionState.ACTIVE, ProductionState.COMPLETED),
        (ProductionState.ACTIVE, ProductionState.ARCHIVED),
        (ProductionState.PAUSED, ProductionState.ACTIVE),
        (ProductionState.PAUSED, ProductionState.ARCHIVED),
        (ProductionState.COMPLETED, ProductionState.ACTIVE),
        (ProductionState.COMPLETED, ProductionState.ARCHIVED),
    ],
)
def test_approved_production_transitions(
    source: ProductionState, target: ProductionState
) -> None:
    production = Production(
        id=uuid4(),
        workspace_id=uuid4(),
        project_id=uuid4(),
        name="Primary Production",
        state=source,
        version=3,
        created_at=NOW,
        updated_at=NOW,
    )
    updated = production.transition(
        target=target,
        expected_version=3,
        project_lifecycle=ProjectLifecycle.ACTIVE,
        now=NOW + timedelta(seconds=1),
    )
    assert updated.state is target
    assert updated.version == 4


def test_archived_production_is_terminal_and_archived_project_is_read_only() -> None:
    production = Production(
        id=uuid4(),
        workspace_id=uuid4(),
        project_id=uuid4(),
        name="Primary Production",
        state=ProductionState.ARCHIVED,
        version=2,
        created_at=NOW,
        updated_at=NOW,
    )
    with pytest.raises(InvariantViolation):
        production.transition(
            target=ProductionState.ACTIVE,
            expected_version=2,
            project_lifecycle=ProjectLifecycle.ACTIVE,
            now=NOW,
        )
    planned = Production.create(
        production_id=uuid4(),
        workspace_id=uuid4(),
        project_id=uuid4(),
        name="Primary Production",
        now=NOW,
    )
    with pytest.raises(InvariantViolation):
        planned.transition(
            target=ProductionState.ACTIVE,
            expected_version=1,
            project_lifecycle=ProjectLifecycle.ARCHIVED,
            now=NOW,
        )
