import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid5

from app.application.ports import (
    AuditDeliveryPort,
    TransactionalIdempotencyPort,
    UnitOfWork,
    UnitOfWorkFactory,
)
from app.domain.characters import Character
from app.domain.enums import AgentKind, IdentityKind
from app.domain.errors import AuthorizationDenied, ResourceNotFound
from app.domain.projects import Project, ProjectLifecycle, require_project_mutation_role
from app.domain.types import Activity, Identity, Principal


class CharacterService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        idempotency: TransactionalIdempotencyPort,
        audit_delivery: AuditDeliveryPort,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._uow_factory = uow_factory
        self._idempotency = idempotency
        self._audit_delivery = audit_delivery
        self._clock = clock or (lambda: datetime.now(UTC))

    async def list_characters(
        self,
        principal: Principal,
        *,
        project_id: UUID,
    ) -> list[dict[str, Any]]:
        self._require_human_actor(principal, "character:read")
        now = self._clock()
        async with self._uow_factory(principal) as uow:
            await self._require_current_workspace_actor(uow, principal, now, lock=False)
            project = await self._require_project(uow, project_id, lock=False)
            await uow.project_memberships.require_role(
                project_id=project.id,
                principal_id=principal.principal_id,
                at=now,
            )
            characters = await uow.characters.list_for_project(project.id)
            return [_character_response(character) for character in characters]

    async def get_character(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        character_id: UUID,
    ) -> dict[str, Any]:
        self._require_human_actor(principal, "character:read")
        now = self._clock()
        async with self._uow_factory(principal) as uow:
            await self._require_current_workspace_actor(uow, principal, now, lock=False)
            project = await self._require_project(uow, project_id, lock=False)
            await uow.project_memberships.require_role(
                project_id=project.id,
                principal_id=principal.principal_id,
                at=now,
            )
            character = await self._require_character(
                uow, project_id=project.id, character_id=character_id, lock=False
            )
            return _character_response(character)

    async def create_character(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        display_name: str,
        role_label: str | None,
        idempotency_key: str,
    ) -> dict[str, Any]:
        self._require_human_actor(principal, "character:create")
        request_hash = self._hash(
            {
                "operation": "character.create",
                "project_id": str(project_id),
                "display_name": display_name.strip(),
                "role_label": _normalized_request_role_label(role_label),
            }
        )
        claim = await self._idempotency.claim(
            principal=principal,
            key=idempotency_key,
            request_hash=request_hash,
        )
        if claim.is_replay:
            return claim.response or {}
        owner_token = _require_owner_token(claim.owner_token)
        now = self._clock()
        character_id = uuid5(project_id, f"character:{idempotency_key}")
        activity_id = uuid5(character_id, "character-created-activity")
        async with self._uow_factory(principal) as uow:
            await self._require_lease(
                uow, principal, idempotency_key, request_hash, owner_token
            )
            await self._require_current_workspace_actor(uow, principal, now, lock=True)
            project = await self._require_project(uow, project_id, lock=False)
            await self._require_project_mutation_authority(
                uow, principal, project, now
            )
            character = Character.create(
                character_id=character_id,
                workspace_id=principal.workspace_id,
                project_id=project.id,
                created_by_principal_id=principal.principal_id,
                display_name=display_name,
                role_label=role_label,
                now=now,
            )
            await uow.semantic_projects.add_identity(
                Identity(
                    id=character.id,
                    workspace_id=character.workspace_id,
                    kind=IdentityKind.CHARACTER,
                    canonical_key=f"character:{character.id}",
                    created_at=now,
                )
            )
            await uow.characters.add(character)
            await self._append_character_activity(
                uow=uow,
                principal=principal,
                project=project,
                character=character,
                activity_id=activity_id,
                activity_type="character.created",
                now=now,
            )
            response = _character_response(character)
            await self._append_transactional_records(
                uow=uow,
                principal=principal,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                owner_token=owner_token,
                response=response,
                character=character,
                event_type="character.created",
                action="character.create",
                details={
                    "project_id": str(project.id),
                    "display_name": character.display_name,
                },
            )
            await uow.commit()
        await self._deliver_without_rolling_back(principal)
        return response

    async def update_character(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        character_id: UUID,
        expected_version: int,
        display_name: str | None,
        role_label: str | None,
        replace_role_label: bool,
        idempotency_key: str,
    ) -> dict[str, Any]:
        self._require_human_actor(principal, "character:update")
        request_hash = self._hash(
            {
                "operation": "character.update",
                "project_id": str(project_id),
                "character_id": str(character_id),
                "expected_version": expected_version,
                "display_name": None if display_name is None else display_name.strip(),
                "replace_role_label": replace_role_label,
                "role_label": (
                    _normalized_request_role_label(role_label)
                    if replace_role_label
                    else None
                ),
            }
        )
        claim = await self._idempotency.claim(
            principal=principal,
            key=idempotency_key,
            request_hash=request_hash,
        )
        if claim.is_replay:
            return claim.response or {}
        owner_token = _require_owner_token(claim.owner_token)
        now = self._clock()
        activity_id = uuid5(character_id, f"character-updated:{idempotency_key}")
        async with self._uow_factory(principal) as uow:
            await self._require_lease(
                uow, principal, idempotency_key, request_hash, owner_token
            )
            await self._require_current_workspace_actor(uow, principal, now, lock=True)
            project = await self._require_project(uow, project_id, lock=False)
            await self._require_project_mutation_authority(
                uow, principal, project, now
            )
            character = await self._require_character(
                uow, project_id=project.id, character_id=character_id, lock=True
            )
            updated = character.update_metadata(
                expected_version=expected_version,
                now=now,
                display_name=display_name,
                role_label=role_label,
                replace_role_label=replace_role_label,
            )
            await uow.characters.update(updated, expected_version=expected_version)
            await self._append_character_activity(
                uow=uow,
                principal=principal,
                project=project,
                character=updated,
                activity_id=activity_id,
                activity_type="character.metadata_updated",
                now=now,
            )
            response = _character_response(updated)
            await self._append_transactional_records(
                uow=uow,
                principal=principal,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                owner_token=owner_token,
                response=response,
                character=updated,
                event_type="character.metadata_updated",
                action="character.update",
                details={
                    "project_id": str(project.id),
                    "version": updated.version,
                },
            )
            await uow.commit()
        await self._deliver_without_rolling_back(principal)
        return response

    async def _require_project_mutation_authority(
        self,
        uow: UnitOfWork,
        principal: Principal,
        project: Project,
        at: datetime,
    ) -> None:
        await uow.projects.require_unlocked(project.id)
        if project.lifecycle is ProjectLifecycle.ARCHIVED:
            raise AuthorizationDenied("Archived Projects are read-only.")
        role = await uow.project_memberships.require_role(
            project_id=project.id,
            principal_id=principal.principal_id,
            at=at,
            lock=False,
        )
        require_project_mutation_role(role)

    @staticmethod
    async def _append_character_activity(
        *,
        uow: UnitOfWork,
        principal: Principal,
        project: Project,
        character: Character,
        activity_id: UUID,
        activity_type: str,
        now: datetime,
    ) -> None:
        await uow.semantic_projects.add_activity(
            Activity(
                id=activity_id,
                workspace_id=principal.workspace_id,
                activity_type=activity_type,
                performed_by=principal.agent_id,
                context_id=project.context_id,
                started_at=now,
                ended_at=now,
                outputs=(character.identity_id,),
                attributes={
                    "authority_principal_id": str(principal.principal_id),
                    "project_id": str(project.id),
                    "character_version": character.version,
                },
            )
        )
        await uow.semantic_projects.add_activity_output(
            workspace_id=principal.workspace_id,
            activity_id=activity_id,
            identity_id=character.identity_id,
        )

    @staticmethod
    async def _append_transactional_records(
        *,
        uow: UnitOfWork,
        principal: Principal,
        idempotency_key: str,
        request_hash: str,
        owner_token: UUID,
        response: dict[str, Any],
        character: Character,
        event_type: str,
        action: str,
        details: dict[str, Any],
    ) -> None:
        await uow.transactional_idempotency.complete(
            workspace_id=principal.workspace_id,
            key=idempotency_key,
            request_hash=request_hash,
            owner_token=owner_token,
            response=response,
        )
        await uow.outbox.append(
            event_type,
            1,
            response,
            aggregate_id=character.id,
            aggregate_sequence=character.version,
        )
        await uow.audit_delivery_queue.append(
            workspace_id=principal.workspace_id,
            deduplication_key=f"{idempotency_key}:{action}:success",
            principal_id=principal.principal_id,
            agent_id=principal.agent_id,
            action=action,
            outcome="success",
            resource_id=character.id,
            details=details,
        )

    @staticmethod
    async def _require_lease(
        uow: UnitOfWork,
        principal: Principal,
        key: str,
        request_hash: str,
        owner_token: UUID,
    ) -> None:
        await uow.transactional_idempotency.require_lease(
            workspace_id=principal.workspace_id,
            key=key,
            request_hash=request_hash,
            owner_token=owner_token,
        )

    @staticmethod
    async def _require_current_workspace_actor(
        uow: UnitOfWork,
        principal: Principal,
        at: datetime,
        *,
        lock: bool,
    ) -> None:
        await uow.workspace_authority.require_current_human_role(
            workspace_id=principal.workspace_id,
            principal_id=principal.principal_id,
            agent_id=principal.agent_id,
            at=at,
            lock=lock,
        )

    @staticmethod
    async def _require_project(
        uow: UnitOfWork, project_id: UUID, *, lock: bool
    ) -> Project:
        project = await uow.projects.get(project_id, lock=lock)
        if project is None:
            raise ResourceNotFound("Project was not found or is not visible.")
        return project

    @staticmethod
    async def _require_character(
        uow: UnitOfWork,
        *,
        project_id: UUID,
        character_id: UUID,
        lock: bool,
    ) -> Character:
        character = await uow.characters.get(character_id, lock=lock)
        if character is None or character.project_id != project_id:
            raise ResourceNotFound("Character was not found in the requested Project.")
        return character

    @staticmethod
    def _require_human_actor(principal: Principal, action: str) -> None:
        if principal.agent_kind is not AgentKind.HUMAN:
            raise AuthorizationDenied("Character authority requires a human acting agent.")
        if (
            principal.delegated_actions
            and action not in principal.delegated_actions
            and "*" not in principal.delegated_actions
        ):
            raise AuthorizationDenied("Delegated token scope reduces this authority.")

    async def _deliver_without_rolling_back(self, principal: Principal) -> None:
        try:
            await self._audit_delivery.deliver_pending(principal=principal)
        except Exception:
            return

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


def _require_owner_token(owner_token: UUID | None) -> UUID:
    if owner_token is None:
        raise RuntimeError("A non-replay idempotency claim requires an owner token.")
    return owner_token


def _normalized_request_role_label(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _character_response(character: Character) -> dict[str, Any]:
    return {
        "character_id": str(character.id),
        "workspace_id": str(character.workspace_id),
        "project_id": str(character.project_id),
        "identity_id": str(character.identity_id),
        "created_by_principal_id": str(character.created_by_principal_id),
        "display_name": character.display_name,
        "role_label": character.role_label,
        "version": character.version,
        "created_at": character.created_at.isoformat(),
        "updated_at": character.updated_at.isoformat(),
    }
