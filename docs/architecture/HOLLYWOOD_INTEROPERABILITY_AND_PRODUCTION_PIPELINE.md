# Hollywood Interoperability and Production Pipeline Contract

**Status:** Adopted architecture direction  
**Applies to:** Brain, BUILD, READY, PRODUCTION, STUDIO, Continuity Engine, Render Orchestrator, asset systems, renderer/tool adapters, production tracking, colour, editorial, audio, mastering and delivery  
**Related contracts:** `STAGE_CAPABILITY_BOUNDARIES.md`, `ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md`, `CINEMATIC_SPATIAL_LAYERING_AND_RENDER_OUTPUT.md`, `RENDERER_CAPABILITY_AWARE_PREVIEW_ROUTING.md`, `SCENE_SHOT_DATA_CONTRACT.md`, `AI_AGENT_ORGANISATION_AND_COST_CONTROL.md`

## 1. Purpose

Nexkosmo should be simpler for the Director than a conventional multi-application film/VFX pipeline without becoming isolated from professional film, animation, VFX, editorial, audio or finishing ecosystems.

The governing principle is:

> **Reduce handoffs, duplication and unnecessary compute; do not remove useful filmmaking checkpoints or professional interoperability.**

Nexkosmo may coordinate work that would traditionally require several separate applications, but the Brain remains the canonical source of truth. External DCC, editorial, compositing, audio, tracking, render-farm and finishing applications are replaceable production capabilities rather than competing project authorities.

