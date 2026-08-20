from dataclasses import dataclass
from uuid import UUID

from app.application.ports import CharacterAssetManifestRepository
from app.domain.characters import (
    SCALAR_SELECTION_FIELDS,
    Character,
    CharacterAssetManifest,
    Species,
)
from app.domain.errors import InvariantViolation, NotFound


@dataclass(frozen=True, slots=True)
class CompatibilityIssue:
    field: str
    asset_id: UUID
    reason: str


@dataclass(frozen=True, slots=True)
class CompatibilityValidation:
    valid: bool
    issues: tuple[CompatibilityIssue, ...]


@dataclass(frozen=True, slots=True)
class CompatibilityChangeSummary:
    previous_species_id: UUID
    species_id: UUID
    preserved_asset_ids: tuple[UUID, ...]
    cleared_asset_ids: tuple[UUID, ...]
    cleared_fields: tuple[str, ...]
    applied_default_asset_ids: tuple[UUID, ...]


COLLECTION_SELECTION_FIELDS: dict[str, str] = {
    "wardrobe": "wardrobe_ids",
    "accessory": "accessory_ids",
    "material": "material_ids",
    "texture": "texture_ids",
    "animation": "animation_ids",
}


def selected_assets(character: Character) -> dict[str, tuple[UUID, ...]]:
    values: dict[str, tuple[UUID, ...]] = {}
    for _category, field_name in SCALAR_SELECTION_FIELDS.items():
        asset_id = getattr(character, field_name)
        if asset_id is not None:
            values[field_name] = (asset_id,)
    for field_name in COLLECTION_SELECTION_FIELDS.values():
        values[field_name] = getattr(character, field_name)
    return values


class CharacterCompatibilityService:
    def __init__(self, assets: CharacterAssetManifestRepository) -> None:
        self._assets = assets

    @staticmethod
    def validate_manifest(
        *,
        character: Character,
        species: Species,
        manifest: CharacterAssetManifest,
        selected_ids: frozenset[UUID],
    ) -> tuple[str, ...]:
        reasons: list[str] = []
        if manifest.species_ids and species.species_id not in manifest.species_ids:
            reasons.append("asset is not declared for the selected species")
        if not manifest.required_capabilities.issubset(species.capabilities):
            reasons.append("species lacks required capabilities")
        if manifest.body_compatibility and character.body_id not in manifest.body_compatibility:
            reasons.append("body is incompatible")
        if manifest.rig_compatibility and character.rig_id not in manifest.rig_compatibility:
            reasons.append("rig is incompatible")
        if (
            manifest.skeleton_compatibility
            and character.skeleton_id not in manifest.skeleton_compatibility
        ):
            reasons.append("skeleton is incompatible")
        if manifest.material_compatibility and not set(character.material_ids).intersection(
            manifest.material_compatibility
        ):
            reasons.append("material profile is incompatible")
        if selected_ids.intersection(manifest.incompatible_asset_ids):
            reasons.append("asset conflicts with an existing selection")
        missing_dependencies = set(manifest.dependent_asset_ids).difference(selected_ids)
        if missing_dependencies:
            reasons.append("required dependent assets are not selected")
        if manifest.status not in {"available", "approved", "development-placeholder"}:
            reasons.append("asset is not available")
        return tuple(reasons)

    async def get_compatible_assets(
        self,
        *,
        character: Character,
        species: Species,
        category: str | None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[CharacterAssetManifest]:
        candidates = await self._assets.list_compatible(
            species_id=species.species_id,
            category=category,
            limit=limit,
            offset=offset,
        )
        current_ids = frozenset(
            asset_id for ids in selected_assets(character).values() for asset_id in ids
        )
        return [
            candidate
            for candidate in candidates
            if not self.validate_manifest(
                character=character,
                species=species,
                manifest=candidate,
                selected_ids=current_ids,
            )
        ]

    async def validate_asset_selection(
        self,
        *,
        character: Character,
        species: Species,
        asset_id: UUID,
    ) -> CharacterAssetManifest:
        manifest = await self._assets.get_by_id(asset_id)
        if manifest is None:
            raise NotFound("Character asset does not exist.")
        current_ids = frozenset(
            selected_id for ids in selected_assets(character).values() for selected_id in ids
        )
        reasons = self.validate_manifest(
            character=character,
            species=species,
            manifest=manifest,
            selected_ids=current_ids | {asset_id},
        )
        if reasons:
            raise InvariantViolation("; ".join(reasons))
        return manifest

    async def validate_character(
        self, *, character: Character, species: Species
    ) -> CompatibilityValidation:
        selections = selected_assets(character)
        all_ids = tuple(asset_id for values in selections.values() for asset_id in values)
        manifests = {item.asset_id: item for item in await self._assets.get_many(all_ids)}
        selected_ids = frozenset(all_ids)
        issues: list[CompatibilityIssue] = []
        for field_name, asset_ids in selections.items():
            for asset_id in asset_ids:
                manifest = manifests.get(asset_id)
                if manifest is None:
                    issues.append(CompatibilityIssue(field_name, asset_id, "asset does not exist"))
                    continue
                reasons = self.validate_manifest(
                    character=character,
                    species=species,
                    manifest=manifest,
                    selected_ids=selected_ids,
                )
                issues.extend(
                    CompatibilityIssue(field_name, asset_id, reason) for reason in reasons
                )
        return CompatibilityValidation(not issues, tuple(issues))

    async def clear_invalid_selections(
        self, *, character: Character, species: Species
    ) -> tuple[
        frozenset[str],
        tuple[UUID, ...],
        tuple[UUID, ...],
        dict[str, tuple[UUID, ...]],
    ]:
        validation = await self.validate_character(character=character, species=species)
        cleared_fields = frozenset(issue.field for issue in validation.issues)
        cleared_ids = tuple(dict.fromkeys(issue.asset_id for issue in validation.issues))
        all_ids = tuple(
            asset_id for values in selected_assets(character).values() for asset_id in values
        )
        preserved_ids = tuple(asset_id for asset_id in all_ids if asset_id not in cleared_ids)
        invalid_ids = frozenset(cleared_ids)
        preserved_collections = {
            field_name: tuple(asset_id for asset_id in asset_ids if asset_id not in invalid_ids)
            for field_name, asset_ids in selected_assets(character).items()
            if field_name in COLLECTION_SELECTION_FIELDS.values() and field_name in cleared_fields
        }
        return cleared_fields, cleared_ids, preserved_ids, preserved_collections

    @staticmethod
    def resolve_default_assets(species: Species) -> tuple[UUID, ...]:
        return tuple(
            asset_id
            for asset_id in (
                species.default_rig_id,
                species.default_skeleton_id,
                species.default_material_profile_id,
                species.default_body_id,
            )
            if asset_id is not None
        )

    @staticmethod
    def resolve_supported_tabs(species: Species) -> tuple[str, ...]:
        return species.supported_tabs

    @staticmethod
    def resolve_rig(species: Species) -> UUID | None:
        return species.default_rig_id

    @staticmethod
    def resolve_materials(species: Species) -> tuple[UUID, ...]:
        return (
            (species.default_material_profile_id,)
            if species.default_material_profile_id is not None
            else ()
        )
