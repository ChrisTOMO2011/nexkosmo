# IDEA -> BUILD Flow Alignment and Director Creative Freedom

**Status:** Adopted product/architecture contract  
**Applies to:** IDEA, DISCOVER, SHAPE, BUILD, READY, Brain, AI Producer, Continuity Engine, Render Orchestrator, Renderer Adapters, frontend and backend implementations  
**Related contracts:** `AGENTS.md`, `SHAPE_BUILD_TANDEM_AND_LAYERING.md`, `SCENE_SHOT_DATA_CONTRACT.md`, `AUTOMATIC_SYNCHRONIZATION_RULES.md`, `SHOT_COVERAGE_SUFFICIENCY.md`, `BUILD_PROGRESSIVE_DISCLOSURE_UI.md`, `PHYSICS_FIRST_CINEMATOGRAPHY.md`, `CINEMATIC_SPATIAL_LAYERING_AND_RENDER_OUTPUT.md`, `RENDERER_CAPABILITY_AWARE_PREVIEW_ROUTING.md`

## 1. Purpose

This contract rechecks and aligns the Director-facing journey from IDEA through BUILD after the addition of physics-first cinematography, cinematic spatial layering, rich render/output preservation, camera support/movement rigs and renderer-capability routing.

It also makes one constitutional product rule explicit:

> Nexkosmo exists to increase the Director's creative agency. Its intelligence may propose, explain, preserve, validate and execute creative intent, but it must not convert cinematography knowledge, conventional coverage, physical realism or renderer limitations into creative authority over the Director.

The stage flow remains:

```text
IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION -> STUDIO
```

This document governs the IDEA -> BUILD portion and clarifies where creative decisions belong.

## 2. The four-stage responsibility split

### IDEA — What am I making?

IDEA captures the creative starting point without forcing premature classification or production decisions.

IDEA may establish or infer, where sufficiently clear:

- project concept;
- project type;
- intended destination/distribution surface;
- broad genre/tone/style;
- known characters, places or events;
- rough duration or format when supplied;
- other initial Director intent.

IDEA does **not** require the Director to decide camera, lens, lighting, rig, shot count, aspect ratio, renderer, delivery codec or other downstream technical details before creativity can begin.

Unknown values may remain unknown until they are actually needed.

Permanent rule:

> IDEA captures what the Director knows. It does not make the Director solve production before discovering the movie.

### DISCOVER — What moments and scenes make up the idea?

DISCOVER develops the movie as scenes, anchor moments and visual story understanding.

DISCOVER may contain:

- one or more known/anchor scenes;
- scene snapshots;
- scene-moment frames;
- whole isolated characters, props, vehicles, environments and effects;
- Build This Moment composition;
- AI-created or retrieved reusable assets;
- unresolved gaps between known moments;
- Brain/Producer story proposals that remain proposals until adopted.

The Director may work non-linearly. One established Scene is enough to begin moving forward.

### DISCOVER scene-moment frames are not BUILD Shots

This boundary is mandatory.

A DISCOVER snapshot or ordered scene-moment frame is a **story-development and visual-composition representation**. It may later inspire, seed or be referenced by one or more BUILD Shots, but it is not automatically a canonical Shot.

For example:

```text
DISCOVER moment:
Sarah finds Chris injured beside a crashed car.

BUILD may later express that moment as:
- one continuous handheld Shot;
- a wide + Sarah close-up + Chris insert;
- a jib reveal;
- a drone establishing move followed by ground coverage;
- another Director-selected construction.
```

Rules:

1. DISCOVER does not pre-decide final shot count merely because several scene-moment frames exist.
2. One DISCOVER frame may become zero, one or many BUILD Shots.
3. Several DISCOVER frames may be combined into one BUILD Shot when the Director wants a continuous take.
4. A DISCOVER frame may remain only a story/reference image and never become a Shot.
5. BUILD Shot identity begins only when a Shot is deliberately created/proposed as cinematic coverage of the Scene.
6. Discover visual composition must not silently constrain later camera position, lens, rig, lighting or blocking unless the Director has explicitly established those as creative intent.

