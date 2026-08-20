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
from app.domain.enums import AgentKind, ContextKind, IdentityKind
from app.domain.errors import AuthorizationDenied, ResourceNotFound
from app.domain.projects import (
    Production,
    ProductionState,
    Project,
    ProjectLifecycle,
    ProjectMembership,
    ProjectRole,
    require_project_mutation_role,
)
from app.domain.types import Activity, Context, Identity, Principal
from app.domain.workspaces import (
    require_project_create_authority,
    require_project_role_compatible,
)


class ProjectService:
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

    async def get_project(
        self,
        principal: Principal,
        *,
        project_id: UUID,
    ) -> dict[str, Any]:
        self._require_human_actor(principal, "project:read")
        now = self._clock()
        async with self._uow_factory(principal) as uow:
            await self._require_current_workspace_actor(uow, principal, now)
            project = await self._require_project(uow, project_id, lock=False)
            await uow.project_memberships.require_role(
                project_id=project_id,
                principal_id=principal.principal_id,
                at=now,
            )
            return _project_response(project)

    async def create_project(
        self,
        principal: Principal,
        *,
        name: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        self._require_human_actor(principal, "project:create")
        request_hash = self._hash({"operation": "project.create", "name": name.strip()})
        claim = await self._idempotency.claim(
            principal=principal,
            key=idempotency_key,
            request_hash=request_hash,
        )
        if claim.is_replay:
            return claim.response or {}
        owner_token = _require_owner_token(claim.owner_token)
        now = self._clock()
        project_id = uuid5(principal.workspace_id, f"project:{idempotency_key}")
        context_id = uuid5(project_id, "project-context")
        activity_id = uuid5(project_id, "project-created-activity")
        project = Project.create(
            project_id=project_id,
            workspace_id=principal.workspace_id,
            context_id=context_id,
            owner_principal_id=principal.principal_id,
            name=name,
            now=now,
        )
        response = _project_response(project)
        async with self._uow_factory(principal) as uow:
            await self._require_lease(
                uow, principal, idempotency_key, request_hash, owner_token
            )
            workspace_role = await uow.workspace_authority.require_current_human_role(
                workspace_id=principal.workspace_id,
                principal_id=principal.principal_id,
                agent_id=principal.agent_id,
                at=now,
                lock=True,
            )
            require_project_create_authority(workspace_role)
            await uow.semantic_projects.add_identity(
                Identity(
                    id=project_id,
                    workspace_id=principal.workspace_id,
                    kind=IdentityKind.PROJECT,
                    canonical_key=f"project:{project_id}",
                    created_at=now,
                )
            )
            await uow.semantic_projects.add_identity(
                Identity(
                    id=context_id,
                    workspace_id=principal.workspace_id,
                    kind=IdentityKind.CONTEXT,
                    canonical_key=f"project-context:{project_id}",
                    created_at=now,
                )
            )
            await uow.semantic_projects.add_context(
                Context(
                    identity_id=context_id,
                    workspace_id=principal.workspace_id,
                    kind=ContextKind.PROJECT,
                    parent_context_id=None,
                )
            )
            await uow.projects.add(project)
            await uow.project_memberships.add(
                ProjectMembership(
                    id=uuid5(project_id, f"owner:{principal.principal_id}"),
                    workspace_id=principal.workspace_id,
                    project_id=project_id,
                    principal_id=principal.principal_id,
                    role=ProjectRole.OWNER,
                    valid_from=now,
                    valid_to=None,
                    granted_by_agent_id=principal.agent_id,
                )
            )
            await uow.semantic_projects.add_activity(
                Activity(
                    id=activity_id,
                    workspace_id=principal.workspace_id,
                    activity_type="project.created",
                    performed_by=principal.agent_id,
                    context_id=context_id,
                    started_at=now,
                    ended_at=now,
                    outputs=(project_id,),
                    attributes={"authority_principal_id": str(principal.principal_id)},
                )
            )
            await uow.semantic_projects.add_activity_output(
                workspace_id=principal.workspace_id,
                activity_id=activity_id,
                identity_id=project_id,
            )
            await self._append_transactional_records(
                uow=uow,
                principal=principal,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                owner_token=owner_token,
                response=response,
                aggregate_id=project_id,
                aggregate_sequence=1,
                event_type="project.created",
                action="project.create",
                details={"name": project.name},
            )
            await uow.commit()
        await self._deliver_without_rolling_back(principal)
        return response

    async def transfer_ownership(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        target_principal_id: UUID,
        expected_version: int,
        idempotency_key: str,
    ) -> dict[str, Any]:
        self._require_human_actor(principal, "project:transfer_owner")
        request_hash = self._hash(
            {
                "operation": "project.transfer_owner",
                "project_id": str(project_id),
                "target_principal_id": str(target_principal_id),
                "expected_version": expected_version,
            }
        )
        claim = await self._idempotency.claim(
            principal=principal, key=idempotency_key, request_hash=request_hash
        )
        if claim.is_replay:
            return claim.response or {}
        owner_token = _require_owner_token(claim.owner_token)
        now = self._clock()
        async with self._uow_factory(principal) as uow:
            await self._require_lease(
                uow, principal, idempotency_key, request_hash, owner_token
            )
            await self._require_current_workspace_actor(uow, principal, now)
            project = await self._require_project(uow, project_id, lock=True)
            await uow.projects.require_unlocked(project_id)
            role = await uow.project_memberships.require_role(
                project_id=project_id,
                principal_id=principal.principal_id,
                at=now,
                lock=True,
            )
            if role is not ProjectRole.OWNER:
                raise AuthorizationDenied("Only the current Project Owner may transfer ownership.")
            target_workspace_role = (
                await uow.workspace_authority.require_active_human_principal(
                    workspace_id=principal.workspace_id,
                    principal_id=target_principal_id,
                    at=now,
                    lock=True,
                )
            )
            require_project_role_compatible(target_workspace_role, ProjectRole.OWNER.value)
            await uow.project_memberships.require_role(
                project_id=project_id,
                principal_id=target_principal_id,
                at=now,
                lock=True,
            )
            updated = project.transfer_ownership(
                current_principal_id=principal.principal_id,
                target_principal_id=target_principal_id,
                expected_version=expected_version,
                now=now,
            )
            # Move the aggregate ownership root while the current owner still
            # holds the active Owner membership used by the database guard.
            # The deferred exactly-one-owner constraint permits the membership
            # hand-off to complete later in this same transaction.
            await uow.projects.update(updated, expected_version=expected_version)
            await uow.project_memberships.transfer_owner(
                project_id=project_id,
                current_owner_id=principal.principal_id,
                target_principal_id=target_principal_id,
                acting_agent_id=principal.agent_id,
                at=now,
            )
            response = _project_response(updated)
            await self._append_transactional_records(
                uow=uow,
                principal=principal,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                owner_token=owner_token,
                response=response,
                aggregate_id=project_id,
                aggregate_sequence=updated.version,
                event_type="project.ownership_transferred",
                action="project.transfer_owner",
                details={
                    "previous_owner_principal_id": str(principal.principal_id),
                    "new_owner_principal_id": str(target_principal_id),
                },
            )
            await uow.commit()
        await self._deliver_without_rolling_back(principal)
        return response

    async def set_project_archived(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        archived: bool,
        expected_version: int,
        idempotency_key: str,
    ) -> dict[str, Any]:
        action = "project:restore" if not archived else "project:archive"
        self._require_human_actor(principal, action)
        request_hash = self._hash(
            {
                "operation": action,
                "project_id": str(project_id),
                "expected_version": expected_version,
            }
        )
        claim = await self._idempotency.claim(
            principal=principal, key=idempotency_key, request_hash=request_hash
        )
        if claim.is_replay:
            return claim.response or {}
        owner_token = _require_owner_token(claim.owner_token)
        now = self._clock()
        async with self._uow_factory(principal) as uow:
            await self._require_lease(
                uow, principal, idempotency_key, request_hash, owner_token
            )
            await self._require_current_workspace_actor(uow, principal, now)
            project = await self._require_project(uow, project_id, lock=True)
            await uow.projects.require_unlocked(project_id)
            role = await uow.project_memberships.require_role(
                project_id=project_id,
                principal_id=principal.principal_id,
                at=now,
                lock=True,
            )
            if archived:
                if role is not ProjectRole.OWNER:
                    raise AuthorizationDenied("Only the Project Owner may archive the Project.")
                updated = project.archive(expected_version=expected_version, now=now)
                event_type = "project.archived"
            else:
                updated = project.restore(
                    principal_id=principal.principal_id,
                    expected_version=expected_version,
                    now=now,
                )
                event_type = "project.restored"
            await uow.projects.update(updated, expected_version=expected_version)
            response = _project_response(updated)
            await self._append_transactional_records(
                uow=uow,
                principal=principal,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                owner_token=owner_token,
                response=response,
                aggregate_id=project_id,
                aggregate_sequence=updated.version,
                event_type=event_type,
                action=action.replace(":", "."),
                details={},
            )
            await uow.commit()
        await self._deliver_without_rolling_back(principal)
        return response

    async def create_production(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        name: str,
        idempotency_key: str,
    ) -> dict[str, Any]:
        self._require_human_actor(principal, "production:create")
        request_hash = self._hash(
            {"operation": "production.create", "project_id": str(project_id), "name": name}
        )
        claim = await self._idempotency.claim(
            principal=principal, key=idempotency_key, request_hash=request_hash
        )
        if claim.is_replay:
            return claim.response or {}
        owner_token = _require_owner_token(claim.owner_token)
        now = self._clock()
        production_id = uuid5(project_id, f"production:{idempotency_key}")
        async with self._uow_factory(principal) as uow:
            await self._require_lease(
                uow, principal, idempotency_key, request_hash, owner_token
            )
            await self._require_current_workspace_actor(uow, principal, now)
            project = await self._require_project(uow, project_id, lock=True)
            await uow.projects.require_unlocked(project_id)
            if project.lifecycle is ProjectLifecycle.ARCHIVED:
                raise AuthorizationDenied("Archived Projects are read-only.")
            role = await uow.project_memberships.require_role(
                project_id=project_id, principal_id=principal.principal_id, at=now
            )
            require_project_mutation_role(role)
            production = Production.create(
                production_id=production_id,
                workspace_id=principal.workspace_id,
                project_id=project_id,
                name=name,
                now=now,
            )
            await uow.productions.add(production)
            response = _production_response(production)
            await self._append_transactional_records(
                uow=uow,
                principal=principal,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                owner_token=owner_token,
                response=response,
                aggregate_id=production_id,
                aggregate_sequence=1,
                event_type="production.created",
                action="production.create",
                details={"project_id": str(project_id)},
            )
            await uow.commit()
        await self._deliver_without_rolling_back(principal)
        return response

    async def transition_production(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        production_id: UUID,
        target_state: ProductionState,
        expected_version: int,
        idempotency_key: str,
    ) -> dict[str, Any]:
        self._require_human_actor(principal, "production:transition")
        request_hash = self._hash(
            {
                "operation": "production.transition",
                "project_id": str(project_id),
                "production_id": str(production_id),
                "target_state": target_state.value,
                "expected_version": expected_version,
            }
        )
        claim = await self._idempotency.claim(
            principal=principal, key=idempotency_key, request_hash=request_hash
        )
        if claim.is_replay:
            return claim.response or {}
        owner_token = _require_owner_token(claim.owner_token)
        now = self._clock()
        async with self._uow_factory(principal) as uow:
            await self._require_lease(
                uow, principal, idempotency_key, request_hash, owner_token
            )
            await self._require_current_workspace_actor(uow, principal, now)
            production = await uow.productions.get(production_id, lock=True)
            if production is None:
                raise ResourceNotFound("Production was not found or is not visible.")
            if production.project_id != project_id:
                raise ResourceNotFound("Production was not found in the requested Project.")
            project = await self._require_project(uow, project_id, lock=True)
            await uow.projects.require_unlocked(project.id)
            role = await uow.project_memberships.require_role(
                project_id=project.id, principal_id=principal.principal_id, at=now
            )
            require_project_mutation_role(role)
            updated = production.transition(
                target=target_state,
                expected_version=expected_version,
                project_lifecycle=project.lifecycle,
                now=now,
            )
            await uow.productions.update(updated, expected_version=expected_version)
            response = _production_response(updated)
            await self._append_transactional_records(
                uow=uow,
                principal=principal,
                idempotency_key=idempotency_key,
                request_hash=request_hash,
                owner_token=owner_token,
                response=response,
                aggregate_id=production_id,
                aggregate_sequence=updated.version,
                event_type="production.state_changed",
                action="production.transition",
                details={"state": target_state.value},
            )
            await uow.commit()
        await self._deliver_without_rolling_back(principal)
        return response

    async def _append_transactional_records(
        self,
        *,
        uow: UnitOfWork,
        principal: Principal,
        idempotency_key: str,
        request_hash: str,
        owner_token: UUID,
        response: dict[str, Any],
        aggregate_id: UUID,
        aggregate_sequence: int,
        event_type: str,
        action: str,
        details: dict[str, Any],
    ) -> None:
        await uow.outbox.append(
            event_type,
            1,
            {**response, "workspace_id": str(principal.workspace_id)},
            aggregate_id=aggregate_id,
            aggregate_sequence=aggregate_sequence,
        )
        await uow.audit_delivery_queue.append(
            workspace_id=principal.workspace_id,
            deduplication_key=f"{idempotency_key}:{action}:success",
            principal_id=principal.principal_id,
            agent_id=principal.agent_id,
            action=action,
            outcome="success",
            resource_id=aggregate_id,
            details=details,
        )
        await uow.transactional_idempotency.complete(
            workspace_id=principal.workspace_id,
            key=idempotency_key,
            request_hash=request_hash,
            owner_token=owner_token,
            response=response,
        )

    async def _require_lease(
        self,
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

    async def _require_current_workspace_actor(
        self, uow: UnitOfWork, principal: Principal, at: datetime
    ) -> None:
        await uow.workspace_authority.require_current_human_role(
            workspace_id=principal.workspace_id,
            principal_id=principal.principal_id,
            agent_id=principal.agent_id,
            at=at,
            lock=True,
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
    def _require_human_actor(principal: Principal, action: str) -> None:
        if principal.agent_kind is not AgentKind.HUMAN:
            raise AuthorizationDenied("Project authority requires a human acting agent.")
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
            # The transactional queue is the durable retry source. The independent
            # audit store remains canonical only after successful delivery.
            return

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()


def _require_owner_token(owner_token: UUID | None) -> UUID:
    if owner_token is None:
        raise RuntimeError("A non-replay idempotency claim requires an owner token.")
    return owner_token


def _project_response(project: Project) -> dict[str, Any]:
    return {
        "project_id": str(project.id),
        "workspace_id": str(project.workspace_id),
        "identity_id": str(project.identity_id),
        "context_id": str(project.context_id),
        "owner_principal_id": str(project.owner_principal_id),
        "name": project.name,
        "lifecycle": project.lifecycle.value,
        "version": project.version,
    }


def _production_response(production: Production) -> dict[str, Any]:
    return {
        "production_id": str(production.id),
        "workspace_id": str(production.workspace_id),
        "project_id": str(production.project_id),
        "name": production.name,
        "state": production.state.value,
        "version": production.version,
    }
