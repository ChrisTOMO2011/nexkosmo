from typing import Any, cast
from uuid import UUID, uuid4

import pytest

from app.application.environment_service import EnvironmentApplicationService
from app.application.ports import AuditDeliveryPort, IdempotencyPort, UnitOfWorkFactory
from app.domain.enums import AgentKind
from app.domain.errors import NotFound
from app.domain.types import Principal


class FailingIdempotency:
    async def fail(self, *_args: object) -> None:
        raise RuntimeError("idempotency unavailable")


class FailingAudit:
    async def record_or_queue(self, **_kwargs: object) -> None:
        raise RuntimeError("audit unavailable")


@pytest.mark.asyncio
async def test_failure_bookkeeping_never_masks_original_domain_error() -> None:
    principal = Principal(
        principal_id=UUID("51000000-0000-4000-8000-000000000002"),
        workspace_id=UUID("51000000-0000-4000-8000-000000000001"),
        agent_id=UUID("51000000-0000-4000-8000-000000000002"),
        agent_kind=AgentKind.HUMAN,
    )
    service = EnvironmentApplicationService(
        cast(UnitOfWorkFactory, cast(Any, None)),
        cast(AuditDeliveryPort, FailingAudit()),
        cast(IdempotencyPort, FailingIdempotency()),
    )

    await service._mutation_failure(
        principal,
        "environment-failure-test",
        "environment.identity_updated",
        uuid4(),
        NotFound("Environment does not exist."),
    )
