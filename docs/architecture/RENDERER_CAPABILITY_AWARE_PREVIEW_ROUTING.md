# Renderer Capability-Aware Preview Routing

**Status:** Adopted product/architecture contract  
**Applies to:** BUILD, PRODUCTION, Brain, Continuity Engine, Render Orchestrator, Renderer Adapters  
**Related contract:** `ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md`

## 1. Purpose

This contract defines how Nexkosmo creates shot preview frames without assuming that every renderer can consume every canonical control.

The canonical Scene/Shot state may contain approved 3D structure, camera definitions, depth, motion, identity references, masks, lighting, blocking and other rich production data. A renderer may support all, some or none of those controls.

The governing rule is:

> A Renderer Adapter must explicitly declare which canonical controls it can faithfully consume. Render Orchestration may use only supported controls and must choose another compatible or hybrid route when required controls cannot be honoured.

## 2. Capability declaration is mandatory

Every Renderer Adapter must expose a typed Renderer Capability Profile.

A capability must not be represented as a vague boolean when the renderer only partially supports it. At minimum, each relevant capability should classify support as one of:

- `supported` — the renderer can consume the control directly and the adapter can map it faithfully;
- `constrained` — the renderer supports the control only within declared limits or approximation bounds;
- `unsupported` — the renderer cannot consume the control in a reliable way;
- `unknown` — support has not been verified and must not be assumed.

A renderer with `unknown` support is treated as unsupported for requirements that materially affect continuity, identity or camera fidelity until verified.

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
- focal length/lens controls;
- framing controls;
- camera movement controls;
- depth-map input;
- normal-map input;
- motion-vector input/output;
- segmentation/mask input;
- alpha/matte output;
- depth/normal/motion passes;
- lighting controls;
- environment conditioning;
- object-placement controls;
- multi-character consistency capability;
- temporal consistency capability;
- lip-sync/performance controls;
- VFX/simulation support;
- compositing/layer output;
- cancellation/retry/resume support;
- expected cost and latency;
- model/engine/checkpoint/version metadata;
- licence/provenance constraints.

The profile must describe real verified adapter capability, not marketing claims.

## 4. Shot Requirement Profile

Before preview routing, Brain/Continuity/Render Orchestrator derives a Shot Requirement Profile from canonical Scene/Shot state.

Requirements may be classified as:

- **required** — losing the control would materially misrepresent the Shot, identity, continuity or Director intent;
- **preferred** — improves fidelity but a declared approximation may still be useful for exploration;
- **optional** — can be omitted without materially changing the intended preview purpose.

Example:

```text
Shot 12 preview requirements
- Sarah identity reference: required
- exact 50mm lens: required
- shared 3D blocking: preferred
- depth conditioning: preferred
- alpha output: optional
- final-quality lighting: optional
```

## 5. Capability matching

The Render Orchestrator must compare the Shot Requirement Profile against candidate Renderer Capability Profiles before execution.

Conceptually:

```text
Canonical Shot State
-> Shot Requirement Profile
-> candidate Renderer Capability Profiles
-> capability match
-> compatible route / hybrid route / declared approximation
-> Render Manifest
-> preview execution
```

Rules:

1. Required controls must never be silently dropped.
2. Unsupported required controls disqualify a single-renderer route unless an approved hybrid route can satisfy them.
3. Constrained capabilities may be used only when the Shot requirements fall inside the declared constraints.
4. Unknown capability must not be treated as supported.
5. Preferred controls may be omitted only when the preview remains useful and the omission is recorded as a known limitation.
6. Optional controls may be omitted without changing canonical state.

## 6. No false fidelity

A preview must not imply that a renderer honoured controls it never received or cannot interpret.

Examples:

- If an AI renderer cannot consume exact camera focal length, Nexkosmo must not label the result as exact 50mm camera compliance.
- If it cannot use the approved 3D scene structure, the result must not be treated as evidence that spatial blocking matches the 3D source.
- If identity locking is weak or unsupported, the preview must not silently become an approved identity reference.
- If depth conditioning is unsupported, the adapter must not pretend the depth map constrained the output.

