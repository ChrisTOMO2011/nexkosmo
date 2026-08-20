# ruff: noqa: E402

import os
from dataclasses import replace
from uuid import UUID

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

from app.application.character_service import CharacterApplicationService
from app.domain.enums import AgentKind
from app.domain.errors import DomainError
from app.domain.types import Principal
from app.interfaces.http.character_routes import router
from app.interfaces.http.character_schemas import CharacterResponse
from app.interfaces.http.dependencies import (
    character_application_service,
    get_principal,
)
from tests.character_fakes import (
    AGENT_ID,
    GOBLIN_ID,
    HUMAN_HAIR_ID,
    HUMAN_ID,
    PRINCIPAL_ID,
    PRODUCTION_ID,
    PROJECT_ID,
    SHARED_VOICE_ID,
    WORKSPACE_ID,
    FakeAudit,
    FakeIdempotency,
    FakeStore,
    FakeUnitOfWorkFactory,
    manifest,
)

for _key, _value in _previous_environment.items():
    if _value is None:
        os.environ.pop(_key, None)
    else:
        os.environ[_key] = _value


def build_client():
    store = FakeStore()
    service = CharacterApplicationService(
        FakeUnitOfWorkFactory(store), FakeAudit(store), FakeIdempotency(store)
    )
    principal_holder = {
        "value": Principal(
            principal_id=PRINCIPAL_ID,
            workspace_id=WORKSPACE_ID,
            agent_id=AGENT_ID,
            agent_kind=AgentKind.HUMAN,
        )
    }
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[character_application_service] = lambda: service
    app.dependency_overrides[get_principal] = lambda: principal_holder["value"]

    @app.exception_handler(DomainError)
    async def handle_domain_error(request: Request, exc: DomainError) -> JSONResponse:
        status = 404 if exc.code == "not_found" else 409
        if exc.code in {"invariant_violation", "validation_failed"}:
            status = 422
        if exc.code == "authorization_denied":
            status = 403
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

    return TestClient(app), store, principal_holder


def test_character_api_create_get_list_and_stale_conflict():
    client, store, _principal = build_client()
    created = client.post(
        f"/api/v1/projects/{PROJECT_ID}/characters",
        headers={"Idempotency-Key": "api-create"},
        json={
            "production_id": str(PRODUCTION_ID),
            "display_name": "Christopher",
            "role": "Lead",
            "species_id": str(HUMAN_ID),
        },
    )
    assert created.status_code == 201
    payload = created.json()
    character_id = payload["character"]["character_id"]
    assert UUID(character_id).version == 4

    loaded = client.get(f"/api/v1/characters/{character_id}")
    listed = client.get(f"/api/v1/projects/{PROJECT_ID}/characters")
    assert loaded.status_code == 200
    assert listed.json()["items"][0]["character_id"] == character_id
    assert len(store.characters) == 1

    first_patch = client.patch(
        f"/api/v1/characters/{character_id}",
        headers={"Idempotency-Key": "api-rename"},
        json={"expected_version": 1, "display_name": "Christopher Vale"},
    )
    stale_patch = client.patch(
        f"/api/v1/characters/{character_id}",
        headers={"Idempotency-Key": "api-stale"},
        json={"expected_version": 1, "display_name": "Stale Name"},
    )
    assert first_patch.status_code == 200
    assert first_patch.json()["character"]["version"] == 2
    assert stale_patch.status_code == 409
    assert stale_patch.json()["code"] == "concurrency_conflict"


def test_character_api_idempotency_and_cross_tenant_read():
    client, store, principal_holder = build_client()
    request = {
        "production_id": str(PRODUCTION_ID),
        "display_name": "Christopher",
        "role": "Lead",
        "species_id": str(HUMAN_ID),
    }
    first = client.post(
        f"/api/v1/projects/{PROJECT_ID}/characters",
        headers={"Idempotency-Key": "repeat-create"},
        json=request,
    )
    replay = client.post(
        f"/api/v1/projects/{PROJECT_ID}/characters",
        headers={"Idempotency-Key": "repeat-create"},
        json=request,
    )
    assert first.json() == replay.json()
    assert len(store.characters) == 1

    principal_holder["value"] = Principal(
        principal_id=UUID("90000000-0000-4000-8000-000000000002"),
        workspace_id=UUID("90000000-0000-4000-8000-000000000001"),
        agent_id=UUID("90000000-0000-4000-8000-000000000003"),
        agent_kind=AgentKind.HUMAN,
    )
    cross_tenant = client.get(f"/api/v1/characters/{first.json()['character']['character_id']}")
    assert cross_tenant.status_code == 403


