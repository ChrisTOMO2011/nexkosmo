"""Build canonical folder hierarchies from detected asset identity."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from .models import AssetKind
from .taxonomy import Domain, TaxonomyMatch


@dataclass(frozen=True, slots=True)
class IdentityHierarchy:
    domain: Domain
    family: str | None = None
    species: str | None = None
    individual: str | None = None
    asset_kind: AssetKind = AssetKind.UNKNOWN
    variant: str | None = None


_STANDARD_SUBFOLDERS: tuple[str, ...] = (
    "source",
    "metadata",
    "references",
    "design-specs",
    "reconstructions",
    "review",
    "production",
    "versions",
)

_COMPONENT_FOLDERS: dict[AssetKind, tuple[str, ...]] = {
    AssetKind.CHARACTER: ("identity", "portraits", "expressions", "poses", "turnarounds"),
    AssetKind.CREATURE: ("identity", "anatomy", "behaviours", "turnarounds"),
    AssetKind.EYE: ("eyes", "iris", "pupil", "sclera", "wetness", "reflections"),
    AssetKind.TEETH: ("teeth", "fangs", "gums", "bite-reference"),
    AssetKind.PAW: ("paws", "pads", "claws", "contact-reference"),
    AssetKind.CLAW: ("claws", "materials", "damage-variants"),
    AssetKind.FUR: ("fur", "grooms", "maps", "swatches"),
    AssetKind.SKIN: ("skin", "maps", "swatches"),
    AssetKind.SKELETON: ("anatomy", "skeleton", "joints"),
    AssetKind.MUSCULATURE: ("anatomy", "musculature", "deformation-reference"),
    AssetKind.TURNAROUND: ("turnarounds", "front", "side", "back", "three-quarter"),
    AssetKind.TRANSFORMATION: ("transformations", "stages", "timing", "continuity"),
    AssetKind.EXPRESSION: ("expressions", "neutral", "emotion", "phonemes"),
    AssetKind.PROP: ("props", "models", "materials", "turnarounds"),
    AssetKind.WEAPON: ("weapons", "models", "materials", "damage-variants"),
    AssetKind.VEHICLE: ("vehicles", "models", "interiors", "materials", "lods"),
    AssetKind.ENVIRONMENT: ("environments", "layouts", "lighting", "materials", "set-dressing"),
    AssetKind.MATERIAL: ("materials", "maps", "swatches", "presets"),
    AssetKind.TEXTURE: ("textures", "source", "maps", "tiles"),
    AssetKind.AUDIO: ("audio", "masters", "stems", "metadata"),
    AssetKind.VIDEO: ("video", "masters", "proxies", "metadata"),
    AssetKind.DOCUMENT: ("documents", "source", "exports", "metadata"),
}


def slugify(value: str) -> str:
    """Return a stable lowercase path segment."""

    slug = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return slug or "unknown"


def from_taxonomy(
    taxonomy: TaxonomyMatch,
    *,
    asset_kind: AssetKind,
    individual: str | None = None,
    variant: str | None = None,
) -> IdentityHierarchy:
    """Convert a taxonomy match into a complete registration hierarchy."""

    return IdentityHierarchy(
        domain=taxonomy.domain,
        family=taxonomy.family,
        species=taxonomy.species,
        individual=individual,
        asset_kind=asset_kind,
        variant=variant,
    )


def build_asset_root(base: Path, hierarchy: IdentityHierarchy) -> Path:
    """Build Domain / Family / Species / Individual / Asset Type / Variant."""

    parts = [base, Path(hierarchy.domain.value)]
    for value in (
        hierarchy.family,
        hierarchy.species,
        hierarchy.individual,
        hierarchy.asset_kind.value,
        hierarchy.variant,
    ):
        if value:
            parts.append(Path(slugify(value)))

    root = parts[0]
    for part in parts[1:]:
        root /= part
    return root


def planned_directories(base: Path, hierarchy: IdentityHierarchy) -> tuple[Path, ...]:
    """Return every folder the registrar should create for this asset."""

    root = build_asset_root(base, hierarchy)
    names = list(_STANDARD_SUBFOLDERS)
    names.extend(_COMPONENT_FOLDERS.get(hierarchy.asset_kind, ()))

    ordered_unique = tuple(dict.fromkeys(names))
    return (root,) + tuple(root / name for name in ordered_unique)


def example_werewolf_eye(base: Path = Path("assets")) -> tuple[Path, ...]:
    """Reference structure for an Alpha werewolf amber-eye master."""

    hierarchy = IdentityHierarchy(
        domain=Domain.WEREWOLVES,
        family="lycanthropes",
        species="werewolf",
        individual="alpha",
        asset_kind=AssetKind.EYE,
        variant="amber-master",
    )
    return planned_directories(base, hierarchy)
