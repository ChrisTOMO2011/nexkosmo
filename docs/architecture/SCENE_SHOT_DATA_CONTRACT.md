# Canonical Scene -> Shot Data Contract

**Status:** Adopted product/architecture contract  
**Applies to:** DISCOVER, SHAPE, BUILD, READY, PRODUCTION, STUDIO, Brain, Continuity Engine, Render Orchestrator, frontend and backend implementations

## 1. Purpose

This contract defines exactly what belongs to Project, Sequence, Scene and Shot; how scene state is inherited by shots; how shot-level overrides work; how versions and dependencies are represented; and how a resolved shot becomes a Continuity Snapshot and Render Manifest.

The purpose is to ensure that frontend, backend, Brain, Continuity and rendering systems implement one shared model rather than inventing competing interpretations.

The canonical hierarchy remains:

```text
Project
  -> Sequence
      -> Scene
          -> Shot (1..N)
              -> Continuity Snapshot
                  -> Render Manifest
                      -> Render Job
                          -> Render Result
```

BUILD may visually present the simpler relationship `Scene -> 1..N Shots`, but Sequence remains part of canonical production structure where applicable.

## 2. Governing principle

> A Scene owns shared narrative, world and continuity-bearing state. A Shot owns how a selected portion of that Scene is cinematically presented plus any explicit local overrides. Shots inherit Scene state; they do not duplicate the Scene.

## 3. Stable identity and immutable revisions

Project, Sequence, Scene and Shot use stable identities. Changes create new revisions rather than silently rewriting the historical state used by earlier renders or approvals.

Conceptually:

```text
scene_id      = stable identity
scene_revision = immutable revision of that scene

shot_id       = stable identity
shot_revision  = immutable revision of that shot
```

Implementation may use UUIDs or another approved opaque identifier scheme. Display numbers such as `Scene 7` or `Shot 7.04` are presentation/order labels and MUST NOT be used as canonical identity.

Rules:

1. Reordering shots MUST NOT create new Shot identities merely because their display position changes.
2. Historical revisions remain traceable to the assets, dependencies, snapshots, manifests and render results produced from them.
3. A new Scene revision does not silently mutate old Shot revisions or old render evidence.
4. A new Shot revision remains linked to the Scene revision from which its effective state was resolved.
5. Accepted render results remain evidence of the exact revisions that produced them even after later edits.

## 4. Project ownership

Project owns production-wide identity and settings that are broader than any single Scene.

Project-level state may include:

- project identity and workspace ownership;
- project type and destination when established;
- project-wide delivery intent and defaults;
- canonical reusable asset/library relationships;
- global rights, permissions and provenance references;
- project-level production settings and policies;
- sequence ordering and membership;
- project-wide style or creative intent when explicitly established at that scope.

Project state MUST NOT be copied independently into every Scene or Shot as competing truth. Scenes and Shots reference the relevant project-level state or approved versions.

## 5. Sequence ownership

Sequence groups and orders related Scenes where the production uses sequences.

Sequence-level state may include:

- sequence identity;
- scene membership/order;
- sequence narrative purpose;
- sequence-level timing intent;
- sequence-wide continuity or style state when explicitly established;
- transitions or structural relationships between Scenes.

Sequence MUST remain optional from the Director-facing workflow where showing it would add unnecessary complexity, but the canonical hierarchy may retain it underneath.

## 6. Scene ownership

Scene owns what materially exists or happens across the Scene and what should normally persist into every relevant Shot.

Scene-level state includes, where established:

### Narrative

- scene identity and narrative purpose;
- scene action and event order;
- dialogue and dialogue-beat references;
- reactions;
- entrances and exits;
- transformations and meaningful state changes;
- scene-level timing intent;
- narrative truth state such as Established, Inferred, Proposed or Unknown where relevant.

### Participants and identity

- characters/creatures/entities present;
- canonical character/entity identity references;
- approved identity-package versions;
- scene-level performance/emotional state;
- reusable voice identity references.

### Environment and world

- environment/location identity and version;
- shared 3D/spatial scene source where applicable;
- time of day;
- weather;
- scene-wide environment state;
- persistent set dressing and world state.

### Shared assets and continuity state

- props and vehicles that materially exist in the Scene;
- wardrobe state;
- accessories where scene-wide;
- Injury States and damage where scene-wide;
- dirt/blood/condition where scene-wide;
- persistent object ownership/location/condition;
- other scene-wide attachments or modifiers.

### Audio intent and linked assets

- dialogue-performance references;
- scene-level ambience;
- required SFX linked to narrative events;
- music/score intent and cue references;
- other audio dependencies established in SHAPE.

### Shared production state

- scene-wide lighting intent/state where applicable;
- shared geometry, 3D assets and reusable scene source data;
- continuity transitions that occur during the Scene;
- dependency references needed by the shots.

A Scene MUST NOT own a specific camera/lens/framing decision merely because one Shot uses it, unless the Director intentionally establishes a scene-wide cinematic rule.

## 7. Scene state transitions

A Scene is not assumed to be static from beginning to end. Material state changes may occur within it.

Examples:

