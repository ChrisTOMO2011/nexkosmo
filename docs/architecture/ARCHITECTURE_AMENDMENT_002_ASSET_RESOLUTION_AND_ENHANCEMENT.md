# Architecture Amendment 002 — Asset Resolution and Enhancement

## Status

Canonical Brain policy.

## Purpose

The Nexkosmo Brain must treat asset resolution conversion as an explicit production decision, not as a blind resize operation. Whenever a source image or extracted panel is registered, the Brain must inspect its quality, select the safest conversion route, preserve the original source, and generate production derivatives when required.

## Governing rule

For every raster asset, the Brain must:

1. preserve the immutable source file;
2. inspect dimensions, sharpness, compression, noise, text density, edge quality, transparency, and subject coverage;
3. classify the asset by content type;
4. select a conversion route;
5. produce a 4K or 8K derivative when policy requires it;
6. never overwrite the source;
7. record all processing, models, settings, checksums, and quality decisions in metadata;
8. require visual review before an AI-reconstructed derivative becomes production-approved.

## Resolution targets

The term 4K or 8K refers to the long edge unless a production profile defines a fixed canvas.

| Profile | Long edge | Typical use |
|---|---:|---|
| preview | 2048 px | UI previews and browsing |
| production-4k | 4096 px | standard production reference |
| production-8k | 8192 px | hero assets, detailed materials, print and close inspection |

The Brain must preserve aspect ratio unless the target profile explicitly requests a canvas or crop.

## Required source preservation

Every registered raster asset must retain:

```text
<asset-id>_source_original.<ext>
<asset-id>_source_crop_v001.png
<asset-id>_enhanced_4k_v001.png
<asset-id>_enhanced_8k_v001.png
```

Only derivatives that were actually generated should exist. The source is immutable.

## Decision routes

### Route A — Preserve and crop

Use when the extracted panel already contains sufficient native detail for the requested target.

Actions:

- exact panel crop;
- border and neighbouring-panel removal;
- colour-profile normalisation;
- lossless export where practical;
- no generative reconstruction.

### Route B — Restoration and super-resolution

Use when the source is usable but below the target resolution.

Actions may include:

- deblocking;
- denoising;
- deblurring;
- controlled sharpening;
- colour and exposure correction;
- non-generative or conservative AI super-resolution;
- alpha-edge refinement where transparency is requested.

The Brain must not materially alter anatomy, identity, proportions, markings, colours, costume, geometry, or composition.

### Route C — AI-assisted reconstruction

Use when the panel is too small or damaged for reliable restoration, but enough design information remains to reconstruct it.

Requirements:

- use the source crop as a locked visual reference;
- preserve canonical identity and design traits;
- generate a new derivative rather than replacing the source;
- mark provenance as `ai-reconstructed`;
- set approval state to `needs-visual-review`;
- calculate a design-consistency score;
- reject the output when identity or anatomy drifts beyond policy thresholds.

### Route D — Regeneration required

Use when the source lacks enough information for reliable reconstruction.

Requirements:

- do not claim the result is an enhanced copy;
- mark the source asset as `regeneration-recommended`;
- generate from canonical metadata, prompts, references, and linked identity assets;
- register the output as a new version or related asset;
- require human approval.

## Automatic target selection

The default target is determined by asset importance and content type.

### Generate 8K by default

- hero character portraits;
- identity masters;
- turnarounds used for modelling;
- anatomy and musculature references;
- texture and material masters;
- detailed environment plates;
- print-design-bible sheets;
- assets explicitly marked `hero` or `master`.

### Generate 4K by default

- secondary character variants;
- transformation stages;
- expression sheets;
- props and weapons references;
- animation pose references;
- supporting environments;
- ordinary library references.

### Do not upscale automatically

- thumbnails;
- temporary previews;
- duplicate assets;
- rejected assets;
- assets with unresolved licence or provenance;
- assets whose source integrity check failed.

## Quality gates

An enhanced derivative cannot be marked `production-approved` unless all required checks pass:

- source preserved and checksum recorded;
- target dimensions reached;
- aspect ratio preserved or intentional crop recorded;
- no clipped subject anatomy;
- no neighbouring panels or labels unless requested;
- no visible halos, ringing, tiling, excessive sharpening, or compression blocks;
- identity and design consistency within threshold;
- text either preserved accurately or excluded from image reconstruction;
- metadata complete;
- visual review completed for reconstructed or regenerated assets.

## Text handling

Small infographic text must not be hallucinated by an image model.

The Brain must choose one of these routes:

1. preserve the original text region when legible;
2. extract authoritative text from metadata and re-render it using layout tools;
3. omit text from the visual derivative and store it as structured metadata;
4. mark unreadable text for manual review.

AI-generated replacement text is not authoritative.

## Brain metadata contract

Every resolution conversion must record at least:

```yaml
asset_id: NKS-WRW-000001
source_asset_id: NKS-SRC-WRW-000001
content_type: character-identity
importance: hero
source:
  width: 420
  height: 610
  checksum_sha256: "..."
conversion:
  requested_profile: production-8k
  selected_route: ai-assisted-reconstruction
  target_long_edge: 8192
  preserve_aspect_ratio: true
  preserve_identity: true
  preserve_anatomy: true
  preserve_colours: true
  preserve_markings: true
  background_mode: preserve
  model: "runtime-selected"
  model_version: "runtime-recorded"
  settings: {}
output:
  width: 5640
  height: 8192
  checksum_sha256: "..."
quality:
  status: needs-visual-review
  design_consistency_score: null
  clipping_detected: false
  artefacts_detected: false
approval:
  state: pending
  approved_by: null
  approved_at: null
```

## Orchestration responsibility

The Brain owns the policy and decision record. The Render Orchestrator or Asset Processing service performs the conversion using the best available compatible model or tool. Tools and models are replaceable; this policy and the asset history remain canonical.

## Learning loop

After review, the Brain must store:

- route selected;
- tool and model used;
- processing settings;
- quality scores;
- reviewer outcome;
- rejection reasons;
- asset category;
- runtime and resource cost.

Future conversions should use this evidence to rank processing methods, but learned preferences may never bypass preservation, provenance, or approval requirements.

## Trigger behaviour

The Brain must invoke this policy when:

- a raster asset is imported;
- a panel is extracted from a source sheet;
- a user requests enhancement, 4K, 8K, restoration, cleanup, or production readiness;
- an asset is promoted to hero or master status;
- a renderer requests a minimum resolution that the current derivative does not satisfy.

## Failure behaviour

If no compatible enhancement service is available, the Brain must:

- preserve and register the source;
- create a pending conversion job;
- record the requested target and reason;
- report that conversion is queued or unavailable;
- never falsely mark the asset as 4K, 8K, enhanced, or production-approved.