def test_asset_response_does_not_expose_internal_file_references():
    client, _store, _principal = build_client()
    response = client.get("/api/v1/assets/41000001-0000-4000-8000-000000000001")
    assert response.status_code == 200
    assert "file_references" not in response.json()
    assert "provenance" not in response.json()


def test_species_asset_endpoint_filters_by_canonical_species_and_keeps_shared_assets():
    client, _store, _principal = build_client()

    human = client.get(f"/api/v1/species/{HUMAN_ID}/assets").json()["items"]
    goblin = client.get(f"/api/v1/species/{GOBLIN_ID}/assets").json()["items"]
    human_ids = {item["asset_id"] for item in human}
    goblin_ids = {item["asset_id"] for item in goblin}

    assert str(HUMAN_HAIR_ID) in human_ids
    assert str(HUMAN_HAIR_ID) not in goblin_ids
    assert str(SHARED_VOICE_ID) in human_ids
    assert str(SHARED_VOICE_ID) in goblin_ids


def test_phase3_identity_physical_and_validation_endpoints():
    client, _store, _principal = build_client()
    created = client.post(
        f"/api/v1/projects/{PROJECT_ID}/characters",
        headers={"Idempotency-Key": "phase3-api-create"},
        json={
            "production_id": str(PRODUCTION_ID),
            "display_name": "Christopher",
            "role": "Lead",
            "species_id": str(HUMAN_ID),
        },
    ).json()["character"]
    character_id = created["character_id"]
    identity = client.patch(
        f"/api/v1/characters/{character_id}/identity-properties",
        headers={"Idempotency-Key": "phase3-api-identity"},
        json={
            "expected_version": 1,
            "identity_type": "Human Male",
            "gender_presentation": "Masculine",
        },
    )
    physical = client.patch(
        f"/api/v1/characters/{character_id}/physical-properties",
        headers={"Idempotency-Key": "phase3-api-physical"},
        json={"expected_version": 2, "age": 40, "height_cm": 185, "skin_tone": 74},
    )
    validated = client.post(
        f"/api/v1/characters/{character_id}/validate-package",
        headers={"Idempotency-Key": "phase3-api-validate"},
        json={"expected_version": 3},
    )
    assert identity.status_code == 200
    assert identity.json()["character"]["gender_presentation"] == "Masculine"
    assert physical.status_code == 200
    assert physical.json()["character"]["height_cm"] == 185
    assert validated.status_code == 200
    assert validated.json()["character"]["readiness_status"] == "invalid"


def test_character_response_serializes_nullable_and_populated_fields():
    client, store, _principal = build_client()
    created = client.post(
        f"/api/v1/projects/{PROJECT_ID}/characters",
        headers={"Idempotency-Key": "serialization-create"},
        json={
            "production_id": str(PRODUCTION_ID),
            "display_name": "Serialization Character",
            "role": "Lead",
            "species_id": str(HUMAN_ID),
        },
    ).json()["character"]
    character = store.characters[UUID(created["character_id"])]

    nullable = CharacterResponse.from_domain(character).model_dump(mode="json")
    assert nullable["face_id"] is None
    assert nullable["voice_id"] is None
    assert nullable["accessory_ids"] == []

    populated_ids = [
        UUID(f"6100000{index}-0000-4000-8000-00000000000{index}") for index in range(1, 8)
    ]
    populated = replace(
        character,
        type_id=populated_ids[0],
        style_profile_id=populated_ids[1],
        identity_id=populated_ids[2],
        face_id=populated_ids[3],
        hair_id=populated_ids[4],
        accessory_ids=(populated_ids[5], populated_ids[6]),
        wardrobe_ids=(populated_ids[0],),
        uploaded_asset_ids=(populated_ids[1],),
        generated_asset_ids=(populated_ids[2],),
    )
    payload = CharacterResponse.from_domain(populated).model_dump(mode="json")
    assert payload["face_id"] == str(populated_ids[3])
    assert payload["hair_id"] == str(populated_ids[4])
    assert payload["accessory_ids"] == [str(populated_ids[5]), str(populated_ids[6])]
    assert payload["wardrobe_ids"] == [str(populated_ids[0])]


