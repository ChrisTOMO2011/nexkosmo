# BUILD Progressive Disclosure UI Contract

**Status:** Adopted product/architecture contract  
**Applies to:** BUILD frontend, Brain/Producer interaction, design system and future BUILD tools  
**Related contracts:** `SCENE_SHOT_DATA_CONTRACT.md`, `AUTOMATIC_SYNCHRONIZATION_RULES.md`, `SHOT_COVERAGE_SUFFICIENCY.md`, `PHYSICS_FIRST_CINEMATOGRAPHY.md`

## 1. Purpose

BUILD is intentionally powerful. It may contain shot creation, shared 3D scene structure, character/object placement, blocking, cameras, lenses, focus, lighting, layered assets, target-aware drag-and-drop, AI asset creation, VFX requirements, preview generation, route selection and price estimates.

Those capabilities belong in BUILD architecturally, but they MUST NOT all compete for attention at the same time.

The governing rule is:

> BUILD keeps full production power underneath one workspace, but reveals controls progressively according to the Director's current selection and task. Capability depth must not become simultaneous interface complexity.

## 2. Default BUILD surface

The default BUILD page should remain visually simple enough that a new or young Director can understand the next useful action without learning the entire production system.

The default surface should emphasize:

- current Scene;
- current Shot or Shot list;
- visual scene/shot workspace;
- simple add/create/search interactions;
- Producer assistance;
- clear next/preview actions;
- compact cost visibility where useful.

Advanced controls stay available but collapsed/contextual until needed.

## 3. Selection-driven controls

BUILD should reveal controls based primarily on what the Director selects.

Examples:

### No selection

Show:

- Scene/Shot overview;
- add/create asset;
- Shot navigation;
- Preview/Render entry;
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
- camera movement;
- lighting relationship/preview impact;
- camera-linked preview controls.

A simple Director should be able to work with perceptual choices such as `wider / closer`, `longer / more isolated`, `more / less background focus`, `locked / handheld / moving`, or approved camera/lens presets without seeing every optical parameter.

Advanced users may expose exact filmback, focal length, camera transform/distance, aperture/T-stop, focus distance, shutter, measured lens profile, distortion, breathing, vignetting and other supported optical characteristics.

Changing one camera/lens variable should not imply that the others are independent. Where the result depends on a coupled physical relationship, BUILD/Brain should update or explain the consequence rather than presenting controls as unrelated style sliders.

Hide unrelated deep character, prop or lighting tools unless explicitly opened.

### Character selected

Reveal relevant controls such as:

- scene/shot position;
- blocking/movement;
- wardrobe/accessories;
- injury/damage/state;
- target-aware attachments;
- performance references where appropriate;
- identity-safe asset actions.

### Object/prop/vehicle selected

Reveal relevant controls such as:

- placement/transform;
- attachment relationships;
- condition/damage;
- scene-vs-shot scope;
- replace/remove;
- object-specific AI creation or variation.

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

Reveal relevant controls such as:

- effect type;
- timing;
- source/target;
- simulation/AI/traditional route where relevant;
- layer/matte requirements;
- preview options.

### Preview/Render selected

Reveal relevant controls such as:

- preview vs production quality;
- supported route choices;
- physical/optical fidelity limitations when material;
- estimated credits and money value;
- expected duration;
- capability limitations when material;
- max charge before execution.

## 4. Progressive depth levels

BUILD may use progressive depth rather than separate disconnected pages.

A useful conceptual model is:

```text
Level 1 - Direct
  move, add, remove, create, choose Shot, preview

Level 2 - Contextual
  camera/lens, blocking, attachments, lighting, VFX, audio links

Level 3 - Advanced
  exact filmback/camera/lens/optical controls, precise transforms,
  renderer route, technical passes, dependency/provenance,
  detailed pricing/compute diagnostics
```

The exact UI may evolve, but the Director should not need to open Level 3 controls to perform ordinary creative work.

## 5. Visual-first interaction

Where an operation can be performed safely through direct manipulation, BUILD should prefer visual/direct interaction over exposing raw technical forms.

Examples:

- drag character into Scene instead of requiring coordinates;
- drag accessory onto valid target instead of manually editing relationship IDs;
- move camera visually, then expose lens/focus controls contextually;
- choose a perceptual camera change and let Brain preserve the underlying physical relationships;
- select a Shot preview to edit it rather than navigating through backend entities;
- use natural-language/voice creation for missing assets while preserving typed canonical state underneath.

Technical precision remains available for advanced users.

## 6. Context persistence

