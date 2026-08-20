import os
from dataclasses import replace
from datetime import UTC, datetime
from uuid import UUID

from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.characters import Character
from app.infrastructure.character_repositories import (
    SqlAlchemyCharacterAssetManifestRepository,
    SqlAlchemyCharacterRepository,
)


async def test_character_repository_round_trip_and_optimistic_update(db):
    workspace_id = UUID("aaaaaaaa-0000-4000-8000-000000000001")
    project_id = UUID("aaaaaaaa-0000-4000-8000-000000000002")
    production_id = UUID("aaaaaaaa-0000-4000-8000-000000000003")
    owner_id = UUID("aaaaaaaa-0000-4000-8000-000000000004")
    owner_engine = create_engine(os.environ["MIGRATION_DATABASE_URL"])
    try:
        with owner_engine.begin() as connection:
            connection.execute(
                text(
                    """
                    INSERT INTO workspaces (id, canonical_key)
                    VALUES (:id, 'character-repository-test')
                    ON CONFLICT (id) DO NOTHING
                    """
                ),
                {"id": str(workspace_id)},
            )
            connection.execute(
                text(
                    """
                    INSERT INTO projects (
                        project_id, workspace_id, name, description, status,
                        owner_id, version
                    )
                    VALUES (
                        :project_id, :workspace_id, 'Repository Project', '',
                        'active', :owner_id, 1
                    )
                    ON CONFLICT (project_id) DO NOTHING
                    """
                ),
                {
                    "project_id": str(project_id),
                    "workspace_id": str(workspace_id),
                    "owner_id": str(owner_id),
                },
            )
            connection.execute(
                text(
                    """
                    INSERT INTO project_members (
                        workspace_id, project_id, principal_id, role
                    )
                    VALUES (:workspace_id, :project_id, :owner_id, 'Owner')
                    ON CONFLICT DO NOTHING
                    """
                ),
                {
                    "project_id": str(project_id),
                    "workspace_id": str(workspace_id),
                    "owner_id": str(owner_id),
                },
            )
            connection.execute(
                text(
                    """
                    INSERT INTO productions (
                        production_id, project_id, workspace_id, name,
                        production_type, status, owner_id, version
                    )
                    VALUES (
                        :production_id, :project_id, :workspace_id,
                        'Repository Production', 'Feature Film',
                        'pre-production', :owner_id, 1
                    )
                    ON CONFLICT (production_id) DO NOTHING
                    """
                ),
                {
                    "production_id": str(production_id),
                    "project_id": str(project_id),
                    "workspace_id": str(workspace_id),
                    "owner_id": str(owner_id),
                },
            )
    finally:
        owner_engine.dispose()

    await db.execute(text("RESET ROLE"))
    await db.execute(
        text("SELECT set_config('app.workspace_id', :workspace_id, true)"),
        {"workspace_id": str(workspace_id)},
    )
    now = datetime.now(UTC)
    character = Character.create(
        workspace_id=workspace_id,
        project_id=project_id,
        production_id=production_id,
        display_name="Repository Character",
        role="Lead",
        species_id=UUID("20000001-0000-4000-8000-000000000001"),
        compatibility_profile_id=UUID("40000001-0000-4000-8000-000000000001"),
        rig_id=UUID("30000003-0000-4000-8000-000000000003"),
        skeleton_id=UUID("30000004-0000-4000-8000-000000000004"),
        material_ids=(UUID("30000005-0000-4000-8000-000000000005"),),
        body_id=UUID("30000007-0000-4000-8000-000000000007"),
        now=now,
    )
    accessory_ids = (
        UUID("32000002-0000-4000-8000-000000000001"),
        UUID("43000001-0000-4000-8000-000000000001"),
        UUID("43000006-0000-4000-8000-000000000001"),
    )
    character = replace(character, accessory_ids=accessory_ids)
    session = AsyncSession(bind=db, expire_on_commit=False)
    repository = SqlAlchemyCharacterRepository(session)
    await repository.add(character)
    loaded = await repository.get_by_id(character.character_id)
    assert loaded == character
    assert loaded.accessory_ids == accessory_ids

    renamed = character.rename("Repository Character Updated")
    await repository.update(renamed, expected_version=1)
    reloaded = await repository.get_by_id(character.character_id)
    assert reloaded is not None
    assert reloaded.display_name == "Repository Character Updated"
    assert reloaded.version == 2


async def test_character_asset_repository_accepts_unfiltered_postgresql_query(db):
    await db.execute(text("RESET ROLE"))
    await db.execute(text("SET LOCAL ROLE nexkosmo_app"))
    await db.execute(
        text("SELECT set_config('app.workspace_id', :workspace_id, true)"),
        {"workspace_id": "aaaaaaaa-0000-4000-8000-000000000001"},
    )
    session = AsyncSession(bind=db, expire_on_commit=False)
    repository = SqlAlchemyCharacterAssetManifestRepository(session)

    assets = await repository.list_compatible(
        species_id=UUID("20000001-0000-4000-8000-000000000001"),
        category=None,
        limit=100,
        offset=0,
    )

    assert assets
    assert all(
        not asset.species_ids or UUID("20000001-0000-4000-8000-000000000001") in asset.species_ids
        for asset in assets
    )