This contract does **not** add new top-level product stages. The canonical journey remains:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION -> STUDIO`

## 2. Audit outcome

Comparison with high-end film/VFX workflows shows that Nexkosmo already covers the major creative and execution domains: story, Scene/Shot construction, cinematography, assets, animation, CGI, VFX/simulation, AI generation, offline/real-time rendering, layers/AOVs, editorial, compositing, colour, sound, mastering and delivery.

The main gaps are not missing top-level stages. They are the professional bridges that allow those stages to participate safely in a large production pipeline:

1. camera-original / dailies / plate ingest;
2. VFX plate preparation, matchmove, camera solve, lens workflow, roto and cleanup;
3. professional interchange standards for scenes, assets, materials, images, colour, editorial and audio;
4. production tracking, review, turnover and vendor interoperability;
5. formal mastering, localisation, QC and cinema/streamer delivery contracts.

These capabilities shall be added inside the existing stage architecture rather than creating a second workflow.

## 3. Hollywood interoperability spine

Nexkosmo should prefer open, versioned and well-supported interchange standards where they preserve meaning and reduce vendor lock-in.

The target interoperability spine is:

### 3.1 OpenUSD

Use OpenUSD where appropriate for structured 3D scene and asset interchange, including hierarchy, transforms, references, variants, cameras, geometry, animation relationships and other scene-description data that can be represented faithfully.

USD interchange must not replace canonical Brain identity, approval or continuity state. It is a transport/working representation linked to canonical records.

### 3.2 MaterialX

Use MaterialX where appropriate for portable material/look descriptions across compatible DCC and rendering systems.

Material interchange must preserve source/version/provenance and must record renderer-specific substitutions or unsupported nodes rather than silently changing the approved look.

### 3.3 OpenAssetIO or equivalent bounded asset interface

Use OpenAssetIO or an equivalent approved abstraction where useful to connect DCC tools to Nexkosmo asset identity, version and resolution services without hard-binding project truth to one asset-management application.

The Brain/asset system remains authoritative for canonical identity and approval.

### 3.4 OpenEXR

Use OpenEXR where appropriate for high-dynamic-range production image interchange and rich render outputs, including multi-channel/multipart or deep-image workflows when the selected route genuinely supports them.

Beauty, alpha, depth, normals, motion, IDs, mattes, light groups and AOVs must remain explicitly typed and validated. A flattened delivery image must not be treated as equivalent to a rich production master.

### 3.5 ACES and OpenColorIO

Nexkosmo shall formalise a colour-management path capable of interoperating with ACES and OpenColorIO where appropriate.

The colour contract must distinguish:

`capture/source -> scene/working state -> creative look/grade -> display/mastering transform -> delivery encode`

LUTs, CDLs, camera transforms and display transforms are evidence-bearing operations and must not silently become canonical illumination or camera truth.

### 3.6 OpenTimelineIO plus professional editorial interchange

Use OpenTimelineIO where appropriate for timeline structure, clips, tracks, timing, transitions, markers and editorial metadata.

Support other professional turnover formats where required by the receiving/producing system, including AAF, EDL and other approved editorial/audio interchange formats.

Interchange must preserve stable Shot/Scene identity so editorial edits do not create a competing project graph.

### 3.7 Geometry, animation and VFX caches

Where USD is not the correct transport or a baked cache is operationally preferable, Nexkosmo may support formats such as Alembic for baked geometry/animation caches and OpenVDB for volumetric/simulation data.

Cache formats are execution artifacts and remain traceable to canonical source state, software/version, frame range, units, coordinate system and dependency revisions.

### 3.8 VFX Reference Platform compatibility

For native integrations used in a professional VFX environment, Nexkosmo should track the applicable VFX Reference Platform target and compatible dependency versions where practical.

This is an engineering compatibility baseline, not a requirement that every Nexkosmo user install a VFX facility software stack.

## 4. Professional software adapter priorities

Nexkosmo does not need every application to be a core dependency. Tools remain adapters/capabilities selected by project requirements.

### Priority A — professional bridge coverage

- **Autodesk Maya** — animation, rigging, modelling/layout and established DCC interoperability.
- **Foundry Nuke** — high-end node compositing, plate work, keying/roto/paint integration and professional VFX turnover.
- **Avid Media Composer** — editorial interchange and collaboration compatibility.
- **Avid Pro Tools** — dialogue, sound editorial, mix and AAF-based post-production interoperability.
- **3DEqualizer and/or Mocha Pro class capability** — matchmove, camera solve, tracking, lens workflow and roto/plate preparation.

### Priority B — pipeline, review and compute interoperability

- **Flow Production Tracking / ShotGrid class interoperability** — external shot/asset/task/version/review exchange where a facility requires it.
- **OpenCue / Deadline-class render-farm interoperability** — external queue/farm execution where useful, while Nexkosmo Render Orchestrator remains the canonical execution planner.

### Priority C — specialist production adapters

- **RenderMan** — additional production renderer route.
- **Katana** — lighting/lookdev pipeline interoperability.
- **Mari** — hero texture/look-development interoperability.
- **ZBrush** — high-detail sculpting interoperability.
- **MotionBuilder** or equivalent — motion-capture/animation interchange where required.
- **Flame / Baselight class systems** — high-end finishing/DI interoperability where required.

Existing planned/approved routes such as Blender, Unreal Engine, Arnold, V-Ray, Houdini, DaVinci Resolve, Substance 3D, ComfyUI and approved AI image/video systems remain valid and are not displaced by this list.

## 5. Dailies and camera-original ingest

Real-footage workflows require more than copying a video file into a project.

Where applicable, PRODUCTION ingest should support a governed pipeline such as:

```text
camera original / production audio
-> verified copy / checksum evidence
-> media identity + metadata ingest
-> timecode / reel / clip / camera metadata preservation
-> production-audio sync where required
-> colour metadata / LUT / CDL association
-> proxy / editorial-media generation
-> review/dailies derivative
-> editorial and VFX turnover links
```

The source camera original must remain immutable or otherwise protected according to media policy. Proxies and dailies are derivatives, not replacements for source evidence.

The ingest record should preserve, where available and material:

- source file identity and checksum;
- camera/clip/reel identity;
- frame rate and timecode;
- resolution and pixel aspect;
- camera/lens metadata where available;
- production-audio references and sync evidence;
- colour-management metadata;
- creation/import timestamps;
- source storage location and derivative relationships;
- rights/provenance/access state.

## 6. VFX plate preparation and matchmove

Live-action VFX may require a plate-preparation pipeline before CG/VFX integration.

Where applicable, PRODUCTION should be able to represent and coordinate:

- camera tracking / matchmove;
- object tracking;
- lens distortion/undistortion models;
- camera solve and survey/reference evidence;
- roto and holdout mattes;
- keying;
- paint/cleanup/object removal;
- plate stabilization where appropriate;
- grain/noise characterization;
- set/environment reconstruction;
- lidar/photogrammetry/reference linkage where used;
- frame-range and handle management;
- plate colour-state and transform evidence.

A solved camera or lens model is evidence/derived production state. It does not overwrite Director-approved creative intent without an explicit reconciliation decision.

The same Shot may therefore contain both:

- approved creative camera intent; and
- measured/solved camera evidence from real footage.

Brain must preserve the distinction and reconcile conflicts explicitly.

## 7. Production tracking, review and turnover

Brain remains the source of project truth, but Nexkosmo should interoperate with professional production-tracking/review systems when required by a studio, vendor or collaborator.

A turnover/review record should be able to preserve:

- Project / Sequence / Scene / Shot identity;
- task/workstream;
- assigned/receiving party where authorised;
- source version;
- requested work;
- frame range and handles;
- input assets/plates/caches;
- colour/output assumptions;
- delivery package/version;
- review notes;
- approval/rejection state;
- dependencies/blockers;
- due/schedule metadata where used;
- checksum/provenance/evidence links.

External tracking identifiers may be mapped to canonical Nexkosmo identities but must not become a second source of project truth.

Review notes are evidence/proposals until the authorised workflow promotes the resulting decision into canonical state.

## 8. Visible checkpoints without redundant compute

Professional workflow visibility is valuable because it isolates faults early.

Nexkosmo shall therefore preserve meaningful checkpoints even when it streamlines the underlying software and compute path.

Example:

```text
Assets ready
-> plate/ingest valid where applicable
-> blocking/layout valid
-> camera/lens/matchmove valid
-> lighting/look valid
-> identity/continuity valid
-> motion/performance valid
-> VFX/simulation valid
-> render/output contract valid
-> composite/grade/audio valid
-> master/QC valid
-> delivery valid
```

A checkpoint does not automatically require a separate expensive render. Validation may use canonical state, deterministic checks, cached evidence, still frames, short test ranges, low-resolution previews, native renderer passes or other lower-cost proof.

Permanent rule:

> **Preserve checkpoints. Minimise redundant compute.**

A passed checkpoint remains reusable until one of its dependencies changes.

## 9. BUILD and READY responsibilities

BUILD continues to define and prove the Shot. It may define downstream professional requirements without performing final downstream work, including:

- camera/lens and matchmove requirements;
- required handles/frame ranges;
- plate/element expectations;
- output/pass/AOV requirements;
- colour working assumptions;
- editorial timing constraints;
- VFX/simulation requirements;
- required interoperability or receiving-facility constraints.

READY must verify that committed PRODUCTION has a viable, qualified route for required material capabilities and handoffs.

READY must block when a required professional handoff would lose material meaning such as identity, frame range, colour state, camera solve, required layer/AOV data, timing or provenance and no approved alternative exists.

## 10. PRODUCTION responsibilities

PRODUCTION owns creation/acquisition of approved source material and therefore also owns, where applicable:

- camera-original and production-audio ingest;
- dailies/proxy derivation required for production/editorial;
- matchmove/camera solve and lens workflow;
- plate preparation required before source VFX integration;
- 3D layout/animation/CGI;
- simulation and source VFX;
- AI image/video execution;
- real-time/offline rendering;
- rich production passes/AOVs;
- source-version validation;
- production turnover packages;
- render-farm/distributed execution through approved orchestration;
- evidence/provenance of source execution.

PRODUCTION may use Maya, Blender, Houdini, Unreal, Nuke-class plate tools, Arnold, V-Ray, RenderMan, AI renderers or other approved systems without transferring canonical ownership to those tools.

## 11. STUDIO responsibilities

STUDIO owns finishing and therefore also owns, where applicable:

- professional editorial/conform;
- compositing and finishing VFX;
- colour management and grade;
- dialogue edit and cleanup;
- sound design/music editorial;
- mix and mastering;
- titles and credits;
- subtitles/captions;
- localisation/versioning;
- final picture/audio QC;
- IMF packaging where required;
- DCP creation where required;
- SDR/HDR mastering;
- Dolby Vision or other approved dynamic-metadata workflows where required and licensed/supported;
- broadcast/streaming/file delivery variants;
- checksum/package validation;
- archive/master derivation evidence.

A failed QC check prevents the affected master/delivery from being accepted as complete until repaired or explicitly waived by authorised policy.

## 12. Mastering and QC contract direction

Final delivery must be treated as a validated production outcome rather than a simple export button.

A delivery profile may specify:

- picture resolution/aspect/frame rate;
- codec/container or image sequence;
- colour space/gamut/transfer/mastering target;
- SDR/HDR state;
- audio layout/channel mapping;
- sample rate/bit depth;
- loudness/true-peak requirements where applicable;
- subtitle/caption language and format;
- localisation/version identifiers;
- IMF/DCP/package requirements;
- metadata requirements;
- naming/versioning;
- checksum/package integrity;
- slate/bars/tone/head-tail requirements where applicable;
- platform/studio/network specification version.

QC should be layered:

1. deterministic technical validation where possible;
2. automated perceptual/content checks where reliable and authorised;
3. human review for requirements that cannot be safely reduced to automated proof.

A technically valid file is not automatically a creatively approved master.

## 13. Tool-neutral canonical identity

Every professional interchange package must map back to stable Nexkosmo identity.

Conceptually:

```text
Nexkosmo canonical identity/revision
-> adapter/export package
-> external tool/facility work
-> import/turnover result
-> validation/reconciliation
-> canonical update only when authorised
```

External filenames, folder names, shot codes, vendor IDs and tracking-system IDs may be retained as aliases/references, but none may silently replace canonical UUID/identity state.

## 14. No false interoperability

Nexkosmo must not claim support merely because it can open or export a file extension.

A tool/format integration is considered production-qualified only when the relevant workflow is validated end to end for its claimed scope, including where material:

- identity mapping;
- units/axes/transforms;
- frame rate/timecode/frame range;
- camera/lens state;
- geometry/animation;
- materials/textures;
- colour state;
- layers/AOVs/channels;
- audio sync;
- editorial timing;
- metadata/provenance;
- round-trip or one-way handoff expectations;
- version compatibility;
- failure/recovery behaviour.

Unknown or unverified interoperability remains experimental and must not underpin a guaranteed production promise.

## 15. Implementation priority

The recommended implementation order is:

```text
1. Formal interchange spine
   OpenUSD + MaterialX + OpenAssetIO-class asset interface
   OpenEXR + ACES/OpenColorIO
   OpenTimelineIO + required AAF/EDL interchange

