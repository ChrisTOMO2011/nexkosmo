"""semantic kernel v1 foundation

Revision ID: 0001_semantic_kernel
Revises:
"""

from alembic import op

revision = "0001_semantic_kernel"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    op.execute("""
    CREATE TABLE workspaces (
        id uuid PRIMARY KEY,
        canonical_key text NOT NULL UNIQUE,
        created_at timestamptz NOT NULL DEFAULT now()
    )
    """)

    op.execute("""
    CREATE TABLE identities (
        id uuid PRIMARY KEY,
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        kind text NOT NULL,
        canonical_key text NOT NULL,
        revision bigint NOT NULL DEFAULT 1 CHECK (revision > 0),
        created_at timestamptz NOT NULL DEFAULT now(),
        retired_at timestamptz,
        UNIQUE (workspace_id, canonical_key),
        UNIQUE (workspace_id, id)
    )
    """)

    op.execute("""
    CREATE TABLE agents (
        identity_id uuid PRIMARY KEY REFERENCES identities(id) ON DELETE RESTRICT,
        workspace_id uuid NOT NULL,
        kind text NOT NULL CHECK (kind IN ('human','ai','service','organization')),
        display_name text NOT NULL,
        UNIQUE (workspace_id, identity_id),
        FOREIGN KEY (workspace_id, identity_id)
            REFERENCES identities(workspace_id, id) ON DELETE RESTRICT
    )
    """)

    op.execute("""
    CREATE TABLE workspace_memberships (
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        principal_id uuid NOT NULL,
        agent_id uuid NOT NULL REFERENCES agents(identity_id) ON DELETE RESTRICT,
        role text NOT NULL,
        valid_from timestamptz NOT NULL,
        valid_to timestamptz,
        PRIMARY KEY (workspace_id, principal_id, agent_id, role, valid_from),
        CHECK (valid_to IS NULL OR valid_to > valid_from)
    )
    """)

    op.execute("""
    CREATE TABLE contexts (
        identity_id uuid PRIMARY KEY REFERENCES identities(id) ON DELETE RESTRICT,
        workspace_id uuid NOT NULL,
        kind text NOT NULL,
        parent_context_id uuid REFERENCES contexts(identity_id) ON DELETE RESTRICT,
        created_at timestamptz NOT NULL DEFAULT now(),
        UNIQUE (workspace_id, identity_id),
        FOREIGN KEY (workspace_id, identity_id)
            REFERENCES identities(workspace_id, id) ON DELETE RESTRICT
    )
    """)

    op.execute("""
    CREATE TABLE registry_entries (
        id uuid PRIMARY KEY,
        workspace_id uuid REFERENCES workspaces(id) ON DELETE RESTRICT,
        namespace text NOT NULL,
        key text NOT NULL,
        version integer NOT NULL CHECK (version > 0),
        definition jsonb NOT NULL,
        status text NOT NULL CHECK (status IN ('active','deprecated','retired')),
        created_by uuid NOT NULL REFERENCES agents(identity_id) ON DELETE RESTRICT,
        created_at timestamptz NOT NULL DEFAULT now(),
        UNIQUE NULLS NOT DISTINCT (workspace_id, namespace, key, version)
    )
    """)

    op.execute("""
    CREATE TABLE assertions (
        id uuid PRIMARY KEY,
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        subject_id uuid NOT NULL,
        predicate_namespace text NOT NULL DEFAULT 'kernel',
        predicate_key text NOT NULL,
        predicate_version integer NOT NULL DEFAULT 1,
        object_kind text NOT NULL CHECK (object_kind IN ('identity','literal')),
        object_identity_id uuid,
        object_value jsonb,
        context_id uuid NOT NULL,
        asserted_by uuid NOT NULL,
        epistemic_status text NOT NULL,
        valid_from timestamptz,
        valid_to timestamptz,
        recorded_at timestamptz NOT NULL DEFAULT now(),
        supersedes_id uuid REFERENCES assertions(id) ON DELETE RESTRICT,
        CHECK (
            (object_kind='identity' AND object_identity_id IS NOT NULL AND object_value IS NULL)
            OR
            (object_kind='literal' AND object_identity_id IS NULL AND object_value IS NOT NULL)
        ),
        CHECK (valid_to IS NULL OR valid_from IS NULL OR valid_to > valid_from),
        FOREIGN KEY (workspace_id, subject_id)
            REFERENCES identities(workspace_id, id) ON DELETE RESTRICT,
        FOREIGN KEY (workspace_id, context_id)
            REFERENCES contexts(workspace_id, identity_id) ON DELETE RESTRICT,
        FOREIGN KEY (workspace_id, asserted_by)
            REFERENCES agents(workspace_id, identity_id) ON DELETE RESTRICT,
        FOREIGN KEY (workspace_id, object_identity_id)
            REFERENCES identities(workspace_id, id) ON DELETE RESTRICT
    )
    """)
    op.execute(
        "CREATE INDEX assertions_subject_context_idx "
        "ON assertions(workspace_id, subject_id, context_id, recorded_at, id)"
    )
    op.execute(
        "CREATE INDEX assertions_predicate_idx "
        "ON assertions(workspace_id, predicate_namespace, predicate_key, predicate_version)"
    )

    op.execute("""
    CREATE TABLE evidence_links (
        id uuid PRIMARY KEY,
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        assertion_id uuid NOT NULL REFERENCES assertions(id) ON DELETE RESTRICT,
        evidence_identity_id uuid NOT NULL REFERENCES identities(id) ON DELETE RESTRICT,
        relation text NOT NULL CHECK (
            relation IN ('supports','contradicts','qualifies','corroborates')
        ),
        recorded_by uuid NOT NULL REFERENCES agents(identity_id) ON DELETE RESTRICT,
        recorded_at timestamptz NOT NULL DEFAULT now(),
        UNIQUE (assertion_id, evidence_identity_id, relation)
    )
    """)

    op.execute("""
    CREATE TABLE activities (
        id uuid PRIMARY KEY,
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        activity_type text NOT NULL,
        performed_by uuid NOT NULL,
        context_id uuid NOT NULL,
        started_at timestamptz NOT NULL,
        ended_at timestamptz,
        attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
        CHECK (ended_at IS NULL OR ended_at >= started_at),
        FOREIGN KEY (workspace_id, performed_by)
            REFERENCES agents(workspace_id, identity_id) ON DELETE RESTRICT,
        FOREIGN KEY (workspace_id, context_id)
            REFERENCES contexts(workspace_id, identity_id) ON DELETE RESTRICT
    )
    """)

    op.execute("""
    CREATE TABLE activity_participations (
        activity_id uuid NOT NULL REFERENCES activities(id) ON DELETE RESTRICT,
        identity_id uuid NOT NULL REFERENCES identities(id) ON DELETE RESTRICT,
        role text NOT NULL,
        ordinal integer,
        PRIMARY KEY(activity_id, identity_id, role)
    )
    """)

    op.execute("""
    CREATE TABLE policies (
        id uuid PRIMARY KEY,
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        policy_type text NOT NULL,
        action text NOT NULL,
        effect text NOT NULL CHECK (effect IN ('permit','prohibit','duty')),
        subject_agent_id uuid NOT NULL,
        resource_identity_id uuid NOT NULL,
        context_id uuid NOT NULL,
        purpose text NOT NULL,
        valid_from timestamptz NOT NULL,
        valid_to timestamptz,
        constraints jsonb NOT NULL DEFAULT '{}'::jsonb,
        issued_by uuid NOT NULL,
        issued_at timestamptz NOT NULL DEFAULT now(),
        withdrawn_by_decision_id uuid,
        CHECK (valid_to IS NULL OR valid_to > valid_from),
        FOREIGN KEY (workspace_id, subject_agent_id)
            REFERENCES agents(workspace_id, identity_id) ON DELETE RESTRICT,
        FOREIGN KEY (workspace_id, resource_identity_id)
            REFERENCES identities(workspace_id, id) ON DELETE RESTRICT,
        FOREIGN KEY (workspace_id, context_id)
            REFERENCES contexts(workspace_id, identity_id) ON DELETE RESTRICT,
        FOREIGN KEY (workspace_id, issued_by)
            REFERENCES agents(workspace_id, identity_id) ON DELETE RESTRICT
    )
    """)

    op.execute("""
    CREATE TABLE decisions (
        id uuid PRIMARY KEY,
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        decision_type text NOT NULL,
        outcome text NOT NULL CHECK (outcome IN ('accept','reject','escalate','withdraw')),
        decided_by uuid NOT NULL,
        context_id uuid NOT NULL,
        reasons jsonb NOT NULL,
        alternatives jsonb NOT NULL DEFAULT '[]'::jsonb,
        decided_at timestamptz NOT NULL,
        FOREIGN KEY (workspace_id, decided_by)
            REFERENCES agents(workspace_id, identity_id) ON DELETE RESTRICT,
        FOREIGN KEY (workspace_id, context_id)
            REFERENCES contexts(workspace_id, identity_id) ON DELETE RESTRICT
    )
    """)

    op.execute("""
    CREATE TABLE decision_targets (
        decision_id uuid NOT NULL REFERENCES decisions(id) ON DELETE RESTRICT,
        target_identity_id uuid REFERENCES identities(id) ON DELETE RESTRICT,
        target_assertion_id uuid REFERENCES assertions(id) ON DELETE RESTRICT,
        PRIMARY KEY(decision_id, target_identity_id, target_assertion_id),
        CHECK ((target_identity_id IS NOT NULL)::int + (target_assertion_id IS NOT NULL)::int = 1)
    )
    """)

    op.execute("""
    CREATE TABLE decision_basis (
        decision_id uuid NOT NULL REFERENCES decisions(id) ON DELETE RESTRICT,
        basis_kind text NOT NULL CHECK (basis_kind IN ('policy','evidence','assertion','activity')),
        basis_id uuid NOT NULL,
        PRIMARY KEY(decision_id, basis_kind, basis_id)
    )
    """)

    op.execute("""
    CREATE TABLE idempotency_records (
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        idempotency_key text NOT NULL,
        request_hash text NOT NULL,
        status text NOT NULL CHECK (status IN ('processing','completed','failed')),
        owner_token uuid NOT NULL,
        lease_expires_at timestamptz NOT NULL,
        response jsonb,
        error_code text,
        created_at timestamptz NOT NULL DEFAULT now(),
        updated_at timestamptz NOT NULL DEFAULT now(),
        PRIMARY KEY(workspace_id, idempotency_key)
    )
    """)

    op.execute("""
    CREATE TABLE outbox_events (
        id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
        workspace_id uuid NOT NULL REFERENCES workspaces(id) ON DELETE RESTRICT,
        aggregate_id uuid NOT NULL,
        aggregate_sequence bigint NOT NULL CHECK (aggregate_sequence > 0),
        event_type text NOT NULL,
        event_version integer NOT NULL CHECK (event_version > 0),
        payload jsonb NOT NULL,
        occurred_at timestamptz NOT NULL DEFAULT now(),
        available_at timestamptz NOT NULL DEFAULT now(),
        lease_owner uuid,
        lease_expires_at timestamptz,
        delivered_at timestamptz,
        attempts integer NOT NULL DEFAULT 0,
        last_error text,
        UNIQUE(aggregate_id, aggregate_sequence)
    )
    """)

    op.execute("""
    CREATE TABLE consumer_inbox (
        consumer_name text NOT NULL,
        event_id uuid NOT NULL,
        event_type text NOT NULL,
        event_version integer NOT NULL,
        received_at timestamptz NOT NULL DEFAULT now(),
        processed_at timestamptz,
        result_hash text,
        PRIMARY KEY(consumer_name, event_id)
    )
    """)

    # Audit is intentionally not FK-coupled to mutable business records.
    op.execute("""
    CREATE TABLE audit_stream_heads (
        stream_key text PRIMARY KEY,
        last_sequence bigint NOT NULL,
        last_hash text NOT NULL
    )
    """)
    op.execute("""
    CREATE TABLE audit_log (
        stream_key text NOT NULL,
        sequence bigint NOT NULL,
        recorded_at timestamptz NOT NULL DEFAULT clock_timestamp(),
        workspace_id uuid,
        principal_id uuid,
        agent_id uuid,
        action text NOT NULL,
        outcome text NOT NULL CHECK (outcome IN ('success','denial','failure')),
        resource_id uuid,
        details jsonb NOT NULL DEFAULT '{}'::jsonb,
        previous_hash text NOT NULL,
        entry_hash text NOT NULL,
        PRIMARY KEY(stream_key, sequence),
        UNIQUE(entry_hash)
    )
    """)

    # Append-only protection.
    op.execute("""
    CREATE FUNCTION kernel_forbid_mutation() RETURNS trigger LANGUAGE plpgsql AS $$
    BEGIN
      RAISE EXCEPTION 'permanent kernel records are append-only';
    END $$;
    """)
    for table in [
        "assertions",
        "evidence_links",
        "activities",
        "activity_participations",
        "decisions",
        "decision_targets",
        "decision_basis",
        "audit_log",
    ]:
        op.execute(f"""
        CREATE TRIGGER {table}_immutable
        BEFORE UPDATE OR DELETE ON {table}
        FOR EACH ROW EXECUTE FUNCTION kernel_forbid_mutation()
        """)

    # Tenant isolation: FORCE RLS and transaction-local app.workspace_id.
    tenant_tables = [
        "identities",
        "agents",
        "workspace_memberships",
        "contexts",
        "assertions",
        "evidence_links",
        "activities",
        "policies",
        "decisions",
        "idempotency_records",
        "outbox_events",
    ]
    for table in tenant_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY")
        op.execute(f"""
        CREATE POLICY {table}_workspace_isolation ON {table}
        USING (
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        WITH CHECK (
            workspace_id = nullif(current_setting('app.workspace_id', true), '')::uuid
        )
        """)

    # Owner retains migration access; app/audit roles get least privilege.
    op.execute("GRANT USAGE ON SCHEMA public TO nexkosmo_app")
    op.execute("GRANT SELECT, INSERT ON ALL TABLES IN SCHEMA public TO nexkosmo_app")
    op.execute(
        "REVOKE UPDATE, DELETE ON assertions, evidence_links, activities, "
        "activity_participations, decisions, decision_targets, decision_basis "
        "FROM nexkosmo_app"
    )
    op.execute(
        "GRANT SELECT, INSERT, UPDATE ON idempotency_records, outbox_events, "
        "consumer_inbox TO nexkosmo_app"
    )
    op.execute("GRANT SELECT, INSERT, UPDATE ON audit_stream_heads TO nexkosmo_audit")
    op.execute("GRANT SELECT, INSERT ON audit_log TO nexkosmo_audit")


def downgrade() -> None:
    raise RuntimeError(
        "Destructive downgrade is prohibited. Use a forward migration or rehearsed restore."
    )
