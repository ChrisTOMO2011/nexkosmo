# Renderer Capability-Aware Preview Routing

**Status:** Adopted product/architecture contract  
**Applies to:** BUILD, READY, PRODUCTION, Brain, Continuity Engine, Render Orchestrator, Renderer Adapters  
**Related contracts:** `ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md`, `PHYSICS_FIRST_CINEMATOGRAPHY.md`, `PRICING_BENCHMARK_CALIBRATION.md`

## 1. Purpose

This contract defines how Nexkosmo creates shot previews and chooses production routes without assuming that every renderer can consume every canonical control or that a technically capable route is reliable enough for guaranteed paid production.

The canonical Scene/Shot state may contain approved 3D structure, camera definitions, depth, motion, identity references, masks, lighting, blocking and other rich production data. A renderer may support all, some or none of those controls.

The governing rules are:

> A Renderer Adapter must explicitly declare which canonical controls it can faithfully consume. Render Orchestration may use only supported controls and must choose another compatible or hybrid route when required controls cannot be honoured.

> Capability alone is not production qualification. A route used for guaranteed paid production must also have measured reliability evidence for the relevant Shot class and versioned execution configuration.

## 2. Capability declaration is mandatory

Every Renderer Adapter must expose a typed Renderer Capability Profile.

A capability must not be represented as a vague boolean when the renderer only partially supports it. At minimum, each relevant capability should classify support as one of:

- `supported` — the renderer can consume the control directly and the adapter can map it faithfully;
- `constrained` — the renderer supports the control only within declared limits or approximation bounds;
- `unsupported` — the renderer cannot consume the control in a reliable way;
- `unknown` — support has not been verified and must not be assumed.

A renderer with `unknown` support is treated as unsupported for requirements that materially affect continuity, identity, camera fidelity or guaranteed production until verified.

## 3. Capability Profile

A Renderer Capability Profile may include, where relevant:

- media type and output type;
- image/video/3D/real-time/offline capability;
- duration limits;
- resolution limits;
- frame-rate limits;
- deterministic/stochastic behaviour;
- seed support;
- image/reference conditioning;
- identity-reference controls;
- likeness/identity-lock strength where measurable;
- pose conditioning;
- skeleton/rig controls;
- 3D geometry conditioning;
- camera position/orientation controls;
- camera support / movement-rig controls;
- support-rig class semantics such as tripod, slider, dolly, jib/crane, pedestal, handheld, shoulder, Steadicam, motorized gimbal, drone, vehicle mount, cable cam, motion-control rig, body/POV mount, or another declared platform;
- mount offset / pivot / boom / arm geometry where relevant;
- constrained-axis and pan/tilt/roll controls;
- camera path controls;
- velocity / acceleration / deceleration / easing controls;
- stabilisation / damping / inertia controls;
- operator-like micro-motion or rig-character controls where supported;
- repeatable motion-control path support where applicable;
- sensor/filmback controls;
- focal length/lens controls;
- field-of-view controls;
- aperture controls;
- focus-distance controls;
- optical depth-of-field support;
- shutter-angle/exposure-time controls;
- motion-blur controls;
- lens distortion controls;
- vignetting controls;
- chromatic-aberration controls;
- focus-breathing controls;
- flare/ghosting controls;
- anamorphic squeeze/optical controls;
- measured lens-profile support;
- framing controls;
- camera movement controls;
- depth-map input;
- normal-map input;
- motion-vector input/output;
- segmentation/mask input;
- alpha/matte output;
- depth/normal/motion passes;
- lighting controls;
- physical-light transport support;
- environment conditioning;
- object-placement controls;
- multi-character consistency capability;
- temporal consistency capability;
- lip-sync/performance controls;
- VFX/simulation support;
- compositing/layer output;
- colour-management / camera-response support where verified;
- cancellation/retry/resume support;
- expected cost and latency;
- model/engine/checkpoint/version metadata;
- licence/provenance constraints.

