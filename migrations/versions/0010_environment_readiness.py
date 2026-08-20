"""extend canonical Environment readiness persistence

Revision ID: 0010_environment_readiness
Revises: 0009_environment_domain
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0010_environment_readiness"
down_revision: str | None = "0009_environment_domain"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE environments
            DROP CONSTRAINT environments_readiness_status_check;
        ALTER TABLE environments
            ADD CONSTRAINT environments_readiness_status_check
            CHECK (readiness_status IN (
                'incomplete','valid','processing_required','ready_for_scene','blocked'
            ));
        ALTER TABLE environments
            ADD COLUMN readiness_warnings jsonb NOT NULL DEFAULT '[]'::jsonb,
            ADD COLUMN missing_requirements text[] NOT NULL DEFAULT '{}',
            ADD COLUMN invalid_asset_ids uuid[] NOT NULL DEFAULT '{}',
            ADD COLUMN required_processing_jobs text[] NOT NULL DEFAULT '{}',
            ADD COLUMN readiness_validated_version bigint,
            ADD COLUMN readiness_validated_at timestamptz;
        """
    )


def downgrade() -> None:
    raise RuntimeError("Destructive downgrade is prohibited; restore from backup instead")
