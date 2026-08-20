import asyncio
from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4, uuid5

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from app.application.project_service import ProjectService
from app.domain.enums import AgentKind
from app.domain.errors import (
    AuthorizationDenied,
    ConcurrencyConflict,
    IdempotencyConflict,
    ResourceNotFound,
)
from app.domain.projects import ProductionState
from app.domain.types import Principal
from app.infrastructure.audit_delivery import (
    SqlAuditDeliveryDispatcher,
    SqlAuditDeliveryQueueRepository,
)
from app.infrastructure.idempotency import SqlTransactionalIdempotency
from app.infrastructure.project_repositories import SqlOutboxRepository
from app.infrastructure.uow import SqlAlchemyUnitOfWork


class NoopAuditDelivery:
    async def deliver_pending(self, *, principal: Principal) -> int:
        return 0


class CapturingIndependentAudit:
    def __init__(self) -> None:
        self.principals: list[Principal] = []

    async def record_independent(
        self,
        *,
        principal: Principal | None,
        action: str,
        outcome: str,
        resource_id: UUID | None,
        details: dict[str, object],
    ) -> None:
        assert action == "project.create"
        assert outcome == "success"
        assert resource_id is not None
        assert details["audit_delivery_key"]
        assert principal is not None
        self.principals.append(principal)


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
                values (:agent_id, :workspace_id, 'human', 'Test Human')
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
                  :workspace_id, :principal_id, :agent_id, :role, now() - interval '1 minute'
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


def _service(factory: async_sessionmaker[AsyncSession]) -> ProjectService:
    return ProjectService(
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
    principal: Principal,
    project_id: UUID,
    member_principal_id: UUID,
    role: str = "editor",
) -> None:
    async with engine.begin() as conn:
        await _set_context(conn, principal)
        await conn.execute(
            text(
                """
                insert into project_memberships (
                  id, workspace_id, project_id, principal_id, role,
                  valid_from, granted_by_agent_id
                ) values (
                  gen_random_uuid(), :workspace_id, :project_id, :principal_id,
                  :role, now() - interval '1 second', :agent_id
                )
                """
            ),
            {
                "workspace_id": principal.workspace_id,
                "project_id": project_id,
                "principal_id": member_principal_id,
                "role": role,
                "agent_id": principal.agent_id,
            },
        )


@pytest.mark.asyncio
async def test_atomic_project_identity_context_and_evidence_creation(
    db, workspace_admin_engine
) -> None:
    workspace_id, principal_id, agent_id = uuid4(), uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=principal_id,
        agent_id=agent_id,
        role="owner",
    )
    factory = async_sessionmaker(db.engine, expire_on_commit=False)
    result = await _service(factory).create_project(
        _principal(workspace_id, principal_id, agent_id),
        name="Atomic Project",
        idempotency_key=f"project-{uuid4()}",
    )
    project_id = UUID(result["project_id"])
    async with workspace_admin_engine.connect() as verify:
        counts = (
            await verify.execute(
                text(
                    """
                    select
                      (select count(*) from projects where id=:project_id) as projects,
                      (select count(*) from identities where id=:project_id and kind='project')
                        as project_identities,
                      (select count(*) from contexts c join projects p on p.context_id=c.identity_id
                        where p.id=:project_id and c.kind='project') as project_contexts,
                      (select count(*) from project_memberships
                        where project_id=:project_id and role='owner') as owners,
                      (select count(*) from activities a
                        join projects p on p.context_id=a.context_id
                        where p.id=:project_id and a.activity_type='project.created') as activities,
                      (select count(*) from outbox_events
                        where aggregate_id=:project_id) as outbox,
                      (select count(*) from audit_delivery_queue
                        where resource_id=:project_id) as audit_intents
                    """
                ),
                {"project_id": project_id},
            )
        ).one()
    assert tuple(counts) == (1, 1, 1, 1, 1, 1, 1)


@pytest.mark.asyncio
async def test_workspace_admin_has_no_implicit_project_content_read(
    db, workspace_admin_engine
) -> None:
    workspace_id = uuid4()
    owner_id, owner_agent = uuid4(), uuid4()
    admin_id, admin_agent = uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=owner_id,
        agent_id=owner_agent,
        role="owner",
    )
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=admin_id,
        agent_id=admin_agent,
        role="admin",
    )
    factory = async_sessionmaker(db.engine, expire_on_commit=False)
    await _service(factory).create_project(
        _principal(workspace_id, owner_id, owner_agent),
        name="Private Project",
        idempotency_key=f"private-{uuid4()}",
    )
    async with db.engine.begin() as conn:
        await _set_context(conn, _principal(workspace_id, admin_id, admin_agent))
        assert await conn.scalar(text("select count(*) from projects")) == 0


