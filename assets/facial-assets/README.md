# Nexkosmo Facial Asset Library

This directory is the canonical home for reusable facial assets registered with the Nexkosmo Brain.

The library is PNG-first for 2D facial components, overlays, texture details, expression sheets and visemes. Three-dimensional geometry, rigs and animation data remain separated in their native formats.

## Canonical structure

```text
assets/facial-assets/
├── source/                     # Original files, never overwritten
├── 2d/
│   └── png/
│       ├── eyes/
│       ├── eyebrows/
│       ├── mouths/
│       ├── expressions/
│       ├── visemes/
│       ├── wrinkles/
│       ├── makeup/
│       ├── scars/
│       ├── facial-hair/
│       ├── skin-details/
│       ├── tattoos/
│       ├── masks/
│       └── decals/
├── 3d/                         # Face meshes and sculpted components
├── rigs/                       # Facial rigs and control systems
├── animations/                 # Facial animation and performance data
├── textures/                   # Full texture sets and non-PNG maps
├── previews/                   # Contact sheets and inspection previews
├── metadata/                   # Brain-readable asset records and index
└── schemas/                    # Validation rules
```

## PNG requirements

PNG facial assets should use transparency where appropriate and retain a lossless master. Every approved PNG should record:

- stable asset ID
- category and semantic tags
- character and rig compatibility
- canvas dimensions and aspect ratio
- colour space and bit depth
- transparent-background status
- anchor points and facial region
- expression, viseme or phoneme meaning
- layer order and blending guidance
- source, creator, licence and provenance
- related character identities and projects
- checksum for duplicate detection

## Naming convention

```text
face_<category>_<description>_<variant>_<asset-id>.png
```

Example:

```text
face_mouth_viseme_aa_front_nks-face-000001.png
```

## Brain lifecycle

```text
Import -> Analyse -> Classify -> Validate -> Preview -> Approve -> Register -> Reuse -> Learn
```

The Brain remains the canonical source of truth for identity, compatibility, version, relationships and production use. Original files remain under `source/`; approved derivatives are stored in the correct library category.
