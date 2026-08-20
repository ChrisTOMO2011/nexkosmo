"""canonical character pipeline persistence

Revision ID: 0003_character_pipeline
Revises: 0002_fix_tenant_join_tables
"""

from alembic import op

revision = "0003_character_pipeline"
down_revision = "0002_fix_tenant_join_tables"
branch_labels = None
depends_on = None


SPECIES = (
    (
        "human",
        "Human",
        "humanoid",
        ("facial-animation", "hair", "beard", "wears-accessories", "voice"),
    ),
    ("elf", "Elf", "humanoid", ("facial-animation", "hair", "wears-accessories", "voice")),
    ("goblin", "Goblin", "humanoid", ("facial-animation", "wears-accessories", "voice")),
    ("orc", "Orc", "humanoid", ("facial-animation", "hair", "beard", "wears-accessories", "voice")),
    ("robot", "Robot", "synthetic", ("facial-animation", "modular-body", "voice")),
    ("dragon", "Dragon", "creature", ("facial-animation", "creature-rig", "voice")),
    ("alien", "Alien", "extraterrestrial", ("facial-animation", "modular-body", "voice")),
    ("monkey", "Monkey", "creature", ("facial-animation", "hair", "wears-accessories", "voice")),
    ("demon", "Demon", "creature", ("facial-animation", "wears-accessories", "voice")),
)

SUPPORTED_TABS = (
    "Identity",
    "Face",
    "Hair",
    "Skin",
    "Eyes",
    "Beard",
    "Body",
    "Age",
    "Expression",
    "Wardrobe",
    "Accessories",
    "Rig",
    "Animation",
    "Voice",
)


def _uuid(namespace: int, sequence: int) -> str:
    return f"{namespace:08x}-0000-4000-8000-{sequence:012x}"


def _sql_array(values: tuple[str, ...]) -> str:
    escaped = ",".join("'" + value.replace("'", "''") + "'" for value in values)
    return f"ARRAY[{escaped}]::text[]"


def _enable_workspace_rls(table: str, *, allow_global_reads: bool = False) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    read_scope = (
        "workspace_id IS NULL OR "
        if allow_global_reads
        else ""
    )
    op.execute(
        f"""
        CREATE POLICY {table}_read_scope ON {table} FOR SELECT
        USING (
            {read_scope}
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY {table}_write_scope ON {table} FOR ALL
        USING (
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        WITH CHECK (
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        """
    )


def _create_reference_tables() -> None:
    op.execute(
        """
        CREATE TABLE compatibility_profiles (
            compatibility_profile_id uuid PRIMARY KEY,
            key text NOT NULL UNIQUE,
            name text NOT NULL,
            required_capabilities text[] NOT NULL DEFAULT '{}',
            supported_categories text[] NOT NULL DEFAULT '{}',
            version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CHECK (updated_at >= created_at)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE character_asset_manifests (
            asset_id uuid PRIMARY KEY,
            workspace_id uuid REFERENCES workspaces(id) ON DELETE RESTRICT,
            name text NOT NULL,
            category text NOT NULL,
            subcategory text NOT NULL DEFAULT '',
            thumbnail_reference text,
            preview_reference text,
            source text NOT NULL,
            status text NOT NULL CHECK (
                status IN (
                    'development-placeholder','draft','available',
                    'needs-review','approved','blocked','archived'
                )
            ),
            tags text[] NOT NULL DEFAULT '{}',
            gender_compatibility text[] NOT NULL DEFAULT '{}',
            age_compatibility text[] NOT NULL DEFAULT '{}',
            body_compatibility uuid[] NOT NULL DEFAULT '{}',
            rig_compatibility uuid[] NOT NULL DEFAULT '{}',
            skeleton_compatibility uuid[] NOT NULL DEFAULT '{}',
            material_compatibility uuid[] NOT NULL DEFAULT '{}',
            required_capabilities text[] NOT NULL DEFAULT '{}',
            file_references text[] NOT NULL DEFAULT '{}',
            generated boolean NOT NULL DEFAULT false,
            uploaded boolean NOT NULL DEFAULT false,
            provenance jsonb NOT NULL DEFAULT '{}'::jsonb,
            version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE NULLS NOT DISTINCT (workspace_id, asset_id),
            CHECK (updated_at >= created_at)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE species (
            species_id uuid PRIMARY KEY,
            key text NOT NULL UNIQUE CHECK (key = lower(key)),
            name text NOT NULL,
            category text NOT NULL,
            enabled boolean NOT NULL DEFAULT true,
            capabilities text[] NOT NULL DEFAULT '{}',
            supported_tabs text[] NOT NULL DEFAULT '{}',
            compatibility_profile_id uuid NOT NULL
                REFERENCES compatibility_profiles(compatibility_profile_id) ON DELETE RESTRICT,
            default_rig_id uuid REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            default_skeleton_id uuid
                REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            default_material_profile_id uuid
                REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            default_body_id uuid REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CHECK (updated_at >= created_at)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE character_asset_species (
            workspace_id uuid REFERENCES workspaces(id) ON DELETE RESTRICT,
            asset_id uuid NOT NULL,
            species_id uuid NOT NULL REFERENCES species(species_id) ON DELETE RESTRICT,
            PRIMARY KEY (asset_id, species_id),
            FOREIGN KEY (workspace_id, asset_id)
                REFERENCES character_asset_manifests(workspace_id, asset_id) ON DELETE CASCADE
        )
        """
    )
    op.execute(
        """
        CREATE TABLE character_asset_types (
            workspace_id uuid REFERENCES workspaces(id) ON DELETE RESTRICT,
            asset_id uuid NOT NULL,
            type_id uuid NOT NULL,
            PRIMARY KEY (asset_id, type_id),
            FOREIGN KEY (workspace_id, asset_id)
                REFERENCES character_asset_manifests(workspace_id, asset_id) ON DELETE CASCADE
        )
        """
    )
    for table, related_column in (
        ("character_asset_dependencies", "dependent_asset_id"),
        ("character_asset_incompatibilities", "incompatible_asset_id"),
    ):
        op.execute(
            f"""
            CREATE TABLE {table} (
                workspace_id uuid REFERENCES workspaces(id) ON DELETE RESTRICT,
                asset_id uuid NOT NULL,
                {related_column} uuid NOT NULL
                    REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
                PRIMARY KEY (asset_id, {related_column}),
                FOREIGN KEY (workspace_id, asset_id)
                    REFERENCES character_asset_manifests(workspace_id, asset_id) ON DELETE CASCADE,
                CHECK (asset_id <> {related_column})
            )
            """
        )
    op.execute(
        "CREATE INDEX character_asset_manifests_category_idx "
        "ON character_asset_manifests(category, subcategory, status)"
    )
    op.execute(
        "CREATE INDEX character_asset_manifests_tags_idx "
        "ON character_asset_manifests USING gin(tags)"
    )
    op.execute(
        "CREATE INDEX character_asset_species_species_idx "
        "ON character_asset_species(species_id, asset_id)"
    )