@pytest.mark.asyncio
async def test_ownership_transfer_is_atomic_and_concurrent_attempt_loses(
    db, workspace_admin_engine
) -> None:
    workspace_id = uuid4()
    owner_id, owner_agent = uuid4(), uuid4()
    target_ids = [(uuid4(), uuid4()), (uuid4(), uuid4())]
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=owner_id,
        agent_id=owner_agent,
        role="owner",
    )
    for target_id, target_agent in target_ids:
        await _seed_human_member(
            workspace_admin_engine,
            workspace_id=workspace_id,
            principal_id=target_id,
            agent_id=target_agent,
            role="member",
        )
    factory = async_sessionmaker(db.engine, expire_on_commit=False)
    principal = _principal(workspace_id, owner_id, owner_agent)
    service = _service(factory)
    created = await service.create_project(
        principal,
        name="Transfer Project",
        idempotency_key=f"transfer-create-{uuid4()}",
    )
    project_id = UUID(created["project_id"])
    async with db.engine.begin() as conn:
        await _set_context(conn, principal)
        for target_id, _ in target_ids:
            await conn.execute(
                text(
                    """
                    insert into project_memberships (
                      id, workspace_id, project_id, principal_id, role,
                      valid_from, granted_by_agent_id
                    ) values (
                      gen_random_uuid(), :workspace_id, :project_id, :principal_id,
                      'editor', now() - interval '1 second', :agent_id
                    )
                    """
                ),
                {
                    "workspace_id": workspace_id,
                    "project_id": project_id,
                    "principal_id": target_id,
                    "agent_id": owner_agent,
                },
            )

    async def transfer(target: UUID) -> object:
        try:
            return await service.transfer_ownership(
                principal,
                project_id=project_id,
                target_principal_id=target,
                expected_version=1,
                idempotency_key=f"transfer-{target}",
            )
        except (AuthorizationDenied, ConcurrencyConflict) as exc:
            return exc

    outcomes = await asyncio.gather(*(transfer(target_id) for target_id, _ in target_ids))
    assert sum(isinstance(outcome, dict) for outcome in outcomes) == 1
    async with workspace_admin_engine.connect() as verify:
        project = (
            await verify.execute(
                text("select owner_principal_id, version from projects where id=:id"),
                {"id": project_id},
            )
        ).one()
        memberships = (
            await verify.execute(
                text(
                    """
                    select principal_id, role from project_memberships
                    where project_id=:id and valid_to is null
                    order by role, principal_id
                    """
                ),
                {"id": project_id},
            )
        ).all()
    assert project.version == 2
    assert sum(row.role == "owner" for row in memberships) == 1
    assert any(row.principal_id == owner_id and row.role == "admin" for row in memberships)


@pytest.mark.asyncio
async def test_application_role_cannot_mutate_workspace_membership(
    db, workspace_admin_engine
) -> None:
    workspace_id, principal_id, agent_id = uuid4(), uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=principal_id,
        agent_id=agent_id,
        role="owner",
    )
    async with db.engine.connect() as conn:
        transaction = await conn.begin()
        await _set_context(conn, _principal(workspace_id, principal_id, agent_id))
        with pytest.raises(DBAPIError):
            await conn.execute(
                text(
                    "update workspace_memberships set valid_to=:valid_to "
                    "where workspace_id=:workspace_id and principal_id=:principal_id"
                ),
                {
                    "valid_to": datetime.now(UTC) + timedelta(minutes=1),
                    "workspace_id": workspace_id,
                    "principal_id": principal_id,
                },
            )
        await transaction.rollback()


@pytest.mark.asyncio
async def test_idempotent_replay_and_request_hash_conflict(
    db, workspace_admin_engine
) -> None:
    workspace_id, principal_id, agent_id = uuid4(), uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=principal_id,
        agent_id=agent_id,
        role="owner",
    )
    principal = _principal(workspace_id, principal_id, agent_id)
    service = _service(async_sessionmaker(db.engine, expire_on_commit=False))
    key = f"replay-{uuid4()}"
    first = await service.create_project(principal, name="Replay", idempotency_key=key)
    replay = await service.create_project(principal, name="Replay", idempotency_key=key)
    assert replay == first
    with pytest.raises(IdempotencyConflict):
        await service.create_project(principal, name="Different", idempotency_key=key)

    async with workspace_admin_engine.connect() as verify:
        counts = (
            await verify.execute(
                text(
                    """
                    select
                      (select count(*) from projects where id=:project_id),
                      (select count(*) from outbox_events where aggregate_id=:project_id),
                      (select count(*) from audit_delivery_queue where resource_id=:project_id),
                      (select count(*) from idempotency_records
                        where workspace_id=:workspace_id and idempotency_key=:key
                          and status='completed')
                    """
                ),
                {
                    "project_id": UUID(first["project_id"]),
                    "workspace_id": workspace_id,
                    "key": key,
                },
            )
        ).one()
    assert tuple(counts) == (1, 1, 1, 1)


