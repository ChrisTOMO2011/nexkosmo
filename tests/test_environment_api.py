# ruff: noqa: E402

import os
from datetime import UTC, datetime
from uuid import UUID

for key in ("DATABASE_URL", "MIGRATION_DATABASE_URL", "AUDIT_DATABASE_URL"):
    os.environ.setdefault(key, "postgresql+asyncpg://unused:unused@127.0.0.1:9/unused")
os.environ.setdefault("OIDC_ISSUER", "https://issuer.invalid")
os.environ.setdefault("OIDC_AUDIENCE", "nexkosmo-test")
os.environ.setdefault("OIDC_JWKS_URL", "https://issuer.invalid/jwks")

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.application.environment_service import EnvironmentMutationResult
from app.domain.enums import AgentKind
from app.domain.environments import Environment, EnvironmentReadiness, EnvironmentType
from app.domain.errors import ConcurrencyConflict, DomainError
from app.domain.types import Principal
from app.interfaces.http.dependencies import environment_application_service, get_principal
from app.interfaces.http.environment_routes import router

WORKSPACE_ID = UUID("51000000-0000-4000-8000-000000000001")
PRINCIPAL_ID = UUID("51000000-0000-4000-8000-000000000002")
PROJECT_ID = UUID("51000000-0000-4000-8000-000000000003")
PRODUCTION_ID = UUID("51000000-0000-4000-8000-000000000004")
TYPE_ID = UUID("22000000-0000-4000-8000-000000000001")
NOW = datetime(2026, 8, 3, tzinfo=UTC)


