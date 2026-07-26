# Canonical Human Base Male

This asset is the default faceless male proxy for human characters that do not yet have a finished bespoke 3D model.

## Canonical identity

- Asset ID: `NKS-3D-CHAR-HUMAN-BASE-MALE-000001`
- Asset type: character base mesh
- Role: temporary production proxy
- Status: awaiting binary model
- Canonical replacement policy: character identity remains unchanged when this proxy is replaced by a final character mesh

## Intended use

Use this asset for:

- scene blocking and layout
- scale and proportion checks
- camera and lighting tests
- clothing and equipment fitting
- basic rig and animation tests
- placeholder rendering

Do not treat this asset as final character likeness, final facial anatomy, or an approved hero mesh.

## Required folder contents

```text
human_base_male/
├── README.md
├── metadata/
│   └── human_base_male.json
├── source/          # original imported mesh, preserved unchanged
├── rig/             # compatible proxy rig and skeleton derivatives
├── materials/       # neutral proxy materials
├── textures/        # optional proxy textures
├── previews/        # front, side, back and turntable previews
└── exports/         # GLB, FBX, USD or renderer-specific derivatives
```

## Model requirements

The first approved binary should be:

- adult male human proportions
- neutral anatomical form
- no unique face or recognisable identity
- neutral expression
- clean topology suitable for deformation
- symmetrical base pose
- real-world scale in metres
- Y-up orientation unless a derivative explicitly states otherwise
- free of embedded copyrighted character likenesses
- accompanied by licence and provenance metadata

## Replacement workflow

```text
Character registered
-> Canonical Human Base Male assigned as proxy
-> Character-specific proportions, clothing and head developed
-> Final production mesh approved
-> Proxy relationship retired
-> Character canonical ID remains unchanged
```

The proxy is a reusable dependency, not the canonical identity of any character using it.
