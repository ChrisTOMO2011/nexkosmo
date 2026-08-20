from contextlib import AbstractAsyncContextManager
from dataclasses import dataclass
from typing import Any, Literal, Protocol
from uuid import UUID

from app.domain.characters import Character, CharacterAssetManifest, Species
from app.domain.environments import Environment, EnvironmentAssetManifest, EnvironmentType
from app.domain.projects import Production, Project, ProjectMemberRole
from app.domain.types import Assertion, Decision, Identity, Policy, Principal


class CharacterRepository(Protocol):
    async def add(self, character: Character) -> None: ...
    async def get_by_id(self, character_id: UUID) -> Character | None: ...
    async def list_by_project(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[Character]: ...
    async def list_by_production(
        self, production_id: UUID, *, limit: int, offset: int
    ) -> list[Character]: ...
    async def update(self, character: Character, *, expected_version: int) -> None: ...
    async def archive(self, character_id: UUID, *, expected_version: int) -> None: ...
    async def exists(self, character_id: UUID) -> bool: ...
    async def get_version(self, character_id: UUID) -> int | None: ...


class SpeciesRepository(Protocol):
    async def get_by_id(self, species_id: UUID) -> Species | None: ...
    async def get_by_key(self, key: str) -> Species | None: ...
    async def list_enabled(self) -> list[Species]: ...
    async def upsert_seed_data(self, species: tuple[Species, ...]) -> None: ...


class CharacterAssetManifestRepository(Protocol):
    async def get_by_id(self, asset_id: UUID) -> CharacterAssetManifest | None: ...
    async def get_many(self, asset_ids: tuple[UUID, ...]) -> list[CharacterAssetManifest]: ...
    async def list_by_species(
        self,
        species_id: UUID,
        *,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[CharacterAssetManifest]: ...
    async def list_by_category(
        self, category: str, *, limit: int, offset: int
    ) -> list[CharacterAssetManifest]: ...
    async def list_compatible(
        self,
        *,
        species_id: UUID,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[CharacterAssetManifest]: ...
    async def upsert(self, manifest: CharacterAssetManifest) -> None: ...
    async def batch_upsert(self, manifests: tuple[CharacterAssetManifest, ...]) -> None: ...


class EnvironmentRepository(Protocol):
    async def add(self, environment: Environment) -> None: ...
    async def get_by_id(self, environment_id: UUID) -> Environment | None: ...
    async def list_by_project(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[Environment]: ...
    async def list_by_production(
        self, production_id: UUID, *, limit: int, offset: int
    ) -> list[Environment]: ...
    async def update(self, environment: Environment, *, expected_version: int) -> None: ...
    async def archive(self, environment_id: UUID, *, expected_version: int) -> None: ...
    async def exists(self, environment_id: UUID) -> bool: ...
    async def get_version(self, environment_id: UUID) -> int | None: ...


class EnvironmentTypeRepository(Protocol):
    async def get_by_id(self, environment_type_id: UUID) -> EnvironmentType | None: ...
    async def get_by_key(self, key: str) -> EnvironmentType | None: ...
    async def list_enabled(self) -> list[EnvironmentType]: ...


class EnvironmentAssetManifestRepository(Protocol):
    async def get_by_id(self, asset_id: UUID) -> EnvironmentAssetManifest | None: ...
    async def get_many(self, asset_ids: tuple[UUID, ...]) -> list[EnvironmentAssetManifest]: ...
    async def batch_load_dependencies(
        self, asset_ids: tuple[UUID, ...]
    ) -> list[EnvironmentAssetManifest]: ...
    async def list_visible(self, *, limit: int, offset: int) -> list[EnvironmentAssetManifest]: ...
    async def list_by_category(
        self, category: str, *, limit: int, offset: int
    ) -> list[EnvironmentAssetManifest]: ...
    async def list_by_filter(
        self,
        *,
        category: str | None,
        subcategory: str | None,
        limit: int,
        offset: int,
    ) -> list[EnvironmentAssetManifest]: ...
    async def list_compatible(
        self,
        *,
        environment_type_id: UUID,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[EnvironmentAssetManifest]: ...


class ProjectRepository(Protocol):
    async def add(self, project: Project) -> None: ...
    async def get_by_id(self, project_id: UUID) -> Project | None: ...
    async def list_workspace_projects(self, *, limit: int, offset: int) -> list[Project]: ...
    async def update(self, project: Project, *, expected_version: int) -> None: ...
    async def archive(self, project_id: UUID, *, expected_version: int) -> None: ...
    async def get_version(self, project_id: UUID) -> int | None: ...
    async def get_member_role(
        self, project_id: UUID, principal_id: UUID
    ) -> ProjectMemberRole | None: ...
    async def set_member_role(
        self,
        project_id: UUID,
        principal_id: UUID,
        role: ProjectMemberRole,
    ) -> None: ...
    async def remove_member(self, project_id: UUID, principal_id: UUID) -> None: ...


class ProductionRepository(Protocol):
    async def add(self, production: Production) -> None: ...
    async def get_by_id(self, production_id: UUID) -> Production | None: ...
    async def list_project_productions(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[Production]: ...
    async def update(self, production: Production, *, expected_version: int) -> None: ...
    async def archive(self, production_id: UUID, *, expected_version: int) -> None: ...
    async def get_version(self, production_id: UUID) -> int | None: ...


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
    async def append(
        self,
        event_type: str,
        version: int,
        payload: dict[str, Any],
        *,
        aggregate_id: UUID | None = None,
        aggregate_sequence: int | None = None,
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
        deduplication_key: str | None = None,
    ) -> None: ...


class TransactionalIdempotencyPort(Protocol):
    async def complete(self, key: str, response: dict[str, Any]) -> None: ...


class AuditDeliveryQueuePort(Protocol):
    async def enqueue(
        self,
        *,
        deduplication_key: str,
        principal: Principal,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None: ...


class AuditDeliveryPort(Protocol):
    async def deliver(self, workspace_id: UUID, deduplication_key: str) -> bool: ...
    async def record_or_queue(
        self,
        *,
        deduplication_key: str,
        principal: Principal,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None: ...


@dataclass(frozen=True, slots=True)
class IdempotencyClaim:
    state: Literal["acquired", "completed"]
    response: dict[str, Any] | None = None


class IdempotencyPort(Protocol):
    async def acquire(
        self, workspace_id: UUID, key: str, request_hash: str
    ) -> IdempotencyClaim: ...
    async def complete(self, workspace_id: UUID, key: str, response: dict[str, Any]) -> None: ...
    async def fail(self, workspace_id: UUID, key: str, error_code: str) -> None: ...


class UnitOfWork(Protocol, AbstractAsyncContextManager["UnitOfWork"]):
    projects: ProjectRepository
    productions: ProductionRepository
    characters: CharacterRepository
    species: SpeciesRepository
    character_assets: CharacterAssetManifestRepository
    environments: EnvironmentRepository
    environment_types: EnvironmentTypeRepository
    environment_assets: EnvironmentAssetManifestRepository
    idempotency: TransactionalIdempotencyPort
    audit_queue: AuditDeliveryQueuePort
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
