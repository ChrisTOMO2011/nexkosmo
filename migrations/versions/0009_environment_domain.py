"""add the canonical pre-production environment domain

Revision ID: 0009_environment_domain
Revises: 0008_accessory_categories
"""

from alembic import op

revision = "0009_environment_domain"
down_revision = "0008_accessory_categories"
branch_labels = None
depends_on = None


ENVIRONMENT_TYPES = (
    ("city", "City", ("urban-layout", "buildings", "traffic-ready")),
    ("forest", "Forest", ("terrain", "nature", "weather")),
    ("desert", "Desert", ("terrain", "weather", "atmosphere")),
    ("mountain", "Mountain", ("terrain", "nature", "weather")),
    ("beach", "Beach", ("terrain", "nature", "weather")),
    ("ocean", "Ocean", ("water", "weather", "atmosphere")),
    ("rural", "Rural", ("terrain", "nature", "buildings")),
    ("industrial", "Industrial", ("buildings", "practicals", "weather")),
    ("hospital", "Hospital", ("interior", "buildings", "practicals")),
    ("office", "Office", ("interior", "buildings", "practicals")),
    ("residential", "Residential", ("interior", "buildings", "nature")),
    ("warehouse", "Warehouse", ("interior", "buildings", "practicals")),
    ("castle", "Castle", ("terrain", "buildings", "nature")),
    ("fantasy", "Fantasy", ("terrain", "nature", "atmosphere")),
    ("sci-fi", "Sci-Fi", ("buildings", "practicals", "atmosphere")),
    ("space", "Space", ("virtual", "atmosphere", "vfx-ready")),
    ("custom", "Custom", ("custom",)),
)

COMMON_TABS = (
    "Identity",
    "Terrain",
    "Buildings",
    "Nature",
    "Weather",
    "Time",
    "Atmosphere",
    "Materials",
    "Details",
)


def _uuid(namespace: int, sequence: int) -> str:
    return f"{namespace:08x}-0000-4000-8000-{sequence:012x}"


def _array(values: tuple[str, ...]) -> str:
    quoted = ",".join("'" + value.replace("'", "''") + "'" for value in values)
    return f"ARRAY[{quoted}]::text[]"


