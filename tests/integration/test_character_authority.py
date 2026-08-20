from uuid import UUID, uuid4, uuid5

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.character_service import CharacterService
from app.application.project_service import ProjectService
from app.domain.enums import AgentKind
from app.domain.errors import (
    AuthorityRemediationRequired,
    AuthorizationDenied,
    ConcurrencyConflict,
    IdempotencyConflict,
    ResourceNotFound,
)
from app.domain.types import Principal
from app.infrastructure.audit_delivery import SqlAuditDeliveryQueueRepository
from app.infrastructure.character_repositories import SqlCharacterRepository
from app.infrastructure.idempotency import SqlTransactionalIdempotency
from app.infrastructure.project_repositories import SqlOutboxRepository
from app.infrastructure.semantic_repositories import SqlSemanticProjectRepository
from app.infrastructure.uow import SqlAlchemyUnitOfWork


class NoopAuditDelivery:
    async def deliver_pending(self, *, principal: Principal) -> int:
        return 0


async def _seed_human_member(
    engine: AsyncEngine,
    *,
    workspace_id: UUID,
    principal_id: UUID,
    agent_id: UUID,
    role: str,
) -> None:
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "insert into workspaces (id, canonical_key) values (:id, :key) "
                "on conflict (id) do nothing"
            ),
            {"id": workspace_id, "key": f"workspace-{workspace_id}"},
        )
        await conn.execute(
            text(
                """
                insert into identities (id, workspace_id, kind, canonical_key)
                values (:agent_id, :workspace_id, 'agent', :canonical_key)
                """
            ),
            {
                "agent_id": agent_id,
                "workspace_id": workspace_id,
                "canonical_key": f"agent:{agent_id}",
            },
        )
        await conn.execute(
            text(
                """
                insert into agents (identity_id, workspace_id, kind, display_name)
                values (:agent_id, :workspace_id, 'human', 'Character Test Human')
                """
            ),
            {"agent_id": agent_id, "workspace_id": workspace_id},
        )
        await conn.execute(
            text(
                """
                insert into workspace_memberships (
                  workspace_id, principal_id, agent_id, role, valid_from
                ) values (
                  :workspace_id, :principal_id, :agent_id, :role,
                  now() - interval '1 minute'
                )
                """
            ),
            {
                "workspace_id": workspace_id,
                "principal_id": principal_id,
                "agent_id": agent_id,
                "role": role,
            },
        )


def _principal(workspace_id: UUID, principal_id: UUID, agent_id: UUID) -> Principal:
    return Principal(
        principal_id=principal_id,
        workspace_id=workspace_id,
        agent_id=agent_id,
        agent_kind=AgentKind.HUMAN,
    )


def _project_service(factory: async_sessionmaker[AsyncSession]) -> ProjectService:
    return ProjectService(
        lambda principal: SqlAlchemyUnitOfWork(factory, principal),
        SqlTransactionalIdempotency(factory),
        NoopAuditDelivery(),
    )


def _character_service(factory: async_sessionmaker[AsyncSession]) -> CharacterService:
    return CharacterService(
        lambda principal: SqlAlchemyUnitOfWork(factory, principal),
        SqlTransactionalIdempotency(factory),
        NoopAuditDelivery(),
    )


async def _set_context(conn, principal: Principal) -> None:
    for setting, value in (
        ("app.workspace_id", principal.workspace_id),
        ("app.principal_id", principal.principal_id),
        ("app.agent_id", principal.agent_id),
    ):
        await conn.execute(
            text("select set_config(:setting, :value, true)"),
            {"setting": setting, "value": str(value)},
        )


async def _add_project_member(
    engine: AsyncEngine,
    *,
    owner: Principal,
    project_id: UUID,
    member_principal_id: UUID,
    role: str,
) -> None:
    async with engine.begin() as conn:
        await _set_context(conn, owner)
        await conn.execute(
            text(
                """
                insert into project_memberships (
                  id, workspace_id, project_id, principal_id, role,
                  valid_from, granted_by_agent_id
                ) values (
                  :id, :workspace_id, :project_id, :principal_id, :role,
                  now() - interval '1 second', :agent_id
                )
                """
            ),
            {
                "id": uuid4(),
                "workspace_id": owner.workspace_id,
                "project_id": project_id,
                "principal_id": member_principal_id,
                "role": role,
                "agent_id": owner.agent_id,
            },
        )