def _create_character_tables() -> None:
    scalar_assets = (
        "type_id",
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
    )
    scalar_columns = ",\n".join(
        f"{column} uuid REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT"
        for column in scalar_assets
    )
    op.execute(
        f"""
        CREATE TABLE characters (
            character_id uuid PRIMARY KEY,
            workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
            project_id uuid NOT NULL,
            production_id uuid NOT NULL,
            display_name text NOT NULL CHECK (
                display_name = btrim(display_name) AND display_name <> ''
            ),
            role text NOT NULL CHECK (
                role IN ('Lead','Co-Lead','Supporting','Background','Creature','Custom')
            ),
            species_id uuid NOT NULL REFERENCES species(species_id) ON DELETE RESTRICT,
            {scalar_columns},
            compatibility_profile_id uuid NOT NULL
                REFERENCES compatibility_profiles(compatibility_profile_id) ON DELETE RESTRICT,
            pipeline_status text NOT NULL CHECK (
                pipeline_status IN (
                    'draft','validating','preview-pending','ready','blocked','archived'
                )
            ),
            version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (workspace_id, character_id),
            CHECK (updated_at >= created_at)
        )
        """
    )
    op.execute(
        "CREATE INDEX characters_project_idx "
        "ON characters(workspace_id, project_id, updated_at DESC, character_id)"
    )
    op.execute(
        "CREATE INDEX characters_production_idx "
        "ON characters(workspace_id, production_id, updated_at DESC, character_id)"
    )
    op.execute(
        "CREATE INDEX characters_species_idx ON characters(workspace_id, species_id)"
    )

    relation_tables = {
        "character_accessories": "accessory_id",
        "character_wardrobe": "wardrobe_asset_id",
        "character_materials": "material_id",
        "character_textures": "texture_id",
        "character_animations": "animation_id",
        "character_uploaded_assets": "asset_id",
        "character_generated_assets": "asset_id",
    }
    for table, asset_column in relation_tables.items():
        op.execute(
            f"""
            CREATE TABLE {table} (
                workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
                character_id uuid NOT NULL,
                {asset_column} uuid NOT NULL
                    REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
                ordinal integer NOT NULL CHECK (ordinal >= 0),
                PRIMARY KEY (workspace_id, character_id, {asset_column}),
                FOREIGN KEY (workspace_id, character_id)
                    REFERENCES characters(workspace_id, character_id) ON DELETE CASCADE
            )
            """
        )
        op.execute(
            f"CREATE INDEX {table}_character_idx "
            f"ON {table}(workspace_id, character_id, ordinal)"
        )

    op.execute(
        """
        CREATE TABLE character_downstream_dependencies (
            workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
            character_id uuid NOT NULL,
            stage text NOT NULL,
            status text NOT NULL CHECK (status IN ('valid','stale','blocked','pending')),
            invalidated_at timestamptz,
            reason text,
            PRIMARY KEY (workspace_id, character_id, stage),
            FOREIGN KEY (workspace_id, character_id)
                REFERENCES characters(workspace_id, character_id) ON DELETE CASCADE,
            CHECK (status <> 'stale' OR invalidated_at IS NOT NULL)
        )
        """
    )


