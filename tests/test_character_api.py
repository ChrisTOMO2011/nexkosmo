import os
from datetime import UTC, datetime
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
from app.interfaces.http.dependencies import (  # noqa: E402
    character_service,
    get_principal,
)
from app.interfaces.http.main import app  # noqa: E402

NOW = datetime(2026, 8, 20, tzinfo=UTC)


class FakeCharacterService:
    def __init__(self, workspace_id: UUID, project_id: UUID) -> None:
        self.workspace_id = workspace_id
        self.project_id = project_id
        self.character_id = uuid4()

    def response(self, *, version: int = 1) -> dict[str, object]:
        return {
            "character_id": self.character_id,
            "workspace_id": self.workspace_id,
            "project_id": self.project_id,
            "identity_id": self.character_id,
            "created_by_principal_id": uuid4(),
            "display_name": "Christopher",
            "role_label": "Lead",
            "version": version,
            "created_at": NOW,
            "updated_at": NOW,
        }

    async def create_character(self, *args: object, **kwargs: object) -> dict[str, object]:
        return self.response()

    async def list_characters(self, *args: object, **kwargs: object) -> list[dict[str, object]]:
        return [self.response()]

    async def get_character(self, *args: object, **kwargs: object) -> dict[str, object]:
        return self.response()

    async def update_character(self, *args: object, **kwargs: object) -> dict[str, object]:
        assert kwargs["expected_version"] == 1
        assert kwargs["replace_role_label"] is True
        return self.response(version=2)


@pytest.mark.asyncio
async def test_character_http_contract_is_nested_and_writes_require_idempotency() -> None:
    workspace_id, project_id = uuid4(), uuid4()
    principal = Principal(
        principal_id=uuid4(),
        workspace_id=workspace_id,
        agent_id=uuid4(),
        agent_kind=AgentKind.HUMAN,
    )
    service = FakeCharacterService(workspace_id, project_id)
    app.dependency_overrides[get_principal] = lambda: principal
    app.dependency_overrides[character_service] = lambda: service
    base = f"/v1/workspaces/{workspace_id}/projects/{project_id}/characters"
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
        ) as client:
            missing_key = await client.post(base, json={"display_name": "Christopher"})
            assert missing_key.status_code == 422

            created = await client.post(
                base,
                headers={"Idempotency-Key": "character-create-1"},
                json={"display_name": "Christopher", "role_label": "Lead"},
            )
            assert created.status_code == 201
            assert UUID(created.json()["project_id"]) == project_id

            listed = await client.get(base)
            assert listed.status_code == 200
            assert len(listed.json()) == 1

            fetched = await client.get(f"{base}/{service.character_id}")
            assert fetched.status_code == 200

            invalid_patch = await client.patch(
                f"{base}/{service.character_id}",
                headers={"Idempotency-Key": "character-update-empty"},
                json={"expected_version": 1},
            )
            assert invalid_patch.status_code == 422

            updated = await client.patch(
                f"{base}/{service.character_id}",
                headers={"Idempotency-Key": "character-update-1"},
                json={"expected_version": 1, "role_label": None},
            )
            assert updated.status_code == 200
            assert updated.json()["version"] == 2

            wrong_workspace = await client.get(
                f"/v1/workspaces/{uuid4()}/projects/{project_id}/characters"
            )
            assert wrong_workspace.status_code == 403
    finally:
        app.dependency_overrides.clear()
