# Automatic Synchronization Rule Table

**Status:** Adopted product/architecture contract  
**Applies to:** DISCOVER, SHAPE, BUILD, READY, Brain, Continuity Engine, frontend and backend implementations  
**Related contracts:** `SCENE_SHOT_DATA_CONTRACT.md`, `SHAPE_BUILD_TANDEM_AND_LAYERING.md`

## 1. Purpose

This contract makes SHAPE <-> BUILD synchronization deterministic.

The governing principle is:

> Classify the meaning and scope of the change, not the page where the Director made it.

A narrative change made in BUILD may therefore update SHAPE. A purely cinematic change made in BUILD normally remains local to the Shot. The same classification rules apply regardless of whether the Director used text, voice, drag-and-drop, direct manipulation, script editing or another supported interaction.

This document refines the existing Scene -> Shot and SHAPE <-> BUILD contracts. It does not create a second source of truth.

## 2. Core synchronization primitives

Every material edit is resolved into one of the following primary propagation classes.

### A. Scene Fact

A fact that is true across the relevant Scene span and should normally be inherited by every affected Shot.

Examples:

- Sarah wears glasses throughout the Scene;
- the Scene takes place in the warehouse;
- the pistol exists on the table at the start of the Scene;
- Sarah is wearing the red jacket;
- the Scene is taking place at night.

Propagation:

```text
Scene revision
-> dependent Shot resolved state
-> affected previews/snapshots/manifests as required
```

SHAPE changes only when the fact materially belongs in screenplay/story meaning.

### B. Scene Transition

A fact changes at a specific narrative/time/beat boundary inside the Scene.

Examples:

- Sarah picks up the pistol;
- Sarah removes her glasses after a line;
- Chris enters the room;
- the rain begins;
- the lights go out;
- Sarah receives an injury;
- the car catches fire.

Propagation:

```text
SHAPE narrative/action when materially relevant
+ Scene transition
+ dependent Shots at/after the transition
+ dependent audio/VFX/performance/preview/render state
```

Shots before the transition preserve the earlier Scene state. Shots after the transition inherit the new state unless an explicit valid override applies.

### C. Shot Override

A local choice about how one Shot presents the established Scene.

Examples:

- change lens from 35mm to 50mm;
- move Sarah left in frame;
- move the cup closer to camera for one angle;
- hide the pistol because it is outside the frame;
- change focus;
- add a local foreground object;
- make Shot 4 slightly darker for presentation without changing world-state lighting.

Propagation:

```text
Shot revision only
-> dependent preview/snapshot/manifest/render for that Shot
```

The Scene and SHAPE remain unchanged unless the edit also introduces a material story event.

## 3. Deterministic rule table

