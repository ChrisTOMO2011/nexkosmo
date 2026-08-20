from datetime import UTC, datetime
from types import TracebackType
from typing import Any, Self, cast
from uuid import UUID, uuid4

import pytest

from app.application.character_service import CharacterService
from app.application.ports import IdempotencyClaim, UnitOfWorkFactory
from app.domain.enums import AgentKind, IdentityKind
from app.domain.errors import AuthorizationDenied
from app.domain.projects import Project, ProjectRole
from app.domain.types import Principal
from app.domain.workspaces import WorkspaceRole

NOW = datetime(2026, 8, 20, tzinfo=UTC)


class FakeIdempotency:
    def __init__(self, replay: dict[str, Any] | None = None) -> None:
        self.replay = replay
        self.claims = 0

    async def claim(
        self, *, principal: Principal, key: str, request_hash: str
    ) -> IdempotencyClaim:
        self.claims += 1
        if self.replay is not None:
            return IdempotencyClaim(owner_token=None, response=self.replay)
        return IdempotencyClaim(owner_token=uuid4())


class FakeSemantic:
    def __init__(self) -> None:
        self.identities: list[Any] = []
        self.activities: list[Any] = []
        self.outputs: list[tuple[UUID, UUID, UUID]] = []

    async def add_identity(self, identity: object) -> None:
        self.identities.append(identity)

    async def add_activity(self, activity: object) -> None:
        self.activities.append(activity)

    async def add_activity_output(
        self, *, workspace_id: UUID, activity_id: UUID, identity_id: UUID
    ) -> None:
        self.outputs.append((workspace_id, activity_id, identity_id))


class FakeWorkspaceAuthority:
    async def require_current_human_role(self, **_: object) -> WorkspaceRole:
        return WorkspaceRole.OWNER


class FakeProjects:
    def __init__(self, project: Project) -> None:
        self.project = project
        self.unlocked = False

    async def get(self, project_id: UUID, *, lock: bool = False) -> Project | None:
        return self.project if project_id == self.project.id else None

    async def require_unlocked(self, project_id: UUID) -> None:
        assert project_id == self.project.id
        self.unlocked = True


class FakeProjectMemberships:
    def __init__(self, role: ProjectRole) -> None:
        self.role = role

    async def require_role(self, **_: object) -> ProjectRole:
        return self.role


class FakeCharacters:
    def __init__(self) -> None:
        self.items: dict[UUID, Any] = {}

    async def add(self, character: Any) -> None:
        self.items[character.id] = character

    async def get(self, character_id: UUID, *, lock: bool = False) -> Any:
        return self.items.get(character_id)

    async def list_for_project(self, project_id: UUID) -> list[Any]:
        return [item for item in self.items.values() if item.project_id == project_id]

    async def update(self, character: Any, *, expected_version: int) -> None:
        assert self.items[character.id].version == expected_version
        self.items[character.id] = character


class FakeTransactionalIdempotency:
    def __init__(self) -> None:
        self.lease_checked = False
        self.completed: dict[str, Any] | None = None
        self.order: list[str] = []

    async def require_lease(self, **_: object) -> None:
        self.lease_checked = True

    async def complete(self, *, response: dict[str, Any], **_: object) -> None:
        self.completed = response
        self.order.append("idempotency")


class FakeOutbox:
    def __init__(self, order: list[str]) -> None:
        self.events: list[str] = []
        self.order = order

    async def append(
        self, event_type: str, version: int, payload: dict[str, Any], **_: object
    ) -> None:
        self.events.append(event_type)
        self.order.append("outbox")


class FakeAuditQueue:
    def __init__(self, order: list[str]) -> None:
        self.actions: list[str] = []
        self.order = order

    async def append(self, *, action: str, **_: object) -> None:
        self.actions.append(action)
        self.order.append("audit")


class FakeUow:
    def __init__(self, project: Project, role: ProjectRole = ProjectRole.OWNER) -> None:
        self.semantic_projects = FakeSemantic()
        self.workspace_authority = FakeWorkspaceAuthority()
        self.projects = FakeProjects(project)
        self.project_memberships = FakeProjectMemberships(role)
        self.characters = FakeCharacters()
        self.transactional_idempotency = FakeTransactionalIdempotency()
        self.outbox = FakeOutbox(self.transactional_idempotency.order)
        self.audit_delivery_queue = FakeAuditQueue(self.transactional_idempotency.order)
        self.committed = False

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        return None

    async def commit(self) -> None:
        self.committed = True


