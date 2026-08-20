from datetime import UTC, datetime
from types import TracebackType
from typing import Any, Self
from uuid import UUID, uuid4

import pytest

from app.application.ports import IdempotencyClaim
from app.application.project_service import ProjectService
from app.domain.enums import AgentKind
from app.domain.errors import AuthorizationDenied
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
        self.identities: list[object] = []
        self.contexts: list[object] = []
        self.activities: list[object] = []
        self.outputs: list[tuple[UUID, UUID, UUID]] = []

    async def add_identity(self, identity: object) -> None:
        self.identities.append(identity)

    async def add_context(self, context: object) -> None:
        self.contexts.append(context)

    async def add_activity(self, activity: object) -> None:
        self.activities.append(activity)

    async def add_activity_output(
        self, *, workspace_id: UUID, activity_id: UUID, identity_id: UUID
    ) -> None:
        self.outputs.append((workspace_id, activity_id, identity_id))


class FakeWorkspaceAuthority:
    async def require_current_human_role(self, **_: object) -> WorkspaceRole:
        return WorkspaceRole.OWNER


class FakeCollection:
    def __init__(self) -> None:
        self.items: list[object] = []

    async def add(self, item: object) -> None:
        self.items.append(item)

    async def list_for_principal(self, **_: object) -> list[object]:
        return self.items


class FakeTransactionalIdempotency:
    def __init__(self) -> None:
        self.lease_checked = False
        self.completed: dict[str, Any] | None = None

    async def require_lease(self, **_: object) -> None:
        self.lease_checked = True

    async def complete(self, *, response: dict[str, Any], **_: object) -> None:
        self.completed = response


class FakeOutbox:
    def __init__(self) -> None:
        self.events: list[str] = []

    async def append(
        self,
        event_type: str,
        version: int,
        payload: dict[str, Any],
        **_: object,
    ) -> None:
        self.events.append(event_type)


class FakeAuditQueue:
    def __init__(self) -> None:
        self.actions: list[str] = []

    async def append(self, *, action: str, **_: object) -> None:
        self.actions.append(action)


class FakeUow:
    def __init__(self) -> None:
        self.semantic_projects = FakeSemantic()
        self.workspace_authority = FakeWorkspaceAuthority()
        self.projects = FakeCollection()
        self.project_memberships = FakeCollection()
        self.transactional_idempotency = FakeTransactionalIdempotency()
        self.outbox = FakeOutbox()
        self.audit_delivery_queue = FakeAuditQueue()
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
    def __init__(self, fail: bool = False) -> None:
        self.fail = fail
        self.calls = 0

    async def deliver_pending(self, *, principal: Principal) -> int:
        self.calls += 1
        if self.fail:
            raise RuntimeError("audit unavailable")
        return 1


def _principal(kind: AgentKind = AgentKind.HUMAN) -> Principal:
    return Principal(
        principal_id=uuid4(),
        workspace_id=uuid4(),
        agent_id=uuid4(),
        agent_kind=kind,
    )


@pytest.mark.asyncio
async def test_project_listing_requires_workspace_and_project_membership_visibility() -> None:
    uow = FakeUow()
    service = ProjectService(
        lambda _: uow,
        FakeIdempotency(),
        FakeAuditDelivery(),
        clock=lambda: NOW,
    )
    result = await service.list_projects(_principal())
    assert result == []


@pytest.mark.asyncio
async def test_project_creation_is_one_transactional_semantic_bundle() -> None:
    uow = FakeUow()
    idempotency = FakeIdempotency()
    audit = FakeAuditDelivery()
    service = ProjectService(lambda _: uow, idempotency, audit, clock=lambda: NOW)
    result = await service.create_project(
        _principal(), name="The Lost Star", idempotency_key="create-project-1"
    )
    assert result["name"] == "The Lost Star"
    assert len(uow.semantic_projects.identities) == 2
    assert len(uow.semantic_projects.contexts) == 1
    assert len(uow.semantic_projects.activities) == 1
    assert len(uow.projects.items) == 1
    assert len(uow.project_memberships.items) == 1
    assert uow.transactional_idempotency.lease_checked
    assert uow.transactional_idempotency.completed == result
    assert uow.outbox.events == ["project.created"]
    assert uow.audit_delivery_queue.actions == ["project.create"]
    assert uow.committed
    assert audit.calls == 1


@pytest.mark.asyncio
async def test_completed_idempotent_replay_does_not_open_uow() -> None:
    expected = {"project_id": str(uuid4()), "version": 1}
    idempotency = FakeIdempotency(replay=expected)

    def forbidden_factory(_: Principal) -> FakeUow:
        raise AssertionError("replay must not open a business UoW")

    service = ProjectService(forbidden_factory, idempotency, FakeAuditDelivery())
    result = await service.create_project(
        _principal(), name="The Lost Star", idempotency_key="replay"
    )
    assert result == expected


@pytest.mark.asyncio
async def test_non_human_agent_cannot_claim_project_authority() -> None:
    idempotency = FakeIdempotency()
    service = ProjectService(lambda _: FakeUow(), idempotency, FakeAuditDelivery())
    with pytest.raises(AuthorizationDenied):
        await service.create_project(
            _principal(AgentKind.AI), name="The Lost Star", idempotency_key="ai"
        )
    assert idempotency.claims == 0


@pytest.mark.asyncio
async def test_audit_outage_does_not_reverse_committed_business_state() -> None:
    uow = FakeUow()
    service = ProjectService(
        lambda _: uow,
        FakeIdempotency(),
        FakeAuditDelivery(fail=True),
        clock=lambda: NOW,
    )
    result = await service.create_project(
        _principal(), name="The Lost Star", idempotency_key="audit-outage"
    )
    assert result["version"] == 1
    assert uow.committed
    assert uow.audit_delivery_queue.actions == ["project.create"]
