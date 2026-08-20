from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.errors import ConcurrencyConflict, NotFound
from app.domain.projects import Production, Project, ProjectMemberRole

PROJECT_COLUMNS = (
    "project_id",
    "workspace_id",
    "name",
    "description",
    "status",
    "owner_id",
    "created_at",
    "updated_at",
    "version",
)
PRODUCTION_COLUMNS = (
    "production_id",
    "project_id",
    "workspace_id",
    "name",
    "production_type",
    "status",
    "owner_id",
    "created_at",
    "updated_at",
    "version",
)


def _value(value: object) -> object:
    return str(value) if isinstance(value, UUID) else value


class SqlAlchemyProjectRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, project: Project) -> None:
        await self._session.execute(
            text(
                f"INSERT INTO projects ({', '.join(PROJECT_COLUMNS)}) "
                f"VALUES ({', '.join(f':{column}' for column in PROJECT_COLUMNS)})"
            ),
            {column: _value(getattr(project, column)) for column in PROJECT_COLUMNS},
        )
        await self.set_member_role(project.project_id, project.owner_id, "Owner")

    async def get_by_id(self, project_id: UUID) -> Project | None:
        rows = (
            (
                await self._session.execute(
                    text(
                        f"SELECT {', '.join(PROJECT_COLUMNS)} FROM projects "
                        "WHERE project_id = :project_id"
                    ),
                    {"project_id": str(project_id)},
                )
            )
            .mappings()
            .all()
        )
        hydrated = await self._hydrate(rows)
        return hydrated[0] if hydrated else None

    async def list_workspace_projects(self, *, limit: int, offset: int) -> list[Project]:
        rows = (
            (
                await self._session.execute(
                    text(
                        f"SELECT {', '.join(PROJECT_COLUMNS)} FROM projects "
                        "ORDER BY updated_at DESC, project_id "
                        "LIMIT :limit OFFSET :offset"
                    ),
                    {"limit": limit, "offset": offset},
                )
            )
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def update(self, project: Project, *, expected_version: int) -> None:
        assignments = ", ".join(
            f"{column} = :{column}"
            for column in PROJECT_COLUMNS
            if column not in {"project_id", "workspace_id", "created_at"}
        )
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    f"UPDATE projects SET {assignments} "
                    "WHERE project_id = :project_id AND version = :expected_version"
                ),
                {
                    **{
                        column: _value(getattr(project, column))
                        for column in PROJECT_COLUMNS
                        if column not in {"workspace_id", "created_at"}
                    },
                    "expected_version": expected_version,
                },
            ),
        )
        if result.rowcount != 1:
            await self._raise_version_conflict(project.project_id, expected_version)
        await self._session.execute(
            text(
                """
                DELETE FROM project_members
                WHERE project_id = :project_id
                  AND principal_id NOT IN :member_ids
                """
            ).bindparams(bindparam("member_ids", expanding=True)),
            {
                "project_id": str(project.project_id),
                "member_ids": list(project.member_ids),
            },
        )

    async def archive(self, project_id: UUID, *, expected_version: int) -> None:
        current = await self.get_by_id(project_id)
        if current is None:
            raise NotFound("Project does not exist.")
        await self.update(current.archive(), expected_version=expected_version)

    async def get_version(self, project_id: UUID) -> int | None:
        version = await self._session.scalar(
            text("SELECT version FROM projects WHERE project_id = :project_id"),
            {"project_id": str(project_id)},
        )
        return int(version) if version is not None else None

    async def get_member_role(
        self, project_id: UUID, principal_id: UUID
    ) -> ProjectMemberRole | None:
        role = await self._session.scalar(
            text(
                """
                SELECT role FROM project_members
                WHERE project_id = :project_id AND principal_id = :principal_id
                """
            ),
            {
                "project_id": str(project_id),
                "principal_id": str(principal_id),
            },
        )
        return cast(ProjectMemberRole | None, role)

    async def set_member_role(
        self,
        project_id: UUID,
        principal_id: UUID,
        role: ProjectMemberRole,
    ) -> None:
        await self._session.execute(
            text(
                """
                INSERT INTO project_members (
                    workspace_id, project_id, principal_id, role
                )
                SELECT workspace_id, project_id, :principal_id, :role
                FROM projects WHERE project_id = :project_id
                ON CONFLICT (workspace_id, project_id, principal_id)
                DO UPDATE SET role = EXCLUDED.role, updated_at = now()
                """
            ),
            {
                "project_id": str(project_id),
                "principal_id": str(principal_id),
                "role": role,
            },
        )

    async def remove_member(self, project_id: UUID, principal_id: UUID) -> None:
        await self._session.execute(
            text(
                """
                DELETE FROM project_members
                WHERE project_id = :project_id AND principal_id = :principal_id
                """
            ),
            {
                "project_id": str(project_id),
                "principal_id": str(principal_id),
            },
        )

    async def _hydrate(self, rows: Sequence[Any]) -> list[Project]:
        if not rows:
            return []
        project_ids = [row["project_id"] for row in rows]
        members: dict[UUID, list[UUID]] = defaultdict(list)
        statement = text(
            """
            SELECT project_id, principal_id
            FROM project_members
            WHERE project_id IN :project_ids
            ORDER BY project_id, created_at, principal_id
            """
        ).bindparams(bindparam("project_ids", expanding=True))
        for member in (
            await self._session.execute(statement, {"project_ids": project_ids})
        ).mappings():
            members[member["project_id"]].append(member["principal_id"])
        return [
            Project(
                **cast(
                    Any,
                    {
                        **dict(row),
                        "member_ids": tuple(members[row["project_id"]]),
                    },
                )
            )
            for row in rows
        ]

    async def _raise_version_conflict(self, project_id: UUID, expected_version: int) -> None:
        current_version = await self.get_version(project_id)
        if current_version is None:
            raise NotFound("Project does not exist.")
        raise ConcurrencyConflict(
            f"Expected project version {expected_version}, found {current_version}."
        )


class SqlAlchemyProductionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, production: Production) -> None:
        await self._session.execute(
            text(
                f"INSERT INTO productions ({', '.join(PRODUCTION_COLUMNS)}) "
                f"VALUES ({', '.join(f':{column}' for column in PRODUCTION_COLUMNS)})"
            ),
            {column: _value(getattr(production, column)) for column in PRODUCTION_COLUMNS},
        )

    async def get_by_id(self, production_id: UUID) -> Production | None:
        row = (
            (
                await self._session.execute(
                    text(
                        f"SELECT {', '.join(PRODUCTION_COLUMNS)} FROM productions "
                        "WHERE production_id = :production_id"
                    ),
                    {"production_id": str(production_id)},
                )
            )
            .mappings()
            .first()
        )
        return Production(**cast(Any, dict(row))) if row else None

    async def list_project_productions(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[Production]:
        rows = (
            await self._session.execute(
                text(
                    f"SELECT {', '.join(PRODUCTION_COLUMNS)} FROM productions "
                    "WHERE project_id = :project_id "
                    "ORDER BY updated_at DESC, production_id "
                    "LIMIT :limit OFFSET :offset"
                ),
                {
                    "project_id": str(project_id),
                    "limit": limit,
                    "offset": offset,
                },
            )
        ).mappings()
        return [Production(**cast(Any, dict(row))) for row in rows]

    async def update(self, production: Production, *, expected_version: int) -> None:
        assignments = ", ".join(
            f"{column} = :{column}"
            for column in PRODUCTION_COLUMNS
            if column not in {"production_id", "project_id", "workspace_id", "created_at"}
        )
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    f"UPDATE productions SET {assignments} "
                    "WHERE production_id = :production_id "
                    "AND version = :expected_version"
                ),
                {
                    **{
                        column: _value(getattr(production, column))
                        for column in PRODUCTION_COLUMNS
                        if column not in {"project_id", "workspace_id", "created_at"}
                    },
                    "expected_version": expected_version,
                },
            ),
        )
        if result.rowcount != 1:
            current_version = await self.get_version(production.production_id)
            if current_version is None:
                raise NotFound("Production does not exist.")
            raise ConcurrencyConflict(
                f"Expected production version {expected_version}, found {current_version}."
            )

    async def archive(self, production_id: UUID, *, expected_version: int) -> None:
        current = await self.get_by_id(production_id)
        if current is None:
            raise NotFound("Production does not exist.")
        await self.update(current.archive(), expected_version=expected_version)

    async def get_version(self, production_id: UUID) -> int | None:
        version = await self._session.scalar(
            text("SELECT version FROM productions WHERE production_id = :production_id"),
            {"production_id": str(production_id)},
        )
        return int(version) if version is not None else None