| Change class | Example | Canonical scope | SHAPE synchronization | BUILD/Shot synchronization | Default consequence |
| --- | --- | --- | --- | --- | --- |
| Narrative event | Sarah picks up the gun | Scene Transition | Update action/event | Update gun state, Sarah hand/blocking and affected Shots | Shots after event inherit new state |
| Dialogue text | `Run!` -> `Get out!` | Scene/Dialogue Beat | Update line | Update affected Shot timing/performance dependencies | Regenerate only dependent audio/lip-sync/render where needed |
| Character entrance | Chris enters room | Scene Transition | Update action | Update participants, blocking and affected Shots | Later Shots inherit Chris present |
| Character exit | Sarah leaves room | Scene Transition | Update action | Update participants/visibility/blocking | Later Shots inherit Sarah absent |
| Meaningful prop interaction | Sarah gives gun to Chris | Scene Transition | Update action | Update prop ownership/location/hand state | Later Shots inherit Chris holding gun |
| Scene-wide wardrobe | Sarah wears red jacket | Scene Fact | Update only if narratively relevant | All relevant Shots inherit wardrobe | No per-Shot duplication |
| Scene-wide appearance | Sarah wears glasses throughout Scene | Scene Fact | Update only if narratively relevant | All relevant Shots inherit glasses state | Scene-level state |
| Timed appearance change | Sarah removes glasses after dialogue | Scene Transition | Update if meaningful action | Shots after transition inherit no glasses | Transition rather than unrelated Shot copies |
| Injury event | Sarah cuts cheek | Scene Transition | Update action | Create/update Injury State and later Shot dependencies | Later Shots inherit injury |
| Persistent damage | Car remains damaged | Scene Fact after transition | Update if story relevant | Affected later Shots inherit damage | Shared continuity state |
| Environment identity | Warehouse -> hospital | Scene Fact / Scene revision | Update scene heading/context | All relevant Shots inherit environment | Scene-level change |
| Weather begins | Rain starts halfway through Scene | Scene Transition | Update if materially depicted | Later Shots, ambience/VFX/lighting dependencies update | Time-bounded transition |
| World-state lighting | Power goes out | Scene Transition | Update action if story event | Later Shots inherit dark/power-out state | Not a mere grading change |
| Camera lens | 35mm -> 50mm | Shot Override | None | Current Shot only | New Shot revision |
| Framing | Wide -> close-up | Shot Override | None | Current Shot only | Scene unchanged |
| Camera movement | Static -> dolly in | Shot Override | None unless story meaning changes | Current Shot only | Cinematic presentation |
| Camera height/position | Lower camera | Shot Override | None | Current Shot only | Scene unchanged |
| Focus | Rack focus to Sarah | Shot Override | None unless it creates a new material event | Current Shot only | Cinematic presentation |
| Character composition | Move Sarah left in frame | Shot Override | None | Current Shot only | Does not change Scene blocking unless explicitly intended |
| Shot-local staging | Move cup closer to camera | Shot Override | None | Current Shot only | Local staging by default |
| Scene-wide object placement | Put cup on table for the Scene | Scene Fact | Update only if meaningful | All relevant Shots inherit placement | Scene state |
| Scene object removal | Remove gun from whole Scene | Scene Fact/Transition depending timing | Update if narrative changes | All dependent Shots update | Scope follows timing/meaning |
| Shot visibility | Gun not visible in Shot 5 | Shot Override | None | Shot 5 visibility only | Gun still exists in Scene |
| Shot-local lighting | Make Shot 4 moodier | Shot Override | None | Shot 4 only | World lighting unchanged |
| Scene lighting state | Room lights switch off | Scene Transition | Update if action/story event | Later Shots inherit new lighting state | Scene transition |
| Cosmetic VFX | Add lens flare | Shot Override | None | Current Shot only | Presentation only |
| Narrative VFX | Building explodes | Scene Transition | Update action/event | VFX + affected Scene/Shot state | Story event propagates |
| New reaction shot | Add close-up of existing reaction | Shot structure | None if no new story fact | Add Shot covering existing beat | BUILD-only coverage |
| New story action in Shot | Sarah discovers bomb | Scene event | Add/update SHAPE action | Scene state + dependent Shots | Cannot remain merely Shot-local if it happens in movie |
| Shot reorder | Swap two coverage Shots | Shot structure | None if narrative order unchanged | Reorder display/coverage | Stable Shot identities retained |
| Narrative reorder | Physical event now happens earlier | Scene narrative order | Update SHAPE | Re-resolve affected Shot coverage/transitions | Story change, not merely shot reorder |
| Background dressing | Add crate behind Sarah for this angle | Shot Override by default | None | Current Shot only | May be promoted to Scene if intended persistent |
| Persistent set dressing | Crate exists throughout Scene | Scene Fact | None unless story relevant | Relevant Shots inherit it | Shared world state |
| Audio performance style | Make this line angrier | Dialogue/performance beat | Update performance intent if established there | Affected dialogue/performance Shot dependencies | Other lines/shots unchanged |
| Ambience state | Siren begins after explosion | Scene Transition/audio dependency | Update cue/intent | Later Shot/audio dependencies | Targeted synchronization |
| Music score treatment | Change score cue | Scene/sequence audio cue | SHAPE audio intent updates | Picture Shot state unchanged unless timing dependency changes | Audio dependency only |

## 4. Meaning outranks interface location

The same Director action can produce different scope depending on its meaning.

Example:

