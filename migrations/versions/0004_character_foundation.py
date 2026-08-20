"""minimal Project-owned Character foundation

Revision ID: 0004_character_foundation
Revises: 0003_project_authority
"""

from alembic import op

revision = "0004_character_foundation"
down_revision = "0003_project_authority"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE characters (
          id uuid PRIMARY KEY,
          workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
          project_id uuid NOT NULL,
          identity_id uuid NOT NULL,
          created_by_principal_id uuid NOT NULL,
          display_name text NOT NULL CHECK (
            display_name = btrim(display_name)
            AND length(display_name) BETWEEN 1 AND 160
          ),
          role_label text CHECK (
            role_label IS NULL
            OR (
              role_label = btrim(role_label)
              AND length(role_label) BETWEEN 1 AND 160
            )
          ),
          version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
          created_at timestamptz NOT NULL,
          updated_at timestamptz NOT NULL,
          UNIQUE (workspace_id, id),
          UNIQUE (workspace_id, identity_id),
          CHECK (id = identity_id),
          CHECK (updated_at >= created_at),
          FOREIGN KEY (workspace_id, project_id)
            REFERENCES projects(workspace_id, id) ON DELETE RESTRICT,
          FOREIGN KEY (workspace_id, identity_id)
            REFERENCES identities(workspace_id, id) ON DELETE RESTRICT
        )
        """
    )
    op.execute(
        "CREATE INDEX characters_project_idx "
        "ON characters(workspace_id, project_id, created_at, id)"
    )

    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.guard_character_mutation()
        RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
        DECLARE
          project_record public.projects%ROWTYPE;
          identity_kind text;
        BEGIN
          SELECT * INTO project_record
          FROM public.projects
          WHERE id = NEW.project_id
          FOR SHARE;
          IF project_record.id IS NULL
             OR project_record.workspace_id <> NEW.workspace_id THEN
            RAISE EXCEPTION 'Character must belong to a Project in the same Workspace';
          END IF;

          SELECT kind INTO identity_kind
          FROM public.identities
          WHERE workspace_id = NEW.workspace_id AND id = NEW.identity_id;
          IF identity_kind IS DISTINCT FROM 'character' THEN
            RAISE EXCEPTION 'Character identity must use IdentityKind.CHARACTER';
          END IF;

          IF NOT nexkosmo_private.can_mutate_project(NEW.project_id) THEN
            RAISE EXCEPTION 'Mutable Project Character authority is required';
          END IF;

          IF TG_OP = 'INSERT' THEN
            IF NEW.id <> NEW.identity_id THEN
              RAISE EXCEPTION 'Character id and identity id must match';
            END IF;
            IF NEW.created_by_principal_id
               <> nexkosmo_private.current_principal_id() THEN
              RAISE EXCEPTION 'Character creation provenance must match the acting principal';
            END IF;
            IF NEW.version <> 1 THEN
              RAISE EXCEPTION 'Character begins at version 1';
            END IF;
            RETURN NEW;
          END IF;

          IF NEW.id <> OLD.id
             OR NEW.workspace_id <> OLD.workspace_id
             OR NEW.project_id <> OLD.project_id
             OR NEW.identity_id <> OLD.identity_id
             OR NEW.created_by_principal_id <> OLD.created_by_principal_id
             OR NEW.created_at <> OLD.created_at THEN
            RAISE EXCEPTION 'Character identity, ownership, and creation facts are immutable';
          END IF;
          IF NEW.version <> OLD.version + 1 THEN
            RAISE EXCEPTION 'Character version must increment exactly once';
          END IF;
          RETURN NEW;
        END $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER characters_mutation_guard
        BEFORE INSERT OR UPDATE ON characters
        FOR EACH ROW EXECUTE FUNCTION nexkosmo_private.guard_character_mutation()
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.prohibit_character_delete()
        RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
        BEGIN
          RAISE EXCEPTION 'Characters are retained canonical Project records';
        END $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER characters_delete_guard
        BEFORE DELETE ON characters
        FOR EACH ROW EXECUTE FUNCTION nexkosmo_private.prohibit_character_delete()
        """
    )
    op.execute(
        "REVOKE ALL ON FUNCTION nexkosmo_private.guard_character_mutation() FROM PUBLIC"
    )
    op.execute(
        "REVOKE ALL ON FUNCTION nexkosmo_private.prohibit_character_delete() FROM PUBLIC"
    )

    op.execute("ALTER TABLE characters ENABLE ROW LEVEL SECURITY")
    op.execute("ALTER TABLE characters FORCE ROW LEVEL SECURITY")
    op.execute(
        """
        CREATE POLICY characters_select ON characters FOR SELECT
        USING (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND nexkosmo_private.can_read_project(project_id)
        )
        """
    )
    op.execute(
        """
        CREATE POLICY characters_insert ON characters FOR INSERT
        WITH CHECK (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND created_by_principal_id = nexkosmo_private.current_principal_id()
          AND nexkosmo_private.can_mutate_project(project_id)
        )
        """
    )
    op.execute(
        """
        CREATE POLICY characters_update ON characters FOR UPDATE
        USING (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND nexkosmo_private.can_mutate_project(project_id)
        )
        WITH CHECK (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND nexkosmo_private.can_mutate_project(project_id)
        )
        """
    )

    op.execute("GRANT SELECT, INSERT, UPDATE ON characters TO nexkosmo_app")
    op.execute("REVOKE DELETE ON characters FROM nexkosmo_app")


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
