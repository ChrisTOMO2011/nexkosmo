# Stage Capability Boundaries

**Status:** Adopted product/architecture contract  
**Applies to:** IDEA, DISCOVER, SHAPE, BUILD, READY, PRODUCTION, STUDIO, Brain, AI Producer, Continuity Engine, Render Orchestrator, Renderer Adapters, frontend and backend implementations  
**Related contracts:** `IDEA_TO_BUILD_FLOW_ALIGNMENT_AND_DIRECTOR_FREEDOM.md`, `BUILD_PROGRESSIVE_DISCLOSURE_UI.md`, `SCENE_SHOT_DATA_CONTRACT.md`, `PHYSICS_FIRST_CINEMATOGRAPHY.md`, `CINEMATIC_SPATIAL_LAYERING_AND_RENDER_OUTPUT.md`, `HOLLYWOOD_INTEROPERABILITY_AND_PRODUCTION_PIPELINE.md`

## 1. Governing principle

Nexkosmo may understand and technically possess many capabilities before the Director-facing workflow should expose or execute them.

The permanent rule is:

> A capability belongs in the earliest stage that genuinely needs it, and no earlier.

A second permanent rule is:

> Do not unlock a capability merely because Nexkosmo can perform it. Unlock it when the current stage needs it to fulfill that stage's purpose.

This prevents later-stage production and finishing systems from leaking into earlier creative stages and preserves a clear, understandable filmmaking flow.

Professional interoperability does not create new top-level stages. Dailies, plate preparation, matchmove, production tracking/turnover, editorial interchange, colour management, mastering and QC are capabilities inside the existing stages according to their purpose.

## 2. Canonical stage flow

```text
IDEA
-> DISCOVER
-> SHAPE
-> BUILD
-> READY
-> PRODUCTION
-> STUDIO
```

The stages are connected views over one canonical project, but each stage has a distinct job.

## 3. IDEA

Purpose:

> Capture what the Director wants to make.

IDEA may establish or infer concept, project type, destination, broad genre/tone/style and other initial intent when known.

IDEA must not expose production construction, rendering, final cinematography, editing, compositing or mastering merely because the underlying systems exist.

## 4. DISCOVER

Purpose:

> Find and develop the important moments, scenes and visual story understanding.

DISCOVER may use scene snapshots, whole isolated assets, Build This Moment, visual references and lightweight derived representations when those directly help the Director discover the Scene.

DISCOVER must not become global BUILD, final PRODUCTION or STUDIO.

A Discover scene-moment frame remains reference/story-development state and is not automatically a BUILD Shot.

## 5. SHAPE

Purpose:

> Establish what happens, what is said, what is heard and what it means.

SHAPE may create or link dialogue, voice, SFX, ambience and music assets when they are needed to shape the Scene.

That does not unlock final sound editing, mixing or mastering. Those remain STUDIO responsibilities.

SHAPE may preserve a Director-specified camera or other cinematic fact if explicitly given, but it does not require final Shot construction.

## 6. BUILD

Purpose:

> Turn the established Scene into Shots and define how the audience should see and experience them.

BUILD may define:

- Shot structure and coverage;
- blocking and spatial construction;
- camera/lens/focus/exposure intent;
- camera support/movement rigs;
- lighting intent;
- spatial layering;
- props/states/dependencies;
- CGI/VFX requirements;
- output/pass requirements needed downstream;
- renderer/hybrid compatibility;
- preview/test renders needed to judge the Shot;
- required frame ranges/handles where downstream VFX/editorial work depends on them;
- plate/element expectations where live-action or hybrid production is planned;
- downstream colour-management and interchange requirements where these materially affect Production.

BUILD may invoke a renderer, AI model, real-time engine, 3D renderer or hybrid route when a preview/test is necessary to evaluate the Shot.

That does not unlock committed final Production execution.

Permanent rule:

> BUILD defines and proves the Shot.

## 7. READY

Purpose:

> Determine whether the approved creative construction can enter committed Production without Production inventing consequential creative decisions or violating critical identity/continuity constraints.

READY validates; it does not become another authoring or rendering stage.

Warnings should remain warnings when the Shot is intentionally unconventional but producible.

READY must also verify, where material, that required professional handoffs have a viable path. A required handoff is blocked if it would silently lose material identity, frame range, timing, camera/lens state, colour state, layer/AOV data, audio sync, provenance or other required production meaning and no approved route can preserve it.