def _enable_workspace_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY {table}_read_scope ON {table} FOR SELECT
        USING (workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid)
        """
    )
    op.execute(
        f"""
        CREATE POLICY {table}_write_scope ON {table} FOR ALL
        USING (workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid)
        WITH CHECK (workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid)
        """
    )


def _seed_asset(
    sequence: int,
    name: str,
    category: str,
    subcategory: str,
    type_keys: tuple[str, ...] = (),
    required_capabilities: tuple[str, ...] = (),
) -> None:
    asset_id = _uuid(0x44000000, sequence)
    op.execute(
        f"""
        INSERT INTO character_asset_manifests (
            asset_id, workspace_id, name, category, subcategory,
            thumbnail_reference, preview_reference, source, status, tags,
            required_capabilities, provenance, visibility, profile_metadata,
            domain, placeholder
        ) VALUES (
            '{asset_id}', NULL, '{name.replace("'", "''")}', '{category}', '{subcategory}',
            'brain://environment-assets/{asset_id}/thumbnail',
            'brain://environment-assets/{asset_id}/preview',
            'development-seed', 'development-placeholder',
            ARRAY['development-seed','phase-4a','environment']::text[],
            {_array(required_capabilities)},
            '{{"seed": true, "phase": "4A", "binary": false}}'::jsonb,
            'global', '{{"processing": "deferred"}}'::jsonb,
            'environment', true
        )
        ON CONFLICT (asset_id) DO UPDATE SET
            name = EXCLUDED.name,
            category = EXCLUDED.category,
            subcategory = EXCLUDED.subcategory,
            domain = 'environment',
            placeholder = true,
            updated_at = now()
        """
    )
    for key in type_keys:
        op.execute(
            f"""
            INSERT INTO environment_asset_types (workspace_id, asset_id, environment_type_id)
            SELECT NULL, '{asset_id}', environment_type_id
            FROM environment_types WHERE key = '{key}'
            ON CONFLICT (asset_id, environment_type_id) DO NOTHING
            """
        )


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE character_asset_manifests
            ADD COLUMN domain text NOT NULL DEFAULT 'character'
                CHECK (domain IN ('character', 'environment')),
            ADD COLUMN compatible_location_types text[] NOT NULL DEFAULT '{}',
            ADD COLUMN compatible_biomes text[] NOT NULL DEFAULT '{}',
            ADD COLUMN compatible_climates text[] NOT NULL DEFAULT '{}',
            ADD COLUMN compatible_times_of_day text[] NOT NULL DEFAULT '{}',
            ADD COLUMN compatible_weather_profile_ids uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN compatible_style_profile_ids uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN compatible_lighting_profile_ids uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN compatible_camera_profile_ids uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN incompatible_asset_ids uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN dependent_asset_ids uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN material_references uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN texture_references uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN placeholder boolean NOT NULL DEFAULT false;

        CREATE INDEX character_asset_manifests_domain_category_idx
            ON character_asset_manifests(domain, category, subcategory, status);

        CREATE TABLE environment_types (
            environment_type_id uuid PRIMARY KEY,
            key text NOT NULL UNIQUE CHECK (key = lower(key)),
            name text NOT NULL CHECK (btrim(name) <> ''),
            enabled boolean NOT NULL DEFAULT true,
            capabilities text[] NOT NULL DEFAULT '{}',
            supported_tabs text[] NOT NULL DEFAULT '{}',
            version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            CHECK (updated_at >= created_at)
        );

        CREATE TABLE environment_asset_types (
            workspace_id uuid REFERENCES workspaces(id) ON DELETE RESTRICT,
            asset_id uuid NOT NULL REFERENCES character_asset_manifests(asset_id) ON DELETE CASCADE,
            environment_type_id uuid NOT NULL
                REFERENCES environment_types(environment_type_id) ON DELETE RESTRICT,
            PRIMARY KEY (asset_id, environment_type_id)
        );

        CREATE TABLE environments (
            environment_id uuid PRIMARY KEY,
            workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
            project_id uuid NOT NULL,
            production_id uuid NOT NULL,
            display_name text NOT NULL
                CHECK (display_name = btrim(display_name) AND display_name <> ''),
            description text NOT NULL DEFAULT '' CHECK (description = btrim(description)),
            environment_type_id uuid NOT NULL
                REFERENCES environment_types(environment_type_id) ON DELETE RESTRICT,
            location_type text NOT NULL CHECK (location_type IN (
                'room','corridor','street','plaza','building','landscape','vehicle-interior',
                'spacecraft-interior','abstract-environment','custom'
            )),
            interior_exterior text NOT NULL CHECK (interior_exterior IN (
                'interior','exterior','mixed','virtual','studio-stage'
            )),
            biome text NOT NULL,
            climate_profile text NOT NULL,
            terrain_profile_id uuid
                REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            weather_profile_id uuid
                REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            time_of_day text NOT NULL,
            atmosphere_profile_id uuid
                REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            style_profile_id uuid REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            lighting_compatibility_profile_id uuid,
            camera_compatibility_profile_id uuid,
            audio_compatibility_profile_id uuid,
            vfx_compatibility_profile_id uuid,
            preview_asset_id uuid REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            scale integer NOT NULL DEFAULT 100 CHECK (scale BETWEEN 1 AND 1000),
            navigation_constraints text NOT NULL DEFAULT 'Standard character navigation',
            camera_access_constraints text NOT NULL DEFAULT 'Standard camera access',
            package_status text NOT NULL DEFAULT 'draft'
                CHECK (package_status IN ('draft','active','archived')),
            readiness_status text NOT NULL DEFAULT 'incomplete'
                CHECK (readiness_status IN (
                    'incomplete','invalid','ready-for-set'
                )),
            validation_issues jsonb NOT NULL DEFAULT '[]'::jsonb,
            version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (workspace_id, environment_id),
            FOREIGN KEY (workspace_id, project_id)
                REFERENCES projects(workspace_id, project_id) ON DELETE RESTRICT,
            FOREIGN KEY (workspace_id, production_id, project_id)
                REFERENCES productions(workspace_id, production_id, project_id) ON DELETE RESTRICT,
            CHECK (updated_at >= created_at)
        );

        CREATE TABLE environment_asset_selections (
            workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
            environment_id uuid NOT NULL,
            asset_id uuid NOT NULL
                REFERENCES character_asset_manifests(asset_id) ON DELETE RESTRICT,
            category text NOT NULL CHECK (category IN (
                'background','terrain','building','nature','practical','material','texture','detail'
            )),
            ordinal integer NOT NULL CHECK (ordinal >= 0),
            PRIMARY KEY (workspace_id, environment_id, category, asset_id),
            UNIQUE (workspace_id, environment_id, category, ordinal),
            FOREIGN KEY (workspace_id, environment_id)
                REFERENCES environments(workspace_id, environment_id) ON DELETE CASCADE
        );

        CREATE INDEX environments_project_idx
            ON environments(workspace_id, project_id, updated_at DESC);
        CREATE INDEX environments_production_idx
            ON environments(workspace_id, production_id, updated_at DESC);
        CREATE INDEX environment_asset_types_type_idx
            ON environment_asset_types(environment_type_id, asset_id);
        """
    )

    for index, (key, name, capabilities) in enumerate(ENVIRONMENT_TYPES, start=1):
        op.execute(
            f"""
            INSERT INTO environment_types (
                environment_type_id, key, name, capabilities, supported_tabs
            ) VALUES (
                '{_uuid(0x22000000, index)}', '{key}', '{name}',
                {_array(capabilities)}, {_array(COMMON_TABS)}
            ) ON CONFLICT (environment_type_id) DO NOTHING
            """
        )

    assets = (
        (1, "Cinematic Realism", "style-profile", "cinematic", (), ()),
        (2, "City Street", "terrain", "street", ("city",), ("urban-layout",)),
        (3, "Forest Floor", "terrain", "woodland", ("forest",), ("terrain",)),
        (4, "Desert Dunes", "terrain", "sand", ("desert",), ("terrain",)),
        (5, "Mountain Ridge", "terrain", "rock", ("mountain",), ("terrain",)),
        (6, "Beach Shore", "terrain", "coast", ("beach",), ("terrain",)),
        (7, "Rural Field", "terrain", "field", ("rural",), ("terrain",)),
        (8, "Office Interior", "building", "office", ("office",), ("buildings",)),
        (9, "Hospital Ward", "building", "hospital", ("hospital",), ("buildings",)),
        (10, "Warehouse Structure", "building", "warehouse", ("warehouse",), ("buildings",)),
        (11, "Castle Keep", "building", "castle", ("castle", "fantasy"), ("buildings",)),
        (12, "Residential Home", "building", "residential", ("residential",), ("buildings",)),
        (13, "Woodland Canopy", "nature", "trees", ("forest", "rural"), ("nature",)),
        (14, "Coastal Vegetation", "nature", "coastal", ("beach",), ("nature",)),
        (15, "Alpine Rocks", "nature", "alpine", ("mountain",), ("nature",)),
        (16, "Clear Skies", "weather-profile", "clear", (), ()),
        (17, "Rain", "weather-profile", "rain", (), ("weather",)),
        (18, "Snow", "weather-profile", "snow", ("mountain", "forest"), ("weather",)),
        (19, "Fog", "weather-profile", "fog", (), ()),
        (20, "Storm", "weather-profile", "storm", (), ()),
        (21, "Clean Air", "atmosphere-profile", "clean", (), ()),
        (22, "Cinematic Haze", "atmosphere-profile", "haze", (), ()),
        (23, "Industrial Smoke", "atmosphere-profile", "smoke", ("industrial",), ()),
        (24, "Concrete", "material", "masonry", (), ()),
        (25, "Weathered Timber", "material", "wood", (), ()),
        (26, "Wet Asphalt", "material", "road", ("city", "industrial"), ()),
        (27, "Distant Skyline", "background", "city", ("city",), ()),
        (28, "Mountain Horizon", "background", "mountain", ("mountain", "rural"), ()),
        (29, "Street Lamps", "practical", "lighting", ("city", "industrial"), ("practicals",)),
        (30, "Set Dressing", "detail", "dressing", (), ()),
    )
    for asset in assets:
        _seed_asset(*asset)

    _enable_workspace_rls("environments")
    _enable_workspace_rls("environment_asset_selections")
    op.execute(
        """
        ALTER TABLE environment_asset_types ENABLE ROW LEVEL SECURITY;
        ALTER TABLE environment_asset_types FORCE ROW LEVEL SECURITY;
        CREATE POLICY environment_asset_types_read_scope ON environment_asset_types FOR SELECT
        USING (
            workspace_id IS NULL OR
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        );
        CREATE POLICY environment_asset_types_write_scope ON environment_asset_types FOR ALL
        USING (workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid)
        WITH CHECK (
            workspace_id IS NOT NULL AND
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        );
        GRANT SELECT ON environment_types TO nexkosmo_app;
        GRANT SELECT, INSERT, UPDATE ON environments TO nexkosmo_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON environment_asset_selections TO nexkosmo_app;
        GRANT SELECT, INSERT, UPDATE, DELETE ON environment_asset_types TO nexkosmo_app;
        """
    )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
