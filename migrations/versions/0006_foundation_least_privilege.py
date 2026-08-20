"""enforce the audit role boundary

Revision ID: 0006_foundation_least_privilege
Revises: 0005_foundation_reliability
"""

from alembic import op

revision = "0006_foundation_least_privilege"
down_revision = "0005_foundation_reliability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        REVOKE ALL PRIVILEGES ON TABLE audit_log FROM nexkosmo_app;
        REVOKE ALL PRIVILEGES ON TABLE audit_stream_heads FROM nexkosmo_app;
        """
    )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