## 8. PRODUCTION

Purpose:

> Create, acquire, animate, simulate or render the approved source Shot material.

PRODUCTION owns committed execution such as, where applicable:

- final AI image/video generation;
- final 3D/offline rendering;
- Unreal/real-time production output;
- Arnold/V-Ray/Blender/RenderMan or other renderer execution;
- Maya/Blender/Houdini or other approved DCC execution;
- animation execution;
- simulations;
- final source VFX generation;
- real footage acquisition/ingest;
- camera-original and production-audio ingest with checksum/metadata evidence where applicable;
- proxy/dailies derivatives required for production/editorial;
- matchmove/camera solve, lens workflow, tracking and other plate-preparation work where required;
- roto/key/paint/cleanup and source plate preparation where required for VFX production;
- hybrid source creation;
- production-quality rerenders;
- required rich render passes/AOVs/mattes;
- scene/material/image/colour/timeline interchange required for approved production handoffs;
- production tracking/turnover package generation where required by collaborators/facilities;
- render-farm/distributed execution through approved orchestration;
- evidence/provenance from execution.

PRODUCTION consumes approved Shot intent from BUILD/READY. It must not silently redesign the movie to fit a tool.

External DCC files, tracking IDs, vendor shot codes and render-farm records may map to canonical Nexkosmo identity but may not become a competing source of truth.

Permanent rule:

> PRODUCTION makes the approved Shot.

## 9. STUDIO

Purpose:

> Turn produced material into the finished work.

STUDIO owns finishing functions such as, where applicable:

- editorial timing and assembly;
- professional conform and timeline interchange;
- compositing;
- colour correction/grading and colour-management transforms;
- dialogue editing;
- sound design;
- music placement/editing;
- mixing;
- titles/credits;
- transitions;
- finishing VFX/compositing operations;
- subtitles/captions;
- localisation/versioning;
- mastering;
- final picture/audio QC;
- IMF/DCP or other delivery packaging where required;
- SDR/HDR mastering and approved dynamic-metadata workflows where required;
- delivery encoding and final outputs;
- checksum/package validation and archive/master derivation evidence.

STUDIO may discover that a source Shot must change. In that case it may request or invoke a targeted return to PRODUCTION while preserving the same canonical Shot/Scene relationships.

STUDIO does not become the canonical owner of source-shot production merely because it can request a replacement render.

A failed required QC check prevents the affected master/delivery from being accepted as complete until repaired or explicitly waived by authorised policy.

Permanent rule:

> STUDIO finishes the produced material.

## 10. Same technology, different stage authority

The same underlying technology may legitimately appear in more than one stage for different purposes.

Example:

```text
BUILD
Arnold test render to judge camera/lens/light relationships
-> preview evidence

PRODUCTION
Arnold final-quality render of the approved Shot with required passes
-> source production result

STUDIO
uses those passes for compositing/grade/finishing
-> master/delivery result
```

The technology is shared. The authority and purpose are not.

Another example:

```text
SHAPE
AI voice draft to establish performance/timing

PRODUCTION
approved performance generation/recording where part of source production

STUDIO
dialogue edit, cleanup, mix and mastering
```

Therefore capability placement is decided by **purpose**, not by tool identity.

Professional applications such as Maya, Nuke, Avid Media Composer, Pro Tools, 3DEqualizer/Mocha-class systems, ShotGrid-class tracking, OpenCue/Deadline-class render farms, RenderMan, Katana, Mari, ZBrush, Flame or Baselight likewise do not define Nexkosmo stages. They are capabilities/adapters invoked where their production purpose belongs.

## 11. Preview is not Production

A preview/test may use sophisticated technology or even a high-quality renderer.

Its stage meaning remains preview/test when its purpose is to evaluate a creative or technical decision before committed Production.

Permanent rule:

> Preview capability does not imply final Production capability is unlocked.

A preview must not silently become an approved final source merely because it looks good. Promotion into approved Production state requires the appropriate production/approval path.

## 12. Output intent is not finishing

BUILD may define required output characteristics and passes because Production needs to know what to produce.

This can include requirements such as alpha, depth, normals, motion vectors, mattes, AOVs, colour-space intent, resolution, frame rate, frame range/handles, interchange requirements and master requirements.