```text
BUILD Shot 6: "Move the lamp closer to camera."
-> Shot Override
```

But:

```text
BUILD Shot 6: "The lamp is now beside the door for the rest of the scene."
-> Scene Fact / Scene Transition depending when it changes
```

Likewise, dragging a character or prop in BUILD does not automatically mean the change is Shot-only or Scene-wide. Brain classifies the Director's intended meaning using explicit wording, current selection, timing context and established Scene state.

## 5. Visibility is not existence

The following distinctions are mandatory:

```text
not visible in Shot != removed from Scene
framing change       != Scene location change
camera lighting      != world-state lighting change
composition          != narrative blocking/event
foreground placement != persistent Scene placement
```

A Shot may hide, crop, occlude or locally stage an existing Scene asset without mutating its Scene existence/state.

## 6. Scene blocking versus shot composition

Character/object position must distinguish physical Scene state from camera-relative composition.

Examples:

- `Sarah walks from the door to the table` -> Scene Transition / blocking event; synchronize with SHAPE and affected Shots.
- `Frame Sarah more to the left` -> Shot Override; no Scene movement occurs.
- `Move Sarah two metres toward the window for this action` -> Scene blocking change if she physically moves in the story.
- `Move Sarah closer to the lens for this one setup without changing established story blocking` -> Shot-local staging/override when technically valid.

Brain must not convert a framing instruction into a narrative movement or vice versa.

## 7. Event-time propagation

Scene Transitions carry a narrative/time/beat boundary.

Conceptually:

```text
Before transition T:
  inherited_state = State A

At/after transition T:
  inherited_state = State B
```

Example:

```text
Beat 12: Sarah picks up gun

Shots covering beats 1-11:
  gun = table

Shots covering beat 12 onward:
  gun = Sarah/right hand
```

A Shot that spans the transition may contain both states through timed blocking/action rather than being forced into one static value.

## 8. Dependency-aware synchronization

Propagation MUST target dependencies, not broadcast blindly to the whole project.

Example:

```text
Sarah picks up gun
-> SHAPE action
-> Scene transition
-> gun ownership/location
-> Sarah hand/pose/blocking
-> Shots covering/after event
-> affected previews/snapshots/manifests/renders
```

Shots before the pickup remain valid unless another dependency requires change.

Example dialogue change:

```text
Dialogue Beat D17 changed
-> script line
-> voice performance D17
-> affected timing
-> face/lip-sync dependency
-> dependent Shot preview/render/composite
```

Unrelated environment, assets, Shots and audio remain reusable.

## 9. Synchronization direction

Synchronization is bidirectional.

### SHAPE -> BUILD

When SHAPE changes a material event, dialogue beat, entrance/exit, meaningful object interaction, state transition or timing dependency, Brain updates the shared Scene truth and re-resolves only affected BUILD Shots/dependencies.

### BUILD -> SHAPE

When BUILD introduces or changes something that materially happens in the movie, Brain updates the shared Scene truth and therefore SHAPE.

Examples:

- new character entrance;
- gun pickup;
- explosion;
- physical event reorder;
- meaningful discovery;
- injury occurrence.

Purely cinematic/presentational BUILD changes remain BUILD-only.

## 10. Shot creation and screenplay synchronization

Adding a Shot does not automatically add screenplay material.

Rules:

1. A new Shot covering an existing Scene beat is BUILD-only coverage.
2. A new Shot that introduces a new material event must create/update shared Scene narrative state and SHAPE.
3. A reaction close-up showing an already-established reaction does not create a duplicate event.
4. A cutaway/insert that establishes a new story fact must synchronize that fact to Scene/SHAPE.
5. Shot reorder changes only coverage order unless it also changes narrative chronology or cause/effect.

## 11. Asset creation versus story adoption

Creating or placing an asset does not automatically make it a story event.

Examples:

- creating sunglasses in BUILD -> asset exists in project;
- attaching sunglasses to Sarah for one Shot -> Shot Override if intentionally local;
- Sarah wears sunglasses for the Scene -> Scene Fact;
- Sarah puts sunglasses on during the Scene -> Scene Transition + SHAPE if materially depicted.

