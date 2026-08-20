from sqlalchemy import text


async def test_explicit_migration_present_and_rls_forced(db):
    rows = (
        await db.execute(
            text(
                '''
                SELECT relname, relrowsecurity, relforcerowsecurity
                FROM pg_class
                WHERE relname IN ('identities','assertions','policies','decisions','outbox_events')
                ORDER BY relname
                '''
            )
        )
    ).all()
    assert len(rows) == 5
    assert all(row.relrowsecurity and row.relforcerowsecurity for row in rows)


async def test_project_authority_tables_have_forced_rls(db):
    rows = (
        await db.execute(
            text(
                """
                SELECT relname, relrowsecurity, relforcerowsecurity
                FROM pg_class
                WHERE relname IN (
                  'projects', 'project_memberships', 'productions',
                  'project_authority_remediations', 'audit_delivery_queue'
                )
                ORDER BY relname
                """
            )
        )
    ).all()
    assert len(rows) == 5
    assert all(row.relrowsecurity and row.relforcerowsecurity for row in rows)


async def test_character_table_has_forced_rls(db):
    row = (
        await db.execute(
            text(
                """
                SELECT relrowsecurity, relforcerowsecurity
                FROM pg_class WHERE relname = 'characters'
                """
            )
        )
    ).one()
    assert row.relrowsecurity and row.relforcerowsecurity


async def test_app_role_workspace_membership_is_read_only(db):
    privileges = (
        await db.execute(
            text(
                """
                select privilege_type
                from information_schema.role_table_grants
                where grantee = 'nexkosmo_app'
                  and table_schema = 'public'
                  and table_name = 'workspace_memberships'
                order by privilege_type
                """
            )
        )
    ).scalars().all()
    assert privileges == ["SELECT"]


async def test_app_role_cannot_read_without_transaction_workspace_context(db):
    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    counts = []
    for table in (
        "identities",
        "projects",
        "project_memberships",
        "productions",
        "project_authority_remediations",
        "audit_delivery_queue",
        "characters",
    ):
        counts.append(await db.scalar(text(f"SELECT count(*) FROM {table}")))
    assert counts == [0, 0, 0, 0, 0, 0, 0]