async def _project_fixture(db, workspace_admin_engine):
    workspace_id, owner_id, owner_agent = uuid4(), uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=owner_id,
        agent_id=owner_agent,
        role="owner",
    )
    owner = _principal(workspace_id, owner_id, owner_agent)
    factory = async_sessionmaker(db.engine, expire_on_commit=False)
    created = await _project_service(factory).create_project(
        owner,
        name="Character Authority Project",
        idempotency_key=f"project-{uuid4()}",
    )
    return factory, owner, UUID(created["project_id"])


@pytest.mark.asyncio
async def test_owner_admin_editor_mutate_and_viewer_is_read_only(
    db, workspace_admin_engine
) -> None:
    factory, owner, project_id = await _project_fixture(db, workspace_admin_engine)
    service = _character_service(factory)
    actors: dict[str, Principal] = {"owner": owner}
    for project_role, workspace_role in (
        ("admin", "admin"),
        ("editor", "member"),
        ("viewer", "viewer"),
    ):
        principal_id, agent_id = uuid4(), uuid4()
        await _seed_human_member(
            workspace_admin_engine,
            workspace_id=owner.workspace_id,
            principal_id=principal_id,
            agent_id=agent_id,
            role=workspace_role,
        )
        actors[project_role] = _principal(owner.workspace_id, principal_id, agent_id)
        await _add_project_member(
            db.engine,
            owner=owner,
            project_id=project_id,
            member_principal_id=principal_id,
            role=project_role,
        )

    created: list[dict[str, object]] = []
    for role in ("owner", "admin", "editor"):
        try:
            result = await service.create_character(
                actors[role],
                project_id=project_id,
                display_name=f"{role.title()} Character",
                role_label=role,
                idempotency_key=f"character-{role}-{uuid4()}",
            )
        except Exception as exc:
            raise AssertionError(f"{role} Character mutation should be allowed") from exc
        created.append(result)
    with pytest.raises(AuthorizationDenied):
        await service.create_character(
            actors["viewer"],
            project_id=project_id,
            display_name="Denied",
            role_label=None,
            idempotency_key=f"viewer-{uuid4()}",
        )
    visible = await service.list_characters(actors["viewer"], project_id=project_id)
    assert len(visible) == 3

    updated = await service.update_character(
        actors["editor"],
        project_id=project_id,
        character_id=UUID(created[0]["character_id"]),
        expected_version=1,
        display_name="Edited Character",
        role_label=None,
        replace_role_label=False,
        idempotency_key=f"editor-update-{uuid4()}",
    )
    assert updated["version"] == 2
    with pytest.raises(AuthorizationDenied):
        await service.update_character(
            actors["viewer"],
            project_id=project_id,
            character_id=UUID(created[1]["character_id"]),
            expected_version=1,
            display_name="Denied",
            role_label=None,
            replace_role_label=False,
            idempotency_key=f"viewer-update-{uuid4()}",
        )


@pytest.mark.asyncio
async def test_workspace_admin_without_project_membership_is_denied(
    db, workspace_admin_engine
) -> None:
    factory, owner, project_id = await _project_fixture(db, workspace_admin_engine)
    admin_id, admin_agent = uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=owner.workspace_id,
        principal_id=admin_id,
        agent_id=admin_agent,
        role="admin",
    )
    admin = _principal(owner.workspace_id, admin_id, admin_agent)
    with pytest.raises(ResourceNotFound):
        await _character_service(factory).list_characters(admin, project_id=project_id)


@pytest.mark.asyncio
async def test_cross_workspace_and_cross_project_character_access_is_denied(
    db, workspace_admin_engine
) -> None:
    factory, owner, first_project_id = await _project_fixture(db, workspace_admin_engine)
    projects = _project_service(factory)
    second_project = await projects.create_project(
        owner,
        name="Second Project",
        idempotency_key=f"second-project-{uuid4()}",
    )
    service = _character_service(factory)
    character = await service.create_character(
        owner,
        project_id=first_project_id,
        display_name="Christopher",
        role_label="Lead",
        idempotency_key=f"cross-character-{uuid4()}",
    )
    with pytest.raises(ResourceNotFound):
        await service.get_character(
            owner,
            project_id=UUID(second_project["project_id"]),
            character_id=UUID(character["character_id"]),
        )

    other_workspace, other_id, other_agent = uuid4(), uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=other_workspace,
        principal_id=other_id,
        agent_id=other_agent,
        role="owner",
    )
    with pytest.raises(ResourceNotFound):
        await service.get_character(
            _principal(other_workspace, other_id, other_agent),
            project_id=first_project_id,
            character_id=UUID(character["character_id"]),
        )


