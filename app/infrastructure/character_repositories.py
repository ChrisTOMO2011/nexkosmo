from __future__ import annotations

import json
from collections import defaultdict
from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from sqlalchemy import bindparam, text
from sqlalchemy.engine import CursorResult
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.characters import (
    Character,
    CharacterAssetManifest,
    DownstreamDependency,
    Species,
)
from app.domain.errors import ConcurrencyConflict, NotFound

CHARACTER_SCALAR_COLUMNS = (
    "character_id",
    "workspace_id",
    "project_id",
    "production_id",
    "display_name",
    "role",
    "identity_type",
    "age",
    "apparent_age",
    "height_cm",
    "body_type",
    "skin_tone",
    "gender_presentation",
    "physical_profile_version",
    "species_id",
    "type_id",
    "style_profile_id",
    "identity_id",
    "face_id",
    "hair_id",
    "skin_id",
    "eyes_id",
    "beard_id",
    "body_id",
    "age_preset_id",
    "expression_id",
    "rig_id",
    "skeleton_id",
    "voice_id",
    "preview_asset_id",
    "compatibility_profile_id",
    "pipeline_status",
    "readiness_status",
    "validation_issues",
    "validated_version",
    "validated_at",
    "version",
    "created_at",
    "updated_at",
)

CHARACTER_RELATIONS = {
    "accessory_ids": ("character_accessories", "accessory_id"),
    "wardrobe_ids": ("character_wardrobe", "wardrobe_asset_id"),
    "material_ids": ("character_materials", "material_id"),
    "texture_ids": ("character_textures", "texture_id"),
    "animation_ids": ("character_animations", "animation_id"),
    "uploaded_asset_ids": ("character_uploaded_assets", "asset_id"),
    "generated_asset_ids": ("character_generated_assets", "asset_id"),
}


def _params(value: object) -> object:
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, tuple):
        if value and isinstance(value[0], dict):
            return json.dumps(value)
        return [str(item) if isinstance(item, UUID) else item for item in value]
    if isinstance(value, dict):
        return json.dumps(value)
    return value


class SqlAlchemyCharacterRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, character: Character) -> None:
        columns = ", ".join(CHARACTER_SCALAR_COLUMNS)
        values = ", ".join(
            (f"CAST(:{column} AS jsonb)" if column == "validation_issues" else f":{column}")
            for column in CHARACTER_SCALAR_COLUMNS
        )
        await self._session.execute(
            text(f"INSERT INTO characters ({columns}) VALUES ({values})"),
            {
                column: (
                    json.dumps(getattr(character, column))
                    if column == "validation_issues"
                    else _params(getattr(character, column))
                )
                for column in CHARACTER_SCALAR_COLUMNS
            },
        )
        await self._replace_relations(character, delete_existing=False)
        await self._replace_downstream(character, delete_existing=False)

    async def get_by_id(self, character_id: UUID) -> Character | None:
        rows = (
            (
                await self._session.execute(
                    text(
                        f"SELECT {', '.join(CHARACTER_SCALAR_COLUMNS)} "
                        "FROM characters WHERE character_id = :character_id"
                    ),
                    {"character_id": str(character_id)},
                )
            )
            .mappings()
            .all()
        )
        hydrated = await self._hydrate(rows)
        return hydrated[0] if hydrated else None

    async def list_by_project(
        self, project_id: UUID, *, limit: int, offset: int
    ) -> list[Character]:
        rows = (
            (
                await self._session.execute(
                    text(
                        f"SELECT {', '.join(CHARACTER_SCALAR_COLUMNS)} FROM characters "
                        "WHERE project_id = :project_id AND pipeline_status <> 'archived' "
                        "ORDER BY updated_at DESC, character_id LIMIT :limit OFFSET :offset"
                    ),
                    {"project_id": str(project_id), "limit": limit, "offset": offset},
                )
            )
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def list_by_production(
        self, production_id: UUID, *, limit: int, offset: int
    ) -> list[Character]:
        rows = (
            (
                await self._session.execute(
                    text(
                        f"SELECT {', '.join(CHARACTER_SCALAR_COLUMNS)} FROM characters "
                        "WHERE production_id = :production_id AND pipeline_status <> 'archived' "
                        "ORDER BY updated_at DESC, character_id LIMIT :limit OFFSET :offset"
                    ),
                    {"production_id": str(production_id), "limit": limit, "offset": offset},
                )
            )
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def update(self, character: Character, *, expected_version: int) -> None:
        assignments = ", ".join(
            (
                f"{column} = CAST(:{column} AS jsonb)"
                if column == "validation_issues"
                else f"{column} = :{column}"
            )
            for column in CHARACTER_SCALAR_COLUMNS
            if column not in {"character_id", "workspace_id", "created_at"}
        )
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    f"UPDATE characters SET {assignments} "
                    "WHERE character_id = :character_id AND version = :expected_version"
                ),
                {
                    **{
                        column: _params(getattr(character, column))
                        if column != "validation_issues"
                        else json.dumps(getattr(character, column))
                        for column in CHARACTER_SCALAR_COLUMNS
                        if column not in {"workspace_id", "created_at"}
                    },
                    "expected_version": expected_version,
                },
            ),
        )
        if result.rowcount != 1:
            current_version = await self.get_version(character.character_id)
            if current_version is None:
                raise NotFound("Character does not exist.")
            raise ConcurrencyConflict(
                f"Expected character version {expected_version}, found {current_version}."
            )
        await self._replace_relations(character, delete_existing=True)
        await self._replace_downstream(character, delete_existing=True)

    async def archive(self, character_id: UUID, *, expected_version: int) -> None:
        result = cast(
            CursorResult[Any],
            await self._session.execute(
                text(
                    """
                UPDATE characters
                SET pipeline_status = 'archived', version = version + 1, updated_at = now()
                WHERE character_id = :character_id AND version = :expected_version
                """
                ),
                {"character_id": str(character_id), "expected_version": expected_version},
            ),
        )
        if result.rowcount != 1:
            current_version = await self.get_version(character_id)
            if current_version is None:
                raise NotFound("Character does not exist.")
            raise ConcurrencyConflict(
                f"Expected character version {expected_version}, found {current_version}."
            )

    async def exists(self, character_id: UUID) -> bool:
        return bool(
            await self._session.scalar(
                text("SELECT EXISTS(SELECT 1 FROM characters WHERE character_id = :id)"),
                {"id": str(character_id)},
            )
        )

    async def get_version(self, character_id: UUID) -> int | None:
        value = await self._session.scalar(
            text("SELECT version FROM characters WHERE character_id = :id"),
            {"id": str(character_id)},
        )
        return int(value) if value is not None else None

    async def _hydrate(self, rows: Sequence[Any]) -> list[Character]:
        if not rows:
            return []
        ids = [row["character_id"] for row in rows]
        relations: dict[UUID, dict[str, list[UUID]]] = defaultdict(lambda: defaultdict(list))
        unions = []
        for field_name, (table, column) in CHARACTER_RELATIONS.items():
            unions.append(
                f"SELECT character_id, '{field_name}' AS field_name, "
                f"{column} AS asset_id, ordinal FROM {table} "
                "WHERE character_id IN :character_ids"
            )
        statement = text(" UNION ALL ".join(unions)).bindparams(
            bindparam("character_ids", expanding=True)
        )
        for relation in (await self._session.execute(statement, {"character_ids": ids})).mappings():
            relations[relation["character_id"]][relation["field_name"]].append(relation["asset_id"])
        downstream: dict[UUID, list[DownstreamDependency]] = defaultdict(list)
        downstream_statement = text(
            """
            SELECT character_id, stage, status, invalidated_at, reason
            FROM character_downstream_dependencies
            WHERE character_id IN :character_ids
            ORDER BY character_id, stage
            """
        ).bindparams(bindparam("character_ids", expanding=True))
        for item in (
            await self._session.execute(downstream_statement, {"character_ids": ids})
        ).mappings():
            downstream[item["character_id"]].append(
                DownstreamDependency(
                    stage=item["stage"],
                    status=item["status"],
                    invalidated_at=item["invalidated_at"],
                    reason=item["reason"],
                )
            )
        characters = []
        for row in rows:
            payload = {
                **dict(row),
                **{
                    field_name: tuple(relations[row["character_id"]][field_name])
                    for field_name in CHARACTER_RELATIONS
                },
                "downstream_status": tuple(downstream[row["character_id"]]),
            }
            payload["validation_issues"] = tuple(payload["validation_issues"] or ())
            characters.append(Character(**cast(Any, payload)))
        return characters

    async def _replace_relations(self, character: Character, *, delete_existing: bool) -> None:
        for field_name, (table, column) in CHARACTER_RELATIONS.items():
            if delete_existing:
                await self._session.execute(
                    text(
                        f"DELETE FROM {table} "
                        "WHERE workspace_id = :workspace_id AND character_id = :character_id"
                    ),
                    {
                        "workspace_id": str(character.workspace_id),
                        "character_id": str(character.character_id),
                    },
                )
            values: tuple[UUID, ...] = getattr(character, field_name)
            if values:
                await self._session.execute(
                    text(
                        f"INSERT INTO {table} "
                        f"(workspace_id, character_id, {column}, ordinal) "
                        f"VALUES (:workspace_id, :character_id, :asset_id, :ordinal)"
                    ),
                    [
                        {
                            "workspace_id": str(character.workspace_id),
                            "character_id": str(character.character_id),
                            "asset_id": str(asset_id),
                            "ordinal": ordinal,
                        }
                        for ordinal, asset_id in enumerate(values)
                    ],
                )

    async def _replace_downstream(self, character: Character, *, delete_existing: bool) -> None:
        if delete_existing:
            await self._session.execute(
                text(
                    "DELETE FROM character_downstream_dependencies "
                    "WHERE workspace_id = :workspace_id AND character_id = :character_id"
                ),
                {
                    "workspace_id": str(character.workspace_id),
                    "character_id": str(character.character_id),
                },
            )
        if character.downstream_status:
            await self._session.execute(
                text(
                    """
                    INSERT INTO character_downstream_dependencies (
                        workspace_id, character_id, stage, status, invalidated_at, reason
                    ) VALUES (
                        :workspace_id, :character_id, :stage, :status,
                        :invalidated_at, :reason
                    )
                    """
                ),
                [
                    {
                        "workspace_id": str(character.workspace_id),
                        "character_id": str(character.character_id),
                        "stage": item.stage,
                        "status": item.status,
                        "invalidated_at": item.invalidated_at,
                        "reason": item.reason,
                    }
                    for item in character.downstream_status
                ],
            )


class SqlAlchemySpeciesRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, species_id: UUID) -> Species | None:
        row = (
            (
                await self._session.execute(
                    text("SELECT * FROM species WHERE species_id = :species_id"),
                    {"species_id": str(species_id)},
                )
            )
            .mappings()
            .first()
        )
        return self._map(row) if row else None

    async def get_by_key(self, key: str) -> Species | None:
        row = (
            (
                await self._session.execute(
                    text("SELECT * FROM species WHERE key = :key"), {"key": key}
                )
            )
            .mappings()
            .first()
        )
        return self._map(row) if row else None

    async def list_enabled(self) -> list[Species]:
        rows = (
            await self._session.execute(text("SELECT * FROM species WHERE enabled ORDER BY name"))
        ).mappings()
        return [self._map(row) for row in rows]

    async def upsert_seed_data(self, species: tuple[Species, ...]) -> None:
        for item in species:
            await self._session.execute(
                text(
                    """
                    INSERT INTO species (
                        species_id, key, name, category, enabled, capabilities,
                        supported_tabs, compatibility_profile_id, default_rig_id,
                        default_skeleton_id, default_material_profile_id, default_body_id,
                        min_age, max_age, min_height_cm, max_height_cm, surface_control_label,
                        version, created_at, updated_at
                    ) VALUES (
                        :species_id, :key, :name, :category, :enabled, :capabilities,
                        :supported_tabs, :compatibility_profile_id, :default_rig_id,
                        :default_skeleton_id, :default_material_profile_id, :default_body_id,
                        :min_age, :max_age, :min_height_cm, :max_height_cm, :surface_control_label,
                        :version, :created_at, :updated_at
                    )
                    ON CONFLICT (key) DO UPDATE SET
                        name = EXCLUDED.name, category = EXCLUDED.category,
                        enabled = EXCLUDED.enabled, capabilities = EXCLUDED.capabilities,
                        supported_tabs = EXCLUDED.supported_tabs,
                        compatibility_profile_id = EXCLUDED.compatibility_profile_id,
                        default_rig_id = EXCLUDED.default_rig_id,
                        default_skeleton_id = EXCLUDED.default_skeleton_id,
                        default_material_profile_id = EXCLUDED.default_material_profile_id,
                        default_body_id = EXCLUDED.default_body_id,
                        min_age = EXCLUDED.min_age, max_age = EXCLUDED.max_age,
                        min_height_cm = EXCLUDED.min_height_cm,
                        max_height_cm = EXCLUDED.max_height_cm,
                        surface_control_label = EXCLUDED.surface_control_label,
                        version = EXCLUDED.version, updated_at = EXCLUDED.updated_at
                    """
                ),
                {field: _params(getattr(item, field)) for field in item.__dataclass_fields__},
            )

    @staticmethod
    def _map(row: Any) -> Species:
        values = dict(row)
        values["capabilities"] = frozenset(values["capabilities"])
        values["supported_tabs"] = tuple(values["supported_tabs"])
        return Species(**values)


class SqlAlchemyCharacterAssetManifestRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, asset_id: UUID) -> CharacterAssetManifest | None:
        rows = (
            (
                await self._session.execute(
                    text(
                        "SELECT * FROM character_asset_manifests "
                        "WHERE asset_id = :asset_id AND domain = 'character'"
                    ),
                    {"asset_id": str(asset_id)},
                )
            )
            .mappings()
            .all()
        )
        hydrated = await self._hydrate(rows)
        return hydrated[0] if hydrated else None

    async def get_many(self, asset_ids: tuple[UUID, ...]) -> list[CharacterAssetManifest]:
        if not asset_ids:
            return []
        statement = text(
            "SELECT * FROM character_asset_manifests "
            "WHERE domain = 'character' AND asset_id IN :asset_ids"
        ).bindparams(bindparam("asset_ids", expanding=True))
        rows = (
            (await self._session.execute(statement, {"asset_ids": list(asset_ids)}))
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def list_by_species(
        self,
        species_id: UUID,
        *,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[CharacterAssetManifest]:
        rows = await self._list_candidates(
            species_id=species_id, category=category, limit=limit, offset=offset
        )
        return await self._hydrate(rows)

    async def list_by_category(
        self, category: str, *, limit: int, offset: int
    ) -> list[CharacterAssetManifest]:
        rows = (
            (
                await self._session.execute(
                    text(
                        """
                    SELECT * FROM character_asset_manifests
                    WHERE domain = 'character' AND category = :category
                    ORDER BY name, asset_id LIMIT :limit OFFSET :offset
                    """
                    ),
                    {"category": category, "limit": limit, "offset": offset},
                )
            )
            .mappings()
            .all()
        )
        return await self._hydrate(rows)

    async def list_compatible(
        self,
        *,
        species_id: UUID,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[CharacterAssetManifest]:
        rows = await self._list_candidates(
            species_id=species_id, category=category, limit=limit, offset=offset
        )
        return await self._hydrate(rows)

    async def upsert(self, manifest: CharacterAssetManifest) -> None:
        fields = (
            "asset_id",
            "workspace_id",
            "name",
            "category",
            "subcategory",
            "thumbnail_reference",
            "preview_reference",
            "source",
            "status",
            "tags",
            "gender_compatibility",
            "age_compatibility",
            "body_compatibility",
            "rig_compatibility",
            "skeleton_compatibility",
            "material_compatibility",
            "required_capabilities",
            "file_references",
            "generated",
            "uploaded",
            "provenance",
            "visibility",
            "attachment_point",
            "compatible_body_regions",
            "profile_metadata",
            "version",
            "created_at",
            "updated_at",
        )
        await self._session.execute(
            text(
                f"""
                INSERT INTO character_asset_manifests ({", ".join(fields)})
                VALUES ({", ".join(f":{field}" for field in fields)})
                ON CONFLICT (asset_id) DO UPDATE SET
                    name = EXCLUDED.name, category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory,
                    thumbnail_reference = EXCLUDED.thumbnail_reference,
                    preview_reference = EXCLUDED.preview_reference,
                    source = EXCLUDED.source, status = EXCLUDED.status,
                    tags = EXCLUDED.tags,
                    gender_compatibility = EXCLUDED.gender_compatibility,
                    age_compatibility = EXCLUDED.age_compatibility,
                    body_compatibility = EXCLUDED.body_compatibility,
                    rig_compatibility = EXCLUDED.rig_compatibility,
                    skeleton_compatibility = EXCLUDED.skeleton_compatibility,
                    material_compatibility = EXCLUDED.material_compatibility,
                    required_capabilities = EXCLUDED.required_capabilities,
                    file_references = EXCLUDED.file_references,
                    generated = EXCLUDED.generated, uploaded = EXCLUDED.uploaded,
                    provenance = EXCLUDED.provenance, version = EXCLUDED.version,
                    visibility = EXCLUDED.visibility,
                    attachment_point = EXCLUDED.attachment_point,
                    compatible_body_regions = EXCLUDED.compatible_body_regions,
                    profile_metadata = EXCLUDED.profile_metadata,
                    updated_at = EXCLUDED.updated_at
                """
            ),
            {
                **{field: _params(getattr(manifest, field)) for field in fields},
                "provenance": json.dumps(manifest.provenance),
                "profile_metadata": json.dumps(manifest.profile_metadata),
            },
        )
        await self._replace_manifest_relations(manifest)

    async def batch_upsert(self, manifests: tuple[CharacterAssetManifest, ...]) -> None:
        for manifest in manifests:
            await self.upsert(manifest)

    async def _list_candidates(
        self, *, species_id: UUID, category: str | None, limit: int, offset: int
    ) -> list[Any]:
        return list(
            (
                await self._session.execute(
                    text(
                        """
                    SELECT DISTINCT manifest.*
                    FROM character_asset_manifests manifest
                    LEFT JOIN character_asset_species declared
                      ON declared.asset_id = manifest.asset_id
                    WHERE manifest.domain = 'character'
                      AND (declared.species_id = :species_id OR declared.species_id IS NULL)
                      AND (
                        CAST(:category AS text) IS NULL
                        OR manifest.category = CAST(:category AS text)
                      )
                      AND manifest.status IN (
                        'development-placeholder','available','approved'
                      )
                    ORDER BY manifest.name, manifest.asset_id
                    LIMIT :limit OFFSET :offset
                    """
                    ),
                    {
                        "species_id": str(species_id),
                        "category": category,
                        "limit": limit,
                        "offset": offset,
                    },
                )
            )
            .mappings()
            .all()
        )

    async def _hydrate(self, rows: Sequence[Any]) -> list[CharacterAssetManifest]:
        if not rows:
            return []
        ids = [row["asset_id"] for row in rows]
        relation_values: dict[UUID, dict[str, list[UUID]]] = defaultdict(lambda: defaultdict(list))
        relations = (
            ("species_ids", "character_asset_species", "species_id"),
            ("type_ids", "character_asset_types", "type_id"),
            (
                "dependent_asset_ids",
                "character_asset_dependencies",
                "dependent_asset_id",
            ),
            (
                "incompatible_asset_ids",
                "character_asset_incompatibilities",
                "incompatible_asset_id",
            ),
        )
        unions = [
            f"SELECT asset_id, '{field}' AS field_name, {column} AS related_id "
            f"FROM {table} WHERE asset_id IN :asset_ids"
            for field, table, column in relations
        ]
        statement = text(" UNION ALL ".join(unions)).bindparams(
            bindparam("asset_ids", expanding=True)
        )
        for relation in (await self._session.execute(statement, {"asset_ids": ids})).mappings():
            relation_values[relation["asset_id"]][relation["field_name"]].append(
                relation["related_id"]
            )

        manifests = []
        for row in rows:
            values = dict(row)
            for field in (
                "tags",
                "required_capabilities",
            ):
                values[field] = frozenset(values[field])
            for field in (
                "gender_compatibility",
                "age_compatibility",
                "body_compatibility",
                "rig_compatibility",
                "skeleton_compatibility",
                "material_compatibility",
                "file_references",
                "compatible_body_regions",
            ):
                values[field] = tuple(values[field])
            for field, _table, _column in relations:
                values[field] = tuple(relation_values[row["asset_id"]][field])
            allowed = CharacterAssetManifest.__dataclass_fields__
            manifests.append(
                CharacterAssetManifest(
                    **cast(Any, {key: value for key, value in values.items() if key in allowed})
                )
            )
        return manifests

    async def _replace_manifest_relations(self, manifest: CharacterAssetManifest) -> None:
        relations = (
            ("character_asset_species", "species_id", manifest.species_ids),
            ("character_asset_types", "type_id", manifest.type_ids),
            (
                "character_asset_dependencies",
                "dependent_asset_id",
                manifest.dependent_asset_ids,
            ),
            (
                "character_asset_incompatibilities",
                "incompatible_asset_id",
                manifest.incompatible_asset_ids,
            ),
        )
        for table, column, values in relations:
            await self._session.execute(
                text(f"DELETE FROM {table} WHERE asset_id = :asset_id"),
                {"asset_id": str(manifest.asset_id)},
            )
            if values:
                await self._session.execute(
                    text(
                        f"INSERT INTO {table} (workspace_id, asset_id, {column}) "
                        f"VALUES (:workspace_id, :asset_id, :related_id)"
                    ),
                    [
                        {
                            "workspace_id": (
                                str(manifest.workspace_id)
                                if manifest.workspace_id is not None
                                else None
                            ),
                            "asset_id": str(manifest.asset_id),
                            "related_id": str(value),
                        }
                        for value in values
                    ],
                )
