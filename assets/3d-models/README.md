# Nexkosmo 3D Models

This directory is reserved for Nexkosmo 3D model assets and related metadata.

## Intended structure

```text
assets/3d-models/
├── characters/
├── creatures/
├── environments/
├── props/
├── vehicles/
├── materials/
├── rigs/
├── animations/
├── source/
└── exports/
```

## Recommended asset rules

- Every model should have a persistent asset ID.
- Source files and exported runtime files should remain separate.
- Record model version, scale, units, orientation, rig version, materials, textures, licensing, and renderer compatibility.
- Prefer interoperable exchange formats such as glTF/GLB, FBX, USD, or Alembic where appropriate.
- Large binary assets should be stored using Git LFS or an external asset store rather than normal Git history.
- The Brain remains the canonical source of truth for asset identity, state, version, and continuity.

This README keeps the directory tracked in Git until model assets are added.