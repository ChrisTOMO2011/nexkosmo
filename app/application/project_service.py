from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.application.ports import (
    AuditDeliveryPort,
    IdempotencyPort,
    UnitOfWork,
    UnitOfWorkFactory,
)
from app.domain.errors import AuthorizationDenied, ConcurrencyConflict, NotFound
from app.domain.projects import (
    Production,
    ProductionStatus,
    ProductionType,
    Project,
    ProjectMemberRole,
)
from app.domain.types import Principal

READ_ROLES = frozenset({"Owner", "Admin", "Editor", "Viewer"})
EDIT_ROLES = frozenset({"Owner", "Admin", "Editor"})
ADMIN_ROLES = frozenset({"Owner", "Admin"})


@dataclass(frozen=True, slots=True)
class ProjectMutationResult:
    project: Project
    change_summary: dict[str, Any]
    replayed_response: dict[str, Any] | None = None


@dataclass(frozen=True, slots=True)
class ProductionMutationResult:
    production: Production
    change_summary: dict[str, Any]
    replayed_response: dict[str, Any] | None = None


async def require_project_role(
    uow: UnitOfWork,
    principal: Principal,
    project_id: UUID,
    allowed_roles: frozenset[str],
) -> Project:
    project = await uow.projects.get_by_id(project_id)
    if project is None:
        raise NotFound("Project does not exist.")
    role = await uow.projects.get_member_role(project_id, principal.principal_id)
    if role not in allowed_roles:
        raise AuthorizationDenied("Principal is not authorised for this project operation.")
    return project


