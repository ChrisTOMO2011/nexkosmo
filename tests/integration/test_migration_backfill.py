import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, make_url


def _alembic_upgrade(target: str, database_url: URL) -> None:
    environment = dict(os.environ)
    environment["MIGRATION_DATABASE_URL"] = database_url.render_as_string(hide_password=False)
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", target],
        cwd=Path(__file__).resolve().parents[2],
        env=environment,
        check=True,
        capture_output=True,
        text=True,
    )


def test_existing_character_is_backfilled_into_project_and_production() -> None:
    migration_url = make_url(os.environ["MIGRATION_DATABASE_URL"])
    database_name = f"nexkosmo_backfill_{uuid4().hex}"
    test_url = migration_url.set(database=database_name)
    admin_url = migration_url.set(database="postgres")
    admin = create_engine(admin_url, isolation_level="AUTOCOMMIT")
    owner = migration_url.username or "nexkosmo_owner"

    with admin.connect() as connection:
        connection.execute(text(f'CREATE DATABASE "{database_name}" OWNER "{owner}"'))

    try:
        _alembic_upgrade("0003_character_pipeline", test_url)
        test_engine = create_engine(test_url)
        with test_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO workspaces (id, canonical_key)
                    VALUES (
                        '7c000001-0000-4000-8000-000000000001',
                        'migration-backfill-test'
                    );
                    INSERT INTO characters (
                        character_id, workspace_id, project_id, production_id,
                        display_name, role, species_id, compatibility_profile_id,
                        pipeline_status, version
                    )
                    SELECT
                        '7c000001-0000-4000-8000-000000000002',
                        '7c000001-0000-4000-8000-000000000001',
                        '7c000001-0000-4000-8000-000000000003',
                        '7c000001-0000-4000-8000-000000000004',
                        'Existing Character', 'Lead', species_id,
                        compatibility_profile_id, 'draft', 1
                    FROM species WHERE key = 'human';
                    """
                )
            )
        test_engine.dispose()

        _alembic_upgrade("head", test_url)
        verification = create_engine(test_url)
        with verification.connect() as connection:
            result = connection.execute(
                text(
                    """
                    SELECT
                        project.name,
                        production.name,
                        member.role,
                        character.display_name
                    FROM characters character
                    JOIN projects project
                      ON project.workspace_id = character.workspace_id
                     AND project.project_id = character.project_id
                    JOIN productions production
                      ON production.workspace_id = character.workspace_id
                     AND production.project_id = character.project_id
                     AND production.production_id = character.production_id
                    JOIN project_members member
                      ON member.workspace_id = project.workspace_id
                     AND member.project_id = project.project_id
                     AND member.principal_id = project.owner_id
                    WHERE character.character_id =
                        '7c000001-0000-4000-8000-000000000002'
                    """
                )
            ).one()
        verification.dispose()

        assert result[0].startswith("Imported Project ")
        assert result[1].startswith("Imported Production ")
        assert result.role == "Owner"
        assert result.display_name == "Existing Character"
    finally:
        with admin.connect() as connection:
            connection.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :database_name AND pid <> pg_backend_pid()"
                ),
                {"database_name": database_name},
            )
            connection.execute(text(f'DROP DATABASE IF EXISTS "{database_name}"'))
        admin.dispose()