The profile must describe real verified adapter capability, not marketing claims.

A single broad claim such as `supports camera`, `supports lens`, `supports camera movement` or `supports lighting` is insufficient when only a subset of the physical relationship is actually supported.

## 4. Shot Requirement Profile

Before preview or production routing, Brain/Continuity/Render Orchestrator derives a Shot Requirement Profile from canonical Scene/Shot state.

Requirements may be classified as:

- **required** — losing the control would materially misrepresent the Shot, identity, continuity or Director intent;
- **preferred** — improves fidelity but a declared approximation may still be useful for exploration;
- **optional** — can be omitted without materially changing the intended purpose.

Example:

```text
Shot 12 requirements
- Sarah identity reference: required
- physical camera transform: required
- support rig: jib with pivoted boom movement: required
- 50mm focal length on established filmback: required
- camera-to-Sarah distance: required
- T2.8 / focus distance: preferred
- shared 3D blocking: preferred
- depth conditioning: preferred
- alpha output: optional
```

Where physical cinematography is required, related controls must be evaluated as a coupled requirement rather than independently. For example, exact focal length without filmback or camera position may be insufficient to preserve the intended field of view and perspective.

Likewise, a camera path described as a `jib`, `dolly`, `Steadicam`, `gimbal`, `handheld`, `drone` or other support class may carry physical movement semantics beyond a generic transform curve. The required platform behaviour must not be silently reduced to an arbitrary camera animation when it materially affects the Shot.

## 5. Capability matching

The Render Orchestrator must compare the Shot Requirement Profile against candidate Renderer Capability Profiles before execution.

Conceptually:

```text
Canonical Shot State
-> Shot Requirement Profile
-> candidate Renderer Capability Profiles
-> capability match
-> reliability qualification check
-> compatible qualified route / hybrid route / declared approximation
-> Render Manifest
-> execution
```

Rules:

1. Required controls must never be silently dropped.
2. Unsupported required controls disqualify a single-renderer route unless an approved hybrid route can satisfy them.
3. Constrained capabilities may be used only when the Shot requirements fall inside the declared constraints.
4. Unknown capability must not be treated as supported.
5. Preferred controls may be omitted only when the result remains useful and the omission is recorded as a known limitation.
6. Optional controls may be omitted without changing canonical state.
7. Coupled physical controls must not be split in a way that creates false fidelity. If a route supports a focal-length text hint but not filmback/camera geometry, it cannot be treated as physically lens-accurate.
8. Camera support / movement-rig semantics must be capability-matched when they materially define the Shot. A generic smooth camera path is not automatically equivalent to a dolly, jib, crane, stabilised body rig, handheld rig or drone trajectory.
9. A route that is technically capable but not reliability-qualified for the required production scope must not be represented as a guaranteed production route.

## 6. No false fidelity

A preview or result must not imply that a renderer honoured controls it never received or cannot interpret.

Examples:

- If an AI renderer cannot consume exact camera focal length, Nexkosmo must not label the result as exact 50mm camera compliance.
- If it accepts `50mm` only as text conditioning but does not consume filmback, camera transform or optical parameters, the result is a creative approximation rather than a physically defined 50mm image.
- If the Shot requires a jib arc but the renderer only supports a generic camera-motion text hint, the result must not be labelled jib-motion accurate.
- If the Shot requires a tripod-locked translation state, the renderer must not introduce unexplained floating or travelling camera motion and still claim rig fidelity.
- If the Shot requires handheld, Steadicam, gimbal or drone movement, a visually similar path is not automatically equivalent unless the required movement/stabilisation characteristics were actually controlled or validated.
- If it cannot use the approved 3D scene structure, the result must not be treated as evidence that spatial blocking matches the 3D source.
- If identity locking is weak or unsupported, the preview must not silently become an approved identity reference.
- If depth conditioning is unsupported, the adapter must not pretend the depth map constrained the output.
- If a renderer cannot model a measured lens profile, it must not claim exact reproduction of that lens family merely because the prompt names it.