Permanent rule:

> DISCOVER establishes the moment; BUILD decides how that moment is photographed. A Discover frame is reference, not an automatic Shot.

### SHAPE — What exactly happens, is said and is heard?

SHAPE develops the same canonical Scene narratively and performatively.

SHAPE primarily owns:

- scene action;
- dialogue;
- reactions;
- entrances/exits;
- meaningful object interactions;
- transformations and state changes;
- narrative order and timing intent;
- emotional/performance intent;
- dialogue/voice assets;
- ambience;
- SFX requirements;
- music/score intent and linked audio cues.

SHAPE may contain Established, Inferred, Proposed and Unknown material according to the existing narrative truth contract.

SHAPE does not require final camera, lens, rig, lighting or shot construction unless the Director deliberately establishes those details there.

Permanent rule:

> SHAPE establishes what happens, what is said, what is heard and what it means. It does not force the Director to photograph the Scene before the Director is ready.

### BUILD — How should the audience see and experience what happens?

BUILD turns the same canonical Scene into cinematic coverage and producible Shot state.

BUILD does not recreate or copy the Scene. It inherits the Scene, then adds Shot-specific cinematic construction.

The conceptual flow is:

```text
SHAPE Scene / selected Scene moment
-> identify Coverage Obligations
-> apply Director/project cinematic intent
-> propose or create 1..N Shots
-> refine subject/blocking/spatial construction
-> define cinematography state
-> define output intent
-> capability-match execution routes
-> create derived preview(s)
```

The Director remains free to ignore, alter, replace, merge or remove AI-proposed coverage.

## 3. BUILD Shot state after physics-first alignment

A BUILD Shot may resolve the following interconnected state where relevant:

### Coverage and meaning

- covered Scene beat/event/dialogue range;
- intended audience understanding/emotion;
- Shot purpose/rationale where useful;
- timing/duration intent.

### Scene and subject construction

- inherited Scene state;
- participants;
- blocking and movement;
- props/vehicles;
- shot-specific staging;
- visibility/occlusion;
- CGI/VFX dependencies;
- spatial-layering intent.

### Cinematic spatial layering

Where useful, the Shot may reason about:

- extreme foreground;
- foreground;
- principal subject plane;
- secondary subject/midground;
- background;
- deep background/atmosphere;
- physical distance relationships;
- occlusion;
- parallax;
- scale;
- focus relationships;
- lighting/contrast/atmospheric separation.

These are tools, not mandatory slots. A deliberately flat frame is valid Director intent.

### Camera and imaging state

Where relevant:

- camera identity/profile;
- transform/height/distance;
- sensor/filmback;
- framing/field of view;
- lens/focal length;
- optical filtration;
- aperture/T-stop;
- focus distance;
- focus trajectory/rack focus;
- zoom/focal-length trajectory;
- shutter/exposure time;
- ISO/EI;
- white balance/tint;
- sensor/camera-response profile;
- rolling/global shutter behaviour;
- colour/exposure intent.

### Camera Support & Movement Rig State

A Shot may explicitly use a support/movement system such as:

- locked/static camera;
- tripod;
- slider;
- dolly;
- pedestal;
- jib;
- fixed crane;
- telescopic crane / Technocrane-type system;
- handheld;
- shoulder rig;
- Steadicam-type stabilised body rig;
- motorized gimbal/stabiliser;
- drone/aerial platform;
- vehicle mount/car rig;
- cable cam;
- robot arm / motion-control rig;
- POV/body/head mount;
- virtual camera rig;
- another typed support system.

The support class may influence, where relevant:

- allowed/constrained movement axes;
- mount offset;
- pivot location;
- boom/arm length;
- telescoping behaviour;
- pan/tilt/roll behaviour;
- path shape;
- altitude;
- velocity;
- acceleration/deceleration;
- easing;
- damping/inertia;
- stabilisation response;
- operator/body micro-motion;
- horizon/banking behaviour;
- parent-platform movement;
- repeatability.

