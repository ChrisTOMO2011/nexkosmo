"""Trusted control-plane bootstrap for a new Staging Workspace.

This is intentionally a command, not an HTTP route. Every authority identifier is
supplied explicitly; the command never creates a synthetic owner.
"""

import argparse
import asyncio
import json
import sys
from dataclasses import dataclass
from pathlib import Path
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.domain.enums import AgentKind  # noqa: E402
from app.domain.types import Principal  # noqa: E402
from app.infrastructure.audit_delivery import (  # noqa: E402
    SqlAuditDeliveryDispatcher,
    SqlIndependentAuditPort,
)
from app.infrastructure.config import settings  # noqa: E402


@dataclass(frozen=True, slots=True)
class BootstrapRequest:
    workspace_id: UUID
    workspace_key: str
    owner_principal_id: UUID
    owner_agent_id: UUID
    owner_display_name: str
    reason: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("workspace_key", self.workspace_key),
            ("owner_display_name", self.owner_display_name),
            ("reason", self.reason),
        ):
            if not value.strip():
                raise ValueError(f"{field_name} must not be empty.")


async def bootstrap_workspace_records(
    engine: AsyncEngine, request: BootstrapRequest
) -> None:
    async with engine.begin() as connection:
        existing = await connection.scalar(
            text("select 1 from workspaces where id=:id or canonical_key=:key"),
            {"id": request.workspace_id, "key": request.workspace_key},
        )
        if existing is not None:
            raise RuntimeError("Workspace identifier or canonical key already exists.")
        await connection.execute(
            text("insert into workspaces (id, canonical_key) values (:id, :key)"),
            {"id": request.workspace_id, "key": request.workspace_key},
        )
        await connection.execute(
            text(
                """
                insert into identities (id, workspace_id, kind, canonical_key)
                values (:agent_id, :workspace_id, 'agent', :canonical_key)
                """
            ),
            {
                "agent_id": request.owner_agent_id,
                "workspace_id": request.workspace_id,
                "canonical_key": f"agent:{request.owner_agent_id}",
            },
        )
        await connection.execute(
            text(
                """
                insert into agents (identity_id, workspace_id, kind, display_name)
                values (:agent_id, :workspace_id, 'human', :display_name)
                """
            ),
            {
                "agent_id": request.owner_agent_id,
                "workspace_id": request.workspace_id,
                "display_name": request.owner_display_name,
            },
        )
        await connection.execute(
            text(
                """
                insert into workspace_memberships (
                    workspace_id, principal_id, agent_id, role, valid_from
                ) values (
                    :workspace_id, :principal_id, :agent_id, 'owner', now()
                )
                """
            ),
            {
                "workspace_id": request.workspace_id,
                "principal_id": request.owner_principal_id,
                "agent_id": request.owner_agent_id,
            },
        )
        await connection.execute(
            text(
                """
                insert into audit_delivery_queue (
                    workspace_id, deduplication_key, principal_id, agent_id,
                    action, outcome, resource_id, details
                ) values (
                    :workspace_id, :deduplication_key, :principal_id, :agent_id,
                    'workspace.bootstrap', 'success', :workspace_id,
                    cast(:details as jsonb)
                )
                """
            ),
            {
                "workspace_id": request.workspace_id,
                "deduplication_key": f"workspace.bootstrap:{request.workspace_id}",
                "principal_id": request.owner_principal_id,
                "agent_id": request.owner_agent_id,
                "details": json.dumps(
                    {
                        "workspace_key": request.workspace_key,
                        "owner_principal_id": str(request.owner_principal_id),
                        "owner_agent_id": str(request.owner_agent_id),
                        "reason": request.reason,
                    }
                ),
            },
        )


def _async_url(value: str) -> str:
    return str(make_url(value).set(drivername="postgresql+asyncpg"))


async def run(request: BootstrapRequest) -> None:
    config = settings()
    migration_engine = create_async_engine(_async_url(config.migration_database_url))
    app_engine = create_async_engine(config.database_url)
    audit_engine = create_async_engine(config.audit_database_url)
    try:
        await bootstrap_workspace_records(migration_engine, request)
        principal = Principal(
            principal_id=request.owner_principal_id,
            workspace_id=request.workspace_id,
            agent_id=request.owner_agent_id,
            agent_kind=AgentKind.HUMAN,
        )
        app_factory = async_sessionmaker(app_engine, expire_on_commit=False)
        audit_factory = async_sessionmaker(audit_engine, expire_on_commit=False)
        dispatcher = SqlAuditDeliveryDispatcher(
            app_factory,
            SqlIndependentAuditPort(audit_factory),
            max_attempts=config.audit_retry_max_attempts,
            base_delay_seconds=config.audit_retry_base_seconds,
            max_delay_seconds=config.audit_retry_max_seconds,
        )
        await dispatcher.deliver_pending(principal=principal)
        async with migration_engine.connect() as connection:
            delivered = await connection.scalar(
                text(
                    """
                    select delivered_at is not null from audit_delivery_queue
                    where workspace_id=:workspace_id and deduplication_key=:key
                    """
                ),
                {
                    "workspace_id": request.workspace_id,
                    "key": f"workspace.bootstrap:{request.workspace_id}",
                },
            )
        if delivered is not True:
            raise RuntimeError(
                "Workspace exists, but its durable audit intent is still pending delivery."
            )
    finally:
        await migration_engine.dispose()
        await app_engine.dispose()
        await audit_engine.dispose()


def parse_args() -> BootstrapRequest:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-id", required=True, type=UUID)
    parser.add_argument("--workspace-key", required=True)
    parser.add_argument("--owner-principal-id", required=True, type=UUID)
    parser.add_argument("--owner-agent-id", required=True, type=UUID)
    parser.add_argument("--owner-display-name", required=True)
    parser.add_argument("--reason", required=True)
    values = parser.parse_args()
    return BootstrapRequest(
        workspace_id=values.workspace_id,
        workspace_key=values.workspace_key.strip(),
        owner_principal_id=values.owner_principal_id,
        owner_agent_id=values.owner_agent_id,
        owner_display_name=values.owner_display_name.strip(),
        reason=values.reason.strip(),
    )


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