The permanent rule is:

> A visually plausible result is not proof that unsupported canonical controls were obeyed.

## 7. Route selection

When the preferred renderer cannot satisfy required controls, the Render Orchestrator should choose the best compatible route without rewriting the Shot.

Possible routes include:

- another AI renderer;
- real-time 3D;
- offline 3D;
- traditional renderer;
- compositing route;
- hybrid route combining 3D structure with AI appearance/performance;
- lower-fidelity technical preview that clearly declares limitations;
- no preview from that renderer when the result would be misleading.

Renderer limitations must not cause Brain to mutate canonical Scene or Shot truth merely to fit the renderer.

When a Shot depends on physically coherent cinematography, route selection should prefer a renderer or hybrid route that preserves the required camera/lens/light and camera-support/movement-rig relationships defined by `PHYSICS_FIRST_CINEMATOGRAPHY.md`.

For paid production, route selection must consider measured reliability and cost/time per Brain-accepted result, not only per-attempt price or nominal capability.

## 8. Hybrid preview routing

A hybrid route may satisfy requirements that no single renderer supports.

Example:

```text
Shared 3D Scene + physical camera/lens/light setup + camera rig path
-> render camera-valid depth / blocking / motion / lighting reference

Approved human identity references
-> AI appearance/performance renderer

Masks / passes
-> compositor

Result
-> derived preview linked to all participating adapters and inputs
```

Hybrid routing must preserve a unified timing, camera, movement-rig, continuity and identity contract where those controls are required.

## 9. Approximate previews

Approximate previews are allowed for creative exploration when they remain useful and do not masquerade as exact compliance.

An approximate preview should record:

- which required/preferred controls were actually consumed;
- which controls were approximated;
- which controls were unsupported/omitted;
- renderer/model/version;
- expected fidelity limitations;
- whether the preview is suitable for composition, identity, camera, rig motion, motion, lighting or only general mood/look exploration.

The normal UI may simplify this into an understandable label such as `Composition preview`, `Identity-approximate`, `Camera-accurate`, `Rig-motion approximate`, `Lens-look approximation`, `Physics-valid`, or another approved presentation.

## 10. Preview acceptance classes

Nexkosmo may classify derived previews by what they are reliable enough to evaluate.

Examples:

- **Composition-valid** — useful for framing/layout but not identity proof;
- **Camera-valid** — camera transform/filmback/framing controls were faithfully consumed;
- **Rig-motion-valid** — required support-platform, path, pivot/constraint and stabilisation/movement characteristics were faithfully consumed or validated for the claimed scope;
- **Lens-geometry-valid** — focal length/FOV and applicable optical geometry were faithfully consumed;
- **Optics-valid** — required aperture/focus/optical controls were physically or measurably honoured according to policy;
- **Lighting-geometry-valid** — required light positions/sizes/directions were faithfully consumed;
- **Physics-valid** — the required coupled physical image-forming relationships were faithfully executed for the claimed scope;
- **Identity-valid** — approved identity controls and validation passed;
- **Continuity-valid** — required continuity inputs were consumed and validation passed;
- **Look-only** — useful for mood/style exploration only;
- **Production-reference** — sufficiently validated for downstream production reference according to policy.

A preview may carry more than one class.

These classes are evidence labels, not new canonical truth.

## 11. Adapter evidence

Every preview/result must retain enough evidence to determine:

- Renderer Adapter identity/version;
- Renderer Capability Profile version;
- Shot Requirement Profile version;
- controls requested;
- controls actually mapped;
- controls omitted/approximated;
- canonical Scene/Shot/Continuity Snapshot revisions;
- physical cinematography specification revision where applicable;
- camera support / movement-rig profile and revision where applicable;
- lens/camera profile evidence class where applicable;
- renderer/model/checkpoint/version;
- output validation results;
- cost/compute/latency;
- whether another route was considered or required;
- production reliability qualification state where applicable.

