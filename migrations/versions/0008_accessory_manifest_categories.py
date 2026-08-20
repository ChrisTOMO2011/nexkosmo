"""Correct canonical Character accessory manifest categories.

Revision ID: 0008_accessory_categories
Revises: 0007_character_brain_completion
"""

from alembic import op
from sqlalchemy import text

revision = "0008_accessory_categories"
down_revision = "0007_character_brain_completion"
branch_labels = None
depends_on = None

MORE_ACCESSORY_ID = "32000002-0000-4000-8000-000000000008"


def upgrade() -> None:
    op.get_bind().execute(
        text(
            """
            UPDATE character_asset_manifests
            SET subcategory = 'more',
                version = version + 1,
                updated_at = now()
            WHERE asset_id = CAST(:asset_id AS uuid)
              AND category = 'accessory'
              AND subcategory = 'glasses'
            """
        ),
        {"asset_id": MORE_ACCESSORY_ID},
    )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