@pytest.mark.asyncio
async def test_owner_revocation_creates_remediation_and_locks_mutation(
    db, workspace_admin_engine
) -> None:
    workspace_id = uuid4()
    owner_id, owner_agent = uuid4(), uuid4()
    editor_id, editor_agent = uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=owner_id,
        agent_id=owner_agent,
        role="owner",
    )
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=editor_id,
        agent_id=editor_agent,
        role="member",
    )
    factory = async_sessionmaker(db.engine, expire_on_commit=False)
    service = _service(factory)
    owner = _principal(workspace_id, owner_id, owner_agent)
    editor = _principal(workspace_id, editor_id, editor_agent)
    created = await service.create_project(
        owner, name="Remediation", idempotency_key=f"remediation-{uuid4()}"
    )
    project_id = UUID(created["project_id"])
    await _add_project_member(
        db.engine,
        principal=owner,
        project_id=project_id,
        member_principal_id=editor_id,
    )

    async with workspace_admin_engine.begin() as privileged:
        await privileged.execute(
            text(
                """
                update workspace_memberships
                set valid_to=now()
                where workspace_id=:workspace_id and principal_id=:principal_id
                  and valid_to is null
                """
            ),
            {"workspace_id": workspace_id, "principal_id": owner_id},
        )

    with pytest.raises(AuthorizationDenied):
        await service.get_project(owner, project_id=project_id)
    visible = await service.get_project(editor, project_id=project_id)
    assert UUID(visible["project_id"]) == project_id
    with pytest.raises((AuthorizationDenied, ResourceNotFound)):
        await service.create_production(
            editor,
            project_id=project_id,
            name="Blocked",
            idempotency_key=f"blocked-{uuid4()}",
        )
    async with workspace_admin_engine.connect() as verify:
        unresolved = await verify.scalar(
            text(
                """
                select count(*) from project_authority_remediations
                where project_id=:project_id and resolved_at is null
                """
            ),
            {"project_id": project_id},
        )
    assert unresolved == 1


@pytest.mark.asyncio
async def test_cross_workspace_and_cross_project_production_access_is_denied(
    db, workspace_admin_engine
) -> None:
    first_workspace, second_workspace = uuid4(), uuid4()
    first_id, first_agent = uuid4(), uuid4()
    second_id, second_agent = uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=first_workspace,
        principal_id=first_id,
        agent_id=first_agent,
        role="owner",
    )
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=second_workspace,
        principal_id=second_id,
        agent_id=second_agent,
        role="owner",
    )
    service = _service(async_sessionmaker(db.engine, expire_on_commit=False))
    first = _principal(first_workspace, first_id, first_agent)
    second = _principal(second_workspace, second_id, second_agent)
    first_project = await service.create_project(
        first, name="First", idempotency_key=f"first-{uuid4()}"
    )
    other_project = await service.create_project(
        first, name="Other", idempotency_key=f"other-{uuid4()}"
    )
    production = await service.create_production(
        first,
        project_id=UUID(first_project["project_id"]),
        name="Production",
        idempotency_key=f"production-{uuid4()}",
    )
    with pytest.raises(ResourceNotFound):
        await service.get_project(second, project_id=UUID(first_project["project_id"]))
    with pytest.raises(ResourceNotFound):
        await service.transition_production(
            first,
            project_id=UUID(other_project["project_id"]),
            production_id=UUID(production["production_id"]),
            target_state=ProductionState.ACTIVE,
            expected_version=1,
            idempotency_key=f"cross-project-{uuid4()}",
        )


