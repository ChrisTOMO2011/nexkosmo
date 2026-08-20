import json
from datetime import datetime
from typing import Any, cast
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlalchemy.engine import CursorResult, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.errors import (
    AuthorityRemediationRequired,
    ConcurrencyConflict,
    ResourceNotFound,
)
from app.domain.projects import (
    Production,
    ProductionState,
    Project,
    ProjectLifecycle,
    ProjectMembership,
    ProjectRole,
)


class SqlProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, project: Project) -> None:
        await self._session.execute(
            text(
                """
                insert into projects (
                    id, workspace_id, identity_id, context_id, owner_principal_id,
                    created_by_principal_id, name, lifecycle, version,
                    created_at, updated_at, archived_at
                ) values (
                    :id, :workspace_id, :identity_id, :context_id, :owner_principal_id,
                    :created_by_principal_id, :name, :lifecycle, :version,
                    :created_at, :updated_at, :archived_at
                )
                """
            ),
            _project_params(project),
        )

    async def get(self, project_id: UUID, *, lock: bool = False) -> Project | None:
        statement = (
            text("select * from projects where id = :id for update")
            if lock
            else text("select * from projects where id = :id")
        )
        row = (
            (
                await self._session.execute(
                    statement,
                    {"id": project_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _project_from_row(row)

    async def list_for_principal(
        self, *, principal_id: UUID, at: datetime
    ) -> list[Project]:
        rows = (
            (
                await self._session.execute(
                    text(
                        """
                        select p.*
                        from projects p
                        join project_memberships pm
                          on pm.workspace_id = p.workspace_id
                         and pm.project_id = p.id
                        where pm.principal_id = :principal_id
                          and pm.valid_from <= :at
                          and (pm.valid_to is null or :at < pm.valid_to)
                        order by p.updated_at desc, p.id
                        """
                    ),
                    {"principal_id": principal_id, "at": at},
                )
            )
            .mappings()
            .all()
        )
        return [_project_from_row(row) for row in rows]

    async def require_unlocked(self, project_id: UUID) -> None:
        locked = await self._session.scalar(
            text("select nexkosmo_private.project_authority_locked(:project_id)"),
            {"project_id": project_id},
        )
        if locked:
            raise AuthorityRemediationRequired(
                "Project authority is locked pending trusted remediation."
            )

    async def update(self, project: Project, *, expected_version: int) -> None:
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    """
                    update projects
                    set owner_principal_id = :owner_principal_id,
                        name = :name,
                        lifecycle = :lifecycle,
                        version = :version,
                        updated_at = :updated_at,
                        archived_at = :archived_at
                    where id = :id
                      and workspace_id = :workspace_id
                      and version = :expected_version
                    """
                ),
                {**_project_params(project), "expected_version": expected_version},
            ),
        )
        if result.rowcount != 1:
            raise ConcurrencyConflict("Project changed before this operation could commit.")


class SqlProjectMembershipRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, membership: ProjectMembership) -> None:
        await self._session.execute(
            text(
                """
                insert into project_memberships (
                    id, workspace_id, project_id, principal_id, role,
                    valid_from, valid_to, granted_by_agent_id
                ) values (
                    :id, :workspace_id, :project_id, :principal_id, :role,
                    :valid_from, :valid_to, :granted_by_agent_id
                )
                """
            ),
            {
                "id": membership.id,
                "workspace_id": membership.workspace_id,
                "project_id": membership.project_id,
                "principal_id": membership.principal_id,
                "role": membership.role.value,
                "valid_from": membership.valid_from,
                "valid_to": membership.valid_to,
                "granted_by_agent_id": membership.granted_by_agent_id,
            },
        )

    async def require_role(
        self,
        *,
        project_id: UUID,
        principal_id: UUID,
        at: datetime,
        lock: bool = False,
    ) -> ProjectRole:
        statement = (
            text(
                """
            select role from project_memberships
            where project_id = :project_id
              and principal_id = :principal_id
              and valid_from <= :at
              and (valid_to is null or :at < valid_to)
            for update
            """
            )
            if lock
            else text(
                """
            select role from project_memberships
            where project_id = :project_id
              and principal_id = :principal_id
              and valid_from <= :at
              and (valid_to is null or :at < valid_to)
            """
            )
        )
        role = await self._session.scalar(
            statement,
            {"project_id": project_id, "principal_id": principal_id, "at": at},
        )
        if role is None:
            raise ResourceNotFound("No active Project membership is visible for this principal.")
        return ProjectRole(role)

    async def transfer_owner(
        self,
        *,
        project_id: UUID,
        current_owner_id: UUID,
        target_principal_id: UUID,
        acting_agent_id: UUID,
        at: datetime,
    ) -> None:
        rows = (
            (
                await self._session.execute(
                    text(
                        """
                    select id, workspace_id, principal_id, role, valid_from
                    from project_memberships
                    where project_id = :project_id
                      and principal_id in (:current_owner_id, :target_principal_id)
                      and valid_from <= :at
                      and (valid_to is null or :at < valid_to)
                    order by principal_id
                    for update
                    """
                    ),
                    {
                        "project_id": project_id,
                        "current_owner_id": current_owner_id,
                        "target_principal_id": target_principal_id,
                        "at": at,
                    },
                )
            )
            .mappings()
            .all()
        )
        by_principal = {row["principal_id"]: row for row in rows}
        current = by_principal.get(current_owner_id)
        target = by_principal.get(target_principal_id)
        if current is None or current["role"] != ProjectRole.OWNER.value:
            raise ConcurrencyConflict("The current Project Owner membership changed.")
        if target is None:
            raise ResourceNotFound("Target must already be an active Project member.")
        if current["valid_from"] >= at or target["valid_from"] >= at:
            raise ConcurrencyConflict("Ownership cannot change at a membership boundary instant.")

        common = {
            "workspace_id": current["workspace_id"],
            "project_id": project_id,
            "valid_from": at,
            "granted_by_agent_id": acting_agent_id,
        }
        await self.add(
            ProjectMembership(
                id=uuid4(),
                principal_id=current_owner_id,
                role=ProjectRole.ADMIN,
                valid_to=None,
                **common,
            )
        )
        await self.add(
            ProjectMembership(
                id=uuid4(),
                principal_id=target_principal_id,
                role=ProjectRole.OWNER,
                valid_to=None,
                **common,
            )
        )
        await self._session.execute(
            text(
                """
                update project_memberships set valid_to = :at
                where id in (:current_id, :target_id)
                """
            ),
            {"at": at, "current_id": current["id"], "target_id": target["id"]},
        )


class SqlProductionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, production: Production) -> None:
        await self._session.execute(
            text(
                """
                insert into productions (
                    id, workspace_id, project_id, name, state, version,
                    created_at, updated_at
                ) values (
                    :id, :workspace_id, :project_id, :name, :state, :version,
                    :created_at, :updated_at
                )
                """
            ),
            _production_params(production),
        )

    async def get(self, production_id: UUID, *, lock: bool = False) -> Production | None:
        statement = (
            text("select * from productions where id = :id for update")
            if lock
            else text("select * from productions where id = :id")
        )
        row = (
            (
                await self._session.execute(
                    statement,
                    {"id": production_id},
                )
            )
            .mappings()
            .one_or_none()
        )
        return None if row is None else _production_from_row(row)

    async def update(self, production: Production, *, expected_version: int) -> None:
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    """
                    update productions
                    set name = :name, state = :state, version = :version,
                        updated_at = :updated_at
                    where id = :id
                      and workspace_id = :workspace_id
                      and version = :expected_version
                    """
                ),
                {**_production_params(production), "expected_version": expected_version},
            ),
        )
        if result.rowcount != 1:
            raise ConcurrencyConflict("Production changed before this operation could commit.")


class SqlOutboxRepository:
    def __init__(self, session: AsyncSession, workspace_id: UUID) -> None:
        self._session = session
        self._workspace_id = workspace_id

    async def append(
        self,
        event_type: str,
        version: int,
        payload: dict[str, object],
        *,
        aggregate_id: UUID | None = None,
        aggregate_sequence: int = 1,
    ) -> None:
        resolved_aggregate_id = aggregate_id
        if resolved_aggregate_id is None:
            candidate = payload.get("aggregate_id") or payload.get("project_id")
            if candidate is None:
                raise ValueError("aggregate_id is required for an outbox event")
            resolved_aggregate_id = UUID(str(candidate))
        await self._session.execute(
            text(
                """
                insert into outbox_events (
                    workspace_id, aggregate_id, aggregate_sequence,
                    event_type, event_version, payload
                ) values (
                    :workspace_id, :aggregate_id, :aggregate_sequence,
                    :event_type, :event_version, cast(:payload as jsonb)
                )
                """
            ),
            {
                "workspace_id": self._workspace_id,
                "aggregate_id": resolved_aggregate_id,
                "aggregate_sequence": aggregate_sequence,
                "event_type": event_type,
                "event_version": version,
                "payload": json.dumps(payload),
            },
        )


class SqlOperationalStatusRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def delivery_status(self, *, workspace_id: UUID) -> dict[str, Any]:
        values = (
            await self._session.execute(
                text(
                    """
                    select
                      (select count(*) from outbox_events
                       where workspace_id = :workspace_id
                         and delivered_at is null) as outbox_pending,
                      (select count(*) from outbox_events
                       where workspace_id = :workspace_id
                         and delivered_at is not null) as outbox_delivered,
                      (select count(*) from audit_delivery_queue
                       where workspace_id = :workspace_id
                         and delivered_at is null and failed_at is null) as audit_pending,
                      (select count(*) from audit_delivery_queue
                       where workspace_id = :workspace_id
                         and failed_at is not null) as audit_failed,
                      (select count(*) from audit_delivery_queue
                       where workspace_id = :workspace_id
                         and delivered_at is not null) as audit_delivered
                    """
                ),
                {"workspace_id": workspace_id},
            )
        ).mappings().one()
        return {
            "workspace_id": workspace_id,
            "outbox": {
                "mode": "durable-storage-only",
                "pending": int(values["outbox_pending"]),
                "delivered": int(values["outbox_delivered"]),
                "consumer_configured": False,
            },
            "audit_delivery": {
                "pending": int(values["audit_pending"]),
                "failed": int(values["audit_failed"]),
                "delivered": int(values["audit_delivered"]),
            },
        }


def _project_params(project: Project) -> dict[str, object]:
    return {
        "id": project.id,
        "workspace_id": project.workspace_id,
        "identity_id": project.identity_id,
        "context_id": project.context_id,
        "owner_principal_id": project.owner_principal_id,
        "created_by_principal_id": project.created_by_principal_id,
        "name": project.name,
        "lifecycle": project.lifecycle.value,
        "version": project.version,
        "created_at": project.created_at,
        "updated_at": project.updated_at,
        "archived_at": project.archived_at,
    }


def _project_from_row(values: RowMapping) -> Project:
    return Project(
        id=values["id"],
        workspace_id=values["workspace_id"],
        identity_id=values["identity_id"],
        context_id=values["context_id"],
        owner_principal_id=values["owner_principal_id"],
        created_by_principal_id=values["created_by_principal_id"],
        name=values["name"],
        lifecycle=ProjectLifecycle(values["lifecycle"]),
        version=values["version"],
        created_at=values["created_at"],
        updated_at=values["updated_at"],
        archived_at=values["archived_at"],
    )


def _production_params(production: Production) -> dict[str, object]:
    return {
        "id": production.id,
        "workspace_id": production.workspace_id,
        "project_id": production.project_id,
        "name": production.name,
        "state": production.state.value,
        "version": production.version,
        "created_at": production.created_at,
        "updated_at": production.updated_at,
    }


def _production_from_row(values: RowMapping) -> Production:
    return Production(
        id=values["id"],
        workspace_id=values["workspace_id"],
        project_id=values["project_id"],
        name=values["name"],
        state=ProductionState(values["state"]),
        version=values["version"],
        created_at=values["created_at"],
        updated_at=values["updated_at"],
    )
