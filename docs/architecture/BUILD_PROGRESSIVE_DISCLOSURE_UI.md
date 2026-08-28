# BUILD Progressive Disclosure UI Contract

**Status:** Adopted product/architecture contract  
**Applies to:** BUILD frontend, Brain/Producer interaction, design system and future BUILD tools  
**Related contracts:** `SCENE_SHOT_DATA_CONTRACT.md`, `AUTOMATIC_SYNCHRONIZATION_RULES.md`, `SHOT_COVERAGE_SUFFICIENCY.md`, `PHYSICS_FIRST_CINEMATOGRAPHY.md`, `IDEA_TO_BUILD_FLOW_ALIGNMENT_AND_DIRECTOR_FREEDOM.md`

## 1. Purpose

BUILD is intentionally powerful. It may contain shot creation, shared 3D scene structure, character/object placement, blocking, cameras, lenses, focus, camera support/movement rigs, lighting, layered assets, target-aware drag-and-drop, AI asset creation where needed for scene construction, VFX requirements, preview generation, route inspection and price estimates.

Those capabilities belong in BUILD because they are needed to define and judge the Shot. BUILD MUST NOT absorb final PRODUCTION execution or STUDIO finishing merely because the same underlying tools could technically be invoked there.

The governing rules are:

> BUILD keeps full BUILD-authorized production-planning power underneath one workspace, but reveals controls progressively according to the Director's current selection and task. Capability depth must not become simultaneous interface complexity.

> A capability belongs in the earliest stage that genuinely needs it, and no earlier. Preview access does not automatically unlock final Production execution, and defining output intent does not automatically unlock Studio finishing.

## 2. Stage boundary

BUILD answers:

> How should this established Scene be constructed as Shots so the intended result can be produced?

BUILD may therefore define and preview:

- Shot structure and coverage;
- blocking and movement;
- camera, lens, focus and exposure intent;
- tripod/dolly/jib/crane/handheld/Steadicam/gimbal/drone/vehicle/motion-control or other camera-support intent;
- lighting and spatial-layering intent;
- props, states and dependencies;
- CGI/VFX requirements;
- output/pass requirements needed downstream;
- renderer/hybrid compatibility for preview and production planning;
- test renders/previews sufficient to judge the Shot.

BUILD does **not** become the normal home for:

- committed final-quality Shot generation/rendering;
- full production simulations or final animation execution;
- final VFX execution simply because the requirement was specified in BUILD;
- final compositing;
- final colour grade;
- final dialogue edit/mix;
- final sound design/music mix;
- titles/mastering/delivery encoding.

Those responsibilities remain with PRODUCTION and STUDIO according to the canonical journey.

Permanent rule:

> BUILD defines and proves the Shot. PRODUCTION makes the approved Shot. STUDIO finishes the produced material.

## 3. Default BUILD surface

The default BUILD page should remain visually simple enough that a new or young Director can understand the next useful action without learning the entire production system.

The default surface should emphasize:

- current Scene;
- current Shot or Shot list;
- visual scene/shot workspace;
- simple add/create/search interactions;
- Producer assistance;
- clear next/preview actions;
- compact cost visibility where useful.

Advanced BUILD controls stay available but collapsed/contextual until needed. Controls belonging primarily to PRODUCTION or STUDIO should not be exposed merely as hidden advanced BUILD features.

## 4. Selection-driven controls

BUILD should reveal controls based primarily on what the Director selects.

### No selection

Show:

- Scene/Shot overview;
- add/create asset where required for construction;
- Shot navigation;
- Preview/Test entry;
- lightweight scene status/cost.

Do not show full camera, rig, lighting, VFX and object-inspector panels simultaneously.

### Camera selected

Reveal relevant controls progressively such as:

- position/orientation;
- camera height and distance to subject;
- camera/sensor/filmback preset where relevant;
- lens/focal length;
- framing and field of view;
- aperture/T-stop where supported;
- focus distance/depth of field;
- shutter/motion behaviour where relevant;
- camera support/movement platform;
- camera movement;
- lighting relationship/preview impact;
- camera-linked preview controls.

