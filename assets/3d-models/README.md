# Nexkosmo 3D Asset Library

This directory is the canonical home for reusable 3D assets registered with the Nexkosmo Brain.

## Storage model

```text
assets/3d-models/
├── source/                 # Original imports, preserved unchanged
├── library/                # Approved production assets
│   ├── characters/
│   ├── creatures/
│   ├── animals/
│   ├── vehicles/
│   ├── aircraft/
│   ├── buildings/
│   ├── environments/
│   ├── vegetation/
│   ├── furniture/
│   ├── props/
│   ├── weapons/
│   ├── clothing/
│   ├── accessories/
│   └── architecture/
├── materials/
├── textures/
├── shaders/
├── rigs/
├── animations/
├── physics/
├── lod/
├── exports/                # Runtime and renderer-specific derivatives
├── previews/               # Thumbnails, turntables and inspection renders
├── metadata/               # Brain-readable records and searchable index
└── schemas/                # Validation rules for asset metadata
```

## Brain registration

Every approved 3D asset receives a permanent `asset_id` and a metadata record validated against `schemas/3d-asset.schema.json`.

The Brain uses these records to search, compare, relate, version and reuse assets without depending on filenames or folder locations.

Original imports must remain in `source/`. Cleanup, optimisation, retopology, rigging, conversion and renderer preparation produce new derivatives rather than overwriting the source.

## Naming convention

```text
3d_<category>_<subject>_<variant>_<asset-id>.<ext>
```

Example:

```text
3d_animals_horse_thoroughbred_bay_nks-3d-000001.glb
```

## Required metadata

- Stable asset ID, title, description and tags
- Category, subcategory and semantic aliases
- Source, working and approved file paths
- File formats and renderer compatibility
- Polygon, triangle and vertex counts
- Scale, units, orientation and bounding dimensions
- Materials, textures, UV sets and shaders
- Rig, skeleton and animation compatibility
- LOD levels, collision and physics configuration
- Licence, creator, provenance and import source
- Version, approval state and quality status
- Preview images and turntables
- Dependencies and related assets
- Projects, scenes and shots using the asset
- Checksum for duplicate detection and integrity

## Asset lifecycle

```text
Import -> Analyse -> Classify -> Validate -> Preview -> Approve -> Register -> Reuse -> Learn
```

Large binary assets should use Git LFS or an external asset store. Git should retain metadata, schemas, manifests, automation and lightweight previews. The Brain remains the canonical source of truth for identity, state, relationships, versions and production experience.
