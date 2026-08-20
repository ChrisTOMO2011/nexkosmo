"""foundation reliability, audit reconciliation, and outbox dispatch

Revision ID: 0005_foundation_reliability
Revises: 0004_project_production
"""

from alembic import op

revision = "0005_foundation_reliability"
down_revision = "0004_project_production"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE audit_log ADD COLUMN deduplication_key text;
        CREATE UNIQUE INDEX audit_log_deduplication_idx
        ON audit_log(stream_key, deduplication_key)
        WHERE deduplication_key IS NOT NULL;

        ALTER TABLE outbox_events ADD COLUMN dead_lettered_at timestamptz;
        ALTER TABLE outbox_events ADD CONSTRAINT outbox_terminal_state_check
        CHECK (delivered_at IS NULL OR dead_lettered_at IS NULL);
        CREATE INDEX outbox_dispatch_pending_idx
        ON outbox_events(available_at, occurred_at, id)
        WHERE delivered_at IS NULL AND dead_lettered_at IS NULL;
        CREATE INDEX outbox_dispatch_aggregate_idx
        ON outbox_events(aggregate_id, aggregate_sequence)
        WHERE delivered_at IS NULL AND dead_lettered_at IS NULL;

        CREATE TABLE audit_delivery_queue (
            workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
            deduplication_key text NOT NULL,
            principal_id uuid,
            agent_id uuid,
            agent_kind text,
            action text NOT NULL,
            outcome text NOT NULL CHECK (outcome IN ('success','denial','failure')),
            resource_id uuid,
            details jsonb NOT NULL DEFAULT '{}'::jsonb,
            status text NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','delivered','dead-letter')),
            available_at timestamptz NOT NULL DEFAULT now(),
            lease_owner uuid,
            lease_expires_at timestamptz,
            attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
            max_attempts integer NOT NULL DEFAULT 8 CHECK (max_attempts > 0),
            last_error text,
            delivered_at timestamptz,
            dead_lettered_at timestamptz,
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (workspace_id, deduplication_key),
            CHECK (
                (status = 'delivered' AND delivered_at IS NOT NULL AND dead_lettered_at IS NULL)
                OR (status = 'dead-letter' AND dead_lettered_at IS NOT NULL AND delivered_at IS NULL)
                OR (status = 'pending' AND delivered_at IS NULL AND dead_lettered_at IS NULL)
            )
        );

        CREATE INDEX audit_delivery_pending_idx
        ON audit_delivery_queue(available_at, created_at, deduplication_key)
        WHERE status = 'pending';

        ALTER TABLE audit_delivery_queue ENABLE ROW LEVEL SECURITY;
        ALTER TABLE audit_delivery_queue FORCE ROW LEVEL SECURITY;
        CREATE POLICY audit_delivery_queue_workspace_isolation
        ON audit_delivery_queue
        USING (
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        WITH CHECK (
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        );

        GRANT SELECT, INSERT, UPDATE ON audit_delivery_queue TO nexkosmo_app;
        """
    )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
