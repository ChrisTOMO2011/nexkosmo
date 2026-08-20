"""add the canonical Forest structure acceptance asset

Revision ID: 0011_environment_forest
Revises: 0010_environment_readiness
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0011_environment_forest"
down_revision: str | None = "0010_environment_readiness"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

FOREST_TYPE_ID = "22000000-0000-4000-8000-000000000002"
WOODLAND_CABIN_ID = "44000000-0000-4000-8000-00000000001f"


def upgrade() -> None:
    op.execute(
        f"""
        UPDATE environment_types
        SET capabilities = ARRAY(
                SELECT DISTINCT capability
                FROM unnest(capabilities || ARRAY['buildings']::text[]) AS capability
                ORDER BY capability
            ),
            version = version + 1,
            updated_at = now()
        WHERE environment_type_id = '{FOREST_TYPE_ID}'
          AND NOT capabilities @> ARRAY['buildings']::text[];

        INSERT INTO character_asset_manifests (
            asset_id, workspace_id, name, category, subcategory,
            thumbnail_reference, preview_reference, source, status, tags,
            required_capabilities, provenance, visibility, profile_metadata,
            domain, placeholder
        ) VALUES (
            '{WOODLAND_CABIN_ID}', NULL, 'Woodland Cabin', 'building', 'cabin',
            'brain://environment-assets/{WOODLAND_CABIN_ID}/thumbnail',
            'brain://environment-assets/{WOODLAND_CABIN_ID}/preview',
            'development-seed', 'development-placeholder',
            ARRAY['development-seed','phase-4a','environment']::text[],
            ARRAY['buildings']::text[],
            '{{"seed": true, "phase": "4A", "binary": false}}'::jsonb,
            'global', '{{"processing": "deferred"}}'::jsonb,
            'environment', true
        ) ON CONFLICT (asset_id) DO UPDATE SET
            name = EXCLUDED.name,
            category = EXCLUDED.category,
            subcategory = EXCLUDED.subcategory,
            required_capabilities = EXCLUDED.required_capabilities,
            domain = 'environment',
            placeholder = true,
            updated_at = now();

        INSERT INTO environment_asset_types (
            workspace_id, asset_id, environment_type_id
        ) VALUES (NULL, '{WOODLAND_CABIN_ID}', '{FOREST_TYPE_ID}')
        ON CONFLICT (asset_id, environment_type_id) DO NOTHING;
        """
    )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