class FakeAuditDelivery:
    def __init__(self) -> None:
        self.calls = 0

    async def deliver_pending(self, *, principal: Principal) -> int:
        self.calls += 1
        return 1


def _principal(project: Project, kind: AgentKind = AgentKind.HUMAN) -> Principal:
    return Principal(
        principal_id=project.owner_principal_id,
        workspace_id=project.workspace_id,
        agent_id=uuid4(),
        agent_kind=kind,
    )


def _project() -> Project:
    return Project.create(
        project_id=uuid4(),
        workspace_id=uuid4(),
        context_id=uuid4(),
        owner_principal_id=uuid4(),
        name="The Lost Star",
        now=NOW,
    )


def _factory(uow: FakeUow) -> UnitOfWorkFactory:
    return cast(UnitOfWorkFactory, lambda _: uow)


@pytest.mark.asyncio
async def test_character_creation_is_one_project_context_transaction() -> None:
    project = _project()
    uow = FakeUow(project)
    audit = FakeAuditDelivery()
    service = CharacterService(
        _factory(uow), FakeIdempotency(), audit, clock=lambda: NOW
    )
    result = await service.create_character(
        _principal(project),
        project_id=project.id,
        display_name="Christopher",
        role_label="Lead",
        idempotency_key="character-1",
    )
    assert result["project_id"] == str(project.id)
    assert len(uow.semantic_projects.identities) == 1
    assert uow.semantic_projects.identities[0].kind is IdentityKind.CHARACTER
    assert uow.semantic_projects.activities[0].context_id == project.context_id
    assert uow.semantic_projects.activities[0].outputs == (
        uow.semantic_projects.identities[0].id,
    )
    assert uow.transactional_idempotency.order == ["idempotency", "outbox", "audit"]
    assert uow.committed
    assert audit.calls == 1


@pytest.mark.asyncio
async def test_viewer_is_read_only_but_can_list() -> None:
    project = _project()
    uow = FakeUow(project, ProjectRole.VIEWER)
    service = CharacterService(
        _factory(uow), FakeIdempotency(), FakeAuditDelivery(), clock=lambda: NOW
    )
    with pytest.raises(AuthorizationDenied):
        await service.create_character(
            _principal(project),
            project_id=project.id,
            display_name="Christopher",
            role_label=None,
            idempotency_key="viewer-create",
        )
    assert await service.list_characters(_principal(project), project_id=project.id) == []


@pytest.mark.asyncio
async def test_archived_project_blocks_character_mutation() -> None:
    project = _project().archive(expected_version=1, now=NOW)
    service = CharacterService(
        _factory(FakeUow(project)),
        FakeIdempotency(),
        FakeAuditDelivery(),
        clock=lambda: NOW,
    )
    with pytest.raises(AuthorizationDenied, match="Archived"):
        await service.create_character(
            _principal(project),
            project_id=project.id,
            display_name="Christopher",
            role_label=None,
            idempotency_key="archived",
        )


@pytest.mark.asyncio
async def test_non_human_actor_is_rejected_before_idempotency_claim() -> None:
    project = _project()
    idempotency = FakeIdempotency()
    service = CharacterService(
        _factory(FakeUow(project)), idempotency, FakeAuditDelivery()
    )
    with pytest.raises(AuthorizationDenied):
        await service.create_character(
            _principal(project, AgentKind.AI),
            project_id=project.id,
            display_name="Christopher",
            role_label=None,
            idempotency_key="ai",
        )
    assert idempotency.claims == 0


@pytest.mark.asyncio
async def test_completed_replay_does_not_open_business_uow() -> None:
    project = _project()
    expected = {"character_id": str(uuid4()), "version": 1}

    def forbidden_factory(_: Principal) -> FakeUow:
        raise AssertionError("replay must not open a business UoW")

    service = CharacterService(
        cast(UnitOfWorkFactory, forbidden_factory),
        FakeIdempotency(replay=expected),
        FakeAuditDelivery(),
    )
    result = await service.create_character(
        _principal(project),
        project_id=project.id,
        display_name="Christopher",
        role_label=None,
        idempotency_key="replay",
    )
    assert result == expected