@pytest.mark.asyncio
async def test_archived_and_remediation_locked_projects_block_character_mutation(
    db, workspace_admin_engine
) -> None:
    factory, owner, archived_project_id = await _project_fixture(
        db, workspace_admin_engine
    )
    await _project_service(factory).set_project_archived(
        owner,
        project_id=archived_project_id,
        archived=True,
        expected_version=1,
        idempotency_key=f"archive-{uuid4()}",
    )
    with pytest.raises(
        (AuthorizationDenied, AuthorityRemediationRequired, ResourceNotFound)
    ):
        await _character_service(factory).create_character(
            owner,
            project_id=archived_project_id,
            display_name="Archived",
            role_label=None,
            idempotency_key=f"archived-character-{uuid4()}",
        )

    factory, owner, locked_project_id = await _project_fixture(db, workspace_admin_engine)
    async with workspace_admin_engine.begin() as conn:
        await conn.execute(
            text(
                """
                insert into project_authority_remediations (
                  workspace_id, project_id, owner_principal_id, reason, effective_at
                ) values (:workspace_id, :project_id, :owner_id, 'test_lock', now())
                """
            ),
            {
                "workspace_id": owner.workspace_id,
                "project_id": locked_project_id,
                "owner_id": owner.principal_id,
            },
        )
    with pytest.raises(
        (AuthorizationDenied, AuthorityRemediationRequired, ResourceNotFound)
    ):
        await _character_service(factory).create_character(
            owner,
            project_id=locked_project_id,
            display_name="Locked",
            role_label=None,
            idempotency_key=f"locked-character-{uuid4()}",
        )


@pytest.mark.asyncio
async def test_character_optimistic_concurrency_and_idempotency(
    db, workspace_admin_engine
) -> None:
    factory, owner, project_id = await _project_fixture(db, workspace_admin_engine)
    service = _character_service(factory)
    key = f"character-idempotency-{uuid4()}"
    first = await service.create_character(
        owner,
        project_id=project_id,
        display_name="Christopher",
        role_label="Lead",
        idempotency_key=key,
    )
    assert await service.create_character(
        owner,
        project_id=project_id,
        display_name="Christopher",
        role_label="Lead",
        idempotency_key=key,
    ) == first
    with pytest.raises(IdempotencyConflict):
        await service.create_character(
            owner,
            project_id=project_id,
            display_name="Different",
            role_label="Lead",
            idempotency_key=key,
        )

    updated = await service.update_character(
        owner,
        project_id=project_id,
        character_id=UUID(first["character_id"]),
        expected_version=1,
        display_name="Christopher Vale",
        role_label=None,
        replace_role_label=False,
        idempotency_key=f"update-{uuid4()}",
    )
    assert updated["version"] == 2
    with pytest.raises(ConcurrencyConflict):
        await service.update_character(
            owner,
            project_id=project_id,
            character_id=UUID(first["character_id"]),
            expected_version=1,
            display_name="Stale",
            role_label=None,
            replace_role_label=False,
            idempotency_key=f"stale-{uuid4()}",
        )


@pytest.mark.asyncio
async def test_character_identity_activity_and_database_guards(
    db, workspace_admin_engine
) -> None:
    factory, owner, project_id = await _project_fixture(db, workspace_admin_engine)
    created = await _character_service(factory).create_character(
        owner,
        project_id=project_id,
        display_name="Semantic Character",
        role_label="Lead",
        idempotency_key=f"semantic-character-{uuid4()}",
    )
    character_id = UUID(created["character_id"])
    async with workspace_admin_engine.connect() as verify:
        row = (
            await verify.execute(
                text(
                    """
                    select i.kind, a.context_id as activity_context_id, a.performed_by,
                           a.attributes->>'authority_principal_id', ap.role,
                           p.context_id as project_context_id
                    from identities i
                    join activity_participations ap
                      on ap.workspace_id=i.workspace_id and ap.identity_id=i.id
                    join activities a
                      on a.workspace_id=ap.workspace_id and a.id=ap.activity_id
                    join projects p on p.id=:project_id
                    where i.id=:character_id and a.activity_type='character.created'
                    """
                ),
                {"project_id": project_id, "character_id": character_id},
            )
        ).one()
    assert tuple(row) == (
        "character",
        row.activity_context_id,
        owner.agent_id,
        str(owner.principal_id),
        "output",
        row.project_context_id,
    )

    wrong_kind_id = uuid4()
    async with db.engine.begin() as conn:
        await _set_context(conn, owner)
        await conn.execute(
            text(
                """
                insert into identities (id, workspace_id, kind, canonical_key)
                values (:id, :workspace_id, 'project', :key)
                """
            ),
            {
                "id": wrong_kind_id,
                "workspace_id": owner.workspace_id,
                "key": f"wrong-character-kind:{wrong_kind_id}",
            },
        )
    with pytest.raises(DBAPIError):
        async with db.engine.begin() as conn:
            await _set_context(conn, owner)
            await conn.execute(
                text(
                    """
                    insert into characters (
                      id, workspace_id, project_id, identity_id,
                      created_by_principal_id, display_name, version,
                      created_at, updated_at
                    ) values (
                      :id, :workspace_id, :project_id, :id,
                      :principal_id, 'Wrong Kind', 1, now(), now()
                    )
                    """
                ),
                {
                    "id": wrong_kind_id,
                    "workspace_id": owner.workspace_id,
                    "project_id": project_id,
                    "principal_id": owner.principal_id,
                },
            )

    with pytest.raises(DBAPIError):
        async with db.engine.begin() as conn:
            await _set_context(conn, owner)
            await conn.execute(
                text("delete from characters where id=:id"),
                {"id": character_id},
            )


