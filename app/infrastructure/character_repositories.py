from typing import Any, cast
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import CursorResult, RowMapping
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.characters import Character
from app.domain.errors import ConcurrencyConflict


class SqlCharacterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, character: Character) -> None:
        await self._session.execute(
            text(
                """
                insert into characters (
                    id, workspace_id, project_id, identity_id,
                    created_by_principal_id, display_name, role_label,
                    version, created_at, updated_at
                ) values (
                    :id, :workspace_id, :project_id, :identity_id,
                    :created_by_principal_id, :display_name, :role_label,
                    :version, :created_at, :updated_at
                )
                """
            ),
            _character_params(character),
        )

    async def get(self, character_id: UUID, *, lock: bool = False) -> Character | None:
        statement = (
            text("select * from characters where id = :id for update")
            if lock
            else text("select * from characters where id = :id")
        )
        row = (
            (await self._session.execute(statement, {"id": character_id}))
            .mappings()
            .one_or_none()
        )
        return None if row is None else _character_from_row(row)

    async def list_for_project(self, project_id: UUID) -> list[Character]:
        rows = (
            (
                await self._session.execute(
                    text(
                        """
                        select * from characters
                        where project_id = :project_id
                        order by created_at, id
                        """
                    ),
                    {"project_id": project_id},
                )
            )
            .mappings()
            .all()
        )
        return [_character_from_row(row) for row in rows]

    async def update(self, character: Character, *, expected_version: int) -> None:
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    """
                    update characters
                    set display_name = :display_name,
                        role_label = :role_label,
                        version = :version,
                        updated_at = :updated_at
                    where id = :id
                      and workspace_id = :workspace_id
                      and project_id = :project_id
                      and version = :expected_version
                    """
                ),
                {**_character_params(character), "expected_version": expected_version},
            ),
        )
        if result.rowcount != 1:
            raise ConcurrencyConflict("Character changed before this operation could commit.")


def _character_params(character: Character) -> dict[str, object]:
    return {
        "id": character.id,
        "workspace_id": character.workspace_id,
        "project_id": character.project_id,
        "identity_id": character.identity_id,
        "created_by_principal_id": character.created_by_principal_id,
        "display_name": character.display_name,
        "role_label": character.role_label,
        "version": character.version,
        "created_at": character.created_at,
        "updated_at": character.updated_at,
    }


def _character_from_row(values: RowMapping) -> Character:
    return Character(
        id=values["id"],
        workspace_id=values["workspace_id"],
        project_id=values["project_id"],
        identity_id=values["identity_id"],
        created_by_principal_id=values["created_by_principal_id"],
        display_name=values["display_name"],
        role_label=values["role_label"],
        version=values["version"],
        created_at=values["created_at"],
        updated_at=values["updated_at"],
    )
