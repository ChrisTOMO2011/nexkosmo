import os
from uuid import UUID, uuid4

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
from app.interfaces.http.dependencies import get_principal, project_service  # noqa: E402
from app.interfaces.http.main import app  # noqa: E402


class FakeProjectService:
    async def create_project(
        self, principal: Principal, *, name: str, idempotency_key: str
    ) -> dict[str, object]:
        project_id = uuid4()
        return {
            "project_id": project_id,
            "workspace_id": principal.workspace_id,
            "identity_id": project_id,
            "context_id": uuid4(),
            "owner_principal_id": principal.principal_id,
            "name": name,
            "lifecycle": "active",
            "version": 1,
        }


@pytest.mark.asyncio
async def test_create_project_http_contract_requires_idempotency_and_workspace_match() -> None:
    workspace_id = uuid4()
    principal = Principal(
        principal_id=uuid4(),
        workspace_id=workspace_id,
        agent_id=uuid4(),
        agent_kind=AgentKind.HUMAN,
    )
    app.dependency_overrides[get_principal] = lambda: principal
    app.dependency_overrides[project_service] = lambda: FakeProjectService()
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        missing_key = await client.post(
            f"/v1/workspaces/{workspace_id}/projects", json={"name": "Project"}
        )
        assert missing_key.status_code == 422
        created = await client.post(
            f"/v1/workspaces/{workspace_id}/projects",
            headers={"Idempotency-Key": "create-1"},
            json={"name": "Project"},
        )
        assert created.status_code == 201
        assert UUID(created.json()["workspace_id"]) == workspace_id
        denied = await client.post(
            f"/v1/workspaces/{uuid4()}/projects",
            headers={"Idempotency-Key": "create-2"},
            json={"name": "Project"},
        )
        assert denied.status_code == 403
    app.dependency_overrides.clear()