2. Professional bridge adapters
   Maya + Nuke + Avid Media Composer + Pro Tools
   matchmove/roto/plate-prep capability

3. Dailies / real-footage ingest
   checksum + metadata + sync + colour + proxy/turnover

4. Production tracking / review / turnover
   external facility/vendor interoperability without competing truth

5. Mastering / QC / delivery profiles
   IMF/DCP/HDR/localisation/QC where applicable

6. Additional specialist adapters
   RenderMan, Katana, Mari, ZBrush, MotionBuilder, Flame, Baselight and future equivalents as justified
```

Implementation order may change when a real customer/project requires a capability earlier, but the architecture must preserve canonical ownership and evidence.

## 16. Agent responsibility mapping

This contract does not automatically increase the canonical 50-agent count.

Existing responsibilities can coordinate these functions, including:

- Evidence & Provenance — ingest, turnover and review evidence;
- Camera & Sensor / Lens & Optics — camera metadata, solved camera/lens reconciliation;
- CGI Production — DCC/scene/animation interoperability;
- VFX & Simulation — plate/VFX/simulation requirements;
- Renderer Capability & Route — tool/renderer compatibility and route choice;
- Layer / Pass / AOV — EXR/AOV/rich-output preservation;
- Render Validation — production result acceptance;
- Editorial — OTIO/AAF/EDL and conform relationships;
- Compositing & Finishing VFX — Nuke-class plate/composite/finishing work;
- Colour — ACES/OpenColorIO and grade state;
- Dialogue, Sound Design & Music — audio editorial;
- Mix, Master & Delivery — Pro Tools-class mix interchange, IMF/DCP/HDR/localisation/QC/delivery;
- Cost, Quote & Compute Economics — adapter/tool/farm/licence/turnover execution cost.

If evidence later shows one of these responsibilities is too broad, the agent roster may be amended explicitly rather than silently adding hidden agents.

## 17. Permanent rules

> **Nexkosmo should simplify the professional filmmaking journey without severing professional interoperability.**

> **Brain remains the canonical source of truth; external applications remain replaceable tools, adapters and collaboration endpoints.**

> **Reduce handoffs, duplication and unnecessary compute; preserve useful checkpoints and evidence.**

> **Preserve checkpoints. Minimise redundant compute.**

> **Prefer open, versioned interchange standards where they preserve the required production meaning.**

> **OpenUSD, MaterialX, OpenEXR, ACES/OpenColorIO and OpenTimelineIO form the target professional interoperability spine, with additional formats used where the workflow requires them.**

> **A file extension is not proof of interoperability; production support requires end-to-end validated meaning.**

> **Real-footage ingest, matchmove/plate preparation, production tracking/turnover and mastering/QC are professional pipeline capabilities inside PRODUCTION/STUDIO, not new top-level stages.**

> **External tracking systems, filenames and DCC scene files never become competing canonical project truth.**

> **Unknown or unverified professional interoperability is experimental and cannot underpin a guaranteed production promise.**