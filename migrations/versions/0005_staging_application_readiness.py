"""staging application and delivery readiness

Revision ID: 0005_staging_readiness
Revises: 0004_character_foundation
"""

from alembic import op

revision = "0005_staging_readiness"
down_revision = "0004_character_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE audit_log ADD COLUMN delivery_key text")
    op.execute(
        "CREATE UNIQUE INDEX audit_log_delivery_key_idx "
        "ON audit_log(stream_key, delivery_key) WHERE delivery_key IS NOT NULL"
    )
    op.execute("ALTER TABLE audit_delivery_queue ADD COLUMN failed_at timestamptz")
    op.execute(
        "CREATE INDEX audit_delivery_failed_idx "
        "ON audit_delivery_queue(workspace_id, failed_at, created_at) "
        "WHERE delivered_at IS NULL AND failed_at IS NOT NULL"
    )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