@pytest.mark.asyncio
async def test_direct_cross_workspace_character_insert_is_denied(
    db, workspace_admin_engine
) -> None:
    _, first_owner, _ = await _project_fixture(db, workspace_admin_engine)
    _, second_owner, second_project_id = await _project_fixture(
        db, workspace_admin_engine
    )
    foreign_character_id = uuid4()
    async with db.engine.begin() as conn:
        await _set_context(conn, second_owner)
        await conn.execute(
            text(
                """
                insert into identities (id, workspace_id, kind, canonical_key)
                values (:id, :workspace_id, 'character', :key)
                """
            ),
            {
                "id": foreign_character_id,
                "workspace_id": second_owner.workspace_id,
                "key": f"cross-workspace-character:{foreign_character_id}",
            },
        )
    with pytest.raises(DBAPIError):
        async with db.engine.begin() as conn:
            await _set_context(conn, first_owner)
            await conn.execute(
                text(
                    """
                    insert into characters (
                      id, workspace_id, project_id, identity_id,
                      created_by_principal_id, display_name, version,
                      created_at, updated_at
                    ) values (
                      :id, :workspace_id, :project_id, :id,
                      :principal_id, 'Cross Workspace', 1, now(), now()
                    )
                    """
                ),
                {
                    "id": foreign_character_id,
                    "workspace_id": second_owner.workspace_id,
                    "project_id": second_project_id,
                    "principal_id": first_owner.principal_id,
                },
            )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("target", "message"),
    [
        ("character", "character failure"),
        ("semantic", "semantic failure"),
        ("outbox", "outbox failure"),
        ("audit", "audit failure"),
    ],
)
async def test_character_transaction_failures_roll_back_all_canonical_records(
    db, workspace_admin_engine, monkeypatch, target: str, message: str
) -> None:
    factory, owner, project_id = await _project_fixture(db, workspace_admin_engine)
    key = f"rollback-{target}-{uuid4()}"
    character_id = uuid5(project_id, f"character:{key}")

    async def fail(*_: object, **__: object) -> None:
        raise RuntimeError(message)

    if target == "character":
        monkeypatch.setattr(SqlCharacterRepository, "add", fail)
    elif target == "semantic":
        monkeypatch.setattr(SqlSemanticProjectRepository, "add_activity", fail)
    elif target == "outbox":
        monkeypatch.setattr(SqlOutboxRepository, "append", fail)
    else:
        monkeypatch.setattr(SqlAuditDeliveryQueueRepository, "append", fail)

    with pytest.raises(RuntimeError, match=message):
        await _character_service(factory).create_character(
            owner,
            project_id=project_id,
            display_name="Rollback",
            role_label=None,
            idempotency_key=key,
        )

    async with workspace_admin_engine.connect() as verify:
        counts = (
            await verify.execute(
                text(
                    """
                    select
                      (select count(*) from characters where id=:character_id),
                      (select count(*) from identities where id=:character_id),
                      (select count(*) from activities
                        where attributes->>'character_version'='1'
                          and id in (
                            select activity_id from activity_participations
                            where identity_id=:character_id
                          )),
                      (select count(*) from outbox_events
                        where aggregate_id=:character_id),
                      (select count(*) from audit_delivery_queue
                        where resource_id=:character_id),
                      (select count(*) from idempotency_records
                        where workspace_id=:workspace_id and idempotency_key=:key
                          and status='completed')
                    """
                ),
                {
                    "character_id": character_id,
                    "workspace_id": owner.workspace_id,
                    "key": key,
                },
            )
        ).one()
    assert tuple(counts) == (0, 0, 0, 0, 0, 0)
