# Build Render Specification Contract

**Status:** Proposed canonical architecture for Director review  
**Applies to:** BUILD, Scene/Shot preparation, Studio handoff, render orchestration, renderer adapters, previews, regeneration, provenance, and Production render control  
**Authority:** Nexkosmo Canon and explicit Director instruction

## 1. Purpose

BUILD is not merely a visual editor. BUILD is the preparation system that converts the Director's visible Scene or Shot decisions into a complete, machine-readable, versioned render specification.

The governing rule is:

> What the Director sees in BUILD must be what the rendering system receives.

The visual workspace and the machine-readable specification are two views of the same approved state. A visible edit must not exist only in UI state, a transient prompt, or renderer-local memory if it materially affects the requested result.

BUILD shall capture enough validated state, references, exclusions, continuity, provenance, and execution metadata to reproduce, diagnose, compare, or regenerate a Scene or Shot as consistently as technically possible.

Generative rendering is probabilistic. Nexkosmo must not promise visual perfection or absolute determinism where the selected renderer cannot provide it. The system instead optimises for fidelity, consistency, repeatability, diagnosability, and traceability.

## 2. Director Experience and Hidden Complexity

The Director-facing experience should remain simple:

`SEE -> SELECT -> ADJUST -> PREVIEW -> APPROVE`

Underneath, BUILD performs:

`Resolve Canon -> Compose Scoped State -> Validate Continuity -> Build Render Specification -> Preserve Evidence -> Freeze Version -> Dispatch`

The interface should hide unnecessary implementation complexity without hiding material creative state.

Complexity remains available underneath, but the Director should primarily see what is relevant to the current creative decision.

## 3. Freedom Model

Nexkosmo uses three levels of freedom.

### 3.1 Frozen state — no silent interpretation

Once approved, the following may not be silently changed by AI, Studio, orchestration, or a renderer:

- canonical asset identity and exact version;
- Scene and Shot scope;
- Director-approved identity, composition, continuity, and preparation state;
- approved camera/framing where explicitly set;
- explicit inclusions and exclusions;
- accepted preview reference;
- render-specification version and provenance;
- rights, consent, or access constraints.

Any material change requires an explicit proposed change, override, or new render-specification version.

### 3.2 Constrained state — optimisation allowed, meaning preserved

The system may adapt technical execution when required, provided approved creative meaning is preserved and the adaptation is recorded. Examples include:

- renderer/provider selection;
- renderer-specific translation of canonical controls;
- native technical segmentation;
- batching and scheduling;
- retry strategy;
- cache reuse;
- intermediate masks, depth, normals, mattes, control maps, or proxy representations;
- performance and cost optimisation;
- unsupported-parameter fallback only when the semantic effect is preserved and the fallback is disclosed.

### 3.3 Creative state — broad freedom before approval

Before approval, AI may propose alternatives and variations such as:

- lighting ideas;
- camera options;
- wardrobe alternatives;
- expressions and poses;
- environment treatments;
- VFX treatments;
- composition variants;
- renderer-specific creative experiments.

A proposal or variation is never allowed to mutate approved state silently.

### 3.4 Permanent rule

> AI may be creative before approval. After approval, it becomes an executor of the approved specification unless the Director explicitly requests a new variation.

## 4. Render Specification Scope

Every renderable Scene or Shot configuration shall be represented by a typed, versioned Render Specification.

The specification must capture all applicable material state, including:

### 4.1 Identity and canonical assets

- canonical asset IDs;
- exact asset versions/revisions;
- character identity masters;
- environment IDs;
- prop, vehicle, wardrobe, accessory, camera, lighting, material, audio, VFX, and other asset references;
- canonical versus Scene-specific versus Shot-specific scope;
- inherited state and explicit overrides.

### 4.2 Character state

Where applicable:

- identity;
- body/species/type;
- wardrobe;
- accessories;
- hair, face, eyes, beard, age, makeup, markings, damage, dirt, injuries, transformation state;
- pose, blocking, hand placement, eyeline, orientation;
- expression and emotional state;
- dialogue/performance reference where preparation requires it.

### 4.3 Spatial state

For applicable assets and subjects:

- position;
- rotation;
- scale;
- depth ordering;
- parent/attachment relationships;
- relative placement;
- occlusion intent;
- masks, mattes, alpha channels, depth maps, normals, motion guides, control images, and other spatial evidence where available.

### 4.4 Environment and set state

- environment identity/version;
- location and world state;
- vegetation;
- weather;
- time of day;
- atmosphere;
- terrain and surfaces;
- set dressing;
- prop placement and condition;
- physical changes inherited from earlier Shots.

### 4.5 Camera and framing

Where applicable:

- camera identity or virtual camera state;
- position and orientation;
- focal length/lens;
- sensor or equivalent framing assumptions;
- shot size and framing;
- aspect ratio;
- focus target;
- depth of field;
- camera movement preparation;
- screen direction and continuity constraints.

### 4.6 Lighting

Where applicable:

- source identity/type;
- position and direction;
- colour/temperature;
- intensity/exposure contribution;
- softness/hardness;
- falloff;
- shadow expectations;
- practical lights;
- environment/ambient contribution;
- lighting continuity inherited from prior Shots.

### 4.7 Materials and surfaces

Where applicable:

- material identity/version;
- texture identity/version;
- surface state;
- roughness, wetness, dirt, damage, wear, reflection, translucency or other relevant material facts;
- continuity-sensitive changes.

### 4.8 CGI, VFX, audio, and specialist references

- CGI asset or simulation references;
- VFX references and layer intent;
- audio, dialogue, ambience, music, SFX, timing, or sync references where relevant to the Shot preparation;
- specialist tool references that affect execution.

### 4.9 Uploaded references and guidance evidence

- uploaded images;
- uploaded video;
- source references;
- reference frames;
- masks;
- alpha channels;
- depth maps;
- pose/control guides;
- segmentation maps;
- sketches and layout references;
- any other conditioning material supplied or generated for faithful execution.

References must preserve provenance, rights, and scope.

### 4.10 Instructions and exclusions

The specification shall preserve both:

- positive instructions describing required intent; and
- explicit exclusions / negative constraints describing what must not appear or change.

Renderer-specific negative-prompt syntax is an adapter concern. The semantic exclusions themselves remain renderer-independent Brain state.

### 4.11 Continuity

The specification shall reference the applicable versioned Continuity Snapshot and make inherited state visible and traceable.

It must distinguish:

- inherited canonical state;
- inherited prior-Shot state;
- Scene-level overrides;
- Shot-level overrides;
- explicit deliberate continuity breaks approved by the Director.

### 4.12 Generation and execution metadata

Where supported or applicable:

- provider;
- model/engine;
- model/checkpoint/version;
- generation settings;
- scheduler/sampler;
- guidance values;
- seed;
- resolution;
- frame rate;
- duration;
- quality tier;
- renderer capability assumptions;
- deterministic/stochastic status;
- technical translation notes;
- provenance.

Unsupported settings must be represented explicitly rather than silently discarded when they materially affect repeatability.

### 4.13 Accepted preview

Director approval must bind the Render Specification to the exact accepted preview or preview evidence that was reviewed.

The accepted preview is evidence of intended appearance, not a replacement for structured state.

The preview and specification must reference each other so Nexkosmo can establish:

> This is the approved visual evidence for this exact specification version.

## 5. Scope and Override Model

BUILD must distinguish master canonical state from scoped production state.

A canonical Character, Environment, Prop, Vehicle, Material, or other reusable asset remains reusable and independently versioned.

Scene- or Shot-specific changes such as:

- wardrobe;
- mud;
- injuries;
- expression;
- pose;
- placement;
- lighting interaction;
- temporary damage;
- local environment state;

must not silently rewrite the reusable canonical master.

The UI must make scope clear before consequential edits are committed.

Recommended conceptual scope levels:

`Canonical Asset -> Scene Override -> Shot Override`

A change to a broader scope must be deliberate and auditable.

## 6. Approval and Versioning

When the Director approves a configuration, Nexkosmo shall freeze it as an immutable versioned Render Specification.

Example identity:

`render-spec-sc024-sh018-v007`

Approval shall preserve at minimum:

- specification ID;
- version;
- project/sequence/scene/shot identity;
- continuity snapshot reference;
- canonical asset/version references;
- accepted preview reference;
- approval actor;
- approval timestamp;
- provenance;
- content hash or equivalent immutable identity where technically appropriate.

A subsequent material change creates a new version rather than silently rewriting the approved version.

## 7. Variation Rule

AI-generated alternatives must branch from approved or draft state as explicit Variations.

Examples:

- alternate camera;
- alternate lighting;
- different expression;
- wardrobe option;
- VFX treatment;
- environmental treatment.

A Variation may be previewed and compared without becoming authoritative.

Only explicit Director approval promotes a Variation into a new approved Render Specification version.

## 8. No Silent Reinterpretation

No subsystem may silently change Director-approved creative meaning.

This includes BUILD, Studio, Brain services, Render Orchestrator, renderer adapters, rendering models, compositors, and optimisation services.

If a requested renderer cannot honour a material requirement, the system must do one of the following:

1. select a compatible execution route;
2. propose a disclosed approximation;
3. request approval for a change;
4. mark the requirement unsupported and STOP the affected path.

