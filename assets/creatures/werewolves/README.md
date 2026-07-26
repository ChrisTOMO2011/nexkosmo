# Nexkosmo Werewolf Asset Library

This directory is the canonical Brain library for werewolf production assets.

## Purpose

Store approved werewolf references, production sheets, metadata, rigs, animation references, materials, textures, audio, lore, and future 3D assets in a consistent reusable structure.

## Canonical structure

```text
werewolves/
├── identity/
├── portraits/
├── turnarounds/
├── anatomy/
├── skeleton/
├── muscles/
├── expressions/
├── eyes/
├── teeth/
├── claws/
├── fur/
├── variants/
│   ├── male/
│   ├── female/
│   ├── juvenile/
│   └── elder/
├── armour/
├── weapons/
├── rigging/
├── animations/
├── materials/
├── textures/
├── audio/
├── lore/
├── source-sheets/
├── separated-assets/
├── metadata/
└── schemas/
```

Git does not preserve empty folders. These directories are created as files are added.

## First registered asset

| Field | Value |
|---|---|
| Asset ID | `NKS-WRW-000001` |
| Name | Alpha Werewolf |
| Category | Creature |
| Species | Werewolf |
| Role | Alpha |
| Status | Registered - source image pending |
| Version | 1.0.0 |

## Source-sheet workflow

1. Preserve the original composite sheet in `source-sheets/`.
2. Separate useful panels into individual files in `separated-assets/`.
3. Classify each separated file into its production folder.
4. Create metadata for every retained file.
5. Validate naming, provenance, resolution, and duplication.
6. Approve the asset before production use.

## Naming standard

```text
<asset-id>_<content-type>_<view-or-variant>_v<version>.<ext>
```

Examples:

```text
NKS-WRW-000001_portrait_hero_v001.png
NKS-WRW-000001_turnaround_front_v001.png
NKS-WRW-000001_turnaround_side-left_v001.png
NKS-WRW-000001_anatomy_musculature_v001.png
NKS-WRW-000001_expression_snarl_v001.png
```

## Required metadata

Every approved asset should record:

- permanent Brain asset ID
- name and description
- species and role
- asset type and view
- creator or source
- original generation prompt when available
- source model or production tool
- creation date
- file format and dimensions
- checksum
- licence and usage rights
- tags and relationships
- compatible rigs and animations
- project usage
- approval state
- version history

## Current limitation

The library structure and first registration are now established, but the generated images from earlier chats are not present in the repository. They must be uploaded or provided as files before they can be separated and registered here.
