from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import UTC, datetime
from types import TracebackType
from typing import Any, Self, cast
from uuid import UUID

from app.application.ports import IdempotencyClaim, UnitOfWork
from app.domain.characters import Character, CharacterAssetManifest, Species
from app.domain.errors import ConcurrencyConflict, IdempotencyConflict
from app.domain.projects import Production, Project, ProjectMemberRole
from app.domain.types import Principal

WORKSPACE_ID = UUID("10000000-0000-4000-8000-000000000001")
PRINCIPAL_ID = UUID("10000000-0000-4000-8000-000000000002")
AGENT_ID = UUID("10000000-0000-4000-8000-000000000003")
PROJECT_ID = UUID("10000000-0000-4000-8000-000000000004")
PRODUCTION_ID = UUID("10000000-0000-4000-8000-000000000005")
HUMAN_ID = UUID("20000001-0000-4000-8000-000000000001")
GOBLIN_ID = UUID("20000003-0000-4000-8000-000000000003")
HUMAN_PROFILE_ID = UUID("40000001-0000-4000-8000-000000000001")
GOBLIN_PROFILE_ID = UUID("40000001-0000-4000-8000-000000000003")
HUMAN_RIG_ID = UUID("30000003-0000-4000-8000-000000000003")
GOBLIN_RIG_ID = UUID("30000003-0000-4000-8000-000000000023")
HUMAN_SKELETON_ID = UUID("30000004-0000-4000-8000-000000000004")
GOBLIN_SKELETON_ID = UUID("30000004-0000-4000-8000-000000000024")
HUMAN_MATERIAL_ID = UUID("30000005-0000-4000-8000-000000000005")
GOBLIN_MATERIAL_ID = UUID("30000005-0000-4000-8000-000000000025")
HUMAN_BODY_ID = UUID("30000007-0000-4000-8000-000000000007")
GOBLIN_BODY_ID = UUID("30000007-0000-4000-8000-000000000027")
HUMAN_HAIR_ID = UUID("41000001-0000-4000-8000-000000000001")
SHARED_VOICE_ID = UUID("41000002-0000-4000-8000-000000000001")
NOW = datetime(2026, 7, 28, tzinfo=UTC)


def default_project() -> Project:
    return Project.create(
        project_id=PROJECT_ID,
        workspace_id=WORKSPACE_ID,
        name="Test Project",
        description="Character test project.",
        owner_id=PRINCIPAL_ID,
        now=NOW,
    )


def default_production() -> Production:
    return Production.create(
        production_id=PRODUCTION_ID,
        project_id=PROJECT_ID,
        workspace_id=WORKSPACE_ID,
        name="Test Production",
        production_type="Feature Film",
        owner_id=PRINCIPAL_ID,
        now=NOW,
    )


def manifest(
    asset_id: UUID,
    *,
    name: str,
    category: str,
    species_ids: tuple[UUID, ...],
    capabilities: frozenset[str] = frozenset(),
) -> CharacterAssetManifest:
    return CharacterAssetManifest(
        asset_id=asset_id,
        workspace_id=None,
        name=name,
        species_ids=species_ids,
        type_ids=(),
        category=category,
        subcategory="test",
        thumbnail_reference=f"brain://assets/{asset_id}/thumbnail",
        preview_reference=f"brain://assets/{asset_id}/preview",
        source="test",
        status="available",
        tags=frozenset({"test"}),
        gender_compatibility=(),
        age_compatibility=(),
        body_compatibility=(),
        rig_compatibility=(),
        skeleton_compatibility=(),
        material_compatibility=(),
        required_capabilities=capabilities,
        incompatible_asset_ids=(),
        dependent_asset_ids=(),
        file_references=(),
        generated=False,
        uploaded=False,
        provenance={"test": True},
        visibility="global",
        attachment_point=None,
        compatible_body_regions=(),
        profile_metadata={},
        version=1,
        created_at=NOW,
        updated_at=NOW,
    )


