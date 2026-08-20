import pytest

from app.application.character_service import CharacterApplicationService
from app.domain.enums import AgentKind
from app.domain.errors import InvariantViolation
from app.domain.types import Principal
from tests.character_fakes import (
    AGENT_ID,
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
)


def setup_service():
    store = FakeStore()
    service = CharacterApplicationService(
        FakeUnitOfWorkFactory(store), FakeAudit(store), FakeIdempotency(store)
    )
    principal = Principal(
        principal_id=PRINCIPAL_ID,
        workspace_id=WORKSPACE_ID,
        agent_id=AGENT_ID,
        agent_kind=AgentKind.HUMAN,
    )
    return service, principal, store


async def create_character(service: CharacterApplicationService, principal: Principal):
    return await service.create_character(
        principal,
        project_id=PROJECT_ID,
        production_id=PRODUCTION_ID,
        display_name="Christopher",
        role="Lead",
        species_id=HUMAN_ID,
        idempotency_key="phase3-create",
    )


async def test_identity_and_physical_properties_are_canonical_and_versioned():
    service, principal, _store = setup_service()
    created = await create_character(service, principal)
    identity = await service.update_identity_properties(
        principal,
        created.character.character_id,
        expected_version=1,
        identity_type="Human Male",
        gender_presentation="Masculine",
        idempotency_key="identity-properties",
    )
    physical = await service.update_physical_properties(
        principal,
        created.character.character_id,
        expected_version=2,
        age=41,
        apparent_age=38,
        height_cm=186,
        body_type="Athletic",
        skin_tone=72,
        idempotency_key="physical-properties",
    )
    assert identity.character.gender_presentation == "Masculine"
    assert physical.character.age == 41
    assert physical.character.apparent_age == 38
    assert physical.character.height_cm == 186
    assert physical.character.physical_profile_version == 2
    assert {item.stage for item in physical.character.downstream_status} == {
        "set",
        "studio",
        "review",
        "render",
    }


async def test_species_physical_ranges_are_enforced():
    service, principal, _store = setup_service()
    created = await create_character(service, principal)
    with pytest.raises(InvariantViolation, match="Height must be between"):
        await service.update_physical_properties(
            principal,
            created.character.character_id,
            expected_version=1,
            age=None,
            apparent_age=None,
            height_cm=300,
            body_type=None,
            skin_tone=None,
            idempotency_key="invalid-height",
        )


async def test_semantic_noop_does_not_increment_version_or_emit_outbox_event():
    service, principal, store = setup_service()
    created = await create_character(service, principal)
    selected = await service.select_asset(
        principal,
        created.character.character_id,
        category="voice",
        asset_id=SHARED_VOICE_ID,
        expected_version=1,
        idempotency_key="select-voice",
    )
    event_count = len(store.outbox)
    repeated = await service.select_asset(
        principal,
        created.character.character_id,
        category="voice",
        asset_id=SHARED_VOICE_ID,
        expected_version=2,
        idempotency_key="select-same-voice",
    )
    assert selected.character.version == 2
    assert repeated.character.version == 2
    assert repeated.change_summary["no_op"] is True
    assert len(store.outbox) == event_count


async def test_package_validation_returns_structured_blockers():
    service, principal, _store = setup_service()
    created = await create_character(service, principal)
    validated = await service.validate_character_package(
        principal,
        created.character.character_id,
        expected_version=1,
        idempotency_key="validate-package",
    )
    assert validated.character.readiness_status == "invalid"
    assert validated.character.validation_issues
    assert all(
        "code" in issue and "field" in issue for issue in validated.character.validation_issues
    )