When the Director selects an item or Shot, BUILD should preserve enough context that creating or editing related material does not force them to leave the workflow.

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
-> adjust lens
-> Brain preserves/explains coupled field-of-view, distance and focus implications
-> preview
-> compare result
-> continue Shot work
```

No unnecessary page detours should be introduced merely because the underlying system is complex.

## 7. Scene scope versus Shot scope

The UI should help the Director understand scope without constant confirmation prompts.

Examples:

- editing from Scene context naturally suggests Scene-wide state;
- editing from a selected Shot naturally suggests Shot-local state when ambiguous;
- explicit language such as `for the whole scene` or `only this shot` overrides contextual default;
- promotion from Shot override to Scene state should be available without recreating the edit.

The automatic synchronization contract remains authoritative for semantic classification.

## 8. Complexity follows intent

Controls should appear when they become relevant to what the Director is trying to do.

Examples:

- do not expose rig controls until character motion/animation requires them;
- do not expose full optical/lens calibration data during ordinary camera composition;
- do not expose renderer capability matrices during ordinary scene composition;
- do not expose detailed VFX simulation settings when no VFX element is selected;
- do not expose full pricing breakdown until the Director is considering a materially chargeable operation;
- do not expose dependency graphs unless troubleshooting or advanced inspection requires them.

## 9. Producer assistance

The AI Producer should reduce interface burden rather than add another permanent control panel.

Producer may:

- suggest the next useful control;
- explain what a selected item can do;
- explain the perceptual effect of a camera/lens/lighting change;
- preserve physics-first camera/lens relationships behind simple Director language;
- create/configure assets from natural language;
- propose Shot coverage;
- explain cost/quality trade-offs;
- surface a continuity issue when it matters;
- open the relevant control context when the Director asks.

Producer must not force the Director through a conversational workflow for actions that are faster visually.

## 10. Pricing visibility without clutter

BUILD should keep cost understandable without turning the workspace into a billing dashboard.

Default presentation may show compact values such as:

```text
Preview: 42 credits / $0.42
Scene estimate: 1,240 credits / $12.40
```

Exact numerical mappings remain governed by the pricing target and must not be frozen until benchmarked.

When the Director opens Preview/Render or another chargeable action, BUILD may reveal deeper breakdowns such as:

- reused assets;
- new asset creation cost;
- per-Shot cost;
- quality tier differences;
- route differences;
- maximum charge.

## 11. Children/new-user usability

Powerful architecture must not require expert vocabulary.

The normal BUILD experience should be understandable through actions such as:

- Add Character
- Move
- Camera
- Lens
- Focus
- Light
- Effect
- Create
- Preview
- Next

Terms such as filmback, T-stop, entrance pupil, MTF, focus breathing, dependency graph, Continuity Snapshot, renderer adapter, motion vectors, normal passes or manifest revision belong in advanced/diagnostic views unless the Director asks for them.

## 12. Advanced-user access

Progressive disclosure must not remove professional control.

Advanced Directors may intentionally expose:

- numeric transforms;
- sensor/filmback metadata;
- exact lens/focal-length and camera-distance metadata;
- aperture/T-stop and focus distance;
- shutter/exposure-time controls;
- measured or physical lens profiles;
- distortion/breathing/vignetting/aberration controls where supported;
- precise lighting measurements where supported;
- layer/pass configuration;
- renderer/route selection;
- asset versions;
- dependency and invalidation details;
- provenance;
- detailed cost/compute estimates;
- technical diagnostics.

The same canonical state is edited regardless of UI depth.

## 13. State-driven panels, not permanent clutter

Implementation should prefer contextual inspectors, drawers, overlays, expandable panels or similar mechanisms over permanently displaying every tool category.

The exact visual design may evolve, but the invariant is:

```text
current task/selection
-> relevant controls visible
-> adjacent useful controls discoverable
-> unrelated deep controls hidden but reachable
```

## 14. No hidden destructive behavior

Progressive disclosure must not hide consequential state changes.

The UI may hide complexity, but it must still communicate when an operation:

- changes the whole Scene rather than one Shot;
- changes canonical identity;
- materially changes camera/lens/perspective or physical cinematography intent;
- replaces/removes a shared asset;
- causes a materially chargeable operation;
- invalidates significant downstream work;
- creates a critical READY issue.

This can be communicated contextually without persistent clutter.

## 15. Performance and responsiveness

Progressive disclosure should also support performance.

BUILD need not load/render every deep inspector, preview or diagnostic at once. Heavy panels may be loaded when selected, provided canonical state remains available and interaction feels immediate.

## 16. READY relationship

BUILD is a creative construction workspace, not the main validation gate.

The Director should be free to explore incomplete or unconventional configurations.

BUILD may surface useful warnings in context, including renderer/physics approximations, but READY remains the serious point where production-critical unresolved conditions are evaluated before committed PRODUCTION.

## 17. Permanent rules

> Keep the architecture powerful underneath and the default BUILD experience simple on the surface.

> Reveal controls because the Director selected something or started a task, not because the capability exists somewhere in the system.

> Direct manipulation first where safe; technical depth remains available when requested.

> Simple camera/lens choices may control a deep physical model underneath; BUILD must not reduce optics to unrelated style sliders.

> Progressive disclosure hides interface complexity, never canonical truth or consequential effects.

> BUILD should feel like one cinematic workspace that grows with the Director, not a wall of professional software panels shown all at once.