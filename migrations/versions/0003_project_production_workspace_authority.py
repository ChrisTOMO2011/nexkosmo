"""project, production, and workspace authority foundation

Revision ID: 0003_project_authority
Revises: 0002_fix_tenant_join_tables
"""

from alembic import op

revision = "0003_project_authority"
down_revision = "0002_fix_tenant_join_tables"
branch_labels = None
depends_on = None


def _enable_forced_rls(table: str) -> None:
    op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
    op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")


def upgrade() -> None:
    # Fail closed. Existing authority data is inspected but never rewritten.
    op.execute(
        """
        DO $$
        BEGIN
          IF EXISTS (
            SELECT 1 FROM workspace_memberships
            WHERE role NOT IN ('owner', 'admin', 'member', 'viewer')
          ) THEN
            RAISE EXCEPTION '0003 preflight: unknown Workspace role';
          END IF;
          IF EXISTS (
            SELECT 1
            FROM workspace_memberships wm
            LEFT JOIN agents a
              ON a.workspace_id = wm.workspace_id
             AND a.identity_id = wm.agent_id
            WHERE a.identity_id IS NULL OR a.kind <> 'human'
          ) THEN
            RAISE EXCEPTION '0003 preflight: invalid same-Workspace human agent';
          END IF;
          IF EXISTS (
            SELECT 1
            FROM workspace_memberships left_membership
            JOIN workspace_memberships right_membership
              ON right_membership.workspace_id = left_membership.workspace_id
             AND right_membership.principal_id = left_membership.principal_id
             AND right_membership.ctid > left_membership.ctid
             AND tstzrange(
                   left_membership.valid_from,
                   left_membership.valid_to,
                   '[)'
                 ) && tstzrange(
                   right_membership.valid_from,
                   right_membership.valid_to,
                   '[)'
                 )
          ) THEN
            RAISE EXCEPTION '0003 preflight: overlapping Workspace membership periods';
          END IF;
          IF EXISTS (
            SELECT 1
            FROM workspace_memberships left_owner
            JOIN workspace_memberships right_owner
              ON right_owner.workspace_id = left_owner.workspace_id
             AND right_owner.ctid > left_owner.ctid
             AND left_owner.role = 'owner'
             AND right_owner.role = 'owner'
             AND tstzrange(left_owner.valid_from, left_owner.valid_to, '[)')
                 && tstzrange(right_owner.valid_from, right_owner.valid_to, '[)')
          ) THEN
            RAISE EXCEPTION '0003 preflight: conflicting Workspace Owner periods';
          END IF;
        END $$
        """
    )

    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    op.execute(
        "ALTER TABLE workspace_memberships ADD CONSTRAINT workspace_memberships_role_check "
        "CHECK (role IN ('owner','admin','member','viewer'))"
    )
    op.execute(
        "ALTER TABLE workspace_memberships ADD CONSTRAINT "
        "workspace_memberships_agent_workspace_fkey "
        "FOREIGN KEY (workspace_id, agent_id) "
        "REFERENCES agents(workspace_id, identity_id) ON DELETE RESTRICT"
    )
    op.execute(
        """
        ALTER TABLE workspace_memberships
        ADD CONSTRAINT workspace_memberships_principal_period_excl
        EXCLUDE USING gist (
          workspace_id WITH =,
          principal_id WITH =,
          tstzrange(valid_from, valid_to, '[)') WITH &&
        ) DEFERRABLE INITIALLY DEFERRED
        """
    )
    op.execute(
        """
        ALTER TABLE workspace_memberships
        ADD CONSTRAINT workspace_memberships_owner_period_excl
        EXCLUDE USING gist (
          workspace_id WITH =,
          tstzrange(valid_from, valid_to, '[)') WITH &&
        ) WHERE (role = 'owner')
        DEFERRABLE INITIALLY DEFERRED
        """
    )

    op.execute(
        """
        CREATE TABLE projects (
          id uuid PRIMARY KEY,
          workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
          identity_id uuid NOT NULL,
          context_id uuid NOT NULL,
          owner_principal_id uuid NOT NULL,
          created_by_principal_id uuid NOT NULL,
          name text NOT NULL CHECK (length(btrim(name)) BETWEEN 1 AND 200),
          lifecycle text NOT NULL CHECK (lifecycle IN ('active','archived')),
          version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
          created_at timestamptz NOT NULL,
          updated_at timestamptz NOT NULL,
          archived_at timestamptz,
          UNIQUE (workspace_id, id),
          UNIQUE (workspace_id, identity_id),
          UNIQUE (workspace_id, context_id),
          CHECK (id = identity_id),
          CHECK (
            (lifecycle = 'active' AND archived_at IS NULL)
            OR (lifecycle = 'archived' AND archived_at IS NOT NULL)
          ),
          FOREIGN KEY (workspace_id, identity_id)
            REFERENCES identities(workspace_id, id) ON DELETE RESTRICT,
          FOREIGN KEY (workspace_id, context_id)
            REFERENCES contexts(workspace_id, identity_id) ON DELETE RESTRICT
        )
        """
    )
    op.execute(
        "CREATE INDEX projects_workspace_lifecycle_idx "
        "ON projects(workspace_id, lifecycle, id)"
    )

    op.execute(
        """
        CREATE TABLE project_memberships (
          id uuid PRIMARY KEY,
          workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
          project_id uuid NOT NULL,
          principal_id uuid NOT NULL,
          role text NOT NULL CHECK (role IN ('owner','admin','editor','viewer')),
          valid_from timestamptz NOT NULL,
          valid_to timestamptz,
          granted_by_agent_id uuid NOT NULL,
          created_at timestamptz NOT NULL DEFAULT now(),
          CHECK (valid_to IS NULL OR valid_to > valid_from),
          UNIQUE (workspace_id, id),
          FOREIGN KEY (workspace_id, project_id)
            REFERENCES projects(workspace_id, id) ON DELETE RESTRICT,
          FOREIGN KEY (workspace_id, granted_by_agent_id)
            REFERENCES agents(workspace_id, identity_id) ON DELETE RESTRICT
        )
        """
    )
    op.execute(
        """
        ALTER TABLE project_memberships
        ADD CONSTRAINT project_memberships_principal_period_excl
        EXCLUDE USING gist (
          project_id WITH =,
          principal_id WITH =,
          tstzrange(valid_from, valid_to, '[)') WITH &&
        ) DEFERRABLE INITIALLY DEFERRED
        """
    )
    op.execute(
        """
        ALTER TABLE project_memberships
        ADD CONSTRAINT project_memberships_owner_period_excl
        EXCLUDE USING gist (
          project_id WITH =,
          tstzrange(valid_from, valid_to, '[)') WITH &&
        ) WHERE (role = 'owner')
        DEFERRABLE INITIALLY DEFERRED
        """
    )
    op.execute(
        "CREATE INDEX project_memberships_active_idx "
        "ON project_memberships(workspace_id, project_id, principal_id, role, valid_from, valid_to)"
    )

    op.execute(
        """
        CREATE TABLE productions (
          id uuid PRIMARY KEY,
          workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
          project_id uuid NOT NULL,
          name text NOT NULL CHECK (length(btrim(name)) BETWEEN 1 AND 200),
          state text NOT NULL CHECK (state IN ('planned','active','paused','completed','archived')),
          version bigint NOT NULL DEFAULT 1 CHECK (version > 0),
          created_at timestamptz NOT NULL,
          updated_at timestamptz NOT NULL,
          UNIQUE (workspace_id, id),
          FOREIGN KEY (workspace_id, project_id)
            REFERENCES projects(workspace_id, id) ON DELETE RESTRICT
        )
        """
    )
    op.execute(
        "CREATE INDEX productions_project_state_idx "
        "ON productions(workspace_id, project_id, state, id)"
    )

    op.execute(
        """
        CREATE TABLE project_authority_remediations (
          id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
          workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
          project_id uuid NOT NULL,
          owner_principal_id uuid NOT NULL,
          reason text NOT NULL CHECK (length(btrim(reason)) > 0),
          effective_at timestamptz NOT NULL,
          detected_at timestamptz NOT NULL DEFAULT clock_timestamp(),
          resolved_at timestamptz,
          resolved_by_principal_id uuid,
          resolved_by_agent_id uuid,
          resolution text,
          UNIQUE (workspace_id, id),
          FOREIGN KEY (workspace_id, project_id)
            REFERENCES projects(workspace_id, id) ON DELETE RESTRICT,
          CHECK (
            (resolved_at IS NULL AND resolved_by_principal_id IS NULL
             AND resolved_by_agent_id IS NULL AND resolution IS NULL)
            OR
            (resolved_at IS NOT NULL AND resolved_by_principal_id IS NOT NULL
             AND resolved_by_agent_id IS NOT NULL AND length(btrim(resolution)) > 0)
          )
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX project_authority_one_unresolved_idx "
        "ON project_authority_remediations(project_id) WHERE resolved_at IS NULL"
    )

    op.execute(
        """
        CREATE TABLE audit_delivery_queue (
          id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
          workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
          deduplication_key text NOT NULL,
          principal_id uuid NOT NULL,
          agent_id uuid NOT NULL,
          action text NOT NULL,
          outcome text NOT NULL CHECK (outcome IN ('success','denial','failure')),
          resource_id uuid,
          details jsonb NOT NULL DEFAULT '{}'::jsonb,
          created_at timestamptz NOT NULL DEFAULT clock_timestamp(),
          available_at timestamptz NOT NULL DEFAULT clock_timestamp(),
          lease_owner uuid,
          lease_expires_at timestamptz,
          delivered_at timestamptz,
          attempts integer NOT NULL DEFAULT 0 CHECK (attempts >= 0),
          last_error text,
          UNIQUE (workspace_id, deduplication_key),
          FOREIGN KEY (workspace_id, agent_id)
            REFERENCES agents(workspace_id, identity_id) ON DELETE RESTRICT
        )
        """
    )
    op.execute(
        "CREATE INDEX audit_delivery_pending_idx "
        "ON audit_delivery_queue(workspace_id, available_at, created_at) "
        "WHERE delivered_at IS NULL"
    )

    op.execute("CREATE SCHEMA IF NOT EXISTS nexkosmo_private")
    op.execute("REVOKE ALL ON SCHEMA nexkosmo_private FROM PUBLIC")
    op.execute("GRANT USAGE ON SCHEMA nexkosmo_private TO nexkosmo_app")

    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.current_workspace_id()
        RETURNS uuid LANGUAGE sql STABLE
        SET search_path = pg_catalog
        AS $$
          SELECT nullif(current_setting('app.workspace_id', true), '')::uuid
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.current_principal_id()
        RETURNS uuid LANGUAGE sql STABLE
        SET search_path = pg_catalog
        AS $$
          SELECT nullif(current_setting('app.principal_id', true), '')::uuid
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.current_agent_id()
        RETURNS uuid LANGUAGE sql STABLE
        SET search_path = pg_catalog
        AS $$
          SELECT nullif(current_setting('app.agent_id', true), '')::uuid
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.active_workspace_role(
          requested_workspace_id uuid,
          requested_principal_id uuid,
          requested_agent_id uuid,
          at_time timestamptz DEFAULT statement_timestamp()
        ) RETURNS text
        LANGUAGE sql STABLE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT wm.role
          FROM public.workspace_memberships wm
          JOIN public.agents a
            ON a.workspace_id = wm.workspace_id
           AND a.identity_id = wm.agent_id
          WHERE wm.workspace_id = requested_workspace_id
            AND wm.principal_id = requested_principal_id
            AND wm.agent_id = requested_agent_id
            AND a.kind = 'human'
            AND wm.valid_from <= at_time
            AND (wm.valid_to IS NULL OR at_time < wm.valid_to)
          LIMIT 1
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.active_human_workspace_role(
          requested_workspace_id uuid,
          requested_principal_id uuid,
          at_time timestamptz DEFAULT statement_timestamp()
        ) RETURNS text
        LANGUAGE sql STABLE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT wm.role
          FROM public.workspace_memberships wm
          JOIN public.agents a
            ON a.workspace_id = wm.workspace_id
           AND a.identity_id = wm.agent_id
          WHERE wm.workspace_id = requested_workspace_id
            AND wm.principal_id = requested_principal_id
            AND a.kind = 'human'
            AND wm.valid_from <= at_time
            AND (wm.valid_to IS NULL OR at_time < wm.valid_to)
          LIMIT 1
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.lock_active_workspace_role(
          requested_workspace_id uuid,
          requested_principal_id uuid,
          requested_agent_id uuid,
          at_time timestamptz
        ) RETURNS text
        LANGUAGE sql VOLATILE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT wm.role
          FROM public.workspace_memberships wm
          JOIN public.agents a
            ON a.workspace_id = wm.workspace_id
           AND a.identity_id = wm.agent_id
          WHERE wm.workspace_id = requested_workspace_id
            AND wm.principal_id = requested_principal_id
            AND wm.agent_id = requested_agent_id
            AND a.kind = 'human'
            AND wm.valid_from <= at_time
            AND (wm.valid_to IS NULL OR at_time < wm.valid_to)
          LIMIT 1
          FOR SHARE OF wm
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.lock_active_human_workspace_role(
          requested_workspace_id uuid,
          requested_principal_id uuid,
          at_time timestamptz
        ) RETURNS text
        LANGUAGE sql VOLATILE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT wm.role
          FROM public.workspace_memberships wm
          JOIN public.agents a
            ON a.workspace_id = wm.workspace_id
           AND a.identity_id = wm.agent_id
          WHERE wm.workspace_id = requested_workspace_id
            AND wm.principal_id = requested_principal_id
            AND a.kind = 'human'
            AND wm.valid_from <= at_time
            AND (wm.valid_to IS NULL OR at_time < wm.valid_to)
          LIMIT 1
          FOR SHARE OF wm
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.active_project_role(
          requested_project_id uuid,
          requested_principal_id uuid,
          at_time timestamptz DEFAULT statement_timestamp()
        ) RETURNS text
        LANGUAGE sql STABLE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT pm.role
          FROM public.project_memberships pm
          WHERE pm.project_id = requested_project_id
            AND pm.principal_id = requested_principal_id
            AND pm.valid_from <= at_time
            AND (pm.valid_to IS NULL OR at_time < pm.valid_to)
          ORDER BY CASE pm.role
            WHEN 'owner' THEN 1 WHEN 'admin' THEN 2
            WHEN 'editor' THEN 3 ELSE 4 END
          LIMIT 1
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.project_authority_locked(requested_project_id uuid)
        RETURNS boolean
        LANGUAGE sql STABLE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT COALESCE((
            SELECT
              nexkosmo_private.active_human_workspace_role(
                p.workspace_id, p.owner_principal_id, statement_timestamp()
              ) IS NULL
              OR nexkosmo_private.active_human_workspace_role(
                p.workspace_id, p.owner_principal_id, statement_timestamp()
              ) = 'viewer'
              OR EXISTS (
                SELECT 1 FROM public.project_authority_remediations remediation
                WHERE remediation.project_id = p.id
                  AND remediation.effective_at <= statement_timestamp()
                  AND remediation.resolved_at IS NULL
              )
            FROM public.projects p WHERE p.id = requested_project_id
          ), true)
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.workspace_can_create_project(requested_workspace_id uuid)
        RETURNS boolean
        LANGUAGE sql STABLE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT
            requested_workspace_id = nexkosmo_private.current_workspace_id()
            AND nexkosmo_private.active_workspace_role(
              requested_workspace_id,
              nexkosmo_private.current_principal_id(),
              nexkosmo_private.current_agent_id(),
              statement_timestamp()
            ) IN ('owner','admin')
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.can_read_project(requested_project_id uuid)
        RETURNS boolean
        LANGUAGE sql STABLE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT COALESCE((
            SELECT
              p.workspace_id = nexkosmo_private.current_workspace_id()
              AND nexkosmo_private.active_workspace_role(
                p.workspace_id,
                nexkosmo_private.current_principal_id(),
                nexkosmo_private.current_agent_id(),
                statement_timestamp()
              ) IS NOT NULL
              AND nexkosmo_private.active_project_role(
                p.id,
                nexkosmo_private.current_principal_id(),
                statement_timestamp()
              ) IS NOT NULL
            FROM public.projects p WHERE p.id = requested_project_id
          ), false)
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.can_mutate_project(requested_project_id uuid)
        RETURNS boolean
        LANGUAGE sql STABLE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT COALESCE((
            SELECT
              p.lifecycle = 'active'
              AND nexkosmo_private.can_read_project(p.id)
              AND NOT nexkosmo_private.project_authority_locked(p.id)
              AND nexkosmo_private.active_project_role(
                p.id,
                nexkosmo_private.current_principal_id(),
                statement_timestamp()
              ) IN ('owner','admin','editor')
            FROM public.projects p WHERE p.id = requested_project_id
          ), false)
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.project_owner_bootstrap_allowed(
          requested_project_id uuid,
          requested_principal_id uuid,
          requested_role text
        ) RETURNS boolean
        LANGUAGE sql STABLE SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
          SELECT COALESCE((
            SELECT requested_role = 'owner'
              AND p.workspace_id = nexkosmo_private.current_workspace_id()
              AND p.owner_principal_id = requested_principal_id
              AND p.created_by_principal_id = requested_principal_id
              AND requested_principal_id = nexkosmo_private.current_principal_id()
              AND NOT EXISTS (
                SELECT 1 FROM public.project_memberships pm
                WHERE pm.project_id = p.id
              )
            FROM public.projects p WHERE p.id = requested_project_id
          ), false)
        $$
        """
    )

    for function in (
        "current_workspace_id()",
        "current_principal_id()",
        "current_agent_id()",
        "active_workspace_role(uuid,uuid,uuid,timestamptz)",
        "active_human_workspace_role(uuid,uuid,timestamptz)",
        "lock_active_workspace_role(uuid,uuid,uuid,timestamptz)",
        "lock_active_human_workspace_role(uuid,uuid,timestamptz)",
        "active_project_role(uuid,uuid,timestamptz)",
        "project_authority_locked(uuid)",
        "workspace_can_create_project(uuid)",
        "can_read_project(uuid)",
        "can_mutate_project(uuid)",
        "project_owner_bootstrap_allowed(uuid,uuid,text)",
    ):
        op.execute(f"REVOKE ALL ON FUNCTION nexkosmo_private.{function} FROM PUBLIC")
        op.execute(f"GRANT EXECUTE ON FUNCTION nexkosmo_private.{function} TO nexkosmo_app")

    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.guard_project_membership()
        RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
        DECLARE
          actor_role text;
          target_workspace_role text;
          project_record public.projects%ROWTYPE;
          initial_owner boolean;
        BEGIN
          SELECT * INTO project_record FROM public.projects WHERE id = NEW.project_id;
          IF project_record.id IS NULL OR project_record.workspace_id <> NEW.workspace_id THEN
            RAISE EXCEPTION 'Project membership must remain in the Project Workspace';
          END IF;
          IF TG_OP = 'UPDATE' AND (
            NEW.id <> OLD.id OR NEW.workspace_id <> OLD.workspace_id
            OR NEW.project_id <> OLD.project_id OR NEW.principal_id <> OLD.principal_id
            OR NEW.role <> OLD.role OR NEW.valid_from <> OLD.valid_from
            OR NEW.granted_by_agent_id <> OLD.granted_by_agent_id
          ) THEN
            RAISE EXCEPTION 'Project membership identity and grant facts are immutable';
          END IF;
          IF nexkosmo_private.active_workspace_role(
               NEW.workspace_id,
               nexkosmo_private.current_principal_id(),
               nexkosmo_private.current_agent_id(),
               statement_timestamp()
             ) IS NULL THEN
            RAISE EXCEPTION 'Active human Workspace authority is required';
          END IF;
          target_workspace_role := nexkosmo_private.active_human_workspace_role(
            NEW.workspace_id, NEW.principal_id, statement_timestamp()
          );
          IF target_workspace_role IS NULL THEN
            RAISE EXCEPTION 'Project member must be an active human Workspace member';
          END IF;
          IF target_workspace_role = 'viewer' AND NEW.role <> 'viewer' THEN
            RAISE EXCEPTION 'Workspace Viewer may only receive Project Viewer';
          END IF;

          actor_role := nexkosmo_private.active_project_role(
            NEW.project_id, nexkosmo_private.current_principal_id(), statement_timestamp()
          );
          initial_owner := TG_OP = 'INSERT'
            AND NEW.role = 'owner'
            AND NEW.principal_id = project_record.owner_principal_id
            AND NEW.principal_id = project_record.created_by_principal_id
            AND NEW.principal_id = nexkosmo_private.current_principal_id()
            AND NOT EXISTS (
              SELECT 1 FROM public.project_memberships existing
              WHERE existing.project_id = NEW.project_id
            );

          IF NOT initial_owner THEN
            IF actor_role = 'owner' THEN
              NULL;
            ELSIF actor_role = 'admin' THEN
              IF TG_OP = 'UPDATE' AND OLD.role NOT IN ('editor','viewer') THEN
                RAISE EXCEPTION 'Project Admin may manage only Editor and Viewer membership';
              END IF;
              IF TG_OP = 'INSERT' AND NEW.role NOT IN ('editor','viewer') THEN
                RAISE EXCEPTION 'Project Admin may grant only Editor and Viewer membership';
              END IF;
            ELSE
              RAISE EXCEPTION 'Project Owner or bounded Admin authority is required';
            END IF;
          END IF;
          RETURN NEW;
        END $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER project_memberships_guard
        BEFORE INSERT OR UPDATE ON project_memberships
        FOR EACH ROW EXECUTE FUNCTION nexkosmo_private.guard_project_membership()
        """
    )

    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.guard_project_mutation()
        RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
        DECLARE actor_role text;
        BEGIN
          IF NEW.id <> OLD.id OR NEW.workspace_id <> OLD.workspace_id
             OR NEW.identity_id <> OLD.identity_id OR NEW.context_id <> OLD.context_id
             OR NEW.created_by_principal_id <> OLD.created_by_principal_id
             OR NEW.created_at <> OLD.created_at THEN
            RAISE EXCEPTION 'Project identity and creation facts are immutable';
          END IF;
          IF nexkosmo_private.project_authority_locked(OLD.id) THEN
            RAISE EXCEPTION 'Project authority remediation is required';
          END IF;
          actor_role := nexkosmo_private.active_project_role(
            OLD.id, nexkosmo_private.current_principal_id(), statement_timestamp()
          );
          IF NEW.version <> OLD.version + 1 THEN
            RAISE EXCEPTION 'Project version must increment exactly once';
          END IF;
          IF NEW.owner_principal_id <> OLD.owner_principal_id THEN
            IF actor_role <> 'owner'
               OR OLD.owner_principal_id <> nexkosmo_private.current_principal_id() THEN
              RAISE EXCEPTION 'Only the current Project Owner may transfer ownership';
            END IF;
          END IF;
          IF NEW.lifecycle <> OLD.lifecycle THEN
            IF actor_role <> 'owner' THEN
              RAISE EXCEPTION 'Only the Project Owner may archive or restore';
            END IF;
            IF NOT (
              (OLD.lifecycle = 'active' AND NEW.lifecycle = 'archived')
              OR (OLD.lifecycle = 'archived' AND NEW.lifecycle = 'active')
            ) THEN
              RAISE EXCEPTION 'Invalid Project lifecycle transition';
            END IF;
          END IF;
          IF OLD.lifecycle = 'archived' AND (
            NEW.lifecycle <> 'active'
            OR NEW.owner_principal_id <> OLD.owner_principal_id
            OR NEW.name <> OLD.name
          ) THEN
            RAISE EXCEPTION 'Archived Project is read-only except Owner restore';
          END IF;
          RETURN NEW;
        END $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER projects_mutation_guard
        BEFORE UPDATE ON projects
        FOR EACH ROW EXECUTE FUNCTION nexkosmo_private.guard_project_mutation()
        """
    )

    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.guard_production_mutation()
        RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
        DECLARE project_record public.projects%ROWTYPE;
        BEGIN
          SELECT * INTO project_record FROM public.projects WHERE id = NEW.project_id FOR SHARE;
          IF project_record.id IS NULL OR project_record.workspace_id <> NEW.workspace_id THEN
            RAISE EXCEPTION 'Production must belong to a Project in the same Workspace';
          END IF;
          IF project_record.lifecycle <> 'active'
             OR nexkosmo_private.project_authority_locked(project_record.id) THEN
            RAISE EXCEPTION 'Production is read-only while Project is archived or authority-locked';
          END IF;
          IF nexkosmo_private.active_project_role(
               project_record.id,
               nexkosmo_private.current_principal_id(),
               statement_timestamp()
             ) NOT IN ('owner','admin','editor') THEN
            RAISE EXCEPTION 'Project Editor, Admin, or Owner authority is required';
          END IF;
          IF TG_OP = 'INSERT' THEN
            IF NEW.state <> 'planned' OR NEW.version <> 1 THEN
              RAISE EXCEPTION 'Production begins planned at version 1';
            END IF;
            RETURN NEW;
          END IF;
          IF NEW.id <> OLD.id OR NEW.workspace_id <> OLD.workspace_id
             OR NEW.project_id <> OLD.project_id OR NEW.created_at <> OLD.created_at THEN
            RAISE EXCEPTION 'Production identity and ownership are immutable';
          END IF;
          IF OLD.state = 'archived' THEN
            RAISE EXCEPTION 'Archived Production is terminal';
          END IF;
          IF NEW.version <> OLD.version + 1 THEN
            RAISE EXCEPTION 'Production version must increment exactly once';
          END IF;
          IF NOT (
            (OLD.state = 'planned' AND NEW.state IN ('active','archived'))
            OR (OLD.state = 'active' AND NEW.state IN ('paused','completed','archived'))
            OR (OLD.state = 'paused' AND NEW.state IN ('active','archived'))
            OR (OLD.state = 'completed' AND NEW.state IN ('active','archived'))
          ) THEN
            RAISE EXCEPTION 'Invalid Production operational-state transition';
          END IF;
          RETURN NEW;
        END $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER productions_mutation_guard
        BEFORE INSERT OR UPDATE ON productions
        FOR EACH ROW EXECUTE FUNCTION nexkosmo_private.guard_production_mutation()
        """
    )

    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.assert_project_owner_integrity()
        RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
        DECLARE requested_project_id uuid;
        DECLARE project_record public.projects%ROWTYPE;
        DECLARE owner_count integer;
        DECLARE active_owner uuid;
        DECLARE workspace_role text;
        BEGIN
          IF TG_TABLE_NAME = 'projects' THEN
            requested_project_id := NEW.id;
          ELSE
            requested_project_id := NEW.project_id;
          END IF;
          SELECT * INTO project_record FROM public.projects WHERE id = requested_project_id;
          IF project_record.id IS NULL THEN RETURN NULL; END IF;
          SELECT count(*)
            INTO owner_count
          FROM public.project_memberships
          WHERE project_id = requested_project_id
            AND role = 'owner'
            AND valid_from <= statement_timestamp()
            AND (valid_to IS NULL OR statement_timestamp() < valid_to);
          SELECT principal_id INTO active_owner
          FROM public.project_memberships
          WHERE project_id = requested_project_id
            AND role = 'owner'
            AND valid_from <= statement_timestamp()
            AND (valid_to IS NULL OR statement_timestamp() < valid_to)
          LIMIT 1;
          IF owner_count <> 1 OR active_owner <> project_record.owner_principal_id THEN
            RAISE EXCEPTION 'Project must have exactly one matching active Owner';
          END IF;
          workspace_role := nexkosmo_private.active_human_workspace_role(
            project_record.workspace_id, active_owner, statement_timestamp()
          );
          IF workspace_role IS NULL OR workspace_role = 'viewer' THEN
            RAISE EXCEPTION 'Project Owner must be an active eligible human Workspace member';
          END IF;
          RETURN NULL;
        END $$
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER projects_owner_integrity
        AFTER INSERT OR UPDATE ON projects
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION nexkosmo_private.assert_project_owner_integrity()
        """
    )
    op.execute(
        """
        CREATE CONSTRAINT TRIGGER project_memberships_owner_integrity
        AFTER INSERT OR UPDATE ON project_memberships
        DEFERRABLE INITIALLY DEFERRED
        FOR EACH ROW EXECUTE FUNCTION nexkosmo_private.assert_project_owner_integrity()
        """
    )

    op.execute(
        """
        CREATE FUNCTION nexkosmo_private.record_owner_authority_remediation()
        RETURNS trigger LANGUAGE plpgsql SECURITY DEFINER
        SET search_path = pg_catalog, public
        AS $$
        DECLARE effective_time timestamptz;
        DECLARE affected_principal uuid;
        DECLARE affected_workspace uuid;
        BEGIN
          affected_principal := OLD.principal_id;
          affected_workspace := OLD.workspace_id;
          IF TG_OP = 'DELETE' THEN
            effective_time := statement_timestamp();
          ELSIF NEW.principal_id = OLD.principal_id
                AND NEW.role IN ('owner','admin','member')
                AND NEW.valid_to IS NOT DISTINCT FROM OLD.valid_to THEN
            RETURN NEW;
          ELSIF NEW.principal_id = OLD.principal_id
                AND NEW.role IN ('owner','admin','member')
                AND NEW.valid_to IS NOT NULL
                AND NEW.valid_to > statement_timestamp() THEN
            effective_time := NEW.valid_to;
          ELSE
            effective_time := statement_timestamp();
          END IF;
          INSERT INTO public.project_authority_remediations (
            workspace_id, project_id, owner_principal_id, reason, effective_at
          )
          SELECT p.workspace_id, p.id, p.owner_principal_id,
                 'workspace_owner_membership_revoked', effective_time
          FROM public.projects p
          WHERE p.workspace_id = affected_workspace
            AND p.owner_principal_id = affected_principal
          ON CONFLICT (project_id) WHERE resolved_at IS NULL DO NOTHING;
          IF TG_OP = 'DELETE' THEN RETURN OLD; END IF;
          RETURN NEW;
        END $$
        """
    )
    op.execute(
        """
        CREATE TRIGGER workspace_owner_remediation
        AFTER UPDATE OR DELETE ON workspace_memberships
        FOR EACH ROW EXECUTE FUNCTION nexkosmo_private.record_owner_authority_remediation()
        """
    )

    _enable_forced_rls("projects")
    _enable_forced_rls("project_memberships")
    _enable_forced_rls("productions")
    _enable_forced_rls("project_authority_remediations")
    _enable_forced_rls("audit_delivery_queue")

    op.execute(
        """
        CREATE POLICY projects_select ON projects FOR SELECT
        USING (nexkosmo_private.can_read_project(id))
        """
    )
    op.execute(
        """
        CREATE POLICY projects_insert ON projects FOR INSERT
        WITH CHECK (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND owner_principal_id = nexkosmo_private.current_principal_id()
          AND created_by_principal_id = nexkosmo_private.current_principal_id()
          AND nexkosmo_private.workspace_can_create_project(workspace_id)
        )
        """
    )
    op.execute(
        """
        CREATE POLICY projects_update ON projects FOR UPDATE
        USING (
          nexkosmo_private.can_read_project(id)
          AND NOT nexkosmo_private.project_authority_locked(id)
          AND nexkosmo_private.active_project_role(
            id, nexkosmo_private.current_principal_id(), statement_timestamp()
          ) IN ('owner','admin')
        )
        WITH CHECK (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND NOT nexkosmo_private.project_authority_locked(id)
        )
        """
    )
    op.execute(
        """
        CREATE POLICY project_memberships_select ON project_memberships FOR SELECT
        USING (nexkosmo_private.can_read_project(project_id))
        """
    )
    op.execute(
        """
        CREATE POLICY project_memberships_insert ON project_memberships FOR INSERT
        WITH CHECK (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND (
            (
              NOT nexkosmo_private.project_authority_locked(project_id)
              AND nexkosmo_private.active_project_role(
                project_id, nexkosmo_private.current_principal_id(), statement_timestamp()
              ) IN ('owner','admin')
            )
            OR nexkosmo_private.project_owner_bootstrap_allowed(
              project_id, principal_id, role
            )
          )
        )
        """
    )
    op.execute(
        """
        CREATE POLICY project_memberships_update ON project_memberships FOR UPDATE
        USING (
          nexkosmo_private.can_read_project(project_id)
          AND NOT nexkosmo_private.project_authority_locked(project_id)
          AND nexkosmo_private.active_project_role(
            project_id, nexkosmo_private.current_principal_id(), statement_timestamp()
          ) IN ('owner','admin')
        )
        WITH CHECK (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND NOT nexkosmo_private.project_authority_locked(project_id)
        )
        """
    )
    op.execute(
        """
        CREATE POLICY productions_select ON productions FOR SELECT
        USING (nexkosmo_private.can_read_project(project_id))
        """
    )
    op.execute(
        """
        CREATE POLICY productions_insert ON productions FOR INSERT
        WITH CHECK (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND nexkosmo_private.can_mutate_project(project_id)
        )
        """
    )
    op.execute(
        """
        CREATE POLICY productions_update ON productions FOR UPDATE
        USING (nexkosmo_private.can_mutate_project(project_id))
        WITH CHECK (
          workspace_id = nexkosmo_private.current_workspace_id()
          AND nexkosmo_private.can_mutate_project(project_id)
        )
        """
    )
    op.execute(
        """
        CREATE POLICY project_authority_remediations_select
        ON project_authority_remediations FOR SELECT
        USING (nexkosmo_private.can_read_project(project_id))
        """
    )
    op.execute(
        """
        CREATE POLICY audit_delivery_queue_workspace
        ON audit_delivery_queue
        USING (workspace_id = nexkosmo_private.current_workspace_id())
        WITH CHECK (workspace_id = nexkosmo_private.current_workspace_id())
        """
    )

    # Replace broad baseline mutation access with read-only Workspace membership access.
    op.execute("REVOKE INSERT, UPDATE, DELETE ON workspace_memberships FROM nexkosmo_app")
    op.execute("GRANT SELECT ON workspace_memberships TO nexkosmo_app")
    op.execute("GRANT SELECT, INSERT, UPDATE ON projects TO nexkosmo_app")
    op.execute("GRANT SELECT, INSERT, UPDATE ON project_memberships TO nexkosmo_app")
    op.execute("GRANT SELECT, INSERT, UPDATE ON productions TO nexkosmo_app")
    op.execute("GRANT SELECT ON project_authority_remediations TO nexkosmo_app")
    op.execute("GRANT SELECT, INSERT, UPDATE ON audit_delivery_queue TO nexkosmo_app")
    op.execute("REVOKE DELETE ON projects, project_memberships, productions FROM nexkosmo_app")


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