## 12. Failure and fallback

If execution shows that a declared capability is unreliable, Nexkosmo should:

1. fail or downgrade the relevant validation class;
2. preserve the canonical Shot unchanged;
3. record adapter evidence;
4. update or quarantine the capability claim if appropriate;
5. reroute to another compatible renderer or hybrid path where useful;
6. avoid charging the user for unusable platform-attributable failed work according to the approved pricing policy;
7. feed the failure into route reliability evidence and circuit-breaker evaluation.

## 13. BUILD behaviour

BUILD asks for a preview of the canonical Shot. It does not need to force the Director to choose technical renderer details unless they want advanced control.

Brain/Render Orchestrator should normally choose a compatible route automatically from:

- required Shot controls;
- required physical cinematography fidelity;
- required camera-support/movement-rig fidelity;
- quality purpose;
- expected fidelity;
- measured reliability where available;
- time;
- cost per Brain-accepted result where available;
- available compute;
- validated Renderer Capability Profiles.

Advanced users may inspect or select routes when useful.

For materially expensive or high-risk production work, BUILD/READY may require a short proof or representative test before committing the full execution route.

## 14. READY relationship

READY should not reject a Scene merely because an exploratory renderer lacks a capability.

READY cares whether committed PRODUCTION has a viable route capable of expressing required canonical intent **and, for a guaranteed production commitment, whether that route is reliability-qualified for the relevant scope**.

If Renderer A cannot consume exact camera, movement-rig or identity state but Renderer B or a hybrid route can, READY may still pass.

A critical blocker exists when:

- no approved production route can satisfy a required material constraint without changing canonical creative meaning; or
- Nexkosmo intends to make a guaranteed production commitment but no route has sufficient reliability evidence for that required Shot class and execution scope.

An experimental/unproven capability may continue through explicitly labelled testing, but it must not silently inherit the same guarantee as a qualified route.

## 15. Production Reliability Qualification

Technical capability and measured production reliability are separate evidence classes.

A route is scoped by the combination of material factors that affect its behaviour, including where relevant:

- Renderer Adapter version;
- provider/model/engine/checkpoint version;
- Shot class and complexity band;
- required identity/continuity/camera/motion/layer/output controls;
- duration/resolution/frame rate/quality tier;
- execution route and important hardware/runtime constraints;
- hybrid components and compositing path.

Reliability evidence from one materially different scope must not be silently generalized to another.

### 15.1 Qualification states

Nexkosmo should maintain a versioned reliability state for each material production route/scope:

- **EXPERIMENTAL** — capability may be under test; insufficient evidence for guaranteed paid production.
- **QUALIFIED** — repeatable measured evidence exists for the declared scope; route is eligible for controlled production according to policy.
- **GUARANTEED** — qualified route is inside the currently approved Nexkosmo customer guarantee envelope for the declared scope and commercial policy.
- **DEGRADED** — recent evidence has materially worsened or drifted; route remains under investigation and must not be treated as healthy guaranteed capacity unless policy explicitly permits a constrained use.
- **QUARANTINED** — route is blocked from normal guaranteed production because evidence shows unacceptable failure, provider/model drift, capability mismatch, or another material risk.

`GUARANTEED` does not mean every underlying attempt succeeds. It means Nexkosmo has enough evidence and recovery capacity to commercially stand behind the accepted outcome within the validated scope.

### 15.2 Mandatory reliability measurements

Qualification evidence should measure, by relevant Shot class and route scope:

- first-pass Brain acceptance rate;
- attempts per Brain-accepted result;
- cost per Brain-accepted result;
- elapsed time per Brain-accepted result;
- technical failure rate;
- identity failure rate where applicable;
- continuity failure rate where applicable;
- camera/movement/physics failure rate where applicable;
- required layer/pass/output-contract failure rate where applicable;
- targeted-repair success rate;
- alternate-route/fallback success rate;
- unresolved failure rate after approved retry/reroute policy;
- sample size and recency of evidence;
- provider/model/version drift indicators.