- a character removes a jacket;
- an injury occurs;
- a prop moves from a table to a character's hand;
- rain begins;
- a door opens;
- a light is switched off;
- a vehicle is damaged.

Such changes are represented as explicit Scene state transitions associated with narrative/time/beat boundaries rather than by silently creating unrelated Shot copies.

A Shot resolves the Scene state that applies at the portion of the Scene it covers.

## 8. Shot ownership

Shot owns cinematic coverage of a portion of the parent Scene plus explicit local overrides.

Shot-level state includes, where applicable:

### Coverage

- stable Shot identity;
- parent Scene identity;
- order/display position;
- covered scene action/beat/dialogue references;
- shot start/end timing or narrative range;
- shot purpose where useful.

### Camera

- camera identity/state;
- position and orientation;
- lens/focal length;
- framing;
- camera height;
- camera movement;
- focus and depth-of-field intent;
- aspect/framing overrides where legitimately shot-specific.

### Shot construction

- shot-specific blocking refinements;
- composition;
- visibility/occlusion choices;
- foreground/background staging that exists only for the Shot;
- shot-specific object placement when intentionally local;
- shot-specific lighting adjustments;
- shot-specific CGI/VFX requirements;
- shot-specific timing/performance refinements;
- local production notes and dependencies.

### Derived working material

- storyboard/anchor-frame references;
- preview-frame/video references;
- shot-level validation state;
- pricing/compute estimate references where applicable.

A Shot MUST NOT duplicate the complete character, environment, prop or 3D asset as a new canonical asset merely to use it from another camera angle.

## 9. Inheritance

The effective state for a Shot is resolved from shared Scene state plus the Scene transitions applicable to that Shot plus explicit Shot overrides.

Conceptually:

```text
Resolved Shot State
  = Project/Sequence context
  + Scene Revision
  + Applicable Scene State Transitions
  + Referenced Asset Versions
  + Shot Revision / Shot Overrides
```

Rules:

1. Scene-level state is inherited by every relevant Shot automatically.
2. Shot overrides replace only the specific inherited property they explicitly override.
3. Unoverridden properties continue to resolve from the Scene.
4. Shot overrides MUST NOT silently mutate Scene state.
5. A Scene-level edit updates or invalidates only dependent Shots.
6. A Shot-level edit affects only that Shot unless deliberately promoted to Scene scope.
7. A Shot may reference a shared 3D character/environment/object source without copying that source into the Shot.

## 10. Scope classification in BUILD

BUILD should normally determine whether an edit is Scene scope or Shot scope from context without interrupting the Director.

Examples:

```text
"Sarah wears glasses in this scene"
-> Scene scope

"Move Sarah left in this shot"
-> Shot scope

"Remove the gun from the scene"
-> Scene scope

"Put the cup closer to camera"
while editing one Shot
-> Shot scope unless the Director establishes otherwise
```

Rules:

1. Clear Scene-wide intent propagates automatically to relevant Shots.
2. Clear Shot-local intent remains local.
3. The Director may promote a Shot-local change to Scene scope.
4. The Director may deliberately create a Shot override against inherited Scene state when continuity permits.
5. When scope is genuinely ambiguous but work can continue safely, Nexkosmo should prefer the least destructive/local interpretation and preserve the ability to promote it later rather than introducing an unnecessary roadblock.
6. Ask the Director only when the ambiguity is consequential and cannot be safely represented without changing creative meaning.

## 11. Shot count and ordering

A Scene contains `1..N` Shots.

Rules:

1. Shot count is never fixed at fifteen or any other quota.
2. Brain/Producer may propose an initial coverage plan from the SHAPE Scene.
3. The Director may add, delete, duplicate, merge, reorder or replace Shots.
4. Shot identity remains stable when order changes.
5. Display numbering may be recalculated without changing canonical Shot identity.
6. Deleting a Shot must preserve historical evidence for already-produced revisions according to audit/retention rules rather than pretending the Shot never existed.

## 12. Version propagation and invalidation

A change creates a new revision at the narrowest correct scope.

Examples:

### Scene-level wardrobe change

```text
Scene v12 -> Scene v13
Sarah wardrobe changed

Affected Shots containing Sarah after the change boundary:
- update resolved state
- mark affected previews/snapshots/manifests stale as required

Unrelated Shots:
- remain valid
```

### Shot-only camera change

```text
Shot 04 v6 -> Shot 04 v7
Lens 35mm -> 50mm

Scene revision:
- unchanged

Other Shots:
- unchanged
```

### Dialogue-line change

The dependency graph may invalidate only:

- changed dialogue asset;
- affected voice performance;
- affected Shot timing;
- face/lip-sync dependencies;
- affected Shot preview/render/composite.

Environment, unrelated Shots and unrelated assets remain reusable where valid.

## 13. Dependency Record

Every material derived object should record the dependencies needed to decide whether it remains valid after an upstream change.

A Dependency Record conceptually contains:

```text
consumer_identity
consumer_revision
source_identity
source_revision
relationship/type
scope
validity/status
```

Dependencies may connect:

- Scene -> Shot;
- Scene transition -> Shot;
- Asset Version -> Scene;
- Asset Version -> Shot;
- Dialogue beat -> Shot;
- Shot -> Continuity Snapshot;
- Continuity Snapshot -> Render Manifest;
- Render Manifest -> Render Job;
- Render Job -> Render Result;
- generated audio/VFX/preview -> source narrative or production state.

Dependency records support targeted regeneration, cache reuse, continuity validation and accurate pricing.

## 14. Continuity Snapshot

A Continuity Snapshot is NOT another editable Scene or Shot.

It is an immutable resolved production state for one renderable Shot revision.

Conceptually:

```text
Scene Revision
+ applicable Scene transitions
+ referenced Asset Versions
+ Shot Revision / overrides
+ continuity resolution
= Continuity Snapshot
```

The snapshot freezes the exact state required to reproduce and validate that Shot without relying on a renderer's memory.

It should reference, as applicable:

- Scene identity/revision;
- Shot identity/revision;
- character/entity versions and states;
- environment/world version/state;
- prop/vehicle/object state;
- wardrobe/accessory/injury/damage state;
- blocking and spatial state;
- camera state;
- lighting state;
- dialogue/performance references;
- timing and continuity references;
- provenance/approval state;
- dependency versions.

## 15. Render Manifest and execution boundary

The Render Manifest is generated from the validated Shot intent and Continuity Snapshot.

```text
Canonical Scene/Shot State
-> Continuity Snapshot
-> Render Manifest
-> Renderer Adapter
-> Render Job
-> Render Result
```

Rules:

1. Renderers do not own Scene or Shot truth.
2. Renderer-specific settings remain behind adapters.
3. A Render Result never silently modifies Scene or Shot state.
4. Renderer observations may return as evidence or proposals for Brain/Director consideration.
5. Old Render Results remain tied to the exact Snapshot and Manifest revisions that produced them.

## 16. Frontend contract

The frontend may simplify the model without flattening it.

BUILD should normally present:

```text
Scene
  Shot 1
  Shot 2
  Shot 3
  ...
```

The user does not need to see revision IDs, dependency records or inheritance graphs during ordinary creative work.

However the frontend must:

- preserve stable Scene/Shot IDs behind the UI;
- distinguish Scene-wide edits from Shot-local edits;
- allow Shot reorder without identity replacement;
- display inherited state naturally;
- make overrides editable/removable;
- surface stale/needs-update state when materially useful;
- avoid forcing manual synchronization between SHAPE and BUILD;
- support advanced provenance/version inspection where appropriate.

## 17. Backend contract

Backend services must implement the same ownership boundaries.

The backend MUST NOT:

- store a full disconnected Scene copy inside every Shot;
- infer identity from display numbering;
- overwrite historical revisions used by accepted renders;
- let renderer output become canonical state automatically;
- invalidate the entire Scene when a narrow dependency change can be identified;
- require frontend clients to manually reconstruct inheritance.

Backend APIs should return enough resolved state for the frontend's task while retaining canonical normalized ownership underneath.

## 18. Pricing relationship

The dependency graph and inheritance model directly support Nexkosmo pricing.

If a reusable asset already exists, the user is not charged as though it were recreated for every Shot. If one Shot changes, only affected compute and dependencies should be rerun and charged where technically practical.

Conceptually:

```text
Scene Cost
= shared scene preparation
+ required new assets
+ sum(affected Shot costs)
+ required scene-level finishing
```

Canonical ownership and dependency tracking therefore support both continuity and fair metering.

## 19. READY relationship

READY validates the resolved Scene -> Shot structure before committed full PRODUCTION.

READY should detect critical conditions such as:

- required Scene state that cannot be resolved for a Shot;
- incompatible or invalid Shot overrides;
- stale critical dependencies;
- conflicting continuity transitions;
- missing production information that would force PRODUCTION to invent a material creative decision.

Non-critical incompleteness should remain warning-level rather than creating unnecessary earlier-stage roadblocks.

## 20. Architectural invariants

1. Project -> Sequence -> Scene -> Shot remains the canonical production hierarchy.
2. A Scene contains one or more Shots; the count is dynamic.
3. Scene owns shared narrative/world/asset/continuity state.
4. Shot owns cinematic coverage and local overrides.
5. Shots inherit Scene state; they do not duplicate the Scene.
6. Shared 3D/source assets are referenced, not recreated per Shot.
7. Stable identity is separate from display order/numbering.
8. Scene and Shot changes create traceable revisions.
9. Dependency records determine targeted invalidation/regeneration.
10. Continuity Snapshot freezes resolved Shot state; it is not an editable competing truth source.
11. Render Manifest executes validated intent; renderers remain replaceable.
12. Render Results are derived evidence, not canonical Scene/Shot truth.
13. Clear changes propagate without manual sync; genuine ambiguity should block only when safe continuation is impossible.

## Permanent rule

> Project -> Sequence -> Scene -> Shot is one connected canonical structure. The Scene owns shared story, world and continuity state; each Shot inherits that state and adds only its cinematic coverage and explicit local overrides. Stable identities, immutable revisions and dependency records make changes traceable, allow targeted regeneration and pricing, and let READY validate one resolved production truth before PRODUCTION.