The same principle applies to props, injuries, damage, wardrobe, vehicles and VFX elements.

## 12. Default-local no-roadblock rule

When scope is genuinely ambiguous but work can continue safely, Nexkosmo should choose the narrowest non-destructive interpretation rather than interrupting the Director.

Default:

```text
ambiguous while editing one Shot
-> preserve as Shot Override
-> allow later promotion to Scene scope
```

This is a workflow default, not permission to ignore obvious Scene intent.

Brain should ask the Director only when:

1. both plausible interpretations would create materially different story/continuity truth; and
2. choosing the local interpretation would not safely preserve the unresolved meaning; and
3. the requested next operation genuinely requires resolution.

Otherwise the Director continues working.

## 13. Promotion and demotion

The Director may change scope without recreating the edit.

### Promote

```text
Shot Override
-> Scene Fact or Scene Transition
-> propagate to dependent Shots
```

Example: a crate positioned for Shot 4 is later established as part of the Scene set dressing.

### Demote/localize

A Scene-level choice may be replaced by a valid Shot-specific override when the Director intends a local presentation difference and continuity permits it.

Promotion/demotion preserves identity, provenance, version history and dependency relationships.

## 14. Conflicts

When an incoming change conflicts with existing continuity, Brain/Continuity classifies the conflict rather than silently resolving it.

Possible outcomes:

- valid Scene revision;
- valid Scene Transition;
- valid Shot Override;
- intentional continuity break;
- stale dependency requiring regeneration;
- unresolved consequential ambiguity.

Only the last category should require a Director clarification before continuing, and only when safe local/provisional continuation is not possible.

## 15. Revision behavior

Synchronization creates revisions at the narrowest correct scope.

```text
Scene Fact/Transition changed
-> new Scene revision
-> affected Shots re-resolve

Shot Override changed
-> new Shot revision
-> Scene unchanged
```

Historical revisions and already-produced evidence remain traceable.

## 16. READY relationship

READY validates synchronization before committed full PRODUCTION.

Critical issues include:

- contradictory Scene transitions;
- a Shot override that cannot coexist with established Scene state;
- screenplay action with no resolvable production state when one is required;
- BUILD action that materially occurs but is absent/contradictory in shared narrative truth;
- unresolved dependency state that would force PRODUCTION to invent a consequential creative decision.

Non-critical or safely provisional conditions remain warnings rather than earlier-stage roadblocks.

## 17. Implementation decision order

For every material edit, Brain/Continuity should evaluate in this order:

```text
1. Does this materially happen/exist in the movie?
   YES -> continue to 2
   NO  -> Shot/presentation scope unless another shared state applies

2. Is it true across the relevant Scene span?
   YES -> Scene Fact
   NO  -> continue to 3

3. Does it become/change at a narrative/time/beat boundary?
   YES -> Scene Transition
   NO  -> continue to 4

4. Is it only how one Shot photographs/presents established truth?
   YES -> Shot Override
   NO  -> use dependency/type-specific rule

5. Is the scope still ambiguous?
   If safe -> narrowest/local representation and continue
   If consequential and unsafe to defer -> ask Director
```

After classification:

```text
-> create narrowest correct revision
-> update canonical dependency records
-> propagate only to affected consumers
-> preserve unaffected state/caches
-> mark stale derived material precisely
-> keep SHAPE/BUILD synchronized without manual reconciliation
```

## 18. Permanent rules

> If it materially happens in the movie, it belongs in shared Scene truth. If it only changes how established truth is photographed or presented, it belongs to the Shot.

> Scene Facts flow to relevant Shots. Scene Transitions flow from their event boundary forward. Shot Overrides stay local unless promoted.

> Visibility is not existence, framing is not physical location, and cinematic treatment is not automatically a story event.

> Synchronize dependencies, not everything. Preserve unaffected Shots, assets, renders and costs whenever valid.

> When intent is obvious, synchronize automatically. When ambiguity is safe to defer, keep it local and continue. Ask only when a consequential decision cannot safely remain unresolved.