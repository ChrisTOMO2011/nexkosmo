import os
from datetime import UTC, datetime
from uuid import UUID

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.environments import Environment
from app.domain.errors import ConcurrencyConflict
from app.infrastructure.environment_repositories import (
    SqlAlchemyEnvironmentAssetManifestRepository,
    SqlAlchemyEnvironmentRepository,
    SqlAlchemyEnvironmentTypeRepository,
)

WORKSPACE_ID = UUID("ac000000-0000-4000-8000-000000000001")
PROJECT_ID = UUID("ac000000-0000-4000-8000-000000000002")
PRODUCTION_ID = UUID("ac000000-0000-4000-8000-000000000003")
OWNER_ID = UUID("ac000000-0000-4000-8000-000000000004")
ENVIRONMENT_ID = UUID("ac000000-0000-4000-8000-000000000005")


def seed_ownership() -> None:
    engine = create_engine(os.environ["MIGRATION_DATABASE_URL"])
    try:
        with engine.begin() as connection:
            parameters = {
                "workspace_id": str(WORKSPACE_ID),
                "project_id": str(PROJECT_ID),
                "production_id": str(PRODUCTION_ID),
                "owner_id": str(OWNER_ID),
                "environment_id": str(ENVIRONMENT_ID),
            }
            statements = (
                "DELETE FROM environments WHERE environment_id = :environment_id",
                """
                    INSERT INTO workspaces (id, canonical_key)
                    VALUES (:workspace_id, 'environment-repository-test')
                    ON CONFLICT (id) DO NOTHING
                """,
                """
                    INSERT INTO projects (
                        project_id, workspace_id, name, description, status, owner_id
                    ) VALUES (
                        :project_id, :workspace_id, 'Environment Project', '', 'active', :owner_id
                    ) ON CONFLICT (project_id) DO NOTHING
                """,
                """
                    INSERT INTO project_members (
                        workspace_id, project_id, principal_id, role
                    ) VALUES (
                        :workspace_id, :project_id, :owner_id, 'Owner'
                    ) ON CONFLICT DO NOTHING
                """,
                """
                    INSERT INTO productions (
                        production_id, project_id, workspace_id, name,
                        production_type, status, owner_id
                    ) VALUES (
                        :production_id, :project_id, :workspace_id, 'Environment Production',
                        'Feature Film', 'pre-production', :owner_id
                    ) ON CONFLICT (production_id) DO NOTHING
                """,
            )
            for statement in statements:
                connection.execute(text(statement), parameters)
    finally:
        engine.dispose()


async def test_environment_repository_round_trip_compatibility_and_concurrency(db) -> None:
    seed_ownership()
    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    await db.execute(
        text("SELECT set_config('app.workspace_id', :workspace_id, true)"),
        {"workspace_id": str(WORKSPACE_ID)},
    )
    session = AsyncSession(bind=db, expire_on_commit=False)
    types = SqlAlchemyEnvironmentTypeRepository(session)
    assets = SqlAlchemyEnvironmentAssetManifestRepository(session)
    environments = SqlAlchemyEnvironmentRepository(session)
    city = await types.get_by_key("city")
    assert city is not None

    environment = Environment.create(
        environment_id=ENVIRONMENT_ID,
        workspace_id=WORKSPACE_ID,
        project_id=PROJECT_ID,
        production_id=PRODUCTION_ID,
        display_name="City Street",
        environment_type_id=city.environment_type_id,
        now=datetime.now(UTC),
    )
    await environments.add(environment)
    loaded = await environments.get_by_id(ENVIRONMENT_ID)
    assert loaded == environment

    compatible = await assets.list_compatible(
        environment_type_id=city.environment_type_id,
        category="terrain",
        limit=100,
        offset=0,
    )
    assert compatible
    updated = environment.select_asset("terrain", compatible[0].asset_id)
    await environments.update(updated, expected_version=1)
    assert (await environments.get_by_id(ENVIRONMENT_ID)).terrain_asset_ids == (
        compatible[0].asset_id,
    )

    with pytest.raises(ConcurrencyConflict):
        await environments.update(updated.update_properties(biome="stale"), expected_version=1)
