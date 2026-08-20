from uuid import UUID, uuid4

import pytest

from app.application.character_service import CharacterApplicationService
from app.domain.enums import AgentKind
from app.domain.errors import ConcurrencyConflict, InvariantViolation, NotFound
from app.domain.types import Principal
from tests.character_fakes import (
    AGENT_ID,
    GOBLIN_ID,
    GOBLIN_RIG_ID,
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


def setup_service():
    store = FakeStore()
    audit = FakeAudit(store)
    idempotency = FakeIdempotency(store)
    service = CharacterApplicationService(FakeUnitOfWorkFactory(store), audit, idempotency)
    principal = Principal(
        principal_id=PRINCIPAL_ID,
        workspace_id=WORKSPACE_ID,
        agent_id=AGENT_ID,
        agent_kind=AgentKind.HUMAN,
    )
    return service, principal, store, audit


async def create_character(service, principal, *, key="create-1"):
    return await service.create_character(
        principal,
        project_id=PROJECT_ID,
        production_id=PRODUCTION_ID,
        display_name="Christopher",
        role="Lead",
        species_id=HUMAN_ID,
        idempotency_key=key,
    )


async def test_create_retrieve_and_list_character_with_audit_and_outbox():
    service, principal, store, audit = setup_service()
    created = await create_character(service, principal)
    loaded = await service.get_character(principal, created.character.character_id)
    by_project = await service.list_project_characters(principal, PROJECT_ID, limit=50, offset=0)
    by_production = await service.list_production_characters(
        principal, PRODUCTION_ID, limit=50, offset=0
    )
    assert loaded == created.character
    assert by_project == [created.character]
    assert by_production == [created.character]
    assert store.outbox[0]["event_type"] == "character.created"
    assert audit.records[0]["action"] == "character.created"


async def test_idempotent_create_does_not_duplicate():
    service, principal, store, _audit = setup_service()
    first = await create_character(service, principal, key="same-key")
    replay = await create_character(service, principal, key="same-key")
    assert replay.replayed_response is not None
    assert replay.character.character_id == first.character.character_id
    assert len(store.characters) == 1
    assert len(store.outbox) == 1


async def test_idempotent_selection_does_not_duplicate_relationship_or_event():
    service, principal, store, _audit = setup_service()
    created = await create_character(service, principal)
    first = await service.select_asset(
        principal,
        created.character.character_id,
        category="voice",
        asset_id=SHARED_VOICE_ID,
        expected_version=1,
        idempotency_key="same-selection",
    )
    replay = await service.select_asset(
        principal,
        created.character.character_id,
        category="voice",
        asset_id=SHARED_VOICE_ID,
        expected_version=1,
        idempotency_key="same-selection",
    )
    assert first.character.voice_id == SHARED_VOICE_ID
    assert replay.replayed_response is not None
    assert replay.character.version == 2
    assert len(store.outbox) == 2


async def test_versions_increment_and_stale_mutation_conflicts():
    service, principal, _store, _audit = setup_service()
    created = await create_character(service, principal)
    updated = await service.update_metadata(
        principal,
        created.character.character_id,
        expected_version=1,
        display_name="Christopher Vale",
        role=None,
        idempotency_key="rename-1",
    )
    assert updated.character.version == 2
    with pytest.raises(ConcurrencyConflict):
        await service.update_metadata(
            principal,
            created.character.character_id,
            expected_version=1,
            display_name="Stale",
            role=None,
            idempotency_key="rename-stale",
        )


async def test_human_only_asset_is_rejected_for_goblin_and_shared_asset_is_allowed():
    service, principal, _store, _audit = setup_service()
    created = await create_character(service, principal)
    changed = await service.change_species(
        principal,
        created.character.character_id,
        species_id=GOBLIN_ID,
        expected_version=1,
        idempotency_key="species-goblin",
    )
    with pytest.raises(InvariantViolation):
        await service.select_asset(
            principal,
            changed.character.character_id,
            category="hair",
            asset_id=HUMAN_HAIR_ID,
            expected_version=2,
            idempotency_key="goblin-hair",
        )
    voice = await service.select_asset(
        principal,
        changed.character.character_id,
        category="voice",
        asset_id=SHARED_VOICE_ID,
        expected_version=2,
        idempotency_key="goblin-voice",
    )
    assert voice.character.voice_id == SHARED_VOICE_ID


async def test_species_asset_queries_and_supported_tabs_are_authoritative():
    service, principal, _store, _audit = setup_service()
    created = await create_character(service, principal)
    human_assets = await service.get_species_assets(
        principal, HUMAN_ID, category=None, limit=100, offset=0
    )
    goblin_assets = await service.get_species_assets(
        principal, GOBLIN_ID, category=None, limit=100, offset=0
    )
    human_ids = {item.asset_id for item in human_assets}
    goblin_ids = {item.asset_id for item in goblin_assets}
    assert HUMAN_HAIR_ID in human_ids
    assert HUMAN_HAIR_ID not in goblin_ids
    assert SHARED_VOICE_ID in human_ids
    assert SHARED_VOICE_ID in goblin_ids
    assert await service.get_supported_tabs(principal, created.character.character_id) == (
        "Identity",
        "Hair",
        "Voice",
    )


async def test_species_change_preserves_shared_and_clears_incompatible_assets():
    service, principal, _store, _audit = setup_service()
    created = await create_character(service, principal)
    with_voice = await service.select_asset(
        principal,
        created.character.character_id,
        category="voice",
        asset_id=SHARED_VOICE_ID,
        expected_version=1,
        idempotency_key="human-voice",
    )
    with_hair = await service.select_asset(
        principal,
        created.character.character_id,
        category="hair",
        asset_id=HUMAN_HAIR_ID,
        expected_version=2,
        idempotency_key="human-hair",
    )
    changed = await service.change_species(
        principal,
        created.character.character_id,
        species_id=GOBLIN_ID,
        expected_version=3,
        idempotency_key="change-goblin",
    )
    assert with_voice.character.voice_id == SHARED_VOICE_ID
    assert with_hair.character.hair_id == HUMAN_HAIR_ID
    assert changed.character.voice_id == SHARED_VOICE_ID
    assert changed.character.hair_id is None
    assert changed.character.rig_id == GOBLIN_RIG_ID
    assert str(HUMAN_HAIR_ID) in changed.change_summary["cleared_asset_ids"]
    assert "hair_id" in changed.change_summary["cleared_fields"]


async def test_species_change_preserves_compatible_items_in_mixed_accessory_collection():
    service, principal, store, _audit = setup_service()
    shared_accessory_id = UUID("43000001-0000-4000-8000-000000000010")
    human_accessory_id = UUID("43000001-0000-4000-8000-000000000011")
    store.assets[shared_accessory_id] = manifest(
        shared_accessory_id,
        name="Shared Glasses",
        category="accessory",
        species_ids=(HUMAN_ID, GOBLIN_ID),
        capabilities=frozenset({"wears-accessories"}),
    )
    store.assets[human_accessory_id] = manifest(
        human_accessory_id,
        name="Human Glasses",
        category="accessory",
        species_ids=(HUMAN_ID,),
        capabilities=frozenset({"wears-accessories"}),
    )
    created = await create_character(service, principal, key="mixed-accessories")
    selected = await service.replace_accessories(
        principal,
        created.character.character_id,
        asset_ids=(shared_accessory_id, human_accessory_id),
        expected_version=1,
        idempotency_key="select-mixed-accessories",
    )

    changed = await service.change_species(
        principal,
        created.character.character_id,
        species_id=GOBLIN_ID,
        expected_version=selected.character.version,
        idempotency_key="change-goblin-mixed-accessories",
    )

    assert changed.character.accessory_ids == (shared_accessory_id,)
    assert changed.character.version == selected.character.version + 1
    assert str(shared_accessory_id) in changed.change_summary["preserved_asset_ids"]
    assert str(human_accessory_id) in changed.change_summary["cleared_asset_ids"]
    assert "accessory_ids" in changed.change_summary["cleared_fields"]


async def test_unknown_species_and_asset_return_safe_domain_errors():
    service, principal, store, audit = setup_service()
    created = await create_character(service, principal)
    original = store.characters[created.character.character_id]
    original_event_count = len(store.outbox)
    with pytest.raises(NotFound):
        await service.change_species(
            principal,
            created.character.character_id,
            species_id=uuid4(),
            expected_version=1,
            idempotency_key="unknown-species",
        )
    with pytest.raises(NotFound):
        await service.select_asset(
            principal,
            created.character.character_id,
            category="hair",
            asset_id=uuid4(),
            expected_version=1,
            idempotency_key="unknown-asset",
        )
    assert store.characters[created.character.character_id] == original
    assert len(store.outbox) == original_event_count
    assert [record["outcome"] for record in audit.records] == [
        "success",
        "failure",
        "failure",
    ]


async def test_accessory_replacement_preserves_categories_and_increments_once():
    service, principal, store, _audit = setup_service()
    accessory_ids = (
        UUID("32000002-0000-4000-8000-000000000001"),
        UUID("43000001-0000-4000-8000-000000000001"),
        UUID("43000006-0000-4000-8000-000000000001"),
    )
    for asset_id, name in zip(accessory_ids, ("Aviator", "Fedora", "Stud"), strict=True):
        store.assets[asset_id] = manifest(
            asset_id,
            name=name,
            category="accessory",
            species_ids=(HUMAN_ID,),
            capabilities=frozenset({"wears-accessories"}),
        )

    created = await create_character(service, principal, key="accessory-character")
    with_glasses = await service.replace_accessories(
        principal,
        created.character.character_id,
        asset_ids=(accessory_ids[0],),
        expected_version=1,
        idempotency_key="accessory-glasses",
    )
    with_hat = await service.replace_accessories(
        principal,
        created.character.character_id,
        asset_ids=(accessory_ids[0], accessory_ids[1]),
        expected_version=2,
        idempotency_key="accessory-hat",
    )
    with_jewellery = await service.replace_accessories(
        principal,
        created.character.character_id,
        asset_ids=accessory_ids,
        expected_version=3,
        idempotency_key="accessory-jewellery",
    )
    without_hat = await service.replace_accessories(
        principal,
        created.character.character_id,
        asset_ids=(accessory_ids[0], accessory_ids[2]),
        expected_version=4,
        idempotency_key="accessory-remove-hat",
    )

    assert with_glasses.character.version == 2
    assert with_hat.character.accessory_ids == accessory_ids[:2]
    assert with_jewellery.character.accessory_ids == accessory_ids
    assert with_jewellery.character.version == 4
    assert without_hat.character.accessory_ids == (accessory_ids[0], accessory_ids[2])
    assert without_hat.character.version == 5
    with pytest.raises(ConcurrencyConflict):
        await service.replace_accessories(
            principal,
            created.character.character_id,
            asset_ids=(accessory_ids[1],),
            expected_version=4,
            idempotency_key="accessory-stale",
        )
    assert store.characters[created.character.character_id] == without_hat.character
