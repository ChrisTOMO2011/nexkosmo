import os
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://unused:unused@localhost/unused")
os.environ.setdefault(
    "MIGRATION_DATABASE_URL", "postgresql+psycopg://unused:unused@localhost/unused"
)
os.environ.setdefault("AUDIT_DATABASE_URL", "postgresql+asyncpg://unused:unused@localhost/unused")
os.environ.setdefault("OIDC_ISSUER", "https://identity.example.invalid/")
os.environ.setdefault("OIDC_AUDIENCE", "nexkosmo-test")
os.environ.setdefault("OIDC_JWKS_URL", "https://identity.example.invalid/jwks.json")

from app.domain.enums import AgentKind  # noqa: E402
from app.domain.types import Principal  # noqa: E402
from app.infrastructure.readiness import ReadinessResult  # noqa: E402
from app.interfaces.http.dependencies import (  # noqa: E402
    get_principal,
    operational_status_service,
    readiness_service,
)
from app.interfaces.http.main import app  # noqa: E402


class FakeOperationalStatus:
    async def get_delivery_status(self, principal: Principal) -> dict[str, object]:
        return {
            "workspace_id": principal.workspace_id,
            "outbox": {
                "mode": "durable-storage-only",
                "pending": 2,
                "delivered": 0,
                "consumer_configured": False,
            },
            "audit_delivery": {"pending": 1, "failed": 0, "delivered": 3},
        }


class FakeReadiness:
    def __init__(self, ready: bool) -> None:
        self.ready = ready

    async def check(self) -> ReadinessResult:
        return ReadinessResult(
            ready=self.ready,
            checks={
                "migration_head": {
                    "expected": "0005_staging_readiness",
                    "actual": "0004_character_foundation",
                    "matches": self.ready,
                }
            },
        )


@pytest.mark.asyncio
async def test_authenticated_operational_status_distinguishes_pending_outbox() -> None:
    workspace_id = uuid4()
    principal = Principal(
        principal_id=uuid4(),
        workspace_id=workspace_id,
        agent_id=uuid4(),
        agent_kind=AgentKind.HUMAN,
    )
    app.dependency_overrides[get_principal] = lambda: principal
    app.dependency_overrides[operational_status_service] = lambda: FakeOperationalStatus()
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get(
                f"/v1/workspaces/{workspace_id}/operations/delivery-status",
                headers={"X-Request-ID": "batch-1-test"},
            )
            assert response.status_code == 200
            assert response.headers["X-Request-ID"] == "batch-1-test"
            assert response.json()["outbox"] == {
                "mode": "durable-storage-only",
                "pending": 2,
                "delivered": 0,
                "consumer_configured": False,
            }
            denied = await client.get(
                f"/v1/workspaces/{uuid4()}/operations/delivery-status"
            )
            assert denied.status_code == 403
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_readiness_returns_503_on_migration_mismatch() -> None:
    app.dependency_overrides[readiness_service] = lambda: FakeReadiness(False)
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            response = await client.get("/health/ready")
        assert response.status_code == 503
        assert response.json()["status"] == "not_ready"
    finally:
        app.dependency_overrides.clear()