A simple Director should be able to work with perceptual choices such as `wider / closer`, `longer / more isolated`, `more / less background focus`, or movement-platform choices such as `locked`, `tripod`, `handheld`, `Steadicam`, `gimbal`, `dolly`, `slider`, `jib/crane`, `drone`, `vehicle` or another appropriate preset without seeing every physical parameter.

Advanced BUILD users may expose exact filmback, focal length, camera transform/distance, aperture/T-stop, focus distance, shutter, measured lens profile, distortion, breathing, vignetting, rig path/pivot constraints and other supported properties that materially define the Shot.

Changing one camera/lens/rig variable should not imply that the others are independent. Where the result depends on a coupled physical relationship, BUILD/Brain should update or explain the consequence rather than presenting controls as unrelated style sliders.

Hide unrelated deep character, prop or lighting tools unless explicitly opened.

### Character selected

Reveal relevant BUILD controls such as:

- scene/shot position;
- blocking/movement intent;
- wardrobe/accessories;
- injury/damage/state;
- target-aware attachments;
- performance references where appropriate;
- identity-safe asset actions.

Final animation/performance execution remains a PRODUCTION responsibility unless a preview/test execution is needed to judge the Shot.

### Object/prop/vehicle selected

Reveal relevant controls such as:

- placement/transform;
- attachment relationships;
- condition/damage;
- scene-vs-shot scope;
- replace/remove;
- object-specific AI creation or variation when required to construct the Shot.

### Lighting selected

Reveal relevant controls such as:

- light placement/orientation;
- source size/softness;
- intensity/exposure contribution;
- distance to subject where relevant;
- colour temperature/colour intent;
- practicals;
- modifiers/negative fill where supported;
- scene-wide vs shot-local lighting;
- camera/exposure relationship;
- preview impact.

Lighting controls should preserve the principle that the visible result emerges from source geometry, camera/exposure and material response where the selected route supports physical treatment.

### VFX/CGI element selected

Reveal BUILD controls needed to define the requirement, such as:

- effect type;
- timing;
- source/target;
- required interaction with scene geometry/characters;
- intended production route where useful;
- layer/matte/pass requirements;
- preview/test options.

Detailed final simulation/render execution remains in PRODUCTION unless a limited test is required to validate the design.

### Preview/Test selected

Reveal relevant controls such as:

- preview/test purpose;
- preview quality;
- supported route choices where useful;
- physical/optical/rig fidelity limitations when material;
- estimated credits and money value;
- expected duration;
- capability limitations when material;
- max charge before execution.

BUILD may invoke AI, real-time, 3D, offline renderers or hybrid routes to create evidence sufficient to judge a Shot. That permission does not convert BUILD into final PRODUCTION.

If the Director requests a committed final-quality Shot, the workflow should move to or invoke PRODUCTION under the PRODUCTION stage contract rather than silently treating BUILD preview as final execution.

## 5. Progressive depth levels

BUILD may use progressive depth rather than separate disconnected pages.

A useful conceptual model is:

```text
Level 1 - Direct
  move, add, remove, create, choose Shot, preview

Level 2 - Contextual
  camera/lens/rig, blocking, attachments, lighting, VFX requirements, audio links

Level 3 - Advanced BUILD
  exact filmback/camera/lens/rig/optical controls, precise transforms,
  preview route, output/pass requirements, dependency/provenance,
  detailed planning/pricing/compute diagnostics
```

Level 3 means advanced **BUILD** control. It is not a backdoor that exposes every PRODUCTION or STUDIO function early.

The exact UI may evolve, but the Director should not need to open Level 3 controls to perform ordinary creative work.

## 6. Visual-first interaction

Where an operation can be performed safely through direct manipulation, BUILD should prefer visual/direct interaction over exposing raw technical forms.

Examples:

