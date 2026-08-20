from __future__ import annotations

import hashlib
import json
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any
from uuid import UUID

from app.application.character_compatibility import (
    CharacterCompatibilityService,
    CompatibilityChangeSummary,
)
from app.application.ports import (
    AuditDeliveryPort,
    IdempotencyPort,
    UnitOfWork,
    UnitOfWorkFactory,
)
from app.application.project_service import (
    EDIT_ROLES,
    READ_ROLES,
    require_project_role,
)
from app.domain.characters import Character, CharacterAssetManifest, PipelineStatus, Species
from app.domain.errors import ConcurrencyConflict, InvariantViolation, NotFound
from app.domain.rules import require_workspace
from app.domain.types import Principal


@dataclass(frozen=True, slots=True)
class CharacterMutationResult:
    character: Character
    change_summary: dict[str, Any]
    replayed_response: dict[str, Any] | None = None


CharacterTransform = Callable[[UnitOfWork, Character], Awaitable[tuple[Character, dict[str, Any]]]]


class CharacterApplicationService:
    def __init__(
        self,
        uow_factory: UnitOfWorkFactory,
        audit: AuditDeliveryPort,
        idempotency: IdempotencyPort,
    ) -> None:
        self._uow_factory = uow_factory
        self._audit = audit
        self._idempotency = idempotency

    async def create_character(
        self,
        principal: Principal,
        *,
        project_id: UUID,
        production_id: UUID,
        display_name: str,
        role: str,
        species_id: UUID,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        request_hash = self._hash(
            {
                "operation": "character.create",
                "project_id": str(project_id),
                "production_id": str(production_id),
                "display_name": display_name,
                "role": role,
                "species_id": str(species_id),
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            replay_character = await self.get_character(
                principal, UUID(claim.response["character"]["character_id"])
            )
            return CharacterMutationResult(replay_character, {}, claim.response)

        character: Character | None = None
        try:
            async with self._uow_factory(principal) as uow:
                await require_project_role(uow, principal, project_id, EDIT_ROLES)
                production = await uow.productions.get_by_id(production_id)
                if (
                    production is None
                    or production.project_id != project_id
                    or production.workspace_id != principal.workspace_id
                ):
                    raise NotFound("Production does not belong to the selected project.")
                species = await uow.species.get_by_id(species_id)
                if species is None or not species.enabled:
                    raise NotFound("Species does not exist or is disabled.")
                character = Character.create(
                    workspace_id=principal.workspace_id,
                    project_id=project_id,
                    production_id=production_id,
                    display_name=display_name,
                    role=role,  # type: ignore[arg-type]
                    species_id=species.species_id,
                    compatibility_profile_id=species.compatibility_profile_id,
                    body_id=species.default_body_id,
                    rig_id=species.default_rig_id,
                    skeleton_id=species.default_skeleton_id,
                    material_ids=(
                        (species.default_material_profile_id,)
                        if species.default_material_profile_id
                        else ()
                    ),
                )
                await uow.characters.add(character)
                await uow.outbox.append(
                    "character.created",
                    1,
                    {
                        "character_id": str(character.character_id),
                        "workspace_id": str(character.workspace_id),
                        "project_id": str(character.project_id),
                        "production_id": str(character.production_id),
                        "version": character.version,
                    },
                    aggregate_id=character.character_id,
                    aggregate_sequence=character.version,
                )
                response = self._mutation_response(character, {})
                await uow.idempotency.complete(idempotency_key, response)
                await self._queue_audit_success(
                    uow,
                    principal,
                    character,
                    idempotency_key=idempotency_key,
                    action="character.created",
                    previous_version=0,
                    summary={"species_id": str(species_id)},
                )
                await uow.commit()
            await self._deliver_audit(
                principal,
                idempotency_key,
                action="character.created",
            )
            return CharacterMutationResult(character, {})
        except Exception as exc:
            await self._mutation_failure(
                principal,
                idempotency_key,
                "character.created",
                character.character_id if character else None,
                exc,
            )
            raise

    async def get_character(self, principal: Principal, character_id: UUID) -> Character:
        async with self._uow_factory(principal) as uow:
            character = await uow.characters.get_by_id(character_id)
            if character is None:
                raise NotFound("Character does not exist.")
            require_workspace(principal, character.workspace_id)
            await require_project_role(uow, principal, character.project_id, READ_ROLES)
            return character

    async def list_project_characters(
        self,
        principal: Principal,
        project_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> list[Character]:
        async with self._uow_factory(principal) as uow:
            await require_project_role(uow, principal, project_id, READ_ROLES)
            return await uow.characters.list_by_project(project_id, limit=limit, offset=offset)

    async def list_production_characters(
        self,
        principal: Principal,
        production_id: UUID,
        *,
        limit: int,
        offset: int,
    ) -> list[Character]:
        async with self._uow_factory(principal) as uow:
            production = await uow.productions.get_by_id(production_id)
            if production is None:
                raise NotFound("Production does not exist.")
            await require_project_role(uow, principal, production.project_id, READ_ROLES)
            return await uow.characters.list_by_production(
                production_id, limit=limit, offset=offset
            )

    async def update_metadata(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        expected_version: int,
        display_name: str | None,
        role: str | None,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            _uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            updated = current.update_metadata(
                display_name=display_name,
                role=role,  # type: ignore[arg-type]
            )
            return updated, {
                "display_name": (
                    {"from": current.display_name, "to": updated.display_name}
                    if current.display_name != updated.display_name
                    else None
                ),
                "role": (
                    {"from": current.role, "to": updated.role}
                    if current.role != updated.role
                    else None
                ),
            }

        action = "character.renamed" if display_name is not None else "character.updated"
        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action=action,
            event_type="character.updated",
            request_payload={"display_name": display_name, "role": role},
            transform=transform,
        )

    async def update_identity_properties(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        expected_version: int,
        identity_type: str | None,
        gender_presentation: str | None,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            _uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            updated = current.update_identity_properties(
                identity_type=identity_type,
                gender_presentation=gender_presentation,
            )
            return updated, {
                "identity_type": identity_type,
                "gender_presentation": gender_presentation,
            }

        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="character.identity_properties_changed",
            event_type="character.identity_properties_changed",
            request_payload={
                "identity_type": identity_type,
                "gender_presentation": gender_presentation,
            },
            transform=transform,
        )

    async def update_physical_properties(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        expected_version: int,
        age: int | None,
        apparent_age: int | None,
        height_cm: int | None,
        body_type: str | None,
        skin_tone: int | None,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            species = await self._require_species(uow, current.species_id)
            effective_age = current.age if age is None else age
            effective_apparent_age = current.apparent_age if apparent_age is None else apparent_age
            effective_height = current.height_cm if height_cm is None else height_cm
            if not species.min_age <= effective_age <= species.max_age:
                raise InvariantViolation(
                    f"Age must be between {species.min_age} and {species.max_age} "
                    f"for {species.name}."
                )
            if not species.min_age <= effective_apparent_age <= species.max_age:
                raise InvariantViolation("Apparent age is outside the selected species range.")
            if not species.min_height_cm <= effective_height <= species.max_height_cm:
                raise InvariantViolation(
                    f"Height must be between {species.min_height_cm} and "
                    f"{species.max_height_cm} cm for {species.name}."
                )
            updated = current.update_physical_properties(
                age=age,
                apparent_age=apparent_age,
                height_cm=height_cm,
                body_type=body_type,
                skin_tone=skin_tone,
            )
            if updated is not current:
                updated = updated.invalidate_downstream(
                    reason="character physical profile changed",
                    stages=("set", "studio", "review", "render"),
                    increment_version=False,
                )
            return updated, {
                "age": age,
                "apparent_age": apparent_age,
                "height_cm": height_cm,
                "body_type": body_type,
                "skin_tone": skin_tone,
            }

        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="character.physical_profile_changed",
            event_type="character.physical_profile_changed",
            request_payload={
                "age": age,
                "apparent_age": apparent_age,
                "height_cm": height_cm,
                "body_type": body_type,
                "skin_tone": skin_tone,
            },
            transform=transform,
        )

    async def validate_character_package(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        expected_version: int,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            species = await self._require_species(uow, current.species_id)
            compatibility = await CharacterCompatibilityService(
                uow.character_assets
            ).validate_character(character=current, species=species)
            issues: list[dict[str, object]] = [
                {
                    "code": "incompatible-asset",
                    "field": issue.field,
                    "asset_id": str(issue.asset_id),
                    "message": issue.reason,
                    "blocking": True,
                }
                for issue in compatibility.issues
            ]
            required = {
                "style_profile_id": current.style_profile_id,
                "rig_id": current.rig_id,
                "skeleton_id": current.skeleton_id,
                "material_ids": current.material_ids,
                "texture_ids": current.texture_ids,
            }
            for field, value in required.items():
                if not value:
                    issues.append(
                        {
                            "code": "missing-required-selection",
                            "field": field,
                            "message": f"{field.replace('_', ' ')} is required.",
                            "blocking": True,
                        }
                    )
            if issues:
                status = "invalid"
            elif current.preview_asset_id is None:
                status = "processing-required"
                issues.append(
                    {
                        "code": "preview-assembly-required",
                        "field": "preview_asset_id",
                        "message": "Preview assembly must complete before Set readiness.",
                        "blocking": False,
                    }
                )
            else:
                status = "ready-for-set"
            updated = current.update_readiness(status=status, issues=tuple(issues))
            return updated, {"readiness_status": status, "issues": issues}

        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="character.package_validated",
            event_type="character.package_validated",
            request_payload={},
            transform=transform,
        )

    async def change_species(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        species_id: UUID,
        expected_version: int,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            if current.species_id == species_id:
                return current, {"species_id": str(species_id)}
            species = await uow.species.get_by_id(species_id)
            if species is None or not species.enabled:
                raise NotFound("Species does not exist or is disabled.")
            compatibility = CharacterCompatibilityService(uow.character_assets)
            (
                cleared_fields,
                cleared_ids,
                preserved_ids,
                preserved_collections,
            ) = await compatibility.clear_invalid_selections(character=current, species=species)
            defaults = compatibility.resolve_default_assets(species)
            updated = current.change_species(
                species_id=species.species_id,
                compatibility_profile_id=species.compatibility_profile_id,
                rig_id=compatibility.resolve_rig(species),
                skeleton_id=species.default_skeleton_id,
                body_id=species.default_body_id,
                material_ids=compatibility.resolve_materials(species),
                cleared_fields=cleared_fields,
                preserved_collections=preserved_collections,
            )
            summary = CompatibilityChangeSummary(
                previous_species_id=current.species_id,
                species_id=species.species_id,
                preserved_asset_ids=preserved_ids,
                cleared_asset_ids=cleared_ids,
                cleared_fields=tuple(sorted(cleared_fields)),
                applied_default_asset_ids=defaults,
            )
            return updated, {
                "previous_species_id": str(summary.previous_species_id),
                "species_id": str(summary.species_id),
                "preserved_asset_ids": [str(item) for item in summary.preserved_asset_ids],
                "cleared_asset_ids": [str(item) for item in summary.cleared_asset_ids],
                "cleared_fields": list(summary.cleared_fields),
                "applied_default_asset_ids": [
                    str(item) for item in summary.applied_default_asset_ids
                ],
                "downstream_invalidated": ["set", "studio", "review", "render"],
            }

        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="character.species_changed",
            event_type="character.species_changed",
            request_payload={"species_id": str(species_id)},
            transform=transform,
        )

    async def select_asset(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        category: str,
        asset_id: UUID,
        expected_version: int,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            species = await self._require_species(uow, current.species_id)
            compatibility = CharacterCompatibilityService(uow.character_assets)
            manifest = await compatibility.validate_asset_selection(
                character=current, species=species, asset_id=asset_id
            )
            if manifest.category != category and not (
                category == "type" and manifest.category == "identity"
            ):
                raise InvariantViolation("Asset category does not match the selection.")
            updated = current.update_selection(category, asset_id)
            if updated is not current:
                updated = updated.invalidate_downstream(
                    reason=f"character {category} selection changed",
                    stages=("set", "studio", "review", "render"),
                    increment_version=False,
                )
            return updated, {"category": category, "asset_id": str(asset_id)}

        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="character.asset_selected",
            event_type="character.asset_selected",
            request_payload={"category": category, "asset_id": str(asset_id)},
            transform=transform,
        )

    async def remove_asset_selection(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        category: str,
        expected_version: int,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            _uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            updated = current.remove_selection(category)
            if updated is not current:
                updated = updated.invalidate_downstream(
                    reason=f"character {category} selection removed",
                    stages=("set", "studio", "review", "render"),
                    increment_version=False,
                )
            return updated, {"category": category}

        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="character.asset_removed",
            event_type="character.asset_removed",
            request_payload={"category": category},
            transform=transform,
        )

    async def replace_accessories(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        asset_ids: tuple[UUID, ...],
        expected_version: int,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        return await self._replace_collection(
            principal,
            character_id,
            field="accessories",
            category="accessory",
            asset_ids=asset_ids,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
        )

    async def replace_wardrobe(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        asset_ids: tuple[UUID, ...],
        expected_version: int,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        return await self._replace_collection(
            principal,
            character_id,
            field="wardrobe",
            category="wardrobe",
            asset_ids=asset_ids,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
        )

    async def update_pipeline_status(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        status: PipelineStatus,
        expected_version: int,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            _uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            return current.update_pipeline_status(status), {
                "from": current.pipeline_status,
                "to": status,
            }

        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action="character.pipeline_status_changed",
            event_type="character.pipeline_status_changed",
            request_payload={"status": status},
            transform=transform,
        )

    async def get_compatible_assets(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[CharacterAssetManifest]:
        async with self._uow_factory(principal) as uow:
            character = await self._require_character(uow, character_id)
            await require_project_role(uow, principal, character.project_id, READ_ROLES)
            species = await self._require_species(uow, character.species_id)
            return await CharacterCompatibilityService(uow.character_assets).get_compatible_assets(
                character=character,
                species=species,
                category=category,
                limit=limit,
                offset=offset,
            )

    async def get_supported_tabs(self, principal: Principal, character_id: UUID) -> tuple[str, ...]:
        async with self._uow_factory(principal) as uow:
            character = await self._require_character(uow, character_id)
            await require_project_role(uow, principal, character.project_id, READ_ROLES)
            species = await self._require_species(uow, character.species_id)
            return CharacterCompatibilityService.resolve_supported_tabs(species)

    async def get_species_registry(self, principal: Principal) -> list[Species]:
        async with self._uow_factory(principal) as uow:
            return await uow.species.list_enabled()

    async def get_species(self, principal: Principal, species_id: UUID) -> Species:
        async with self._uow_factory(principal) as uow:
            return await self._require_species(uow, species_id)

    async def get_species_assets(
        self,
        principal: Principal,
        species_id: UUID,
        *,
        category: str | None,
        limit: int,
        offset: int,
    ) -> list[CharacterAssetManifest]:
        async with self._uow_factory(principal) as uow:
            await self._require_species(uow, species_id)
            return await uow.character_assets.list_by_species(
                species_id, category=category, limit=limit, offset=offset
            )

    async def get_asset_manifest(
        self, principal: Principal, asset_id: UUID
    ) -> CharacterAssetManifest:
        async with self._uow_factory(principal) as uow:
            manifest = await uow.character_assets.get_by_id(asset_id)
            if manifest is None:
                raise NotFound("Character asset does not exist.")
            return manifest

    async def get_downstream_status(
        self, principal: Principal, character_id: UUID
    ) -> tuple[Any, ...]:
        return (await self.get_character(principal, character_id)).downstream_status

    async def _replace_collection(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        field: str,
        category: str,
        asset_ids: tuple[UUID, ...],
        expected_version: int,
        idempotency_key: str,
    ) -> CharacterMutationResult:
        async def transform(
            uow: UnitOfWork, current: Character
        ) -> tuple[Character, dict[str, Any]]:
            species = await self._require_species(uow, current.species_id)
            compatibility = CharacterCompatibilityService(uow.character_assets)
            for asset_id in asset_ids:
                manifest = await compatibility.validate_asset_selection(
                    character=current, species=species, asset_id=asset_id
                )
                if manifest.category != category:
                    raise InvariantViolation(f"Asset {asset_id} is not in the {category} category.")
            updated = (
                current.replace_accessories(asset_ids)
                if field == "accessories"
                else current.replace_wardrobe(asset_ids)
            )
            if updated is not current:
                updated = updated.invalidate_downstream(
                    reason=f"character {field} changed",
                    stages=("set", "studio", "review", "render"),
                    increment_version=False,
                )
            return updated, {"asset_ids": [str(item) for item in asset_ids]}

        return await self._mutate(
            principal,
            character_id,
            expected_version=expected_version,
            idempotency_key=idempotency_key,
            action=f"character.{field}_changed",
            event_type="character.updated",
            request_payload={"field": field, "asset_ids": [str(item) for item in asset_ids]},
            transform=transform,
        )

    async def _mutate(
        self,
        principal: Principal,
        character_id: UUID,
        *,
        expected_version: int,
        idempotency_key: str,
        action: str,
        event_type: str,
        request_payload: dict[str, Any],
        transform: CharacterTransform,
    ) -> CharacterMutationResult:
        request_hash = self._hash(
            {
                "operation": action,
                "character_id": str(character_id),
                "expected_version": expected_version,
                **request_payload,
            }
        )
        claim = await self._idempotency.acquire(
            principal.workspace_id, idempotency_key, request_hash
        )
        if claim.state == "completed" and claim.response:
            character = await self.get_character(principal, character_id)
            return CharacterMutationResult(
                character,
                claim.response.get("change_summary", {}),
                claim.response,
            )

        current: Character | None = None
        updated: Character | None = None
        try:
            async with self._uow_factory(principal) as uow:
                current = await self._require_character(uow, character_id)
                await require_project_role(uow, principal, current.project_id, EDIT_ROLES)
                self._require_version(current, expected_version)
                updated, summary = await transform(uow, current)
                if updated.version == current.version:
                    response = self._mutation_response(current, {**summary, "no_op": True})
                    await uow.idempotency.complete(idempotency_key, response)
                    await uow.commit()
                    return CharacterMutationResult(current, {**summary, "no_op": True})
                await uow.characters.update(updated, expected_version=expected_version)
                await uow.outbox.append(
                    event_type,
                    1,
                    {
                        "character_id": str(updated.character_id),
                        "workspace_id": str(updated.workspace_id),
                        "project_id": str(updated.project_id),
                        "production_id": str(updated.production_id),
                        "previous_version": current.version,
                        "version": updated.version,
                        "change_summary": summary,
                    },
                    aggregate_id=updated.character_id,
                    aggregate_sequence=updated.version,
                )
                response = self._mutation_response(updated, summary)
                await uow.idempotency.complete(idempotency_key, response)
                await self._queue_audit_success(
                    uow,
                    principal,
                    updated,
                    idempotency_key=idempotency_key,
                    action=action,
                    previous_version=current.version,
                    summary=summary,
                )
                await uow.commit()
            await self._deliver_audit(principal, idempotency_key, action=action)
            return CharacterMutationResult(updated, summary)
        except Exception as exc:
            await self._mutation_failure(principal, idempotency_key, action, character_id, exc)
            raise

    @staticmethod
    async def _require_character(uow: UnitOfWork, character_id: UUID) -> Character:
        character = await uow.characters.get_by_id(character_id)
        if character is None:
            raise NotFound("Character does not exist.")
        return character

    @staticmethod
    async def _require_species(uow: UnitOfWork, species_id: UUID) -> Species:
        species = await uow.species.get_by_id(species_id)
        if species is None or not species.enabled:
            raise NotFound("Species does not exist or is disabled.")
        return species

    @staticmethod
    def _require_version(character: Character, expected_version: int) -> None:
        if character.version != expected_version:
            raise ConcurrencyConflict(
                f"Expected character version {expected_version}, found {character.version}."
            )

    @staticmethod
    def _hash(payload: dict[str, Any]) -> str:
        raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return hashlib.sha256(raw).hexdigest()

    @staticmethod
    def _mutation_response(character: Character, summary: dict[str, Any]) -> dict[str, Any]:
        return {
            "character": {
                "character_id": str(character.character_id),
                "project_id": str(character.project_id),
                "production_id": str(character.production_id),
                "display_name": character.display_name,
                "role": character.role,
                "identity_type": character.identity_type,
                "age": character.age,
                "apparent_age": character.apparent_age,
                "height_cm": character.height_cm,
                "body_type": character.body_type,
                "skin_tone": character.skin_tone,
                "gender_presentation": character.gender_presentation,
                "physical_profile_version": character.physical_profile_version,
                "species_id": str(character.species_id),
                **{
                    field: str(value) if value is not None else None
                    for field, value in {
                        "type_id": character.type_id,
                        "style_profile_id": character.style_profile_id,
                        "identity_id": character.identity_id,
                        "face_id": character.face_id,
                        "hair_id": character.hair_id,
                        "skin_id": character.skin_id,
                        "eyes_id": character.eyes_id,
                        "beard_id": character.beard_id,
                        "body_id": character.body_id,
                        "age_preset_id": character.age_preset_id,
                        "expression_id": character.expression_id,
                        "rig_id": character.rig_id,
                        "skeleton_id": character.skeleton_id,
                        "voice_id": character.voice_id,
                        "preview_asset_id": character.preview_asset_id,
                    }.items()
                },
                **{
                    field: [str(item) for item in values]
                    for field, values in {
                        "wardrobe_ids": character.wardrobe_ids,
                        "accessory_ids": character.accessory_ids,
                        "material_ids": character.material_ids,
                        "texture_ids": character.texture_ids,
                        "animation_ids": character.animation_ids,
                        "uploaded_asset_ids": character.uploaded_asset_ids,
                        "generated_asset_ids": character.generated_asset_ids,
                    }.items()
                },
                "compatibility_profile_id": str(character.compatibility_profile_id),
                "pipeline_status": character.pipeline_status,
                "readiness_status": character.readiness_status,
                "validation_issues": list(character.validation_issues),
                "validated_version": character.validated_version,
                "validated_at": (
                    character.validated_at.isoformat() if character.validated_at else None
                ),
                "downstream_status": [
                    {
                        "stage": item.stage,
                        "status": item.status,
                        "invalidated_at": (
                            item.invalidated_at.isoformat() if item.invalidated_at else None
                        ),
                        "reason": item.reason,
                    }
                    for item in character.downstream_status
                ],
                "version": character.version,
                "created_at": character.created_at.isoformat(),
                "updated_at": character.updated_at.isoformat(),
            },
            "change_summary": summary,
        }

    @staticmethod
    def _audit_key(action: str, idempotency_key: str, outcome: str) -> str:
        return f"{action}:{idempotency_key}:{outcome}"

    async def _queue_audit_success(
        self,
        uow: UnitOfWork,
        principal: Principal,
        character: Character,
        *,
        idempotency_key: str,
        action: str,
        previous_version: int,
        summary: dict[str, Any],
    ) -> None:
        await uow.audit_queue.enqueue(
            deduplication_key=self._audit_key(action, idempotency_key, "success"),
            principal=principal,
            action=action,
            outcome="success",
            resource_id=character.character_id,
            details={
                "tenant_id": str(character.workspace_id),
                "project_id": str(character.project_id),
                "production_id": str(character.production_id),
                "character_id": str(character.character_id),
                "previous_version": previous_version,
                "new_version": character.version,
                "change_summary": summary,
            },
        )

    async def _deliver_audit(
        self, principal: Principal, idempotency_key: str, *, action: str
    ) -> None:
        try:
            await self._audit.deliver(
                principal.workspace_id,
                self._audit_key(action, idempotency_key, "success"),
            )
        except Exception:
            # The durable queue row was committed with the operation. A delivery
            # outage must not turn a committed mutation into a client-visible failure.
            return

    async def _mutation_failure(
        self,
        principal: Principal,
        idempotency_key: str,
        action: str,
        resource_id: UUID | None,
        exc: Exception,
    ) -> None:
        error_code = getattr(exc, "code", "internal_error")
        try:
            await self._idempotency.fail(principal.workspace_id, idempotency_key, error_code)
        finally:
            await self._audit.record_or_queue(
                deduplication_key=self._audit_key(action, idempotency_key, "failure"),
                principal=principal,
                action=action,
                outcome="failure",
                resource_id=resource_id,
                details={"error": error_code},
            )