def species_fixtures() -> dict[UUID, Species]:
    return {
        HUMAN_ID: Species(
            species_id=HUMAN_ID,
            key="human",
            name="Human",
            category="humanoid",
            enabled=True,
            capabilities=frozenset({"hair", "voice", "wears-accessories"}),
            supported_tabs=("Identity", "Hair", "Voice"),
            compatibility_profile_id=HUMAN_PROFILE_ID,
            default_rig_id=HUMAN_RIG_ID,
            default_skeleton_id=HUMAN_SKELETON_ID,
            default_material_profile_id=HUMAN_MATERIAL_ID,
            default_body_id=HUMAN_BODY_ID,
            min_age=0,
            max_age=120,
            min_height_cm=120,
            max_height_cm=230,
            surface_control_label="Skin Tone",
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
        GOBLIN_ID: Species(
            species_id=GOBLIN_ID,
            key="goblin",
            name="Goblin",
            category="humanoid",
            enabled=True,
            capabilities=frozenset({"voice", "wears-accessories"}),
            supported_tabs=("Identity", "Voice"),
            compatibility_profile_id=GOBLIN_PROFILE_ID,
            default_rig_id=GOBLIN_RIG_ID,
            default_skeleton_id=GOBLIN_SKELETON_ID,
            default_material_profile_id=GOBLIN_MATERIAL_ID,
            default_body_id=GOBLIN_BODY_ID,
            min_age=0,
            max_age=180,
            min_height_cm=70,
            max_height_cm=170,
            surface_control_label="Skin Tone",
            version=1,
            created_at=NOW,
            updated_at=NOW,
        ),
    }


def asset_fixtures() -> dict[UUID, CharacterAssetManifest]:
    assets = {
        HUMAN_HAIR_ID: manifest(
            HUMAN_HAIR_ID,
            name="Human Hair",
            category="hair",
            species_ids=(HUMAN_ID,),
            capabilities=frozenset({"hair"}),
        ),
        SHARED_VOICE_ID: manifest(
            SHARED_VOICE_ID,
            name="Shared Voice",
            category="voice",
            species_ids=(HUMAN_ID, GOBLIN_ID),
            capabilities=frozenset({"voice"}),
        ),
    }
    for asset_id, name, category, declared_species in (
        (HUMAN_RIG_ID, "Human Rig", "rig", HUMAN_ID),
        (GOBLIN_RIG_ID, "Goblin Rig", "rig", GOBLIN_ID),
        (HUMAN_SKELETON_ID, "Human Skeleton", "skeleton", HUMAN_ID),
        (GOBLIN_SKELETON_ID, "Goblin Skeleton", "skeleton", GOBLIN_ID),
        (HUMAN_MATERIAL_ID, "Human Material", "material", HUMAN_ID),
        (GOBLIN_MATERIAL_ID, "Goblin Material", "material", GOBLIN_ID),
        (HUMAN_BODY_ID, "Human Body", "body", HUMAN_ID),
        (GOBLIN_BODY_ID, "Goblin Body", "body", GOBLIN_ID),
    ):
        assets[asset_id] = manifest(
            asset_id,
            name=name,
            category=category,
            species_ids=(declared_species,),
        )
    return assets


@dataclass
class FakeStore:
    projects: dict[UUID, Project] = field(default_factory=lambda: {PROJECT_ID: default_project()})
    productions: dict[UUID, Production] = field(
        default_factory=lambda: {PRODUCTION_ID: default_production()}
    )
    project_roles: dict[tuple[UUID, UUID], ProjectMemberRole] = field(
        default_factory=lambda: {(PROJECT_ID, PRINCIPAL_ID): "Owner"}
    )
    characters: dict[UUID, Character] = field(default_factory=dict)
    species: dict[UUID, Species] = field(default_factory=species_fixtures)
    assets: dict[UUID, CharacterAssetManifest] = field(default_factory=asset_fixtures)
    outbox: list[dict[str, Any]] = field(default_factory=list)
    idempotency: dict[tuple[UUID, str], dict[str, Any]] = field(default_factory=dict)
    audit_queue: dict[tuple[UUID, str], dict[str, Any]] = field(default_factory=dict)


class FakeCharacterRepository:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    async def add(self, character: Character) -> None:
        self.store.characters[character.character_id] = character

    async def get_by_id(self, character_id: UUID) -> Character | None:
        return self.store.characters.get(character_id)

    async def list_by_project(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[Character]:
        values = [item for item in self.store.characters.values() if item.project_id == project_id]
        return values[offset : offset + limit]

    async def list_by_production(
        self, production_id: UUID, *, limit: int, offset: int
    ) -> list[Character]:
        values = [
            item for item in self.store.characters.values() if item.production_id == production_id
        ]
        return values[offset : offset + limit]

    async def update(self, character: Character, *, expected_version: int) -> None:
        current = self.store.characters.get(character.character_id)
        if current is None or current.version != expected_version:
            raise ConcurrencyConflict("stale character version")
        self.store.characters[character.character_id] = character

    async def archive(self, character_id: UUID, *, expected_version: int) -> None:
        character = self.store.characters[character_id]
        await self.update(
            character.update_pipeline_status("archived"),
            expected_version=expected_version,
        )

    async def exists(self, character_id: UUID) -> bool:
        return character_id in self.store.characters

    async def get_version(self, character_id: UUID) -> int | None:
        character = self.store.characters.get(character_id)
        return character.version if character else None


class FakeProjectRepository:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    async def add(self, project: Project) -> None:
        self.store.projects[project.project_id] = project
        self.store.project_roles[(project.project_id, project.owner_id)] = "Owner"

    async def get_by_id(self, project_id: UUID) -> Project | None:
        return self.store.projects.get(project_id)

    async def list_workspace_projects(self, *, limit: int, offset: int) -> list[Project]:
        values = list(self.store.projects.values())
        return values[offset : offset + limit]

    async def update(self, project: Project, *, expected_version: int) -> None:
        current = self.store.projects.get(project.project_id)
        if current is None or current.version != expected_version:
            raise ConcurrencyConflict("stale project version")
        self.store.projects[project.project_id] = project
        for key in tuple(self.store.project_roles):
            if key[0] == project.project_id and key[1] not in project.member_ids:
                del self.store.project_roles[key]

    async def archive(self, project_id: UUID, *, expected_version: int) -> None:
        project = self.store.projects[project_id]
        await self.update(project.archive(), expected_version=expected_version)

    async def get_version(self, project_id: UUID) -> int | None:
        project = self.store.projects.get(project_id)
        return project.version if project else None

    async def get_member_role(
        self, project_id: UUID, principal_id: UUID
    ) -> ProjectMemberRole | None:
        return self.store.project_roles.get((project_id, principal_id))

    async def set_member_role(
        self,
        project_id: UUID,
        principal_id: UUID,
        role: ProjectMemberRole,
    ) -> None:
        self.store.project_roles[(project_id, principal_id)] = role

    async def remove_member(self, project_id: UUID, principal_id: UUID) -> None:
        self.store.project_roles.pop((project_id, principal_id), None)


class FakeProductionRepository:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    async def add(self, production: Production) -> None:
        self.store.productions[production.production_id] = production

    async def get_by_id(self, production_id: UUID) -> Production | None:
        return self.store.productions.get(production_id)

    async def list_project_productions(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[Production]:
        values = [item for item in self.store.productions.values() if item.project_id == project_id]
        return values[offset : offset + limit]

    async def update(self, production: Production, *, expected_version: int) -> None:
        current = self.store.productions.get(production.production_id)
        if current is None or current.version != expected_version:
            raise ConcurrencyConflict("stale production version")
        self.store.productions[production.production_id] = production

    async def archive(self, production_id: UUID, *, expected_version: int) -> None:
        production = self.store.productions[production_id]
        await self.update(production.archive(), expected_version=expected_version)

    async def get_version(self, production_id: UUID) -> int | None:
        production = self.store.productions.get(production_id)
        return production.version if production else None


class FakeSpeciesRepository:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    async def get_by_id(self, species_id: UUID) -> Species | None:
        return self.store.species.get(species_id)

    async def get_by_key(self, key: str) -> Species | None:
        return next((item for item in self.store.species.values() if item.key == key), None)

    async def list_enabled(self) -> list[Species]:
        return [item for item in self.store.species.values() if item.enabled]

    async def upsert_seed_data(self, species: tuple[Species, ...]) -> None:
        self.store.species.update({item.species_id: item for item in species})


class FakeAssetRepository:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    async def get_by_id(self, asset_id: UUID) -> CharacterAssetManifest | None:
        return self.store.assets.get(asset_id)

    async def get_many(self, asset_ids: tuple[UUID, ...]) -> list[CharacterAssetManifest]:
        return [self.store.assets[item] for item in asset_ids if item in self.store.assets]

    async def list_by_species(
        self,
        species_id: UUID,
        *,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[CharacterAssetManifest]:
        values = [
            item
            for item in self.store.assets.values()
            if (not item.species_ids or species_id in item.species_ids)
            and (category is None or item.category == category)
        ]
        return values[offset : offset + limit]

    async def list_by_category(
        self, category: str, *, limit: int, offset: int
    ) -> list[CharacterAssetManifest]:
        values = [item for item in self.store.assets.values() if item.category == category]
        return values[offset : offset + limit]

    async def list_compatible(
        self,
        *,
        species_id: UUID,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[CharacterAssetManifest]:
        return await self.list_by_species(species_id, category=category, limit=limit, offset=offset)

    async def upsert(self, manifest: CharacterAssetManifest) -> None:
        self.store.assets[manifest.asset_id] = manifest

    async def batch_upsert(self, manifests: tuple[CharacterAssetManifest, ...]) -> None:
        for item in manifests:
            await self.upsert(item)


class FakeOutbox:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    async def append(
        self,
        event_type: str,
        version: int,
        payload: dict[str, Any],
        *,
        aggregate_id: UUID | None = None,
        aggregate_sequence: int | None = None,
    ) -> None:
        self.store.outbox.append(
            {
                "event_type": event_type,
                "event_version": version,
                "payload": payload,
                "aggregate_id": aggregate_id,
                "aggregate_sequence": aggregate_sequence,
            }
        )


class FakeTransactionalIdempotency:
    def __init__(self, store: FakeStore, workspace_id: UUID) -> None:
        self.store = store
        self.workspace_id = workspace_id

    async def complete(self, key: str, response: dict[str, Any]) -> None:
        record = self.store.idempotency.get((self.workspace_id, key))
        if record is None or record.get("status") != "processing":
            raise RuntimeError("idempotency record is not processing")
        record.update({"status": "completed", "response": deepcopy(response)})


class FakeAuditQueue:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    async def enqueue(
        self,
        *,
        deduplication_key: str,
        principal: Principal,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None:
        self.store.audit_queue.setdefault(
            (principal.workspace_id, deduplication_key),
            {
                "principal": principal,
                "action": action,
                "outcome": outcome,
                "resource_id": resource_id,
                "details": deepcopy(details),
                "status": "pending",
            },
        )


class FakeUnitOfWork:
    def __init__(self, store: FakeStore, principal: Principal) -> None:
        self._target = store
        self._principal = principal
        self._working = deepcopy(store)
        self.projects = FakeProjectRepository(self._working)
        self.productions = FakeProductionRepository(self._working)
        self.characters = FakeCharacterRepository(self._working)
        self.species = FakeSpeciesRepository(self._working)
        self.character_assets = FakeAssetRepository(self._working)
        self.outbox = FakeOutbox(self._working)
        self.idempotency = FakeTransactionalIdempotency(self._working, principal.workspace_id)
        self.audit_queue = FakeAuditQueue(self._working)
        self.identities: Any = None
        self.assertions: Any = None
        self.decisions: Any = None
        self.policies: Any = None
        self.registry: Any = None
        self.committed = False

    async def __aenter__(self) -> Self:
        return self

    async def commit(self) -> None:
        self._target.projects = self._working.projects
        self._target.productions = self._working.productions
        self._target.project_roles = self._working.project_roles
        self._target.characters = self._working.characters
        self._target.species = self._working.species
        self._target.assets = self._working.assets
        self._target.outbox = self._working.outbox
        self._target.idempotency = self._working.idempotency
        self._target.audit_queue = self._working.audit_queue
        self.committed = True

    async def rollback(self) -> None:
        self.committed = False

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if exc is not None:
            await self.rollback()


class FakeUnitOfWorkFactory:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    def __call__(self, principal: Principal) -> UnitOfWork:
        return cast(UnitOfWork, FakeUnitOfWork(self.store, principal))


class FakeIdempotency:
    def __init__(self, store: FakeStore) -> None:
        self.store = store

    @property
    def records(self) -> dict[tuple[UUID, str], dict[str, Any]]:
        return self.store.idempotency

    async def acquire(self, workspace_id: UUID, key: str, request_hash: str) -> IdempotencyClaim:
        record = self.records.get((workspace_id, key))
        if record and record.get("request_hash") != request_hash:
            raise IdempotencyConflict("Idempotency key was already used for a different request.")
        if record and record.get("status") == "completed":
            return IdempotencyClaim("completed", record["response"])
        self.records[(workspace_id, key)] = {
            "request_hash": request_hash,
            "status": "processing",
        }
        return IdempotencyClaim("acquired")

    async def complete(self, workspace_id: UUID, key: str, response: dict[str, Any]) -> None:
        self.records[(workspace_id, key)].update(
            {"status": "completed", "response": deepcopy(response)}
        )

    async def fail(self, workspace_id: UUID, key: str, error_code: str) -> None:
        self.records[(workspace_id, key)].update({"status": "failed", "error_code": error_code})


class FakeAudit:
    def __init__(self, store: FakeStore) -> None:
        self.store = store
        self.records: list[dict[str, Any]] = []

    async def record_independent(
        self,
        *,
        principal: Principal | None,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
        deduplication_key: str | None = None,
    ) -> None:
        if deduplication_key and any(
            item.get("deduplication_key") == deduplication_key for item in self.records
        ):
            return
        self.records.append(
            {
                "principal": principal,
                "action": action,
                "outcome": outcome,
                "resource_id": resource_id,
                "details": details,
                "deduplication_key": deduplication_key,
            }
        )

    async def deliver(self, workspace_id: UUID, deduplication_key: str) -> bool:
        queued = self.store.audit_queue.get((workspace_id, deduplication_key))
        if queued is None or queued["status"] != "pending":
            return False
        await self.record_independent(
            principal=queued["principal"],
            action=queued["action"],
            outcome=queued["outcome"],
            resource_id=queued["resource_id"],
            details=queued["details"],
            deduplication_key=deduplication_key,
        )
        queued["status"] = "delivered"
        return True

    async def record_or_queue(
        self,
        *,
        deduplication_key: str,
        principal: Principal,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, Any],
    ) -> None:
        await FakeAuditQueue(self.store).enqueue(
            deduplication_key=deduplication_key,
            principal=principal,
            action=action,
            outcome=outcome,
            resource_id=resource_id,
            details=details,
        )
        await self.deliver(principal.workspace_id, deduplication_key)