It must not silently substitute a different identity, composition, camera, wardrobe, environment, lighting state, or other material creative choice merely to obtain a successful render.

## 9. Renderer Adapter Rule

Renderer adapters translate; they do not creatively redesign.

Adapters may convert canonical state into provider-specific controls, prompts, graphs, scene files, nodes, parameters, or API requests.

The adapter must preserve semantic equivalence as far as the renderer permits and record material translation loss.

A provider's aesthetic bias or default behaviour never outranks approved Brain state.

## 10. Studio Handoff

Studio may enrich an approved BUILD specification with performance and temporal information such as:

- animation;
- timing;
- dialogue timing;
- facial performance;
- body performance;
- camera motion curves;
- simulation timing;
- edit timing;
- sound synchronisation.

Studio must not silently reinterpret approved identity, composition, canonical assets, camera preparation, environment preparation, wardrobe, continuity, or other frozen BUILD state.

If Studio needs to change a frozen BUILD decision, it must create an explicit proposed override or a new specification version for Director approval.

## 11. Render Dispatch

The Render Orchestrator receives validated approved state and creates one or more executable Render Manifests.

The relationship is:

`Approved Render Specification -> Continuity Snapshot -> Render Manifest(s) -> Renderer Adapter(s) -> Render Result(s)`

The Render Specification represents Director-approved creative preparation.

The Render Manifest represents the technical execution plan for one renderer route or render job.

A Render Manifest may add technical detail but may not weaken or reinterpret the approved Render Specification.

## 12. Failure, Diagnosis, and Regeneration

A failed or unsatisfactory render must remain traceable to the same approved evidence.

Nexkosmo should be able to determine whether failure arose from:

- unsupported renderer capability;
- renderer/model stochastic behaviour;
- conflicting references;
- incomplete specification;
- continuity conflict;
- asset/version mismatch;
- adapter translation loss;
- technical execution error;
- generative corruption;
- validation failure;
- Director-requested change.

Regeneration should reuse the same approved Render Specification when the creative intent has not changed.

If the creative intent changes, a new version or Variation must be created.

## 13. UI Contract for BUILD

BUILD is a visual creation workspace, not an administrative form.

The UI shall:

- keep the creative preview as the visual priority;
- reveal controls contextually rather than exposing all parameters permanently;
- prefer visual selection where practical;
- make canonical, Scene, and Shot scope understandable;
- expose inherited continuity and overrides when relevant;
- show what is currently selected and what will be changed;
- avoid dense technical terminology unless requested or required;
- allow advanced technical inspection without forcing it on beginners;
- keep global shell controls visually secondary to the creative workspace;
- support ordinary laptop-height use without burying core actions below the fold;
- provide a clear preview/approve path;
- ensure every material visible edit maps to structured render-specification state.

The UI may simplify presentation, but it must not create materially important hidden creative state that is absent from the specification.

## 14. Validation Gates

An approved Render Specification should not be dispatchable if required material state is unresolved.

Validation may include:

- canonical asset references resolve;
- asset versions exist and are authorised;
- Scene/Shot scope is unambiguous;
- required identity and continuity constraints resolve;
- references are available and authorised;
- camera/framing is internally coherent where required;
- required masks/guides exist where explicitly depended upon;
- exclusions are represented;
- renderer route can honour required constraints or has disclosed limitations;
- accepted preview is bound when approval requires it;
- provenance is complete enough for the selected execution path.

Skipped blocking validation remains blocking.

## 15. Provenance and Audit

For each approved Render Specification and result, Nexkosmo shall retain enough evidence to answer:

- who or what made each material change;
- which canonical assets and versions were used;
- which Scene and Shot were targeted;
- which continuity state was inherited;
- which references and guides were used;
- which instructions and exclusions applied;
- which preview was approved;
- which renderer/provider/model/version executed the work;
- which settings and seed were used where supported;
- which technical translations occurred;
- what validation passed or failed;
- whether the result is reproducible exactly, approximately, or not deterministically;
- who approved the result.

## 16. Architectural Invariants

The following invariants are mandatory:

1. What the Director sees in BUILD and what the renderer receives are representations of the same approved creative state.
2. Material visible edits must map to structured state.
3. Canonical masters are not silently mutated by Scene/Shot overrides.
4. AI may propose freely before approval but may not silently reinterpret approved state.
5. Approved Render Specifications are immutable and versioned.
6. Variations branch; they do not mutate approved state.
7. Renderer adapters translate but do not creatively redesign.
8. Studio may enrich performance and timing but may not silently change frozen BUILD preparation.
9. Failure and regeneration remain traceable to the approved specification and evidence.
10. Renderers remain replaceable.
11. Probabilistic rendering limitations must be stated honestly.
12. Nexkosmo optimises for fidelity, consistency, repeatability, diagnosability, and traceability rather than claiming impossible perfection.