`Drone Shot`, `jib`, `tripod`, `dolly`, `handheld`, `Steadicam`, `gimbal` and similar terms are not merely style tags when physical movement fidelity matters.

### Lighting and material relationship

Where relevant:

- source position/orientation;
- source type/size;
- calibrated or declared intensity units;
- colour temperature/spectrum;
- distance/falloff;
- modifiers/diffusion;
- flags/negative fill;
- practical relationships;
- environment contribution;
- material/light transport;
- temporal lighting changes.

### Output intent

Where useful the Shot may define or inherit:

- resolution/aspect/frame rate;
- bit depth/channels;
- colour working/display state;
- SDR/HDR target;
- alpha;
- depth;
- normals;
- motion vectors;
- mattes/IDs;
- required AOVs/light groups;
- baked/non-destructive operations;
- rich master/intermediate requirements;
- final delivery requirements.

The exact renderer-specific representation remains behind the Renderer Adapter.

## 4. Cinematography State as a grouped canonical concept

To avoid an unmaintainable flat Shot schema, implementations should treat the detailed physical/cinematic state as a grouped versioned concept.

Conceptually:

```text
Shot
  -> Cinematography State
       -> Camera State
       -> Lens / Optics State
       -> Camera Support & Movement Rig State
       -> Focus / Zoom / Exposure Trajectories
       -> Lighting State
       -> Spatial Layering State
       -> Colour / Camera Response State
       -> Output Intent
```

This is a conceptual ownership grouping. Implementations may use separate typed aggregates/value objects where appropriate, but they must preserve one resolved Shot meaning and must not create competing sources of truth.

The Continuity Snapshot should reference the resolved versions required for reproduction/validation.

## 5. Director Creative Freedom Guardrail

The physics-first architecture exists to give the AI and production systems **direction**, not to dictate aesthetics.

The following distinction is mandatory:

```text
creative intent
!=
technical recommendation
!=
validation evidence
!=
creative authority
```

Brain/Producer may say:

- a proposed Shot crosses the conventional 180-degree line;
- a lens/camera choice changes perspective/FOV;
- an impossible camera move cannot be performed by a physical jib;
- a renderer cannot reproduce a required camera path exactly;
- a Shot may be difficult to cut conventionally;
- a physically inconsistent exposure or optical treatment is being used;
- another route may preserve the intended effect more faithfully.

But those observations do not automatically give Brain authority to replace the Director's choice.

### Director choices that remain valid

The Director may intentionally choose:

- one long Shot instead of conventional coverage;
- many Shots where one would technically suffice;
- a jump cut;
- crossing the 180-degree line;
- broken eyelines;
- discontinuous screen direction;
- impossible perspective;
- impossible optics;
- exaggerated lens behaviour;
- deliberately flat staging;
- deep focus or extreme shallow focus;
- overexposure/underexposure;
- unusual shutter behaviour;
- surreal or nonphysical lighting;
- handheld instability;
- perfectly impossible stabilisation;
- a drone-like move in an impossible physical space;
- a virtual crane move no real crane could perform;
- animation/anime/cartoon camera language;
- any other intentional creative departure.

Nexkosmo should classify the result as intentional style/departure where appropriate rather than trying to repair it back to convention.

Permanent rule:

> Physics describes consequences. Continuity protects established truth. Coverage explains what may be needed. None of them outranks an intentional Director decision.

## 6. Coverage sufficiency must not become coverage doctrine

Coverage Obligations remain useful because they tell Brain what the audience may need to understand, see, hear, track or feel.

They MUST NOT become a hidden requirement that every Director use conventional filmmaking grammar.

Rules:

1. Coverage Obligations are analysis/evidence, not creative commands.
2. Brain may propose the smallest justified coherent Shot structure, but the Director may choose a different structure.
3. A Director may deliberately leave an obligation unconventional, ambiguous, obscured or unresolved as part of the creative experience.
4. Brain may explain the consequence of that choice without automatically creating extra Shots.
5. READY should block only when committed PRODUCTION would otherwise have to invent a consequential creative decision or cannot technically execute the Director's established intent through any approved route.
6. Taste, convention or model preference is never by itself a critical READY blocker.

