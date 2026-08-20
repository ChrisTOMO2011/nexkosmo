import os
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.projects import Production, Project
from app.infrastructure.project_repositories import (
    SqlAlchemyProductionRepository,
    SqlAlchemyProjectRepository,
)


async def test_project_and_production_repository_round_trip(db):
    workspace_id = uuid4()
    project_id = uuid4()
    production_id = uuid4()
    owner_id = uuid4()
    owner_engine = create_engine(os.environ["MIGRATION_DATABASE_URL"])
    try:
        with owner_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO workspaces (id, canonical_key)
                    VALUES (:id, :canonical_key)
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {
                    "id": str(workspace_id),
                    "canonical_key": f"project-repository-{workspace_id}",
                },
            )
    finally:
        owner_engine.dispose()
    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    await db.execute(
        text("SELECT set_config('app.workspace_id', :workspace_id, true)"),
        {"workspace_id": str(workspace_id)},
    )
    session = AsyncSession(bind=db, expire_on_commit=False)
    projects = SqlAlchemyProjectRepository(session)
    productions = SqlAlchemyProductionRepository(session)
    now = datetime.now(UTC)
    project = Project.create(
        workspace_id=workspace_id,
        name="Repository Project",
        description="Canonical ownership",
        owner_id=owner_id,
        project_id=project_id,
        now=now,
    )
    await projects.add(project)
    assert await projects.get_by_id(project_id) == project

    renamed = project.rename("Repository Project Updated")
    await projects.update(renamed, expected_version=1)
    assert (await projects.get_by_id(project_id)) == renamed

    production = Production.create(
        project_id=project_id,
        workspace_id=workspace_id,
        name="Repository Production",
        production_type="Feature Film",
        owner_id=owner_id,
        production_id=production_id,
        now=now,
    )
    await productions.add(production)
    assert await productions.get_by_id(production_id) == production

    active = production.change_status("pre-production")
    await productions.update(active, expected_version=1)
    assert (await productions.get_by_id(production_id)) == active