@pytest.mark.asyncio
async def test_outbox_failure_rolls_back_business_and_audit_intent(
    db, workspace_admin_engine, monkeypatch
) -> None:
    workspace_id, principal_id, agent_id = uuid4(), uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=principal_id,
        agent_id=agent_id,
        role="owner",
    )
    principal = _principal(workspace_id, principal_id, agent_id)
    key = f"rollback-{uuid4()}"
    expected_project_id = uuid5(workspace_id, f"project:{key}")

    async def fail_outbox(*_: object, **__: object) -> None:
        raise RuntimeError("simulated outbox failure")

    monkeypatch.setattr(SqlOutboxRepository, "append", fail_outbox)
    service = _service(async_sessionmaker(db.engine, expire_on_commit=False))
    with pytest.raises(RuntimeError, match="simulated outbox failure"):
        await service.create_project(principal, name="Rollback", idempotency_key=key)

    async with workspace_admin_engine.connect() as verify:
        counts = (
            await verify.execute(
                text(
                    """
                    select
                      (select count(*) from projects where id=:project_id),
                      (select count(*) from identities where id=:project_id),
                      (select count(*) from project_memberships where project_id=:project_id),
                      (select count(*) from outbox_events where aggregate_id=:project_id),
                      (select count(*) from audit_delivery_queue where resource_id=:project_id),
                      (select count(*) from idempotency_records
                        where workspace_id=:workspace_id and idempotency_key=:key
                          and status='completed')
                    """
                ),
                {
                    "project_id": expected_project_id,
                    "workspace_id": workspace_id,
                    "key": key,
                },
            )
        ).one()
    assert tuple(counts) == (0, 0, 0, 0, 0, 0)


@pytest.mark.asyncio
async def test_audit_intent_failure_rolls_back_business_and_outbox(
    db, workspace_admin_engine, monkeypatch
) -> None:
    workspace_id, principal_id, agent_id = uuid4(), uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=principal_id,
        agent_id=agent_id,
        role="owner",
    )
    principal = _principal(workspace_id, principal_id, agent_id)
    key = f"audit-rollback-{uuid4()}"
    expected_project_id = uuid5(workspace_id, f"project:{key}")

    async def fail_audit_intent(*_: object, **__: object) -> None:
        raise RuntimeError("simulated audit-intent failure")

    monkeypatch.setattr(SqlAuditDeliveryQueueRepository, "append", fail_audit_intent)
    service = _service(async_sessionmaker(db.engine, expire_on_commit=False))
    with pytest.raises(RuntimeError, match="simulated audit-intent failure"):
        await service.create_project(principal, name="Rollback", idempotency_key=key)

    async with workspace_admin_engine.connect() as verify:
        counts = (
            await verify.execute(
                text(
                    """
                    select
                      (select count(*) from projects where id=:project_id),
                      (select count(*) from identities where id=:project_id),
                      (select count(*) from project_memberships where project_id=:project_id),
                      (select count(*) from outbox_events where aggregate_id=:project_id),
                      (select count(*) from audit_delivery_queue where resource_id=:project_id),
                      (select count(*) from idempotency_records
                        where workspace_id=:workspace_id and idempotency_key=:key
                          and status='completed')
                    """
                ),
                {
                    "project_id": expected_project_id,
                    "workspace_id": workspace_id,
                    "key": key,
                },
            )
        ).one()
    assert tuple(counts) == (0, 0, 0, 0, 0, 0)


@pytest.mark.asyncio
async def test_transfer_and_workspace_revocation_race_fails_closed(
    db, workspace_admin_engine
) -> None:
    workspace_id = uuid4()
    owner_id, owner_agent = uuid4(), uuid4()
    target_id, target_agent = uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=owner_id,
        agent_id=owner_agent,
        role="owner",
    )
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=target_id,
        agent_id=target_agent,
        role="member",
    )
    principal = _principal(workspace_id, owner_id, owner_agent)
    service = _service(async_sessionmaker(db.engine, expire_on_commit=False))
    created = await service.create_project(
        principal, name="Race", idempotency_key=f"race-create-{uuid4()}"
    )
    project_id = UUID(created["project_id"])
    await _add_project_member(
        db.engine,
        principal=principal,
        project_id=project_id,
        member_principal_id=target_id,
    )

    async def transfer() -> object:
        try:
            return await service.transfer_ownership(
                principal,
                project_id=project_id,
                target_principal_id=target_id,
                expected_version=1,
                idempotency_key=f"race-transfer-{uuid4()}",
            )
        except Exception as exc:
            return exc

    async def revoke() -> None:
        async with workspace_admin_engine.begin() as privileged:
            await privileged.execute(
                text(
                    """
                    update workspace_memberships set valid_to=now()
                    where workspace_id=:workspace_id and principal_id=:principal_id
                      and valid_to is null
                    """
                ),
                {"workspace_id": workspace_id, "principal_id": target_id},
            )

    await asyncio.gather(transfer(), revoke())
    async with workspace_admin_engine.connect() as verify:
        project = (
            await verify.execute(
                text("select owner_principal_id, version from projects where id=:id"),
                {"id": project_id},
            )
        ).one()
        owner_count = await verify.scalar(
            text(
                """
                select count(*) from project_memberships
                where project_id=:id and role='owner' and valid_to is null
                """
            ),
            {"id": project_id},
        )
        target_active = await verify.scalar(
            text(
                """
                select count(*) from workspace_memberships
                where workspace_id=:workspace_id and principal_id=:principal_id
                  and valid_from <= now() and (valid_to is null or now() < valid_to)
                """
            ),
            {"workspace_id": workspace_id, "principal_id": target_id},
        )
        remediation_count = await verify.scalar(
            text(
                """
                select count(*) from project_authority_remediations
                where project_id=:id and resolved_at is null
                """
            ),
            {"id": project_id},
        )
    assert owner_count == 1
    assert target_active == 0
    assert project.version in {1, 2}
    if project.owner_principal_id == target_id:
        assert remediation_count == 1
    else:
        assert project.owner_principal_id == owner_id