class ProjectProductionApplicationService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        audit: AuditDeliveryPort,
        idempotency: IdempotencyPort,
    ) -> None:
        self._uow_factory = uow_factory
        self._audit = audit
        self._idempotency = idempotency

    async def create_project(
        self,
        principal: Principal,
        *,
        name: str,
        description: str,
        idempotency_key: str,
    ) -> ProjectMutationResult:
        request_hash = self._hash(
            {
                "operation": "project.create",
                "name": name,
                "description": description,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            project = await self.get_project(
                principal, UUID(claim.response["project"]["project_id"])
            )
            return ProjectMutationResult(project, {}, claim.response)
        project = Project.create(
            workspace_id=principal.workspace_id,
            name=name,
            description=description,
            owner_id=principal.principal_id,
        )
        try:
            async with self._uow_factory(principal) as uow:
                await uow.projects.add(project)
                await self._append_project_event(
                    uow, project, "project.created", previous_version=0
                )
                response = self._project_response(project, {})
                await self._complete_and_queue_audit(
                    uow,
                    principal,
                    idempotency_key=idempotency_key,
                    response=response,
                    action="project.created",
                    resource_id=project.project_id,
                    details={"version": project.version},
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action="project.created")
            return ProjectMutationResult(project, {})
        except Exception as exc:
            await self._failure(
                principal, idempotency_key, "project.created", project.project_id, exc
            )
            raise

    async def get_project(self, principal: Principal, project_id: UUID) -> Project:
        async with self._uow_factory(principal) as uow:
            return await require_project_role(uow, principal, project_id, READ_ROLES)

    async def list_workspace_projects(
        self, principal: Principal, *, limit: int, offset: int
    ) -> list[Project]:
        async with self._uow_factory(principal) as uow:
            projects = await uow.projects.list_workspace_projects(limit=limit, offset=offset)
            return [
                project
                for project in projects
                if await uow.projects.get_member_role(project.project_id, principal.principal_id)
                in READ_ROLES
            ]

    async def update_project(
        self,
        principal: Principal,
        project_id: UUID,
        *,
        expected_version: int,
        name: str | None,
        description: str | None,
        status: str | None,
        idempotency_key: str,
    ) -> ProjectMutationResult:
        action = "project.archived" if status == "archived" else "project.updated"
        request = {
            "name": name,
            "description": description,
            "status": status,
        }
        request_hash = self._hash(
            {
                "operation": action,
                "project_id": str(project_id),
                "expected_version": expected_version,
                **request,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            project = await self.get_project(principal, project_id)
            return ProjectMutationResult(
                project,
                claim.response.get("change_summary", {}),
                claim.response,
            )
        try:
            async with self._uow_factory(principal) as uow:
                current = await require_project_role(uow, principal, project_id, ADMIN_ROLES)
                self._require_version("project", current.version, expected_version)
                updated = current.update(
                    name=name,
                    description=description,
                    status=status,  # type: ignore[arg-type]
                )
                summary = {
                    key: value
                    for key, value in {
                        "name": (
                            {"from": current.name, "to": updated.name}
                            if current.name != updated.name
                            else None
                        ),
                        "description": (
                            {
                                "from": current.description,
                                "to": updated.description,
                            }
                            if current.description != updated.description
                            else None
                        ),
                        "status": (
                            {"from": current.status, "to": updated.status}
                            if current.status != updated.status
                            else None
                        ),
                    }.items()
                    if value is not None
                }
                await uow.projects.update(updated, expected_version=expected_version)
                await self._append_project_event(
                    uow,
                    updated,
                    action,
                    previous_version=current.version,
                    summary=summary,
                )
                response = self._project_response(updated, summary)
                await self._complete_and_queue_audit(
                    uow,
                    principal,
                    idempotency_key=idempotency_key,
                    response=response,
                    action=action,
                    resource_id=updated.project_id,
                    details=summary,
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action=action)
            return ProjectMutationResult(updated, summary)
        except Exception as exc:
            await self._failure(principal, idempotency_key, action, project_id, exc)
            raise

    async def set_project_member_role(
        self,
        principal: Principal,
        project_id: UUID,
        member_id: UUID,
        *,
        role: ProjectMemberRole,
        expected_version: int,
        idempotency_key: str,
    ) -> ProjectMutationResult:
        if role == "Owner":
            raise AuthorizationDenied(
                "Project ownership changes require the dedicated owner operation."
            )
        request_hash = self._hash(
            {
                "operation": "project.member.updated",
                "project_id": str(project_id),
                "member_id": str(member_id),
                "role": role,
                "expected_version": expected_version,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            project = await self.get_project(principal, project_id)
            return ProjectMutationResult(project, {}, claim.response)
        try:
            async with self._uow_factory(principal) as uow:
                current = await require_project_role(uow, principal, project_id, ADMIN_ROLES)
                self._require_version("project", current.version, expected_version)
                updated = current.add_member(member_id)
                if updated is current:
                    updated = current.record_membership_change()
                await uow.projects.update(updated, expected_version=expected_version)
                await uow.projects.set_member_role(project_id, member_id, role)
                summary = {
                    "member_id": str(member_id),
                    "role": role,
                }
                await self._append_project_event(
                    uow,
                    updated,
                    "project.updated",
                    previous_version=current.version,
                    summary=summary,
                )
                response = self._project_response(updated, summary)
                await self._complete_and_queue_audit(
                    uow,
                    principal,
                    idempotency_key=idempotency_key,
                    response=response,
                    action="project.member.updated",
                    resource_id=project_id,
                    details=summary,
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action="project.member.updated")
            return ProjectMutationResult(updated, summary)
        except Exception as exc:
            await self._failure(
                principal,
                idempotency_key,
                "project.member.updated",
                project_id,
                exc,
            )
            raise

    async def remove_project_member(
        self,
        principal: Principal,
        project_id: UUID,
        member_id: UUID,
        *,
        expected_version: int,
        idempotency_key: str,
    ) -> ProjectMutationResult:
        request_hash = self._hash(
            {
                "operation": "project.member.removed",
                "project_id": str(project_id),
                "member_id": str(member_id),
                "expected_version": expected_version,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            project = await self.get_project(principal, project_id)
            return ProjectMutationResult(project, {}, claim.response)
        try:
            async with self._uow_factory(principal) as uow:
                current = await require_project_role(uow, principal, project_id, ADMIN_ROLES)
                self._require_version("project", current.version, expected_version)
                updated = current.remove_member(member_id)
                if updated is current:
                    updated = current.record_membership_change()
                await uow.projects.update(updated, expected_version=expected_version)
                summary = {"removed_member_id": str(member_id)}
                await self._append_project_event(
                    uow,
                    updated,
                    "project.updated",
                    previous_version=current.version,
                    summary=summary,
                )
                response = self._project_response(updated, summary)
                await self._complete_and_queue_audit(
                    uow,
                    principal,
                    idempotency_key=idempotency_key,
                    response=response,
                    action="project.member.removed",
                    resource_id=project_id,
                    details=summary,
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action="project.member.removed")
            return ProjectMutationResult(updated, summary)
        except Exception as exc:
            await self._failure(
                principal,
                idempotency_key,
                "project.member.removed",
                project_id,
                exc,
            )
            raise

    async def create_production(
        self,
        principal: Principal,
        project_id: UUID,
        *,
        name: str,
        production_type: ProductionType,
        idempotency_key: str,
    ) -> ProductionMutationResult:
        request_hash = self._hash(
            {
                "operation": "production.create",
                "project_id": str(project_id),
                "name": name,
                "production_type": production_type,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            cached_production = await self.get_production(
                principal,
                UUID(claim.response["production"]["production_id"]),
            )
            return ProductionMutationResult(cached_production, {}, claim.response)
        production: Production | None = None
        try:
            async with self._uow_factory(principal) as uow:
                await require_project_role(uow, principal, project_id, EDIT_ROLES)
                production = Production.create(
                    project_id=project_id,
                    workspace_id=principal.workspace_id,
                    name=name,
                    production_type=production_type,
                    owner_id=principal.principal_id,
                )
                await uow.productions.add(production)
                await self._append_production_event(
                    uow,
                    production,
                    "production.created",
                    previous_version=0,
                )
                response = self._production_response(production, {})
                await self._complete_and_queue_audit(
                    uow,
                    principal,
                    idempotency_key=idempotency_key,
                    response=response,
                    action="production.created",
                    resource_id=production.production_id,
                    details={"project_id": str(project_id)},
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action="production.created")
            return ProductionMutationResult(production, {})
        except Exception as exc:
            await self._failure(
                principal,
                idempotency_key,
                "production.created",
                production.production_id if production else None,
                exc,
            )
            raise

    async def get_production(self, principal: Principal, production_id: UUID) -> Production:
        async with self._uow_factory(principal) as uow:
            production = await uow.productions.get_by_id(production_id)
            if production is None:
                raise NotFound("Production does not exist.")
            await require_project_role(uow, principal, production.project_id, READ_ROLES)
            return production

    async def list_project_productions(
        self,
        principal: Principal,
        project_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> list[Production]:
        async with self._uow_factory(principal) as uow:
            await require_project_role(uow, principal, project_id, READ_ROLES)
            return await uow.productions.list_project_productions(
                project_id, limit=limit, offset=offset
            )

    async def update_production(
        self,
        principal: Principal,
        production_id: UUID,
        *,
        expected_version: int,
        name: str | None,
        status: ProductionStatus | None,
        idempotency_key: str,
    ) -> ProductionMutationResult:
        action = "production.archived" if status == "archived" else "production.updated"
        request_hash = self._hash(
            {
                "operation": action,
                "production_id": str(production_id),
                "expected_version": expected_version,
                "name": name,
                "status": status,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            production = await self.get_production(principal, production_id)
            return ProductionMutationResult(
                production,
                claim.response.get("change_summary", {}),
                claim.response,
            )
        try:
            async with self._uow_factory(principal) as uow:
                current = await uow.productions.get_by_id(production_id)
                if current is None:
                    raise NotFound("Production does not exist.")
                await require_project_role(uow, principal, current.project_id, EDIT_ROLES)
                self._require_version("production", current.version, expected_version)
                updated = current.update(name=name, status=status)
                summary = {
                    key: value
                    for key, value in {
                        "name": (
                            {"from": current.name, "to": updated.name}
                            if current.name != updated.name
                            else None
                        ),
                        "status": (
                            {"from": current.status, "to": updated.status}
                            if current.status != updated.status
                            else None
                        ),
                    }.items()
                    if value is not None
                }
                await uow.productions.update(updated, expected_version=expected_version)
                await self._append_production_event(
                    uow,
                    updated,
                    action,
                    previous_version=current.version,
                    summary=summary,
                )
                response = self._production_response(updated, summary)
                await self._complete_and_queue_audit(
                    uow,
                    principal,
                    idempotency_key=idempotency_key,
                    response=response,
                    action=action,
                    resource_id=updated.production_id,
                    details=summary,
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action=action)
            return ProductionMutationResult(updated, summary)
        except Exception as exc:
            await self._failure(principal, idempotency_key, action, production_id, exc)
            raise

    @staticmethod
    def _require_version(resource: str, current_version: int, expected_version: int) -> None:
        if current_version != expected_version:
            raise ConcurrencyConflict(
                f"Expected {resource} version {expected_version}, found {current_version}."
            )

    async def _append_project_event(
        self,
        uow: UnitOfWork,
        project: Project,
        event_type: str,
        *,
        previous_version: int,
        summary: dict[str, Any] | None = None,
    ) -> None:
        await uow.outbox.append(
            event_type,
            1,
            {
                "project_id": str(project.project_id),
                "workspace_id": str(project.workspace_id),
                "previous_version": previous_version,
                "version": project.version,
                "change_summary": summary or {},
            },
            aggregate_id=project.project_id,
            aggregate_sequence=project.version,
        )

    async def _append_production_event(
        self,
        uow: UnitOfWork,
        production: Production,
        event_type: str,
        *,
        previous_version: int,
        summary: dict[str, Any] | None = None,
    ) -> None:
        await uow.outbox.append(
            event_type,
            1,
            {
                "production_id": str(production.production_id),
                "project_id": str(production.project_id),
                "workspace_id": str(production.workspace_id),
                "previous_version": previous_version,
                "version": production.version,
                "change_summary": summary or {},
            },
            aggregate_id=production.production_id,
            aggregate_sequence=production.version,
        )

    @staticmethod
    def _audit_key(action: str, idempotency_key: str, outcome: str) -> str:
        return f"{action}:{idempotency_key}:{outcome}"

    async def _complete_and_queue_audit(
        self,
        uow: UnitOfWork,
        principal: Principal,
        *,
        idempotency_key: str,
        response: dict[str, Any],
        action: str,
        resource_id: UUID,
        details: dict[str, Any],
    ) -> None:
        await uow.idempotency.complete(idempotency_key, response)
        await uow.audit_queue.enqueue(
            deduplication_key=self._audit_key(action, idempotency_key, "success"),
            principal=principal,
            action=action,
            outcome="success",
            resource_id=resource_id,
            details=details,
        )

    async def _deliver_audit(
        self, principal: Principal, idempotency_key: str, *, action: str
    ) -> None:
        try:
            await self._audit.deliver(
                principal.workspace_id,
                self._audit_key(action, idempotency_key, "success"),
            )
        except Exception:
            return

    async def _failure(
        self,
        principal: Principal,
        idempotency_key: str,
        action: str,
        resource_id: UUID | None,
        exc: Exception,
    ) -> None:
        error_code = getattr(exc, "code", type(exc).__name__)
        try:
            await self._idempotency.fail(
                principal.workspace_id,
                idempotency_key,
                error_code,
            )
        finally:
            await self._audit.record_or_queue(
                deduplication_key=self._audit_key(action, idempotency_key, "failure"),
                principal=principal,
                action=action,
                outcome="failure",
                resource_id=resource_id,
                details={"error_code": error_code, "message": str(exc)},
            )

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        value = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(value).hexdigest()

    @staticmethod
    def _project_response(project: Project, summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "project": {
                "project_id": str(project.project_id),
                "workspace_id": str(project.workspace_id),
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "owner_id": str(project.owner_id),
                "member_ids": [str(item) for item in project.member_ids],
                "created_at": project.created_at.isoformat(),
                "updated_at": project.updated_at.isoformat(),
                "version": project.version,
            },
            "change_summary": summary,
        }

    @staticmethod
    def _production_response(production: Production, summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "production": {
                "production_id": str(production.production_id),
                "project_id": str(production.project_id),
                "workspace_id": str(production.workspace_id),
                "name": production.name,
                "production_type": production.production_type,
                "status": production.status,
                "owner_id": str(production.owner_id),
                "created_at": production.created_at.isoformat(),
                "updated_at": production.updated_at.isoformat(),
                "version": production.version,
            },
            "change_summary": summary,
        }