Permanent rule:

> Coverage sufficiency informs the Director; it does not standardize the Director.

## 7. Physics-first must not become realism-first

Physics-first means Nexkosmo understands the causes and consequences of image formation when physical coherence is intended.

It does **not** mean every project or Shot must be photoreal, physically possible or conventionally photographed.

The system should preserve three evidence states:

```text
physically coherent
intentional stylisation/departure
renderer limitation / accidental inconsistency
```

Only the third should normally be treated as a technical fidelity problem.

When the Director intentionally chooses the second, Nexkosmo should preserve and execute that choice as faithfully as possible.

Permanent rule:

> Know the physical rule so the Director can obey it, bend it or break it deliberately.

## 8. Renderer capability must not design the movie

Renderer capability matching occurs **after** canonical creative/Shot intent is established sufficiently for the requested operation.

The normal priority is:

```text
Director intent
-> Scene truth
-> coverage/cinematic design
-> physical/stylised Shot specification
-> renderer/hybrid capability matching
-> execution
```

Not:

```text
available renderer
-> simplify or rewrite Shot
-> change creative intent to fit tool
```

Rules:

1. Renderer limitations never rewrite canonical Scene truth.
2. Renderer limitations do not silently redefine required creative coverage.
3. Render Orchestration should first seek another compatible renderer, 3D route, real-time route, VFX/compositing route or hybrid route.
4. A lower-fidelity approximation may be offered when useful, with limitations declared.
5. Redesigning a Shot because of execution limitations is a Director-facing production choice, not an automatic correction.
6. Technical segmentation required by a renderer never creates new canonical Shots.

Permanent rule:

> Define the movie first. Find the execution route second. Change the movie for a tool only when the Director chooses that trade-off.

## 9. Automatic synchronization must preserve experimentation

The automatic synchronization rules continue to classify edits by meaning and scope rather than by page.

This must not prevent experimentation.

Rules:

1. Purely cinematic changes normally remain Shot-local.
2. Material story events update shared Scene truth when clearly intended.
3. Ambiguous Shot experimentation defaults to the narrowest safe non-destructive scope.
4. Experimental camera, rig, lens, lighting, spatial or VFX choices do not become Scene facts merely because they appear in one preview.
5. A preview/render result never becomes canonical creative truth merely because it looks successful.
6. The Director may promote an experiment into Scene/project intent later without recreating it.

Permanent rule:

> Synchronize meaning, not experimentation.

## 10. BUILD UI after camera-rig alignment

The default BUILD UI remains progressive and visual-first.

When Camera is selected, the normal Director-facing controls may include simple meaningful choices such as:

```text
Locked
Tripod
Handheld
Shoulder
Steadicam
Gimbal
Dolly
Slider
Jib / Crane
Drone
Vehicle
Motion Control
Custom
```

The exact labels may evolve and should be appropriate to project type and supported functionality.

A Director selecting `Jib Up` should not be forced to understand pivot coordinates, arm geometry and angular velocity unless they open advanced controls.

A Director selecting `Drone Follow` should not need to configure a six-degree-of-freedom flight model unless desired.

Brain may translate the simple choice into a deeper Camera Support & Movement Rig State underneath.

Advanced users may expose:

- mount and pivot geometry;
- arm/boom/telescope parameters;
- constrained axes;
- path splines;
- speed/acceleration/easing;
- stabilisation/damping;
- micro-motion;
- banking/horizon behaviour;
- repeatability;
- numeric transforms;
- other rig-specific controls.

Permanent rule:

> Professional depth lives underneath simple creative choices. The UI must not make cinematography knowledge a prerequisite for having a cinematic idea.

## 11. Discover -> Shape -> Build inheritance