## 17. Relationship to Existing Architecture

This contract extends `ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md`.

Amendment 001 already establishes that:

- the Brain owns truth;
- continuity is renderer-independent;
- every render originates from validated, versioned state;
- Render Manifests are contracts;
- renderer adapters may translate but may not change approved creative meaning;
- results retain provenance and validation evidence.

This BUILD contract defines the missing upstream preparation layer that converts Director-visible decisions into the approved structured state from which Continuity Snapshots and Render Manifests are produced.

## 18. Production Render Controls and Cost Transparency

After READY validates the approved preparation, PRODUCTION becomes the Director's live render-control board. The Scene/Shot structure remains visible, but cards now represent execution state rather than planning alone.

### 18.1 Scene-level controls

Every renderable Scene card should show, where calculable:

- Scene identity/title;
- number of Shots;
- Scene duration;
- readiness state;
- estimated render cost;
- estimated completion time;
- selected quality tier or render profile;
- current execution state;
- a clear `Render Scene` action.

`Render Scene` is a Director-facing batch action. It does not turn the Scene into one indivisible generation request.

Underneath, Nexkosmo shall preserve the canonical hierarchy:

`Scene -> Shot -> Render Job -> Render Result`

The Render Orchestrator may further segment a Shot internally when technically required, but that segmentation remains an implementation detail and must not replace the Director's Scene/Shot model.

### 18.2 Shot-level controls

Opening a Scene should expose its Shots individually. Each Shot should show, where calculable:

- Shot identity;
- duration;
- readiness state;
- estimated render cost;
- estimated completion time;
- render/validation status;
- last accepted result or preview;
- a `Render` or `Re-render` action;
- a route to Studio when specialist repair or deep editing is required.

The Director may render one Shot without rendering the entire Scene.

### 18.3 Cost estimates

Render prices shown before execution are estimates unless the selected route provides a guaranteed fixed price.

The estimate should be derived from the best available execution evidence, including as applicable:

- Shot duration;
- resolution and frame rate;
- quality tier;
- renderer/provider pricing;
- model or engine selection;
- character and motion complexity;
- camera movement;
- VFX/simulation requirements;
- number of layers/passes;
- expected retries or sampling requirements;
- compute route and hardware class;
- reusable cached/intermediate work;
- current provider/runtime cost data.

The UI must distinguish estimated cost from final actual cost.

Before a paid render is dispatched, the Director should be able to see the current estimate and the scope of what will be rendered. Where cost may materially exceed the estimate, Nexkosmo should require renewed confirmation or apply an explicit approved spending limit rather than silently overspend.

After completion, Nexkosmo shall retain the actual charged/consumed cost, compute usage, renderer/provider, duration, and relevant execution evidence for audit and future estimation.

### 18.4 No unnecessary re-rendering

Rendering or re-rendering a Scene must not automatically regenerate already valid unaffected Shots when the dependency graph permits reuse.

If only one Shot, layer, frame range, simulation, audio element, or other dependency requires regeneration, Nexkosmo should identify and execute the smallest valid affected scope.

Successful unaffected work should be reused when technically safe and traceable.

This principle protects:

- Director time;
- creator money/credits;
- compute resources;
- renderer capacity;
- approved continuity;
- reproducibility.

### 18.5 Scene estimate roll-up

A Scene estimate should normally be the current aggregate of its eligible Shot estimates plus any Scene-level shared execution costs that cannot be attributed to one Shot.

A Production-level estimate may similarly roll up Scene estimates, but must remain visibly an estimate until execution is fixed or completed.

If a renderer/provider changes, a specification changes, quality changes, caches become invalid, or another material cost input changes, the estimate should be recalculated and visibly marked as updated.

### 18.6 Execution states

Production cards should communicate clear states such as:

- Ready to Render;
- Queued;
- Rendering;
- Validating;
- Preview Ready;
- Needs Repair;
- Re-render Required;
- Approved;
- Blocked.

A job reporting technical success is not automatically equivalent to creative or continuity approval.

### 18.7 Director authority

A `Render Scene` or `Render Shot` action authorises execution of the currently displayed approved specification scope. It does not authorise the renderer, orchestrator, Studio, or AI to modify the Director's approved creative meaning.

If execution requires a material creative change, Nexkosmo must stop that affected path and request approval or create an explicit proposed Variation.

## 19. Permanent Rule

> Before approval, help the Director explore. After approval, execute the approved state. Never silently reinterpret what the Director approved. In PRODUCTION, show the Director what will be rendered, what it is expected to cost, and what actually happened.