Defining those requirements does not give BUILD ownership of final compositing, grading, mastering or delivery.

Permanent rule:

> BUILD specifies what downstream stages need; it does not perform every downstream responsibility.

## 13. Capability gating decision order

Before exposing or executing a capability, Brain/UI should evaluate:

```text
1. What is the current stage trying to accomplish?
2. Is this capability necessary to accomplish that stage purpose now?
3. Is a lighter preview/reference/definition sufficient instead?
4. Does the capability primarily belong to a later stage?
5. If later-stage execution is required now, is there an explicit cross-stage reason rather than convenience?
6. Preserve the current stage context and canonical state.
7. Do not relocate the later stage's ownership merely because a tool can be called early.
8. If an external handoff is required, preserve the required production meaning and provenance rather than merely exporting a file extension.
```

## 14. Cross-stage invocation

A stage may request work from another stage/system when genuinely necessary, but the ownership boundary remains explicit.

Examples:

- BUILD requests a limited renderer test from execution infrastructure for preview evidence;
- STUDIO requests a targeted Production rerender;
- SHAPE requests a draft voice asset to judge dialogue timing;
- PRODUCTION creates proxy/dailies media for editorial while preserving camera-original identity;
- STUDIO requests a conform/turnover package derived from canonical Shot/timeline state.

Cross-stage invocation must preserve:

- purpose;
- source state;
- approval status;
- provenance;
- dependency links;
- stage ownership;
- whether the result is preview, proposal, production source or final master;
- external interchange/turnover assumptions where applicable.

## 15. UI rule

The UI must not show every capability Nexkosmo knows about.

It should show what the Director needs for the current stage and task.

A later-stage capability should not appear merely as an advanced toggle in an earlier stage unless the earlier stage genuinely needs a controlled preview/test/definition form of that capability.

Professional interoperability should normally remain automatic or contextually surfaced rather than forcing ordinary users to understand DCC/file-format/facility plumbing.

Permanent rule:

> Nexkosmo can know more than it shows and can possess more than it unlocks.

## 16. Director freedom and stage discipline

Director authority does not mean every capability is exposed everywhere.

The Director remains free to make unconventional creative decisions inside the purpose of the current stage, while the product preserves a disciplined production flow.

For example, BUILD may allow an impossible virtual camera move because it is a Shot-design choice. That does not mean BUILD must also expose final compositing, mastering and delivery controls.

Creative freedom and workflow discipline are compatible.

## 17. Professional interoperability rule

The target professional interchange spine is defined by `HOLLYWOOD_INTEROPERABILITY_AND_PRODUCTION_PIPELINE.md` and includes, where appropriate, OpenUSD, MaterialX, an OpenAssetIO-class asset interface, OpenEXR, ACES/OpenColorIO, OpenTimelineIO and required professional editorial/audio interchange such as AAF/EDL.

These standards and adapters are transport/collaboration mechanisms. They do not replace canonical Brain state.

A file extension is not sufficient evidence of compatibility. Production-qualified interoperability requires validation of the meaning that matters for the relevant handoff, such as identity, units/transforms, timing, camera/lens state, colour, layers/AOVs, audio sync, metadata and provenance.

## 18. Permanent rules

> A capability belongs in the earliest stage that genuinely needs it, and no earlier.

> Do not unlock a capability merely because Nexkosmo can perform it.

> Nexkosmo can know more than it shows and can possess more than it unlocks.

> IDEA captures the idea. DISCOVER finds the moments. SHAPE establishes what happens, is said and is heard. BUILD defines and proves the Shot. READY validates committed production readiness. PRODUCTION makes the approved Shot. STUDIO finishes the produced material.

> Preview capability does not imply final Production capability is unlocked.

> BUILD specifies what downstream stages need; it does not perform every downstream responsibility.

> The same technology may serve multiple stages, but stage purpose and authority remain distinct.

> Cross-stage invocation does not transfer stage ownership.

> Director creative freedom does not require capability sprawl.

> Professional interoperability must preserve production meaning without creating a competing source of truth.

> Real-footage ingest, dailies, matchmove/plate preparation, production tracking/turnover and mastering/QC are capabilities inside PRODUCTION/STUDIO, not new top-level stages.

> Preserve the flow.