# Architecture Amendment 002 — Native Asset Reconstruction

## Status

Canonical Brain policy. This revision supersedes every earlier rule that allowed production upscaling or super-resolution.

## Non-negotiable rule

**The Nexkosmo Brain must never create a production asset by enlarging a lower-resolution raster image.**

A source crop may be preserved, cleaned, analysed, or used as a visual reference, but it must not be resized beyond its native dimensions and presented as a 4K or 8K production asset.

The words `4K` and `8K` may only describe:

- a genuinely new native-resolution render;
- an original source that already meets the target dimensions;
- a verified production export rendered from vector, procedural, 3D, or other resolution-independent source data.

## Purpose

The Brain converts reference material into production assets through native reconstruction, not pixel enlargement. It must preserve evidence, extract design facts, select an appropriate renderer, generate a new asset at the requested native resolution, verify consistency, and require approval before canonisation.

## Governing workflow

```text
Immutable source
      ↓
Panel detection and native crop
      ↓
Reference analysis
      ↓
Structured design specification
      ↓
Native 4K/8K reconstruction
      ↓
Automated consistency checks
      ↓
Human visual review
      ↓
Canonical Brain registration
```

## Governing requirements

For every raster reference, the Brain must:

1. preserve the immutable original;
2. extract panels without enlarging them;
3. record native crop dimensions and checksum;
4. classify the asset by content type and importance;
5. extract canonical design facts into structured metadata;
6. choose a native reconstruction method;
7. render a new 4K or 8K asset from the design specification and references;
8. compare the result against the canonical references;
9. reject identity, anatomy, proportion, colour, marking, or silhouette drift;
10. require human approval before marking a reconstruction canonical;
11. retain complete provenance for the source, prompt, model, renderer, settings, checks, and approvals.

## Prohibited operations

The following operations are prohibited for production outputs:

- bicubic, bilinear, Lanczos, nearest-neighbour, or other enlargement;
- AI super-resolution used to manufacture production detail;
- enlarging a crop and applying sharpening or denoising;
- labelling an enlarged source crop as native 4K or native 8K;
- replacing an immutable source with a generated result;
- silently changing anatomy, identity, markings, colour, costume, geometry, or composition;
- approving a reconstruction solely because its pixel dimensions meet the target.

Small previews may be resized for interface display, but they must be marked `preview-only` and can never become production assets.

## Resolution profiles

The long edge defines the default profile unless a project supplies a fixed canvas.

| Profile | Native long edge | Use |
|---|---:|---|
| reference-native | unchanged | evidence and analysis |
| preview-only | up to 2048 px | interfaces only; never canonical production |
| production-4k-native | 4096 px | normal production assets |
| production-8k-native | 8192 px | hero, master, print, texture, and modelling references |

## Required source preservation

Every reconstructed asset package must retain:

```text
<asset-id>_source_original.<ext>
<asset-id>_source_crop_native_v001.png
<asset-id>_design_spec_v001.yaml
<asset-id>_reconstruction_4k_native_v001.png
<asset-id>_reconstruction_8k_native_v001.png
<asset-id>_verification_v001.json
```

Only outputs that were genuinely rendered should exist. Original files and native crops are immutable.

## Decision routes

### Route A — Native source accepted

Use only when the original source already meets or exceeds the required resolution and passes quality checks.

Permitted actions:

- native crop without enlargement;
- border removal;
- colour-profile normalisation;
- lossless rotation;
- alpha-edge cleanup at native dimensions;
- metadata registration.

### Route B — Native reconstruction from visual reference

Use when the source is visually informative but below production resolution.

Requirements:

- source remains a locked reference;
- renderer starts on a native 4K or 8K canvas;
- output is generated as new imagery, not enlarged pixels;
- canonical traits are supplied as constraints;
- provenance is `native-ai-reconstruction` or the exact renderer type;
- approval state begins as `needs-visual-review`.

### Route C — Reconstruction from canonical specification

Use when a small panel is insufficient alone, but related references and metadata define the asset.

The Brain must combine:

- linked identity masters;
- species anatomy rules;
- silhouette rules;
- canonical palette and markings;
- material or fur definitions;
- approved prompt components;
- pose, camera, lighting, and background requirements.

The result is a new related asset, not an enhanced copy.

### Route D — New source required

Use when the Brain cannot reconstruct faithfully.

The Brain must:

- preserve and register the reference;
- set status to `new-source-required`;
- explain which design facts are missing or contradictory;
- create no alleged production asset;
- request a better reference or an approved design decision.

## Automatic target selection

### Native 8K by default

- hero portraits;
- identity masters;
- modelling turnarounds;
- anatomy and musculature masters;
- texture and material masters;
- detailed environment plates;
- print design-bible sheets;
- assets marked `hero` or `master`.

