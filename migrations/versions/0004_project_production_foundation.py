"""canonical project and production ownership foundation

Revision ID: 0004_project_production
Revises: 0003_character_pipeline
"""

from alembic import op

revision = "0004_project_production"
down_revision = "0003_character_pipeline"
branch_labels = None
depends_on = None

DEVELOPMENT_PRINCIPAL_ID = "00000000-0000-4000-8000-000000000002"


def _enable_workspace_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
    op.execute(
        f"""
        CREATE POLICY {table}_read_scope ON {table} FOR SELECT
        USING (
            workspace_id =
                nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        """
    )
    op.execute(
        f"""
        CREATE POLICY {table}_write_scope ON {table} FOR ALL
        USING (
            workspace_id =
                nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        WITH CHECK (
            workspace_id =
                nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        """
    )


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE projects (
            project_id uuid PRIMARY KEY,
            workspace_id uuid NOT NULL
                REFERENCES workspaces(id) ON DELETE RESTRICT,
            name text NOT NULL
                CHECK (name = btrim(name) AND name <> ''),
            description text NOT NULL DEFAULT ''
                CHECK (description = btrim(description)),
            status text NOT NULL
                CHECK (status IN ('active', 'archived')),
            owner_id uuid NOT NULL,
            version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (workspace_id, project_id),
            CHECK (updated_at >= created_at)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE project_members (
            workspace_id uuid NOT NULL
                REFERENCES workspaces(id) ON DELETE RESTRICT,
            project_id uuid NOT NULL,
            principal_id uuid NOT NULL,
            role text NOT NULL
                CHECK (role IN ('Owner', 'Admin', 'Editor', 'Viewer')),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            PRIMARY KEY (workspace_id, project_id, principal_id),
            FOREIGN KEY (workspace_id, project_id)
                REFERENCES projects(workspace_id, project_id) ON DELETE CASCADE,
            CHECK (updated_at >= created_at)
        )
        """
    )
    op.execute(
        """
        CREATE UNIQUE INDEX project_members_one_owner_idx
        ON project_members(workspace_id, project_id)
        WHERE role = 'Owner'
        """
    )
    op.execute(
        """
        CREATE TABLE productions (
            production_id uuid PRIMARY KEY,
            project_id uuid NOT NULL,
            workspace_id uuid NOT NULL
                REFERENCES workspaces(id) ON DELETE RESTRICT,
            name text NOT NULL
                CHECK (name = btrim(name) AND name <> ''),
            production_type text NOT NULL CHECK (
                production_type IN (
                    'Feature Film', 'Short Film', 'TV', 'Commercial',
                    'Music Video', 'Social', 'Animation', 'Documentary', 'Custom'
                )
            ),
            status text NOT NULL CHECK (
                status IN (
                    'draft', 'pre-production', 'production',
                    'post-production', 'completed', 'archived'
                )
            ),
            owner_id uuid NOT NULL,
            version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
            created_at timestamptz NOT NULL DEFAULT now(),
            updated_at timestamptz NOT NULL DEFAULT now(),
            UNIQUE (workspace_id, production_id),
            UNIQUE (workspace_id, production_id, project_id),
            FOREIGN KEY (workspace_id, project_id)
                REFERENCES projects(workspace_id, project_id) ON DELETE RESTRICT,
            CHECK (updated_at >= created_at)
        )
        """
    )

    op.execute(
        f"""
        INSERT INTO projects (
            project_id, workspace_id, name, description, status, owner_id,
            version, created_at, updated_at
        )
        SELECT
            character.project_id,
            character.workspace_id,
            'Imported Project ' || left(character.project_id::text, 8),
            'Backfilled from the canonical Character pipeline.',
            'active',
            COALESCE(
                (
                    SELECT membership.principal_id
                    FROM workspace_memberships membership
                    WHERE membership.workspace_id = character.workspace_id
                      AND (
                        membership.valid_to IS NULL
                        OR membership.valid_to > now()
                      )
                    ORDER BY membership.valid_from, membership.principal_id
                    LIMIT 1
                ),
                '{DEVELOPMENT_PRINCIPAL_ID}'::uuid
            ),
            1,
            min(character.created_at),
            max(character.updated_at)
        FROM characters character
        GROUP BY character.workspace_id, character.project_id
        """
    )
    op.execute(
        """
        INSERT INTO project_members (
            workspace_id, project_id, principal_id, role, created_at, updated_at
        )
        SELECT
            workspace_id, project_id, owner_id, 'Owner', created_at, updated_at
        FROM projects
        """
    )
    op.execute(
        """
        INSERT INTO productions (
            production_id, project_id, workspace_id, name, production_type,
            status, owner_id, version, created_at, updated_at
        )
        SELECT
            character.production_id,
            character.project_id,
            character.workspace_id,
            'Imported Production ' || left(character.production_id::text, 8),
            'Custom',
            'pre-production',
            project.owner_id,
            1,
            min(character.created_at),
            max(character.updated_at)
        FROM characters character
        JOIN projects project
          ON project.workspace_id = character.workspace_id
         AND project.project_id = character.project_id
        GROUP BY
            character.workspace_id,
            character.project_id,
            character.production_id,
            project.owner_id
        """
    )

    op.execute(
        """
        ALTER TABLE projects
        ADD CONSTRAINT projects_owner_membership_fk
        FOREIGN KEY (workspace_id, project_id, owner_id)
        REFERENCES project_members(workspace_id, project_id, principal_id)
        DEFERRABLE INITIALLY DEFERRED
        """
    )
    op.execute(
        """
        ALTER TABLE productions
        ADD CONSTRAINT productions_owner_membership_fk
        FOREIGN KEY (workspace_id, project_id, owner_id)
        REFERENCES project_members(workspace_id, project_id, principal_id)
        ON DELETE RESTRICT
        """
    )
    op.execute(
        """
        ALTER TABLE characters
        ADD CONSTRAINT characters_project_fk
        FOREIGN KEY (workspace_id, project_id)
        REFERENCES projects(workspace_id, project_id) ON DELETE RESTRICT
        """
    )
    op.execute(
        """
        ALTER TABLE characters
        ADD CONSTRAINT characters_production_fk
        FOREIGN KEY (workspace_id, production_id, project_id)
        REFERENCES productions(workspace_id, production_id, project_id)
        ON DELETE RESTRICT
        """
    )

    op.execute(
        "CREATE INDEX projects_workspace_status_idx "
        "ON projects(workspace_id, status, updated_at DESC, project_id)"
    )
    op.execute(
        "CREATE INDEX project_members_principal_idx "
        "ON project_members(workspace_id, principal_id, role, project_id)"
    )
    op.execute(
        "CREATE INDEX productions_project_status_idx "
        "ON productions(workspace_id, project_id, status, updated_at DESC)"
    )

    for table in ("projects", "project_members", "productions"):
        _enable_workspace_rls(table)

    op.execute(
        "GRANT SELECT, INSERT, UPDATE ON projects, productions TO nexkosmo_app"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE, DELETE ON project_members TO nexkosmo_app"
    )


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