The transition between stages should feel continuous rather than like file handoff between separate applications.

Conceptually:

```text
IDEA
  creative premise / known intent

DISCOVER
  Scene identities
  anchor moments
  scene assets
  visual references
  unresolved story gaps

SHAPE
  same Scene identities
  action/dialogue/performance/audio
  established/proposed/unknown narrative state

BUILD
  same Scene identities
  1..N Shot identities
  inherited Scene truth
  cinematic construction
  physical/stylised cinematography state
  camera rig/movement
  spatial layering
  output intent
  preview evidence
```

No stage should require the Director to recreate truth already established upstream.

## 12. What each stage must not do

### IDEA must not

- force premature technical setup;
- require complete story knowledge;
- guess unresolved creative truth merely to fill fields.

### DISCOVER must not

- turn every visual moment into a final Shot automatically;
- flatten editable scene composition into canonical truth;
- force a linear complete movie before progression.

### SHAPE must not

- silently establish AI-written material as Director truth;
- require final cinematography before screenplay development;
- duplicate the Scene as a separate source of truth.

### BUILD must not

- rewrite established story to make rendering easier;
- impose conventional shot grammar;
- force photoreal physics when stylisation is intended;
- let renderer capability determine creative truth;
- duplicate shared Scene/3D assets per Shot;
- force all technical controls on the Director simultaneously.

## 13. READY remains the serious gate

IDEA, DISCOVER, SHAPE and BUILD are creative working stages.

They should permit incompleteness, unconventional choices, experiments, proposed material and declared approximations while preserving provenance and consequences.

READY is the stage that asks whether committed PRODUCTION can proceed without inventing a consequential creative decision or violating an established critical constraint.

READY may warn about:

- unconventional continuity;
- weak/ambiguous coverage;
- deliberate physical departures;
- renderer approximations;
- costly or difficult execution;
- stylistic inconsistency.

Warnings do not automatically become blockers.

A critical blocker should exist only when the unresolved condition prevents a viable production route from expressing the Director's established intent without an unauthorised creative invention or critical identity/continuity failure.

Permanent rule:

> Earlier stages help the Director create. READY protects committed Production. Do not turn creative guidance into premature gates.

## 14. Implementation decision order

When Brain/Producer assists the Director from IDEA through BUILD, the preferred reasoning order is:

```text
1. Preserve explicit Director intent.
2. Resolve existing canonical Project/Scene/asset truth.
3. Keep unknowns unknown when they are not yet necessary.
4. Distinguish established truth from AI proposals.
5. Identify what the audience may need to understand/feel.
6. Propose, never impose, creative structure or coverage.
7. Build the Director-selected Shot specification.
8. Preserve physical relationships where realism/coherence is intended.
9. Preserve intentional stylisation/departure when chosen.
10. Capability-match renderers/hybrid routes to the Shot.
11. Declare approximation rather than rewriting intent.
12. Produce derived preview/output evidence.
13. Synchronize only meaningful canonical consequences.
14. Ask the Director only when a consequential ambiguity cannot safely remain unresolved.
```

## 15. Permanent rules

> IDEA asks what the Director wants to make. DISCOVER finds the moments. SHAPE establishes what happens, is said and is heard. BUILD decides how the audience sees and experiences that same Scene.

> A Discover scene-moment frame is not automatically a BUILD Shot.

> BUILD adds cinematography to the Scene; it does not rebuild the Scene.

> Camera support and movement rigs are part of cinematic state when they materially define camera motion, not decorative labels.

> Physics gives the AI direction; it does not give the AI creative authority.

> Know the physical rule so the Director can obey it, bend it or break it deliberately.

> Coverage sufficiency informs the Director; it does not standardize the Director.

> Define the movie first. Find the execution route second.

> Renderer limitations never rewrite Director intent or canonical Scene truth.

> Synchronize meaning, not experimentation.

> Professional depth lives underneath simple creative choices.

> Earlier stages remain fluid. READY blocks only production-critical unresolved conditions.

> The Director remains the final creative authority.