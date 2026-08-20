from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.environments import Environment, EnvironmentAssetManifest, EnvironmentType
from app.domain.errors import ConcurrencyConflict, NotFound

ENVIRONMENT_SCALAR_COLUMNS = (
    "environment_id",
    "workspace_id",
    "project_id",
    "production_id",
    "display_name",
    "description",
    "environment_type_id",
    "location_type",
    "interior_exterior",
    "biome",
    "climate_profile",
    "terrain_profile_id",
    "weather_profile_id",
    "time_of_day",
    "atmosphere_profile_id",
    "style_profile_id",
    "lighting_compatibility_profile_id",
    "camera_compatibility_profile_id",
    "audio_compatibility_profile_id",
    "vfx_compatibility_profile_id",
    "preview_asset_id",
    "scale",
    "navigation_constraints",
    "camera_access_constraints",
    "package_status",
    "readiness_status",
    "validation_issues",
    "readiness_warnings",
    "missing_requirements",
    "invalid_asset_ids",
    "required_processing_jobs",
    "readiness_validated_version",
    "readiness_validated_at",
    "version",
    "created_at",
    "updated_at",
)

ENVIRONMENT_RELATIONS = {
    "background_asset_ids": "background",
    "terrain_asset_ids": "terrain",
    "building_asset_ids": "building",
    "nature_asset_ids": "nature",
    "practical_asset_ids": "practical",
    "material_profile_ids": "material",
    "texture_profile_ids": "texture",
    "detail_asset_ids": "detail",
}


def _value(value: object) -> object:
    if isinstance(value, UUID):
        return str(value)
    return value


ENVIRONMENT_JSON_COLUMNS = frozenset({"validation_issues", "readiness_warnings"})


class SqlAlchemyEnvironmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, environment: Environment) -> None:
        columns = ", ".join(ENVIRONMENT_SCALAR_COLUMNS)
        values = ", ".join(
            f"CAST(:{column} AS jsonb)" if column in ENVIRONMENT_JSON_COLUMNS else f":{column}"
            for column in ENVIRONMENT_SCALAR_COLUMNS
        )
        await self._session.execute(
            text(f"INSERT INTO environments ({columns}) VALUES ({values})"),
            {
                column: (
                    json.dumps(getattr(environment, column))
                    if column in ENVIRONMENT_JSON_COLUMNS
                    else list(getattr(environment, column))
                    if column
                    in {"missing_requirements", "invalid_asset_ids", "required_processing_jobs"}
                    else _value(getattr(environment, column))
                )
                for column in ENVIRONMENT_SCALAR_COLUMNS
            },
        )
        await self._replace_relations(environment, delete_existing=False)

    async def get_by_id(self, environment_id: UUID) -> Environment | None:
        rows = (
            (
                await self._session.execute(
                    text(
                        f"SELECT {', '.join(ENVIRONMENT_SCALAR_COLUMNS)} FROM environments "
                        "WHERE environment_id = :environment_id"
                    ),
                    {"environment_id": str(environment_id)},
                )
            )
            .mappings()
            .all()
        )
        hydrated = await self._hydrate(rows)
        return hydrated[0] if hydrated else None

    async def list_by_project(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[Environment]:
        return await self._list("project_id", project_id, limit=limit, offset=offset)

    async def list_by_production(
        self, production_id: UUID, *, limit: int, offset: int
    ) -> list[Environment]:
        return await self._list("production_id", production_id, limit=limit, offset=offset)

    async def _list(self, field: str, value: UUID, *, limit: int, offset: int) -> list[Environment]:
        rows = (
            (
                await self._session.execute(
                    text(
                        f"SELECT {', '.join(ENVIRONMENT_SCALAR_COLUMNS)} FROM environments "
                        f"WHERE {field} = :value AND package_status <> 'archived' "
                        "ORDER BY updated_at DESC, environment_id LIMIT :limit OFFSET :offset"
                    ),
                    {"value": str(value), "limit": limit, "offset": offset},
                )
            )
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def update(self, environment: Environment, *, expected_version: int) -> None:
        assignments = ", ".join(
            f"{column} = CAST(:{column} AS jsonb)"
            if column in ENVIRONMENT_JSON_COLUMNS
            else f"{column} = :{column}"
            for column in ENVIRONMENT_SCALAR_COLUMNS
            if column not in {"environment_id", "workspace_id", "created_at"}
        )
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    f"UPDATE environments SET {assignments} "
                    "WHERE environment_id = :environment_id AND version = :expected_version"
                ),
                {
                    **{
                        column: (
                            json.dumps(getattr(environment, column))
                            if column in ENVIRONMENT_JSON_COLUMNS
                            else list(getattr(environment, column))
                            if column
                            in {
                                "missing_requirements",
                                "invalid_asset_ids",
                                "required_processing_jobs",
                            }
                            else _value(getattr(environment, column))
                        )
                        for column in ENVIRONMENT_SCALAR_COLUMNS
                        if column not in {"workspace_id", "created_at"}
                    },
                    "expected_version": expected_version,
                },
            ),
        )
        if result.rowcount != 1:
            current_version = await self.get_version(environment.environment_id)
            if current_version is None:
                raise NotFound("Environment does not exist.")
            raise ConcurrencyConflict(
                f"Expected environment version {expected_version}, found {current_version}."
            )
        await self._replace_relations(environment, delete_existing=True)

    async def get_version(self, environment_id: UUID) -> int | None:
        value = await self._session.scalar(
            text("SELECT version FROM environments WHERE environment_id = :id"),
            {"id": str(environment_id)},
        )
        return int(value) if value is not None else None

    async def exists(self, environment_id: UUID) -> bool:
        return (await self.get_version(environment_id)) is not None

    async def archive(self, environment_id: UUID, *, expected_version: int) -> None:
        current = await self.get_by_id(environment_id)
        if current is None:
            raise NotFound("Environment does not exist.")
        await self.update(current.archive(), expected_version=expected_version)

    async def _hydrate(self, rows: Sequence[Any]) -> list[Environment]:
        if not rows:
            return []
        ids = [row["environment_id"] for row in rows]
        statement = text(
            """
            SELECT environment_id, category, asset_id, ordinal
            FROM environment_asset_selections
            WHERE environment_id IN :environment_ids
            ORDER BY environment_id, category, ordinal
            """
        ).bindparams(bindparam("environment_ids", expanding=True))
        selections: dict[UUID, dict[str, list[UUID]]] = defaultdict(lambda: defaultdict(list))
        for item in (await self._session.execute(statement, {"environment_ids": ids})).mappings():
            selections[item["environment_id"]][item["category"]].append(item["asset_id"])
        result = []
        for row in rows:
            payload = dict(row)
            payload["validation_issues"] = tuple(payload["validation_issues"] or ())
            payload["readiness_warnings"] = tuple(payload["readiness_warnings"] or ())
            for field_name in (
                "missing_requirements",
                "invalid_asset_ids",
                "required_processing_jobs",
            ):
                payload[field_name] = tuple(payload[field_name] or ())
            for field_name, category in ENVIRONMENT_RELATIONS.items():
                payload[field_name] = tuple(selections[row["environment_id"]][category])
            result.append(Environment(**cast(Any, payload)))
        return result

    async def _replace_relations(self, environment: Environment, *, delete_existing: bool) -> None:
        if delete_existing:
            await self._session.execute(
                text(
                    "DELETE FROM environment_asset_selections "
                    "WHERE workspace_id = :workspace_id AND environment_id = :environment_id"
                ),
                {
                    "workspace_id": str(environment.workspace_id),
                    "environment_id": str(environment.environment_id),
                },
            )
        rows = []
        for field_name, category in ENVIRONMENT_RELATIONS.items():
            for ordinal, asset_id in enumerate(getattr(environment, field_name)):
                rows.append(
                    {
                        "workspace_id": str(environment.workspace_id),
                        "environment_id": str(environment.environment_id),
                        "asset_id": str(asset_id),
                        "category": category,
                        "ordinal": ordinal,
                    }
                )
        if rows:
            await self._session.execute(
                text(
                    """
                    INSERT INTO environment_asset_selections (
                        workspace_id, environment_id, asset_id, category, ordinal
                    ) VALUES (
                        :workspace_id, :environment_id, :asset_id, :category, :ordinal
                    )
                    """
                ),
                rows,
            )


class SqlAlchemyEnvironmentTypeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, environment_type_id: UUID) -> EnvironmentType | None:
        row = (
            (
                await self._session.execute(
                    text(
                        "SELECT * FROM environment_types "
                        "WHERE environment_type_id = :environment_type_id"
                    ),
                    {"environment_type_id": str(environment_type_id)},
                )
            )
            .mappings()
            .first()
        )
        return self._map(row) if row else None

    async def get_by_key(self, key: str) -> EnvironmentType | None:
        row = (
            (
                await self._session.execute(
                    text("SELECT * FROM environment_types WHERE key = :key"), {"key": key}
                )
            )
            .mappings()
            .first()
        )
        return self._map(row) if row else None

    async def list_enabled(self) -> list[EnvironmentType]:
        rows = (
            await self._session.execute(
                text("SELECT * FROM environment_types WHERE enabled ORDER BY name")
            )
        ).mappings()
        return [self._map(row) for row in rows]

    @staticmethod
    def _map(row: Any) -> EnvironmentType:
        values = dict(row)
        values["capabilities"] = frozenset(values["capabilities"])
        values["supported_tabs"] = tuple(values["supported_tabs"])
        return EnvironmentType(**values)


class SqlAlchemyEnvironmentAssetManifestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, asset_id: UUID) -> EnvironmentAssetManifest | None:
        rows = (
            (
                await self._session.execute(
                    text(
                        "SELECT * FROM character_asset_manifests "
                        "WHERE asset_id = :asset_id AND domain = 'environment'"
                    ),
                    {"asset_id": str(asset_id)},
                )
            )
            .mappings()
            .all()
        )
        hydrated = await self._hydrate(rows)
        return hydrated[0] if hydrated else None

    async def get_many(self, asset_ids: tuple[UUID, ...]) -> list[EnvironmentAssetManifest]:
        if not asset_ids:
            return []
        statement = text(
            "SELECT * FROM character_asset_manifests "
            "WHERE domain = 'environment' AND asset_id IN :asset_ids"
        ).bindparams(bindparam("asset_ids", expanding=True))
        rows = (
            (await self._session.execute(statement, {"asset_ids": list(asset_ids)}))
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def batch_load_dependencies(
        self, asset_ids: tuple[UUID, ...]
    ) -> list[EnvironmentAssetManifest]:
        manifests = await self.get_many(asset_ids)
        dependency_ids = tuple(
            dict.fromkeys(
                dependency for manifest in manifests for dependency in manifest.dependent_asset_ids
            )
        )
        dependencies = await self.get_many(dependency_ids)
        return [*manifests, *(item for item in dependencies if item.asset_id not in asset_ids)]

    async def list_visible(self, *, limit: int, offset: int) -> list[EnvironmentAssetManifest]:
        return await self._list_filtered(
            category=None, subcategory=None, limit=limit, offset=offset
        )

    async def list_by_category(
        self, category: str, *, limit: int, offset: int
    ) -> list[EnvironmentAssetManifest]:
        return await self._list_filtered(
            category=category, subcategory=None, limit=limit, offset=offset
        )

    async def list_by_filter(
        self,
        *,
        category: str | None,
        subcategory: str | None,
        limit: int,
        offset: int,
    ) -> list[EnvironmentAssetManifest]:
        return await self._list_filtered(
            category=category, subcategory=subcategory, limit=limit, offset=offset
        )

    async def _list_filtered(
        self,
        *,
        category: str | None,
        subcategory: str | None,
        limit: int,
        offset: int,
    ) -> list[EnvironmentAssetManifest]:
        rows = (
            (
                await self._session.execute(
                    text(
                        """
                        SELECT * FROM character_asset_manifests
                        WHERE domain = 'environment'
                          AND visibility IN ('global','workspace','project')
                          AND status IN ('development-placeholder','available','approved')
                          AND (
                            CAST(:category AS text) IS NULL
                            OR category = CAST(:category AS text)
                          )
                          AND (
                            CAST(:subcategory AS text) IS NULL
                            OR subcategory = CAST(:subcategory AS text)
                          )
                        ORDER BY name, asset_id LIMIT :limit OFFSET :offset
                        """
                    ),
                    {
                        "category": category,
                        "subcategory": subcategory,
                        "limit": limit,
                        "offset": offset,
                    },
                )
            )
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def list_compatible(
        self,
        *,
        environment_type_id: UUID,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[EnvironmentAssetManifest]:
        rows = (
            (
                await self._session.execute(
                    text(
                        """
                        SELECT DISTINCT manifest.*
                        FROM character_asset_manifests manifest
                        LEFT JOIN environment_asset_types declared
                          ON declared.asset_id = manifest.asset_id
                        WHERE manifest.domain = 'environment'
                          AND (
                            declared.environment_type_id = :environment_type_id
                            OR declared.environment_type_id IS NULL
                          )
                          AND (
                            CAST(:category AS text) IS NULL
                            OR manifest.category = CAST(:category AS text)
                          )
                          AND manifest.status IN (
                            'development-placeholder','available','approved'
                          )
                          AND manifest.visibility IN ('global','workspace','project')
                        ORDER BY manifest.name, manifest.asset_id
                        LIMIT :limit OFFSET :offset
                        """
                    ),
                    {
                        "environment_type_id": str(environment_type_id),
                        "category": category,
                        "limit": limit,
                        "offset": offset,
                    },
                )
            )
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def _hydrate(self, rows: Sequence[Any]) -> list[EnvironmentAssetManifest]:
        if not rows:
            return []
        ids = [row["asset_id"] for row in rows]
        statement = text(
            "SELECT asset_id, environment_type_id FROM environment_asset_types "
            "WHERE asset_id IN :asset_ids ORDER BY asset_id, environment_type_id"
        ).bindparams(bindparam("asset_ids", expanding=True))
        declared: dict[UUID, list[UUID]] = defaultdict(list)
        for item in (await self._session.execute(statement, {"asset_ids": ids})).mappings():
            declared[item["asset_id"]].append(item["environment_type_id"])
        manifests = []
        for row in rows:
            values = dict(row)
            values["compatible_environment_type_ids"] = tuple(declared[row["asset_id"]])
            values["required_capabilities"] = frozenset(values["required_capabilities"])
            for field in (
                "compatible_location_types",
                "compatible_biomes",
                "compatible_climates",
                "compatible_times_of_day",
                "compatible_weather_profile_ids",
                "compatible_style_profile_ids",
                "compatible_lighting_profile_ids",
                "compatible_camera_profile_ids",
                "incompatible_asset_ids",
                "dependent_asset_ids",
                "material_references",
                "texture_references",
            ):
                values[field] = tuple(values[field] or ())
            allowed = EnvironmentAssetManifest.__dataclass_fields__
            manifests.append(
                EnvironmentAssetManifest(
                    **cast(Any, {key: value for key, value in values.items() if key in allowed})
                )
            )
        return manifests
