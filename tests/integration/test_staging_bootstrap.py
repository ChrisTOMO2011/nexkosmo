from uuid import uuid4

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker

from app.application.operational_service import OperationalStatusService
from app.domain.enums import AgentKind
from app.domain.types import Principal
from app.infrastructure.uow import SqlAlchemyUnitOfWork
from scripts.bootstrap_staging_workspace import (
    BootstrapRequest,
    bootstrap_workspace_records,
)


@pytest.mark.asyncio
async def test_bootstrap_creates_only_explicit_owner_and_durable_audit_intent(
    db, workspace_admin_engine,
) -> None:
    request = BootstrapRequest(
        workspace_id=uuid4(),
        workspace_key=f"staging-{uuid4()}",
        owner_principal_id=uuid4(),
        owner_agent_id=uuid4(),
        owner_display_name="Staging Owner",
        reason="Director-approved disposable rehearsal",
    )
    await bootstrap_workspace_records(workspace_admin_engine, request)

    async with workspace_admin_engine.connect() as connection:
        owner = (
            await connection.execute(
                text(
                    """
                    select principal_id, agent_id, role
                    from workspace_memberships where workspace_id=:workspace_id
                    """
                ),
                {"workspace_id": request.workspace_id},
            )
        ).one()
        audit = (
            await connection.execute(
                text(
                    """
                    select action, outcome, principal_id, agent_id, details->>'reason'
                    from audit_delivery_queue where workspace_id=:workspace_id
                    """
                ),
                {"workspace_id": request.workspace_id},
            )
        ).one()

    assert tuple(owner) == (
        request.owner_principal_id,
        request.owner_agent_id,
        "owner",
    )
    assert tuple(audit) == (
        "workspace.bootstrap",
        "success",
        request.owner_principal_id,
        request.owner_agent_id,
        request.reason,
    )
    principal = Principal(
        principal_id=request.owner_principal_id,
        workspace_id=request.workspace_id,
        agent_id=request.owner_agent_id,
        agent_kind=AgentKind.HUMAN,
    )
    factory = async_sessionmaker(db.engine, expire_on_commit=False)
    status = await OperationalStatusService(
        lambda actor: SqlAlchemyUnitOfWork(factory, actor)
    ).get_delivery_status(principal)
    assert status["outbox"] == {
        "mode": "durable-storage-only",
        "pending": 0,
        "delivered": 0,
        "consumer_configured": False,
    }
    assert status["audit_delivery"] == {
        "pending": 1,
        "failed": 0,
        "delivered": 0,
    }
    with pytest.raises(RuntimeError, match="already exists"):
        await bootstrap_workspace_records(workspace_admin_engine, request)


def test_bootstrap_rejects_empty_authority_metadata() -> None:
    with pytest.raises(ValueError, match="reason must not be empty"):
        BootstrapRequest(
            workspace_id=uuid4(),
            workspace_key="staging",
            owner_principal_id=uuid4(),
            owner_agent_id=uuid4(),
            owner_display_name="Staging Owner",
            reason=" ",
        )
