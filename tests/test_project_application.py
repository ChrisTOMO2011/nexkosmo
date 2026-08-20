from uuid import UUID

import pytest

from app.application.character_service import CharacterApplicationService
from app.application.project_service import ProjectProductionApplicationService
from app.domain.enums import AgentKind
from app.domain.errors import AuthorizationDenied, ConcurrencyConflict
from app.domain.types import Principal
from tests.character_fakes import (
    AGENT_ID,
    HUMAN_ID,
    PRINCIPAL_ID,
    PRODUCTION_ID,
    PROJECT_ID,
    WORKSPACE_ID,
    FakeAudit,
    FakeIdempotency,
    FakeStore,
    FakeUnitOfWorkFactory,
)

EDITOR_ID = UUID("61000000-0000-4000-8000-000000000001")
VIEWER_ID = UUID("61000000-0000-4000-8000-000000000002")


def principal(principal_id: UUID) -> Principal:
    return Principal(
        principal_id=principal_id,
        workspace_id=WORKSPACE_ID,
        agent_id=AGENT_ID,
        agent_kind=AgentKind.HUMAN,
    )


async def test_project_and_production_services_emit_audit_outbox_and_versions():
    store = FakeStore()
    audit = FakeAudit(store)
    service = ProjectProductionApplicationService(
        FakeUnitOfWorkFactory(store), audit, FakeIdempotency(store)
    )
    owner = principal(PRINCIPAL_ID)

    created = await service.create_project(
        owner,
        name="Canonical Project",
        description="Owned by the workspace.",
        idempotency_key="project-create",
    )
    renamed = await service.update_project(
        owner,
        created.project.project_id,
        expected_version=1,
        name="Canonical Project Renamed",
        description=None,
        status=None,
        idempotency_key="project-rename",
    )
    production = await service.create_production(
        owner,
        created.project.project_id,
        name="Feature Production",
        production_type="Feature Film",
        idempotency_key="production-create",
    )
    updated = await service.update_production(
        owner,
        production.production.production_id,
        expected_version=1,
        name=None,
        status="production",
        idempotency_key="production-status",
    )

    assert renamed.project.version == 2
    assert updated.production.version == 2
    assert [event["event_type"] for event in store.outbox[-4:]] == [
        "project.created",
        "project.updated",
        "production.created",
        "production.updated",
    ]
    assert [record["action"] for record in audit.records[-4:]] == [
        "project.created",
        "project.updated",
        "production.created",
        "production.updated",
    ]
    assert all(record["outcome"] == "success" for record in audit.records[-4:])
    with pytest.raises(ConcurrencyConflict):
        await service.update_production(
            owner,
            production.production.production_id,
            expected_version=1,
            name="Stale",
            status=None,
            idempotency_key="production-stale",
        )
    assert audit.records[-1]["outcome"] == "failure"


async def test_membership_roles_gate_projects_productions_and_character_edits():
    store = FakeStore()
    audit = FakeAudit(store)
    idempotency = FakeIdempotency(store)
    projects = ProjectProductionApplicationService(FakeUnitOfWorkFactory(store), audit, idempotency)
    characters = CharacterApplicationService(FakeUnitOfWorkFactory(store), audit, idempotency)
    owner = principal(PRINCIPAL_ID)

    editor_project = await projects.set_project_member_role(
        owner,
        PROJECT_ID,
        EDITOR_ID,
        role="Editor",
        expected_version=1,
        idempotency_key="add-editor",
    )
    await projects.set_project_member_role(
        owner,
        PROJECT_ID,
        VIEWER_ID,
        role="Viewer",
        expected_version=editor_project.project.version,
        idempotency_key="add-viewer",
    )
    created = await characters.create_character(
        owner,
        project_id=PROJECT_ID,
        production_id=PRODUCTION_ID,
        display_name="Membership Character",
        role="Lead",
        species_id=HUMAN_ID,
        idempotency_key="membership-character",
    )

    editor_update = await characters.update_metadata(
        principal(EDITOR_ID),
        created.character.character_id,
        expected_version=1,
        display_name="Editor Updated Character",
        role=None,
        idempotency_key="editor-character-update",
    )
    assert editor_update.character.version == 2
    assert await characters.get_character(principal(VIEWER_ID), created.character.character_id)
    with pytest.raises(AuthorizationDenied):
        await characters.update_metadata(
            principal(VIEWER_ID),
            created.character.character_id,
            expected_version=2,
            display_name="Viewer Mutation",
            role=None,
            idempotency_key="viewer-character-update",
        )
