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


async def test_app_role_cannot_read_without_transaction_workspace_context(db):
    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    count = await db.scalar(text("SELECT count(*) FROM identities"))
    assert count == 0