Exact numerical qualification thresholds are commercial/operational policy and must be established from measured evidence rather than invented prematurely.

### 15.3 Cheap proof before expensive execution

Where a Shot contains material uncertainty, Brain/Render Orchestrator should prove the risky requirement using the shortest/lowest-cost meaningful test before committing expensive full-quality work.

Examples include testing:

- identity preservation;
- multi-character interaction;
- camera/movement-rig behaviour;
- lip-sync/performance control;
- VFX/simulation behaviour;
- required layer/pass/AOV preservation;
- hybrid timing/depth/matte alignment;
- provider/model behaviour after a version change.

A proof is not accepted final production. It is reliability evidence used to avoid discovering predictable failure after the expensive execution has already been consumed.

### 15.4 Fallback plan before guarantee

For a guaranteed production commitment, Brain should know the recovery path before expensive execution begins where a practical fallback exists.

Conceptually:

```text
Primary qualified route
-> targeted repair / partial rerender
-> qualified alternate route
-> qualified hybrid route
-> unresolved STOP-GATE
```

The fallback may vary by Shot class. Nexkosmo must not promise a guaranteed capability solely because a primary route worked once.

### 15.5 Circuit breaker and automatic downgrade

Production evidence must continuously update route health.

If a route's observed performance materially departs from its qualified evidence, Brain/Render Orchestrator must be able to:

1. stop assigning new guaranteed work to the affected scope;
2. mark the route `DEGRADED` or `QUARANTINED` according to policy;
3. preserve in-flight and accepted evidence;
4. reroute eligible work to a qualified fallback;
5. require requalification after material provider/model/adapter changes;
6. prevent an agent, adapter or provider from self-restoring guaranteed status without governed evidence and authority.

The circuit breaker exists to prevent a degraded route from burning tokens/compute across hundreds of film-scale executions before Nexkosmo reacts.

### 15.6 Guaranteed versus experimental capability boundary

A capability that Nexkosmo has architecturally designed but not yet proven end to end remains `EXPERIMENTAL` for guarantee purposes.

This includes any layering, auxiliary-output, hybrid or other production behaviour whose required fidelity/reliability has not yet been demonstrated for the route in question.

Experimental capability may be tested and improved, but the user must not be led to believe it carries the same production guarantee as a qualified scope.

### 15.7 Route choice objective

For guaranteed production, Brain should optimize for the expected accepted outcome, not the cheapest attempt.

Conceptually:

```text
route value
= required fidelity and capability
+ measured acceptance reliability
+ recovery/fallback strength
+ time per Brain-accepted result
+ cost per Brain-accepted result
```

No single numeric formula is frozen here. The permanent requirement is that route choice must account for reliability and accepted-result economics at film scale.

## 16. Permanent rules

> Renderer capability is declared, verified and versioned; it is never assumed.

> Capability is necessary but not sufficient for guaranteed paid production; the route must also be reliability-qualified for the relevant scope.

> Required Shot controls must be matched to supported adapter capabilities before execution.

> Camera, camera-support/movement rig, lens, filmback, distance, aperture, focus, shutter and lighting may form one coupled physical requirement; capability matching must preserve that relationship where required.

> Unsupported controls are not silently dropped. Reroute, hybridize, declare approximation, or do not use that renderer for the requirement.

> Brain must prefer cost/time per Brain-accepted result over deceptively cheap per-attempt pricing when selecting guaranteed production routes.

> Use short, low-cost proofs to expose material uncertainty before expensive execution where practical.

> A degraded route must be automatically stoppable and quarantinable before failure compounds across film-scale workloads.

> Experimental/unproven capabilities do not inherit the guaranteed production promise until repeatable evidence qualifies them.

> Renderer limitations never rewrite canonical Scene/Shot truth.

> Preview and production evidence must say what the renderer actually controlled and achieved, not what Nexkosmo hoped it controlled.