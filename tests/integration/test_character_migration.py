from pathlib import Path

from sqlalchemy import text


async def test_character_schema_is_minimal_project_owned_and_forced_rls(db) -> None:
    columns = (
        await db.execute(
            text(
                """
                select column_name
                from information_schema.columns
                where table_schema='public' and table_name='characters'
                order by ordinal_position
                """
            )
        )
    ).scalars().all()
    assert columns == [
        "id",
        "workspace_id",
        "project_id",
        "identity_id",
        "created_by_principal_id",
        "display_name",
        "role_label",
        "version",
        "created_at",
        "updated_at",
    ]
    rls = (
        await db.execute(
            text(
                """
                select relrowsecurity, relforcerowsecurity
                from pg_class where relname='characters'
                """
            )
        )
    ).one()
    assert tuple(rls) == (True, True)


async def test_character_grants_and_policies_exclude_delete(db) -> None:
    privileges = (
        await db.execute(
            text(
                """
                select privilege_type
                from information_schema.role_table_grants
                where grantee='nexkosmo_app'
                  and table_schema='public'
                  and table_name='characters'
                order by privilege_type
                """
            )
        )
    ).scalars().all()
    assert privileges == ["INSERT", "SELECT", "UPDATE"]
    policies = (
        await db.execute(
            text(
                """
                select policyname, cmd
                from pg_policies
                where schemaname='public' and tablename='characters'
                order by policyname
                """
            )
        )
    ).all()
    assert [tuple(row) for row in policies] == [
        ("characters_insert", "INSERT"),
        ("characters_select", "SELECT"),
        ("characters_update", "UPDATE"),
    ]


async def test_character_constraints_preserve_identity_and_workspace_ownership(db) -> None:
    definitions = (
        await db.execute(
            text(
                """
                select pg_get_constraintdef(oid)
                from pg_constraint
                where conrelid='characters'::regclass
                order by conname
                """
            )
        )
    ).scalars().all()
    joined = "\n".join(definitions)
    assert "CHECK ((id = identity_id))" in joined
    assert "FOREIGN KEY (workspace_id, project_id)" in joined
    assert "FOREIGN KEY (workspace_id, identity_id)" in joined
    assert "ON DELETE RESTRICT" in joined


def test_character_migration_is_forward_only_and_contains_no_seed_or_backfill() -> None:
    source = Path("migrations/versions/0004_character_foundation.py").read_text(
        encoding="utf-8"
    )
    assert 'revision = "0004_character_foundation"' in source
    assert 'down_revision = "0003_project_authority"' in source
    assert "Destructive downgrade is prohibited" in source
    assert "insert into characters" not in source.lower()
    for rejected in (
        "production_id",
        "species",
        "accessory",
        "pipeline_status",
        "readiness",
        "preview_asset",
        "brain://",
    ):
        assert rejected not in source.lower()
