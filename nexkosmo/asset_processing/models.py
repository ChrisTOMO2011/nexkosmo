"""Core models for automatic asset registration."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path


class AssetKind(StrEnum):
    CHARACTER = "character"
    CREATURE = "creature"
    EYE = "eye"
    TEETH = "teeth"
    PAW = "paw"
    CLAW = "claw"
    FUR = "fur"
    SKIN = "skin"
    SKELETON = "skeleton"
    MUSCULATURE = "musculature"
    TURNAROUND = "turnaround"
    TRANSFORMATION = "transformation"
    EXPRESSION = "expression"
    PROP = "prop"
    WEAPON = "weapon"
    VEHICLE = "vehicle"
    ENVIRONMENT = "environment"
    MATERIAL = "material"
    TEXTURE = "texture"
    MODEL_3D = "3d-model"
    RIG = "rig"
    ANIMATION = "animation"
    MOTION_CAPTURE = "motion-capture"
    VFX = "vfx"
    CGI = "cgi"
    COMPOSITING = "compositing"
    SIMULATION = "simulation"
    SOUND_EFFECT = "sound-effect"
    FOLEY = "foley"
    DIALOGUE = "dialogue"
    MUSIC = "music"
    AMBIENCE = "ambience"
    AUDIO = "audio"
    VIDEO = "video"
    IMAGE = "image"
    DOCUMENT = "document"
    CODE = "code"
    ARCHIVE = "archive"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class RegistrationRequest:
    source: Path
    name: str | None = None
    species: str | None = None
    project: str = "default"
    declared_kind: AssetKind | None = None
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DetectionResult:
    kind: AssetKind
    confidence: float
    evidence: tuple[str, ...]
    species: str | None = None
    variant: str | None = None


@dataclass(frozen=True, slots=True)
class FolderPlan:
    root: Path
    directories: tuple[Path, ...]
    canonical_source: Path
    metadata_file: Path
    manifest_file: Path
    reconstruction_jobs: Path
    review_directory: Path


@dataclass(slots=True)
class RegistrationResult:
    asset_id: str
    detection: DetectionResult
    folder_plan: FolderPlan
    created_directories: list[Path] = field(default_factory=list)
    copied_source: Path | None = None
