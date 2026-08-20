"""Explicit, Workspace-scoped audit redelivery command for trusted operators."""

import argparse
import asyncio
import sys
from pathlib import Path
from uuid import UUID

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
from app.infrastructure.database import (  # noqa: E402
    audit_session_factory,
    session_factory,
)


def _principal(values: argparse.Namespace) -> Principal:
    return Principal(
        principal_id=values.principal_id,
        workspace_id=values.workspace_id,
        agent_id=values.agent_id,
        agent_kind=AgentKind.HUMAN,
    )


async def run(values: argparse.Namespace) -> None:
    config = settings()
    dispatcher = SqlAuditDeliveryDispatcher(
        session_factory,
        SqlIndependentAuditPort(audit_session_factory),
        max_attempts=config.audit_retry_max_attempts,
        base_delay_seconds=config.audit_retry_base_seconds,
        max_delay_seconds=config.audit_retry_max_seconds,
    )
    principal = _principal(values)
    if values.requeue_failed is not None:
        changed = await dispatcher.requeue_failed(
            principal=principal, delivery_id=values.requeue_failed
        )
        if not changed:
            raise RuntimeError("No matching failed delivery was requeued.")
    delivered = await dispatcher.deliver_pending(principal=principal)
    print(f"Delivered audit records: {delivered}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workspace-id", required=True, type=UUID)
    parser.add_argument("--principal-id", required=True, type=UUID)
    parser.add_argument("--agent-id", required=True, type=UUID)
    parser.add_argument("--requeue-failed", type=UUID)
    return parser.parse_args()


if __name__ == "__main__":
    asyncio.run(run(parse_args()))