def test_missing_referenced_asset_returns_controlled_problem_details():
    client, _store, _principal = build_client()
    created = client.post(
        f"/api/v1/projects/{PROJECT_ID}/characters",
        headers={"Idempotency-Key": "missing-asset-create"},
        json={
            "production_id": str(PRODUCTION_ID),
            "display_name": "Missing Asset Character",
            "role": "Lead",
            "species_id": str(HUMAN_ID),
        },
    ).json()["character"]
    response = client.put(
        f"/api/v1/characters/{created['character_id']}/selections/hair",
        headers={"Idempotency-Key": "missing-asset-select"},
        json={
            "asset_id": "6f000001-0000-4000-8000-000000000001",
            "expected_version": created["version"],
        },
    )
    assert response.status_code == 404
    assert response.json()["code"] == "not_found"


def test_viewer_can_read_and_ten_reads_are_stable():
    client, store, principal_holder = build_client()
    created = client.post(
        f"/api/v1/projects/{PROJECT_ID}/characters",
        headers={"Idempotency-Key": "stable-read-create"},
        json={
            "production_id": str(PRODUCTION_ID),
            "display_name": "Stable Read Character",
            "role": "Lead",
            "species_id": str(HUMAN_ID),
        },
    ).json()["character"]
    viewer_id = UUID("10000000-0000-4000-8000-000000000099")
    store.project_roles[(PROJECT_ID, viewer_id)] = "Viewer"
    principal_holder["value"] = Principal(
        principal_id=viewer_id,
        workspace_id=WORKSPACE_ID,
        agent_id=AGENT_ID,
        agent_kind=AgentKind.HUMAN,
    )

    reads = [client.get(f"/api/v1/characters/{created['character_id']}") for _ in range(10)]
    assert all(response.status_code == 200 for response in reads)
    assert all(response.json() == reads[0].json() for response in reads[1:])


def test_accessory_endpoint_persists_multiple_ids_and_rejects_stale_version():
    client, store, _principal = build_client()
    accessory_ids = (
        UUID("32000002-0000-4000-8000-000000000001"),
        UUID("43000001-0000-4000-8000-000000000001"),
    )
    for asset_id, name in zip(accessory_ids, ("Aviator", "Fedora"), strict=True):
        store.assets[asset_id] = manifest(
            asset_id,
            name=name,
            category="accessory",
            species_ids=(HUMAN_ID,),
            capabilities=frozenset({"wears-accessories"}),
        )
    created = client.post(
        f"/api/v1/projects/{PROJECT_ID}/characters",
        headers={"Idempotency-Key": "accessory-api-create"},
        json={
            "production_id": str(PRODUCTION_ID),
            "display_name": "Accessory Character",
            "role": "Lead",
            "species_id": str(HUMAN_ID),
        },
    ).json()["character"]

    updated = client.put(
        f"/api/v1/characters/{created['character_id']}/accessories",
        headers={"Idempotency-Key": "accessory-api-update"},
        json={"asset_ids": [str(item) for item in accessory_ids], "expected_version": 1},
    )
    stale = client.put(
        f"/api/v1/characters/{created['character_id']}/accessories",
        headers={"Idempotency-Key": "accessory-api-stale"},
        json={"asset_ids": [str(accessory_ids[0])], "expected_version": 1},
    )

    assert updated.status_code == 200
    assert updated.json()["character"]["accessory_ids"] == [str(item) for item in accessory_ids]
    assert updated.json()["character"]["version"] == 2
    assert stale.status_code == 409
    assert stale.json()["code"] == "concurrency_conflict"
