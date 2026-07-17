"""fix tenant-scoped join tables and decision targets

Revision ID: 0002_fix_tenant_join_tables
Revises: 0001_semantic_kernel
"""

from alembic import op

revision = "0002_fix_tenant_join_tables"
down_revision = "0001_semantic_kernel"
branch_labels = None
depends_on = None


def _enable_workspace_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY {table}_workspace_isolation ON {table}
        USING (workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid)
        WITH CHECK (workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid)
        """
    )


def upgrade() -> None:
    # Every tenant-owned relation carries its workspace so RLS also protects
    # relationship metadata, not just the parent records.
    op.execute("ALTER TABLE activities ADD CONSTRAINT activities_workspace_id_key UNIQUE (workspace_id, id)")
    op.execute("ALTER TABLE assertions ADD CONSTRAINT assertions_workspace_id_key UNIQUE (workspace_id, id)")
    op.execute("ALTER TABLE decisions ADD CONSTRAINT decisions_workspace_id_key UNIQUE (workspace_id, id)")

    op.execute("ALTER TABLE activity_participations ADD COLUMN workspace_id uuid")
    op.execute(
        "UPDATE activity_participations p SET workspace_id = a.workspace_id "
        "FROM activities a WHERE a.id = p.activity_id"
    )
    op.execute("ALTER TABLE activity_participations ALTER COLUMN workspace_id SET NOT NULL")
    op.execute(
        "ALTER TABLE activity_participations ADD CONSTRAINT activity_participations_workspace_fkey "
        "FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE RESTRICT"
    )
    op.execute(
        "ALTER TABLE activity_participations ADD CONSTRAINT activity_participations_activity_workspace_fkey "
        "FOREIGN KEY (workspace_id, activity_id) REFERENCES activities(workspace_id, id) ON DELETE RESTRICT"
    )
    op.execute(
        "ALTER TABLE activity_participations ADD CONSTRAINT activity_participations_identity_workspace_fkey "
        "FOREIGN KEY (workspace_id, identity_id) REFERENCES identities(workspace_id, id) ON DELETE RESTRICT"
    )

    # The original composite PK made both target columns non-null, contradicting
    # the one-target check. A surrogate key preserves the intended nullable pair.
    op.execute("ALTER TABLE decision_targets DROP CONSTRAINT decision_targets_pkey")
    op.execute("ALTER TABLE decision_targets ADD COLUMN id uuid DEFAULT gen_random_uuid()")
    op.execute("ALTER TABLE decision_targets ALTER COLUMN id SET NOT NULL")
    op.execute("ALTER TABLE decision_targets ADD PRIMARY KEY (id)")
    op.execute("ALTER TABLE decision_targets ADD COLUMN workspace_id uuid")
    op.execute(
        "UPDATE decision_targets t SET workspace_id = d.workspace_id "
        "FROM decisions d WHERE d.id = t.decision_id"
    )
    op.execute("ALTER TABLE decision_targets ALTER COLUMN workspace_id SET NOT NULL")
    op.execute(
        "ALTER TABLE decision_targets ADD CONSTRAINT decision_targets_workspace_fkey "
        "FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE RESTRICT"
    )
    op.execute(
        "ALTER TABLE decision_targets ADD CONSTRAINT decision_targets_decision_workspace_fkey "
        "FOREIGN KEY (workspace_id, decision_id) REFERENCES decisions(workspace_id, id) ON DELETE RESTRICT"
    )
    op.execute(
        "ALTER TABLE decision_targets ADD CONSTRAINT decision_targets_identity_workspace_fkey "
        "FOREIGN KEY (workspace_id, target_identity_id) REFERENCES identities(workspace_id, id) ON DELETE RESTRICT"
    )
    op.execute(
        "ALTER TABLE decision_targets ADD CONSTRAINT decision_targets_assertion_workspace_fkey "
        "FOREIGN KEY (workspace_id, target_assertion_id) REFERENCES assertions(workspace_id, id) ON DELETE RESTRICT"
    )

    op.execute("ALTER TABLE decision_basis ADD COLUMN workspace_id uuid")
    op.execute(
        "UPDATE decision_basis b SET workspace_id = d.workspace_id "
        "FROM decisions d WHERE d.id = b.decision_id"
    )
    op.execute("ALTER TABLE decision_basis ALTER COLUMN workspace_id SET NOT NULL")
    op.execute(
        "ALTER TABLE decision_basis ADD CONSTRAINT decision_basis_workspace_fkey "
        "FOREIGN KEY (workspace_id) REFERENCES workspaces(id) ON DELETE RESTRICT"
    )
    op.execute(
        "ALTER TABLE decision_basis ADD CONSTRAINT decision_basis_decision_workspace_fkey "
        "FOREIGN KEY (workspace_id, decision_id) REFERENCES decisions(workspace_id, id) ON DELETE RESTRICT"
    )

    for table in ("activity_participations", "decision_targets", "decision_basis"):
        _enable_workspace_rls(table)

    # Registry entries may be global (workspace_id IS NULL); the application may
    # read them but must not create or modify globally-scoped definitions.
    op.execute("ALTER TABLE registry_entries ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE registry_entries FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY registry_entries_read_scope ON registry_entries FOR SELECT
        USING (
            workspace_id IS NULL
            OR workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        """
    )
    op.execute("REVOKE ALL ON workspaces, registry_entries FROM nexkosmo_app")
    op.execute("GRANT SELECT ON registry_entries TO nexkosmo_app")


def downgrade() -> None:
    raise RuntimeError("Destructive downgrade is prohibited. Use a forward migration or rehearsed restore.")