class FakeEnvironmentService:
    def __init__(self) -> None:
        self.environment: Environment | None = None
        self.environment_type = EnvironmentType(
            environment_type_id=TYPE_ID,
            key="city",
            name="City",
            enabled=True,
            capabilities=frozenset({"buildings"}),
            supported_tabs=("Identity", "Buildings"),
            version=1,
            created_at=NOW,
            updated_at=NOW,
        )

    async def list_environment_types(self, _principal: Principal) -> list[EnvironmentType]:
        return [self.environment_type]

    async def create_environment(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        production_id: UUID,
        display_name: str,
        environment_type_id: UUID,
        description: str,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        del idempotency_key
        self.environment = Environment.create(
            workspace_id=principal.workspace_id,
            project_id=project_id,
            production_id=production_id,
            display_name=display_name,
            description=description,
            environment_type_id=environment_type_id,
            now=NOW,
        )
        return EnvironmentMutationResult(self.environment, {})

    async def create_production_environment(
        self,
        principal: Principal,
        *,
        production_id: UUID,
        display_name: str,
        environment_type_id: UUID,
        description: str,
        idempotency_key: str,
    ) -> EnvironmentMutationResult:
        return await self.create_environment(
            principal,
            project_id=PROJECT_ID,
            production_id=production_id,
            display_name=display_name,
            environment_type_id=environment_type_id,
            description=description,
            idempotency_key=idempotency_key,
        )

    async def get_environment(self, _principal: Principal, _environment_id: UUID) -> Environment:
        assert self.environment is not None
        return self.environment

    async def list_project_environments(
        self, _principal: Principal, _project_id: UUID, *, limit: int, offset: int
    ) -> list[Environment]:
        del limit, offset
        return [self.environment] if self.environment else []

    async def list_production_environments(
        self, _principal: Principal, _production_id: UUID, *, limit: int, offset: int
    ) -> list[Environment]:
        del limit, offset
        return [self.environment] if self.environment else []

    async def update_identity(
        self,
        _principal: Principal,
        _environment_id: UUID,
        *,
        expected_version: int,
        idempotency_key: str,
        display_name: str | None,
        description: str | None,
    ) -> EnvironmentMutationResult:
        assert self.environment is not None
        del idempotency_key
        if expected_version != self.environment.version:
            raise ConcurrencyConflict("stale Environment version")
        self.environment = self.environment.update_properties(
            display_name=display_name,
            description=description,
        )
        return EnvironmentMutationResult(self.environment, {})

    async def get_readiness(
        self, _principal: Principal, _environment_id: UUID
    ) -> EnvironmentReadiness:
        assert self.environment is not None
        return self.environment.readiness

    async def update_properties(
        self,
        _principal: Principal,
        _environment_id: UUID,
        expected_version: int,
        idempotency_key: str,
        display_name: str | None = None,
        description: str | None = None,
        location_type: str | None = None,
        interior_exterior: str | None = None,
        biome: str | None = None,
        climate_profile: str | None = None,
        time_of_day: str | None = None,
        scale: int | None = None,
        navigation_constraints: str | None = None,
        camera_access_constraints: str | None = None,
    ) -> EnvironmentMutationResult:
        assert self.environment is not None
        del idempotency_key
        if expected_version != self.environment.version:
            raise ConcurrencyConflict("stale Environment version")
        self.environment = self.environment.update_properties(
            display_name=display_name,
            description=description,
            location_type=location_type,  # type: ignore[arg-type]
            interior_exterior=interior_exterior,  # type: ignore[arg-type]
            biome=biome,
            climate_profile=climate_profile,
            time_of_day=time_of_day,
            scale=scale,
            navigation_constraints=navigation_constraints,
            camera_access_constraints=camera_access_constraints,
        )
        return EnvironmentMutationResult(self.environment, {})


def build_client() -> tuple[TestClient, FakeEnvironmentService]:
    service = FakeEnvironmentService()
    principal = Principal(
        principal_id=PRINCIPAL_ID,
        workspace_id=WORKSPACE_ID,
        agent_id=PRINCIPAL_ID,
        agent_kind=AgentKind.HUMAN,
    )
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[environment_application_service] = lambda: service
    app.dependency_overrides[get_principal] = lambda: principal

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        status = 409 if exc.code == "concurrency_conflict" else 422
        return JSONResponse(
            status_code=status,
            content={
                "type": f"urn:nexkosmo:problem:{exc.code}",
                "title": "Domain rule rejected the request",
                "status": status,
                "detail": str(exc),
                "instance": str(request.url.path),
                "code": exc.code,
            },
        )

    return TestClient(app), service


def test_environment_api_create_list_and_stale_version_conflict() -> None:
    client, _service = build_client()
    created = client.post(
        f"/api/v1/projects/{PROJECT_ID}/environments",
        headers={"Idempotency-Key": "environment-create"},
        json={
            "production_id": str(PRODUCTION_ID),
            "display_name": "City Street",
            "environment_type_id": str(TYPE_ID),
            "description": "Night exterior",
        },
    )
    assert created.status_code == 201
    environment_id = created.json()["environment"]["environment_id"]
    assert client.get(f"/api/v1/environments/{environment_id}").status_code == 200
    assert client.get(f"/api/v1/projects/{PROJECT_ID}/environments").json()["items"]

    updated = client.patch(
        f"/api/v1/environments/{environment_id}/properties",
        headers={"Idempotency-Key": "environment-update"},
        json={"expected_version": 1, "biome": "metropolitan"},
    )
    stale = client.patch(
        f"/api/v1/environments/{environment_id}/properties",
        headers={"Idempotency-Key": "environment-stale"},
        json={"expected_version": 1, "biome": "rural"},
    )
    assert updated.status_code == 200
    assert updated.json()["environment"]["version"] == 2
    assert stale.status_code == 409
    assert stale.json()["code"] == "concurrency_conflict"


def test_production_create_list_identity_and_readiness_routes() -> None:
    client, _service = build_client()
    created = client.post(
        f"/api/v1/productions/{PRODUCTION_ID}/environments",
        headers={"Idempotency-Key": "production-environment-create"},
        json={
            "display_name": "Forest Exterior",
            "environment_type_id": str(TYPE_ID),
            "description": "Canonical package",
        },
    )
    assert created.status_code == 201
    environment_id = created.json()["environment"]["environment_id"]
    listed = client.get(f"/api/v1/productions/{PRODUCTION_ID}/environments")
    assert listed.status_code == 200
    assert listed.json()["items"][0]["environment_id"] == environment_id

    renamed = client.patch(
        f"/api/v1/environments/{environment_id}/identity",
        headers={"Idempotency-Key": "environment-identity"},
        json={"expected_version": 1, "display_name": "Forest Night"},
    )
    assert renamed.status_code == 200
    assert renamed.json()["environment"]["display_name"] == "Forest Night"
    readiness = client.get(f"/api/v1/environments/{environment_id}/readiness")
    assert readiness.status_code == 200
    assert readiness.json() == {
        "readiness_status": "incomplete",
        "blocking_issues": [],
        "warnings": [],
        "missing_requirements": [],
        "invalid_asset_ids": [],
        "required_processing_jobs": [],
        "validated_version": None,
        "validated_at": None,
    }