def _seed_reference_data() -> None:
    categories = (
        "type",
        "identity",
        "face",
        "hair",
        "skin",
        "eyes",
        "beard",
        "body",
        "age-preset",
        "expression",
        "wardrobe",
        "accessory",
        "rig",
        "skeleton",
        "material",
        "texture",
        "animation",
        "voice",
        "preview",
    )
    for index, (key, name, _category, capabilities) in enumerate(SPECIES, start=1):
        profile_id = _uuid(0x40000001, index)
        op.execute(
            f"""
            INSERT INTO compatibility_profiles (
                compatibility_profile_id, key, name, required_capabilities,
                supported_categories, version
            ) VALUES (
                '{profile_id}', 'character.{key}.v1', '{name} Character Profile',
                {_sql_array(capabilities)}, {_sql_array(categories)}, 1
            )
            ON CONFLICT (key) DO UPDATE SET
                name = EXCLUDED.name,
                required_capabilities = EXCLUDED.required_capabilities,
                supported_categories = EXCLUDED.supported_categories,
                updated_at = now()
            """
        )

        base = (index - 1) * 10
        default_assets = (
            (_uuid(0x30000001, base + 1), f"{name} Identity Foundation", "identity"),
            (_uuid(0x30000002, base + 2), f"{name} Preview Placeholder", "preview"),
            (_uuid(0x30000003, base + 3), f"{name} Default Rig", "rig"),
            (_uuid(0x30000004, base + 4), f"{name} Default Skeleton", "skeleton"),
            (_uuid(0x30000005, base + 5), f"{name} Base Material", "material"),
            (_uuid(0x30000006, base + 6), f"{name} Base Texture", "texture"),
            (_uuid(0x30000007, base + 7), f"{name} Default Body", "body"),
        )
        for asset_id, asset_name, category in default_assets:
            op.execute(
                f"""
                INSERT INTO character_asset_manifests (
                    asset_id, workspace_id, name, category, subcategory,
                    thumbnail_reference, preview_reference, source, status,
                    tags, provenance, version
                ) VALUES (
                    '{asset_id}', NULL, '{asset_name}', '{category}', 'species-default',
                    'brain://assets/{asset_id}/thumbnail',
                    'brain://assets/{asset_id}/preview',
                    'development-seed', 'development-placeholder',
                    ARRAY['development-seed','{key}']::text[],
                    '{{"seed": true, "species_key": "{key}"}}'::jsonb, 1
                )
                ON CONFLICT (asset_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    category = EXCLUDED.category,
                    updated_at = now()
                """
            )

        species_id = _uuid(0x20000000 + index, index)
        op.execute(
            f"""
            INSERT INTO species (
                species_id, key, name, category, enabled, capabilities,
                supported_tabs, compatibility_profile_id, default_rig_id,
                default_skeleton_id, default_material_profile_id, default_body_id, version
            ) VALUES (
                '{species_id}', '{key}', '{name}', '{_category}', true,
                {_sql_array(capabilities)}, {_sql_array(SUPPORTED_TABS)}, '{profile_id}',
                '{default_assets[2][0]}', '{default_assets[3][0]}',
                '{default_assets[4][0]}', '{default_assets[6][0]}', 1
            )
            ON CONFLICT (key) DO UPDATE SET
                name = EXCLUDED.name,
                category = EXCLUDED.category,
                enabled = EXCLUDED.enabled,
                capabilities = EXCLUDED.capabilities,
                supported_tabs = EXCLUDED.supported_tabs,
                compatibility_profile_id = EXCLUDED.compatibility_profile_id,
                default_rig_id = EXCLUDED.default_rig_id,
                default_skeleton_id = EXCLUDED.default_skeleton_id,
                default_material_profile_id = EXCLUDED.default_material_profile_id,
                default_body_id = EXCLUDED.default_body_id,
                updated_at = now()
            """
        )
        for asset_id, _asset_name, _asset_category in default_assets:
            op.execute(
                f"""
                INSERT INTO character_asset_species (workspace_id, asset_id, species_id)
                VALUES (NULL, '{asset_id}', '{species_id}')
                ON CONFLICT (asset_id, species_id) DO NOTHING
                """
            )

    human_id = _uuid(0x20000001, 1)
    human_hair = _uuid(0x41000001, 1)
    shared_voice = _uuid(0x41000002, 1)
    op.execute(
        f"""
        INSERT INTO character_asset_manifests (
            asset_id, workspace_id, name, category, subcategory, source, status,
            tags, required_capabilities, provenance
        ) VALUES
        (
            '{human_hair}', NULL, 'Human Test Hair', 'hair', 'short',
            'development-seed', 'available', ARRAY['test-fixture','human-only']::text[],
            ARRAY['hair']::text[], '{{"seed": true}}'::jsonb
        ),
        (
            '{shared_voice}', NULL, 'Shared Character Voice', 'voice', 'neutral',
            'development-seed', 'available', ARRAY['test-fixture','shared']::text[],
            ARRAY['voice']::text[], '{{"seed": true}}'::jsonb
        )
        ON CONFLICT (asset_id) DO NOTHING
        """
    )
    op.execute(
        f"""
        INSERT INTO character_asset_species (workspace_id, asset_id, species_id)
        VALUES (NULL, '{human_hair}', '{human_id}')
        ON CONFLICT (asset_id, species_id) DO NOTHING
        """
    )
    for index in range(1, len(SPECIES) + 1):
        species_id = _uuid(0x20000000 + index, index)
        op.execute(
            f"""
            INSERT INTO character_asset_species (workspace_id, asset_id, species_id)
            VALUES (NULL, '{shared_voice}', '{species_id}')
            ON CONFLICT (asset_id, species_id) DO NOTHING
            """
        )

    for namespace, names, category, subcategory in (
        (
            0x32000001,
            ("Realistic", "Cartoon", "Anime", "Game", "Comic", "Stylized"),
            "identity",
            "visual-style",
        ),
        (
            0x32000002,
            (
                "Aviator",
                "Wayfarer",
                "Round",
                "Rectangle",
                "Vintage",
                "Clear Frame",
                "Sunglasses",
                "More",
            ),
            "accessory",
            "glasses",
        ),
    ):
        for asset_index, asset_name in enumerate(names, start=1):
            asset_id = _uuid(namespace, asset_index)
            capability = (
                "ARRAY['wears-accessories']::text[]"
                if category == "accessory"
                else "ARRAY[]::text[]"
            )
            op.execute(
                f"""
                INSERT INTO character_asset_manifests (
                    asset_id, workspace_id, name, category, subcategory,
                    thumbnail_reference, preview_reference, source, status,
                    tags, required_capabilities, provenance
                ) VALUES (
                    '{asset_id}', NULL, '{asset_name}', '{category}', '{subcategory}',
                    'brain://assets/{asset_id}/thumbnail',
                    'brain://assets/{asset_id}/preview',
                    'development-seed', 'development-placeholder',
                    ARRAY['development-seed','{subcategory}']::text[],
                    {capability}, '{{"seed": true}}'::jsonb
                )
                ON CONFLICT (asset_id) DO UPDATE SET
                    name = EXCLUDED.name, category = EXCLUDED.category,
                    subcategory = EXCLUDED.subcategory, updated_at = now()
                """
            )
            supported_species = (
                range(1, len(SPECIES) + 1)
                if category == "identity"
                else (1, 2, 3, 4, 8, 9)
            )
            for species_index in supported_species:
                species_id = _uuid(0x20000000 + species_index, species_index)
                op.execute(
                    f"""
                    INSERT INTO character_asset_species (
                        workspace_id, asset_id, species_id
                    ) VALUES (NULL, '{asset_id}', '{species_id}')
                    ON CONFLICT (asset_id, species_id) DO NOTHING
                    """
                )


def upgrade() -> None:
    _create_reference_tables()
    _seed_reference_data()
    _create_character_tables()

    for table in (
        "character_asset_manifests",
        "character_asset_species",
        "character_asset_types",
        "character_asset_dependencies",
        "character_asset_incompatibilities",
    ):
        _enable_workspace_rls(table, allow_global_reads=True)
    for table in (
        "characters",
        "character_accessories",
        "character_wardrobe",
        "character_materials",
        "character_textures",
        "character_animations",
        "character_uploaded_assets",
        "character_generated_assets",
        "character_downstream_dependencies",
    ):
        _enable_workspace_rls(table)

    op.execute(
        "GRANT SELECT ON compatibility_profiles, species TO nexkosmo_app"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE ON character_asset_manifests TO nexkosmo_app"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON "
        "character_asset_species, character_asset_types, "
        "character_asset_dependencies, character_asset_incompatibilities "
        "TO nexkosmo_app"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE ON characters TO nexkosmo_app"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON "
        "character_accessories, character_wardrobe, character_materials, "
        "character_textures, character_animations, character_uploaded_assets, "
        "character_generated_assets, character_downstream_dependencies "
        "TO nexkosmo_app"
    )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