- drag character into Scene instead of requiring coordinates;
- drag accessory onto valid target instead of manually editing relationship IDs;
- move camera visually, then expose lens/focus/rig controls contextually;
- choose a perceptual camera change and let Brain preserve the underlying physical relationships;
- select a Shot preview to edit it rather than navigating through backend entities;
- use natural-language/voice creation for missing assets while preserving typed canonical state underneath.

Technical precision remains available for advanced users when it belongs to BUILD.

## 7. Context persistence

When the Director selects an item or Shot, BUILD should preserve enough context that creating or editing related material does not force them to leave the workflow unnecessarily.

Example:

```text
Select Sarah
-> Create sunglasses
-> sunglasses generated/retrieved
-> immediately available to attach to Sarah
-> Scene/Shot context remains open
```

Likewise:

```text
Select Shot 4 camera
-> choose Jib Up
-> Brain resolves the deeper rig/camera relationships
-> preview/test
-> compare result
-> continue Shot work
```

Stage ownership still applies. Context persistence is not permission to relocate final Production or Studio responsibilities into BUILD.

## 8. Scene scope versus Shot scope

The UI should help the Director understand scope without constant confirmation prompts.

Examples:

- editing from Scene context naturally suggests Scene-wide state;
- editing from a selected Shot naturally suggests Shot-local state when ambiguous;
- explicit language such as `for the whole scene` or `only this shot` overrides contextual default;
- promotion from Shot override to Scene state should be available without recreating the edit.

The automatic synchronization contract remains authoritative for semantic classification.

## 9. Complexity and capability follow intent

Controls should appear only when both conditions are true:

1. they are relevant to the Director's current task; and
2. the capability belongs to BUILD rather than a later stage.

Examples:

- do not expose full optical/lens calibration data during ordinary camera composition;
- do not expose renderer capability matrices during ordinary scene composition;
- do not expose final VFX simulation controls merely because a VFX requirement exists;
- do not expose Studio mastering or final mix controls in BUILD;
- do not expose full pricing breakdown until the Director is considering a materially chargeable operation;
- do not expose dependency graphs unless troubleshooting or advanced inspection requires them.

The strongest capability boundary rule is:

> Do not unlock a capability merely because Nexkosmo can perform it. Unlock it when the current stage needs it to fulfill that stage's purpose.

## 10. Producer assistance

The AI Producer should reduce interface burden rather than add another permanent control panel.

Producer may:

- suggest the next useful BUILD control;
- explain what a selected item can do at this stage;
- explain the perceptual effect of a camera/lens/rig/lighting change;
- preserve physics-first relationships behind simple Director language;
- create/configure assets from natural language where BUILD genuinely needs them;
- propose Shot coverage;
- explain cost/quality trade-offs;
- surface a continuity issue when it matters;
- explain when a requested action belongs in PRODUCTION or STUDIO;
- open the relevant BUILD control context when the Director asks.

Producer must not force the Director through a conversational workflow for actions that are faster visually, and it must not bypass stage ownership merely because a connected tool is available.

## 11. Pricing visibility without clutter

BUILD should keep cost understandable without turning the workspace into a billing dashboard.

Default presentation may show compact values such as:

```text
Preview: estimated credits / money value
Scene production estimate: estimated credits / money value
```

Exact numerical mappings remain governed by the pricing target and must not be frozen until benchmarked.

When the Director opens Preview/Test or another chargeable BUILD action, BUILD may reveal deeper planning breakdowns such as:

- reused assets;
- new asset creation cost;
- estimated per-Shot Production cost;
- quality-tier differences;
- route differences;
- maximum charge for the current BUILD operation.

A Production estimate is planning information; it does not itself begin committed Production.

## 12. Children/new-user usability

Powerful architecture must not require expert vocabulary.

The normal BUILD experience should be understandable through actions such as:

- Add Character
- Move
- Camera
- Lens
- Focus
- Camera Move
- Light
- Effect
- Create
- Preview
- Next

Terms such as filmback, T-stop, entrance pupil, MTF, focus breathing, rig pivot geometry, dependency graph, Continuity Snapshot, renderer adapter, motion vectors, normal passes or manifest revision belong in advanced/diagnostic views unless the Director asks for them.

