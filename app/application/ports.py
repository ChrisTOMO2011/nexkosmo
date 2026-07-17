from contextlib import AbstractAsyncContextManager
from typing import Any, Protocol
from uuid import UUID

from app.domain.types import Assertion, Decision, Identity, Policy, Principal


class IdentityRepository(Protocol):
    async def add(self, identity: Identity) -> None: ...
    async def get(self, identity_id: UUID) -> Identity | None: ...


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
    async def append(self, event_type: str, version: int, payload: dict[str, Any]) -> None: ...


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


class UnitOfWork(Protocol, AbstractAsyncContextManager["UnitOfWork"]):
    identities: IdentityRepository
    assertions: AssertionRepository
    decisions: DecisionRepository
    policies: PolicyRepository
    registry: RegistryRepository
    outbox: OutboxPort

    async def commit(self) -> None: ...
    async def rollback(self) -> None: ...


class UnitOfWorkFactory(Protocol):
    def __call__(self, principal: Principal) -> UnitOfWork: ...