### Native 4K by default

- secondary variants;
- transformation stages;
- expression sheets;
- props and weapon references;
- animation pose references;
- supporting environments;
- ordinary library assets.

### Reference only

- thumbnails;
- unresolved duplicates;
- rejected assets;
- temporary source crops;
- assets with unresolved licence or provenance;
- assets that fail source-integrity checks.

## Design specification

Before reconstruction, the Brain must create a machine-readable design specification containing relevant facts such as:

```yaml
identity:
  species: werewolf
  role: alpha
  age_class: adult
anatomy:
  stance: digitigrade
  shoulder_width: very-broad
  limb_proportions: canonical-alpha
silhouette:
  ear_shape: tall-pointed
  muzzle: long-heavy
  tail: full-low-set
materials:
  fur_length: medium-long
  fur_colours: [charcoal, black, cool-grey]
markings:
  facial_mask: canonical-alpha-v1
  chest_pattern: canonical-alpha-v1
render:
  target_profile: production-8k-native
  canvas_long_edge: 8192
  background: neutral-studio
  view: front-three-quarter
constraints:
  preserve_identity: true
  preserve_anatomy: true
  preserve_palette: true
  preserve_markings: true
```

## Verification gates

A native reconstruction cannot be marked `production-approved` unless all required checks pass:

- source and native crop preserved with checksums;
- design specification complete;
- output rendered natively at the requested dimensions;
- no resize-based production path used;
- subject not clipped;
- anatomy conforms to species and asset rules;
- identity and silhouette match approved references;
- proportions, colours, markings, materials, and costume remain within project thresholds;
- no duplicated limbs, malformed anatomy, text artefacts, tiling, or generative corruption;
- provenance and renderer settings complete;
- human visual review completed.

Numeric similarity scores are evidence, not automatic truth. The Brain must not claim false precision or auto-approve an asset merely because a score exceeds a threshold.

## Text handling

Infographic text must not be reconstructed inside an image model and treated as authoritative.

The Brain must:

1. preserve legible source text as reference;
2. store authoritative wording as structured metadata;
3. re-render labels using layout and typography tools after image creation;
4. mark unreadable or uncertain text for review.

## Brain metadata contract

```yaml
asset_id: NKS-WRW-000001
source_asset_id: NKS-SRC-WRW-000001
content_type: character-identity
importance: hero
source:
  width: 196
  height: 260
  checksum_sha256: "..."
  resized_for_production: false
reconstruction:
  target_profile: production-8k-native
  selected_route: native-ai-reconstruction
  target_long_edge: 8192
  native_canvas: true
  source_used_as_reference_only: true
  design_spec: NKS-WRW-000001_design_spec_v001.yaml
  renderer: "runtime-selected"
  renderer_version: "runtime-recorded"
  settings: {}
output:
  width: 6144
  height: 8192
  checksum_sha256: "..."
  provenance: native-ai-reconstruction
verification:
  status: needs-visual-review
  identity_match: pending
  anatomy_match: pending
  silhouette_match: pending
  palette_match: pending
  artefacts_detected: false
approval:
  state: pending
  approved_by: null
  approved_at: null
```

## Runtime guard

Every processing implementation must contain a hard guard equivalent to:

```python
if production_output and (output_width > source_width or output_height > source_height):
    if method in {"resize", "super_resolution", "progressive_scale", "upscale"}:
        raise ProductionUpscaleProhibitedError()
```

The guard does not block a newly rendered native canvas. It blocks any production path whose operation is enlargement of source pixels.

## Orchestration responsibility

The Brain owns policy, design constraints, provenance, and approval state. The Render Orchestrator selects replaceable tools that can perform native reconstruction. No renderer may weaken or bypass this policy.

## Learning loop

After review, the Brain stores:

- reconstruction route;
- renderer and version;
- design specification;
- prompt and constraints;
- verification findings;
- reviewer outcome;
- rejection reasons;
- runtime and resource cost.

Learned preferences may rank renderers or settings, but they may never re-enable production upscaling or bypass provenance and approval.

## Trigger behaviour

Invoke this policy when:

- a raster reference is imported;
- a panel is extracted from a source sheet;
- a user requests enhancement, cleanup, 4K, 8K, or production readiness;
- an asset is promoted to hero or master status;
- a renderer requires a resolution unavailable in the current native asset.

## Failure behaviour

If no compatible native reconstruction renderer is available, the Brain must:

- preserve and register the source;
- create a pending reconstruction job;
- record the requested target and missing capability;
- report that native reconstruction is unavailable or queued;
- never fall back to upscaling;
- never falsely label the source as 4K, 8K, enhanced, native, or production-approved.