## 13. Advanced-user access

Progressive disclosure must not remove professional BUILD control.

Advanced Directors may intentionally expose BUILD-relevant controls such as:

- numeric transforms;
- sensor/filmback metadata;
- exact lens/focal-length and camera-distance metadata;
- aperture/T-stop and focus distance;
- shutter/exposure-time controls;
- measured or physical lens profiles;
- camera-support/movement-rig path and constraints;
- distortion/breathing/vignetting/aberration controls where supported;
- precise lighting measurements where supported;
- output/pass requirements for downstream Production/Studio;
- preview renderer/route selection;
- asset versions;
- dependency and invalidation details;
- provenance;
- detailed planning/compute estimates;
- technical diagnostics.

Advanced access MUST NOT silently unlock final Production execution or Studio finishing controls inside BUILD.

The same canonical state is edited regardless of UI depth.

## 14. State-driven panels, not permanent clutter

Implementation should prefer contextual inspectors, drawers, overlays, expandable panels or similar mechanisms over permanently displaying every BUILD tool category.

The exact visual design may evolve, but the invariant is:

```text
current task/selection
-> relevant BUILD controls visible
-> adjacent useful BUILD controls discoverable
-> unrelated BUILD controls hidden but reachable
-> later-stage capabilities remain in their owning stage
```

## 15. No hidden destructive behavior

Progressive disclosure must not hide consequential state changes.

The UI may hide complexity, but it must still communicate when an operation:

- changes the whole Scene rather than one Shot;
- changes canonical identity;
- materially changes camera/lens/rig/perspective or physical cinematography intent;
- replaces/removes a shared asset;
- causes a materially chargeable operation;
- invalidates significant downstream work;
- creates a critical READY issue.

This can be communicated contextually without persistent clutter.

## 16. Performance and responsiveness

Progressive disclosure should also support performance.

BUILD need not load/render every deep inspector, preview or diagnostic at once. Heavy panels may be loaded when selected, provided canonical state remains available and interaction feels immediate.

BUILD also should not pre-load or initialize expensive final Production/Studio systems merely because they exist downstream.

## 17. READY, PRODUCTION and STUDIO relationship

BUILD is a creative construction workspace, not the main validation gate and not the final execution stage.

The Director should be free to explore incomplete or unconventional configurations.

BUILD may surface useful warnings in context, including renderer/physics approximations, but READY remains the serious point where production-critical unresolved conditions are evaluated before committed PRODUCTION.

After READY:

```text
BUILD
  defines and previews the Shot

READY
  validates committed production readiness

PRODUCTION
  creates/acquires/renders/animates/simulates the approved source Shot material

STUDIO
  edits, composites, colours, mixes, titles, masters and delivers the produced material
```

STUDIO may identify a source change that requires targeted return to PRODUCTION. That does not make Studio the owner of source-shot production.

## 18. Permanent rules

> A capability belongs in the earliest stage that genuinely needs it, and no earlier.

> Do not unlock a capability merely because Nexkosmo can perform it. Unlock it when the current stage needs it to fulfill that stage's purpose.

> BUILD defines and proves the Shot. PRODUCTION makes the approved Shot. STUDIO finishes the produced material.

> Preview capability does not imply final Production capability is unlocked.

> Defining output/pass requirements in BUILD does not turn BUILD into final rendering, compositing or mastering.

> Keep the architecture powerful underneath and the default BUILD experience simple on the surface.

> Reveal controls because the Director selected something or started a BUILD task, not because the capability exists somewhere in the system.

> Direct manipulation first where safe; technical depth remains available when requested and stage-appropriate.

> Simple camera/lens/rig choices may control a deep physical model underneath; BUILD must not reduce cinematography to unrelated style sliders.

> Progressive disclosure hides BUILD interface complexity, never canonical truth or consequential effects, and never erases stage ownership.

> BUILD should feel like one cinematic construction workspace, not a wall of every professional capability Nexkosmo has.