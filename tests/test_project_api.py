# ruff: noqa: E402

import os

_test_environment = {
    "DATABASE_URL": "postgresql+asyncpg://unused:unused@127.0.0.1:9/unused",
    "MIGRATION_DATABASE_URL": "postgresql+asyncpg://unused:unused@127.0.0.1:9/unused",
    "AUDIT_DATABASE_URL": "postgresql+asyncpg://unused:unused@127.0.0.1:9/unused",
    "OIDC_ISSUER": "https://issuer.invalid",
    "OIDC_AUDIENCE": "nexkosmo-test",
    "OIDC_JWKS_URL": "https://issuer.invalid/jwks",
}
_previous_environment = {key: os.environ.get(key) for key in _test_environment}
os.environ.update(_test_environment)

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.application.project_service import ProjectProductionApplicationService
from app.domain.enums import AgentKind
from app.domain.errors import DomainError
from app.domain.types import Principal
from app.interfaces.http.dependencies import get_principal, project_application_service
from app.interfaces.http.project_routes import router
from tests.character_fakes import (
    AGENT_ID,
    PRINCIPAL_ID,
    WORKSPACE_ID,
    FakeAudit,
    FakeIdempotency,
    FakeStore,
    FakeUnitOfWorkFactory,
)

for _key, _value in _previous_environment.items():
    if _value is None:
        os.environ.pop(_key, None)
    else:
        os.environ[_key] = _value


def build_client() -> TestClient:
    store = FakeStore()
    service = ProjectProductionApplicationService(
        FakeUnitOfWorkFactory(store), FakeAudit(store), FakeIdempotency(store)
    )
    principal = Principal(
        principal_id=PRINCIPAL_ID,
        workspace_id=WORKSPACE_ID,
        agent_id=AGENT_ID,
        agent_kind=AgentKind.HUMAN,
    )
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[project_application_service] = lambda: service
    app.dependency_overrides[get_principal] = lambda: principal

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        status = 409 if exc.code == "concurrency_conflict" else 403
        if exc.code == "not_found":
            status = 404
        return JSONResponse(
            status_code=status,
            content={
                "detail": str(exc),
                "code": exc.code,
                "instance": str(request.url.path),
            },
        )

    return TestClient(app)


def test_project_and_production_api_round_trip_and_conflict():
    client = build_client()
    project_response = client.post(
        "/api/v1/projects",
        headers={"Idempotency-Key": "api-project"},
        json={"name": "API Project", "description": "Created through FastAPI."},
    )
    assert project_response.status_code == 201
    project = project_response.json()["project"]

    production_response = client.post(
        f"/api/v1/projects/{project['project_id']}/productions",
        headers={"Idempotency-Key": "api-production"},
        json={"name": "API Production", "production_type": "Feature Film"},
    )
    assert production_response.status_code == 201
    production = production_response.json()["production"]

    assert client.get("/api/v1/projects").status_code == 200
    assert client.get(f"/api/v1/projects/{project['project_id']}/productions").status_code == 200
    stale = client.patch(
        f"/api/v1/productions/{production['production_id']}",
        headers={"Idempotency-Key": "api-stale-production"},
        json={"expected_version": 99, "status": "production"},
    )
    assert stale.status_code == 409
    assert stale.json()["code"] == "concurrency_conflict"