@pytest.mark.asyncio
async def test_archive_and_production_transition_race_preserves_read_only_state(
    db, workspace_admin_engine
) -> None:
    workspace_id, owner_id, owner_agent = uuid4(), uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=owner_id,
        agent_id=owner_agent,
        role="owner",
    )
    principal = _principal(workspace_id, owner_id, owner_agent)
    service = _service(async_sessionmaker(db.engine, expire_on_commit=False))
    created = await service.create_project(
        principal, name="Archive Race", idempotency_key=f"archive-race-{uuid4()}"
    )
    project_id = UUID(created["project_id"])
    production = await service.create_production(
        principal,
        project_id=project_id,
        name="Primary",
        idempotency_key=f"archive-production-{uuid4()}",
    )
    production_id = UUID(production["production_id"])

    async def archive() -> object:
        try:
            return await service.set_project_archived(
                principal,
                project_id=project_id,
                archived=True,
                expected_version=1,
                idempotency_key=f"archive-action-{uuid4()}",
            )
        except Exception as exc:
            return exc

    async def transition() -> object:
        try:
            return await service.transition_production(
                principal,
                project_id=project_id,
                production_id=production_id,
                target_state=ProductionState.ACTIVE,
                expected_version=1,
                idempotency_key=f"transition-action-{uuid4()}",
            )
        except Exception as exc:
            return exc

    outcomes = await asyncio.gather(archive(), transition())
    assert any(isinstance(outcome, dict) for outcome in outcomes)
    async with workspace_admin_engine.connect() as verify:
        project_row = (
            await verify.execute(
                text("select lifecycle, version from projects where id=:id"),
                {"id": project_id},
            )
        ).one()
        production_row = (
            await verify.execute(
                text("select state, version from productions where id=:id"),
                {"id": production_id},
            )
        ).one()
    assert tuple(project_row) == ("archived", 2)
    assert tuple(production_row) in {("planned", 1), ("active", 2)}


@pytest.mark.asyncio
async def test_audit_delivery_preserves_original_authority_principal(
    db, workspace_admin_engine
) -> None:
    workspace_id = uuid4()
    owner_id, owner_agent = uuid4(), uuid4()
    worker_id, worker_agent = uuid4(), uuid4()
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=owner_id,
        agent_id=owner_agent,
        role="owner",
    )
    await _seed_human_member(
        workspace_admin_engine,
        workspace_id=workspace_id,
        principal_id=worker_id,
        agent_id=worker_agent,
        role="admin",
    )
    factory = async_sessionmaker(db.engine, expire_on_commit=False)
    owner = _principal(workspace_id, owner_id, owner_agent)
    await _service(factory).create_project(
        owner, name="Audit Provenance", idempotency_key=f"audit-{uuid4()}"
    )

    audit = CapturingIndependentAudit()
    dispatcher = SqlAuditDeliveryDispatcher(factory, audit)
    delivered = await dispatcher.deliver_pending(
        principal=_principal(workspace_id, worker_id, worker_agent)
    )
    assert delivered == 1
    assert len(audit.principals) == 1
    assert audit.principals[0].principal_id == owner_id
    assert audit.principals[0].agent_id == owner_agent
    async with workspace_admin_engine.connect() as verify:
        pending = await verify.scalar(
            text(
                """
                select count(*) from audit_delivery_queue
                where workspace_id=:workspace_id and delivered_at is null
                """
            ),
            {"workspace_id": workspace_id},
        )
    assert pending == 0
