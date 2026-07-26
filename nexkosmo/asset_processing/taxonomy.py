"""Canonical top-level taxonomy for automatic asset registration."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Domain(StrEnum):
    HUMANS = "humans"
    WEREWOLVES = "werewolves"
    VAMPIRES = "vampires"
    ANIMALS = "animals"
    CREATURES = "creatures"
    ALIENS = "aliens"
    ROBOTS = "robots"
    VEHICLES = "vehicles"
    ENVIRONMENTS = "environments"
    PROPS = "props"
    WEAPONS = "weapons"
    MATERIALS = "materials"
    AUDIO = "audio"
    VIDEO = "video"
    DOCUMENTS = "documents"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class TaxonomyMatch:
    domain: Domain
    family: str | None = None
    species: str | None = None
    subtype: str | None = None
    confidence: float = 0.0
    evidence: tuple[str, ...] = ()


_CANONICAL_TERMS: dict[Domain, tuple[str, ...]] = {
    Domain.HUMANS: ("human", "person", "man", "woman", "male", "female"),
    Domain.WEREWOLVES: ("werewolf", "werewolves", "lycan", "lycanthrope"),
    Domain.VAMPIRES: ("vampire", "vampires", "nosferatu"),
    Domain.ANIMALS: (
        "animal",
        "wolf",
        "dog",
        "cat",
        "horse",
        "lion",
        "tiger",
        "bear",
        "bird",
        "eagle",
        "shark",
        "reptile",
    ),
    Domain.ALIENS: ("alien", "extraterrestrial"),
    Domain.ROBOTS: ("robot", "android", "mech", "cyborg"),
    Domain.VEHICLES: ("vehicle", "car", "truck", "ship", "aircraft", "spaceship"),
    Domain.ENVIRONMENTS: ("environment", "forest", "city", "mountain", "interior", "landscape"),
    Domain.PROPS: ("prop", "object", "furniture", "tool"),
    Domain.WEAPONS: ("weapon", "sword", "gun", "rifle", "axe", "bow"),
    Domain.MATERIALS: ("material", "texture", "fur", "skin", "metal", "wood", "stone"),
    Domain.AUDIO: ("audio", "sound", "voice", "music", "dialogue", "sfx"),
    Domain.VIDEO: ("video", "footage", "clip", "animation"),
    Domain.DOCUMENTS: ("document", "script", "storyboard", "brief", "bible", "specification"),
}


def detect_domain(text: str) -> TaxonomyMatch:
    """Detect the strongest canonical domain from names, tags, or model output.

    More specific supernatural domains are intentionally evaluated before broad
    categories such as animals or creatures. A werewolf must therefore register
    under ``werewolves`` rather than ``animals/wolf``.
    """

    normalized = text.casefold()
    priority = (
        Domain.WEREWOLVES,
        Domain.VAMPIRES,
        Domain.HUMANS,
        Domain.ALIENS,
        Domain.ROBOTS,
        Domain.ANIMALS,
        Domain.VEHICLES,
        Domain.ENVIRONMENTS,
        Domain.WEAPONS,
        Domain.PROPS,
        Domain.MATERIALS,
        Domain.AUDIO,
        Domain.VIDEO,
        Domain.DOCUMENTS,
    )

    for domain in priority:
        matches = tuple(term for term in _CANONICAL_TERMS.get(domain, ()) if term in normalized)
        if matches:
            return TaxonomyMatch(
                domain=domain,
                confidence=min(0.99, 0.75 + (0.05 * len(matches))),
                evidence=matches,
            )

    return TaxonomyMatch(
        domain=Domain.CREATURES,
        confidence=0.25,
        evidence=("no canonical domain term matched",),
    )
