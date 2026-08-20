from sqlalchemy import text


async def test_explicit_migration_present_and_rls_forced(db):
    rows = (
        await db.execute(
            text(
                """
                SELECT relname, relrowsecurity, relforcerowsecurity
                FROM pg_class
                WHERE relname IN (
                    'identities','assertions','policies','decisions','outbox_events',
                    'characters','character_asset_manifests',
                    'character_accessories','character_downstream_dependencies',
                    'projects','project_members','productions','audit_delivery_queue',
                    'environments','environment_asset_selections','environment_asset_types'
                )
                ORDER BY relname
                """
            )
        )
    ).all()
    assert len(rows) == 16
    assert all(row.relrowsecurity and row.relforcerowsecurity for row in rows)


async def test_app_role_cannot_read_without_transaction_workspace_context(db):
    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    count = await db.scalar(text("SELECT count(*) FROM identities"))
    assert count == 0


async def test_character_seed_registry_and_cross_tenant_rls(db):
    species_count = await db.scalar(
        text(
            """
            SELECT count(*) FROM species
            WHERE key IN (
                'human','elf','goblin','orc','robot','dragon','alien','monkey','demon'
            )
            """
        )
    )
    assert species_count == 9

    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    await db.execute(
        text("SELECT set_config('app.workspace_id', :workspace_id, true)"),
        {"workspace_id": "bbbbbbbb-0000-4000-8000-000000000001"},
    )
    count = await db.scalar(text("SELECT count(*) FROM characters"))
    assert count == 0


async def test_accessory_manifest_categories_are_canonical(db):
    rows = (
        await db.execute(
            text(
                """
                SELECT name, category, subcategory
                FROM character_asset_manifests
                WHERE category = 'accessory'
                ORDER BY name
                """
            )
        )
    ).all()
    assert rows
    assert all(row.category == "accessory" and row.subcategory for row in rows)
    by_name = {row.name: row.subcategory for row in rows}
    assert by_name["Aviator"] == "glasses"
    assert by_name["Fedora"] == "hats"
    assert by_name["Stud"] == "earrings-jewelry"
    assert by_name["More"] == "more"


async def test_project_and_production_cross_tenant_rls(db):
    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    await db.execute(
        text("SELECT set_config('app.workspace_id', :workspace_id, true)"),
        {"workspace_id": "bbbbbbbb-0000-4000-8000-000000000001"},
    )

    assert await db.scalar(text("SELECT count(*) FROM projects")) == 0
    assert await db.scalar(text("SELECT count(*) FROM project_members")) == 0
    assert await db.scalar(text("SELECT count(*) FROM productions")) == 0


async def test_environment_registry_manifest_and_cross_tenant_rls(db):
    type_count = await db.scalar(text("SELECT count(*) FROM environment_types WHERE enabled"))
    asset_count = await db.scalar(
        text("SELECT count(*) FROM character_asset_manifests WHERE domain = 'environment'")
    )
    forest_capabilities = await db.scalar(
        text("SELECT capabilities FROM environment_types WHERE key = 'forest'")
    )
    woodland_cabin_count = await db.scalar(
        text(
            "SELECT count(*) FROM character_asset_manifests "
            "WHERE domain = 'environment' "
            "AND asset_id = '44000000-0000-4000-8000-00000000001f'"
        )
    )
    assert type_count == 17
    assert asset_count >= 30
    assert "buildings" in forest_capabilities
    assert woodland_cabin_count == 1

    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    await db.execute(
        text("SELECT set_config('app.workspace_id', :workspace_id, true)"),
        {"workspace_id": "bbbbbbbb-0000-4000-8000-000000000001"},
    )
    assert await db.scalar(text("SELECT count(*) FROM environments")) == 0
    assert await db.scalar(text("SELECT count(*) FROM environment_asset_selections")) == 0


async def test_application_role_cannot_access_immutable_audit_ledger(db):
    can_read = await db.scalar(
        text("SELECT has_table_privilege('nexkosmo_app', 'audit_log', 'SELECT')")
    )
    can_insert = await db.scalar(
        text("SELECT has_table_privilege('nexkosmo_app', 'audit_log', 'INSERT')")
    )
    can_update_heads = await db.scalar(
        text("SELECT has_table_privilege('nexkosmo_app', 'audit_stream_heads', 'UPDATE')")
    )

    assert can_read is False
    assert can_insert is False
    assert can_update_heads is False