The permanent rule is:

> A visually plausible preview is not proof that unsupported canonical controls were obeyed.

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

## 8. Hybrid preview routing

A hybrid route may satisfy requirements that no single renderer supports.

Example:

```text
Shared 3D Scene + camera
-> render depth / camera / blocking reference

Approved human identity references
-> AI appearance/performance renderer

Masks / passes
-> compositor

Result
-> derived preview linked to all participating adapters and inputs
```

Hybrid routing must preserve a unified timing, camera, continuity and identity contract where those controls are required.

## 9. Approximate previews

Approximate previews are allowed for creative exploration when they remain useful and do not masquerade as exact compliance.

An approximate preview should record:

- which required/preferred controls were actually consumed;
- which controls were approximated;
- which controls were unsupported/omitted;
- renderer/model/version;
- expected fidelity limitations;
- whether the preview is suitable for composition, identity, camera, motion, lighting or only general mood/look exploration.

The normal UI may simplify this into an understandable label such as `Composition preview`, `Identity-approximate`, `Camera-accurate`, or another approved presentation.

## 10. Preview acceptance classes

Nexkosmo may classify derived previews by what they are reliable enough to evaluate.

Examples:

- **Composition-valid** — useful for framing/layout but not identity proof;
- **Camera-valid** — camera/lens/blocking controls were faithfully consumed;
- **Identity-valid** — approved identity controls and validation passed;
- **Continuity-valid** — required continuity inputs were consumed and validation passed;
- **Look-only** — useful for mood/style exploration only;
- **Production-reference** — sufficiently validated for downstream production reference according to policy.

A preview may carry more than one class.

These classes are evidence labels, not new canonical truth.

## 11. Adapter evidence

Every preview result must retain enough evidence to determine:

- Renderer Adapter identity/version;
- Renderer Capability Profile version;
- Shot Requirement Profile version;
- controls requested;
- controls actually mapped;
- controls omitted/approximated;
- canonical Scene/Shot/Continuity Snapshot revisions;
- renderer/model/checkpoint/version;
- output validation results;
- cost/compute/latency;
- whether another route was considered or required.

## 12. Failure and fallback

If execution shows that a declared capability is unreliable, Nexkosmo should:

1. fail or downgrade the relevant validation class;
2. preserve the canonical Shot unchanged;
3. record adapter evidence;
4. update or quarantine the capability claim if appropriate;
5. reroute to another compatible renderer or hybrid path where useful;
6. avoid charging the user for unusable platform-attributable failed work according to the approved pricing policy.

## 13. BUILD behaviour

BUILD asks for a preview of the canonical Shot. It does not need to force the Director to choose technical renderer details unless they want advanced control.

Brain/Render Orchestrator should normally choose a compatible route automatically from:

- required Shot controls;
- quality purpose;
- expected fidelity;
- time;
- cost;
- available compute;
- validated Renderer Capability Profiles.

Advanced users may inspect or select routes when useful.

## 14. READY relationship

READY should not reject a Scene merely because an exploratory renderer lacks a capability.

READY cares whether committed PRODUCTION has a viable route capable of expressing required canonical intent.

If Renderer A cannot consume exact camera or identity state but Renderer B or a hybrid route can, READY may still pass.

A critical blocker exists only when no approved production route can satisfy a required material constraint without changing canonical creative meaning.

## 15. Permanent rules

> Renderer capability is declared, verified and versioned; it is never assumed.

> Required Shot controls must be matched to supported adapter capabilities before execution.

> Unsupported controls are not silently dropped. Reroute, hybridize, declare approximation, or do not use that renderer for the requirement.

> Renderer limitations never rewrite canonical Scene/Shot truth.

> Preview evidence must say what the renderer actually controlled, not what Nexkosmo hoped it controlled.