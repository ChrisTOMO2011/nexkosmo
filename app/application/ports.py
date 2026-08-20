from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from app.domain.characters import Character
from app.domain.projects import (
    Production,
    Project,
    ProjectMembership,
    ProjectRole,
)
from app.domain.types import Activity, Assertion, Context, Decision, Identity, Policy, Principal
from app.domain.workspaces import WorkspaceRole


@dataclass(frozen=True, slots=True)
class IdempotencyClaim:
    owner_token: UUID | None
    response: dict[str, Any] | None = None

    @property
    def is_replay(self) -> bool:
        return self.response is not None


class IdentityRepository(Protocol):
    async def add(self, identity: Identity) -> None: ...
    async def get(self, identity_id: UUID) -> Identity | None: ...


class SemanticProjectRepository(Protocol):
    async def add_identity(self, identity: Identity) -> None: ...
    async def add_context(self, context: Context) -> None: ...
    async def add_activity(self, activity: Activity) -> None: ...
    async def add_activity_output(
        self, *, workspace_id: UUID, activity_id: UUID, identity_id: UUID
    ) -> None: ...


class WorkspaceAuthorityRepository(Protocol):
    async def require_current_human_role(
        self,
        *,
        workspace_id: UUID,
        principal_id: UUID,
        agent_id: UUID,
        at: datetime,
        lock: bool = False,
    ) -> WorkspaceRole: ...

    async def require_active_human_principal(
        self,
        *,
        workspace_id: UUID,
        principal_id: UUID,
        at: datetime,
        lock: bool = False,
    ) -> WorkspaceRole: ...


class ProjectRepository(Protocol):
    async def add(self, project: Project) -> None: ...
    async def get(self, project_id: UUID, *, lock: bool = False) -> Project | None: ...
    async def require_unlocked(self, project_id: UUID) -> None: ...
    async def update(self, project: Project, *, expected_version: int) -> None: ...


class ProjectMembershipRepository(Protocol):
    async def add(self, membership: ProjectMembership) -> None: ...
    async def require_role(
        self,
        *,
        project_id: UUID,
        principal_id: UUID,
        at: datetime,
        lock: bool = False,
    ) -> ProjectRole: ...
    async def transfer_owner(
        self,
        *,
        project_id: UUID,
        current_owner_id: UUID,
        target_principal_id: UUID,
        acting_agent_id: UUID,
        at: datetime,
    ) -> None: ...


class ProductionRepository(Protocol):
    async def add(self, production: Production) -> None: ...
    async def get(self, production_id: UUID, *, lock: bool = False) -> Production | None: ...
    async def update(self, production: Production, *, expected_version: int) -> None: ...


class CharacterRepository(Protocol):
    async def add(self, character: Character) -> None: ...
    async def get(self, character_id: UUID, *, lock: bool = False) -> Character | None: ...
    async def list_for_project(self, project_id: UUID) -> list[Character]: ...
    async def update(self, character: Character, *, expected_version: int) -> None: ...


class TransactionalIdempotencyRepository(Protocol):
    async def require_lease(
        self,
        *,
        workspace_id: UUID,
        key: str,
        request_hash: str,
        owner_token: UUID,
    ) -> None: ...
    async def complete(
        self,
        *,
        workspace_id: UUID,
        key: str,
        request_hash: str,
        owner_token: UUID,
        response: dict[str, Any],
    ) -> None: ...


class AuditDeliveryQueueRepository(Protocol):
    async def append(
        self,
        *,
        workspace_id: UUID,
        deduplication_key: str,
        principal_id: UUID,
        agent_id: UUID,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None: ...


class AssertionRepository(Protocol):
    async def add(self, assertion: Assertion) -> None: ...
    async def list_for_subject(self, subject_id: UUID, context_id: UUID) -> list[Assertion]: ...


class DecisionRepository(Protocol):
    async def add(self, decision: Decision) -> None: ...
    async def list_for_targets(self, target_ids: tuple[UUID, ...]) -> list[Decision]: ...


class PolicyRepository(Protocol):
    async def list_for_request(self, *, agent_id: UUID, resource_id: UUID) -> list[Policy]: ...


class RegistryRepository(Protocol):
    async def require_active(self, namespace: str, key: str, version: int) -> None: ...


class OutboxPort(Protocol):
    async def append(
        self,
        event_type: str,
        version: int,
        payload: dict[str, Any],
        *,
        aggregate_id: UUID | None = None,
        aggregate_sequence: int = 1,
    ) -> None: ...


class AuditPort(Protocol):
    async def record_independent(
        self,
        *,
        principal: Principal | None,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None: ...


class IdempotencyPort(Protocol):
    async def acquire(self, workspace_id: UUID, key: str, request_hash: str) -> str: ...
    async def complete(self, workspace_id: UUID, key: str, response: dict[str, Any]) -> None: ...
    async def fail(self, workspace_id: UUID, key: str, error_code: str) -> None: ...


class TransactionalIdempotencyPort(Protocol):
    async def claim(
        self,
        *,
        principal: Principal,
        key: str,
        request_hash: str,
    ) -> IdempotencyClaim: ...


class AuditDeliveryPort(Protocol):
    async def deliver_pending(self, *, principal: Principal) -> int: ...


class UnitOfWork(Protocol, AbstractAsyncContextManager["UnitOfWork"]):
    identities: IdentityRepository
    assertions: AssertionRepository
    decisions: DecisionRepository
    policies: PolicyRepository
    registry: RegistryRepository
    outbox: OutboxPort
    semantic_projects: SemanticProjectRepository
    workspace_authority: WorkspaceAuthorityRepository
    projects: ProjectRepository
    project_memberships: ProjectMembershipRepository
    productions: ProductionRepository
    characters: CharacterRepository
    transactional_idempotency: TransactionalIdempotencyRepository
    audit_delivery_queue: AuditDeliveryQueueRepository

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...


class UnitOfWorkFactory(Protocol):
    def __call__(self, principal: Principal) -> UnitOfWork: ...
