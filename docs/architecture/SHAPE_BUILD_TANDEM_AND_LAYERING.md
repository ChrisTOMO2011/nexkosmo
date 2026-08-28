# SHAPE <-> BUILD Tandem and Layered Scene Contract

**Status:** Adopted product/architecture rule

This document defines how SHAPE and BUILD work together in Nexkosmo. They are separate Director-facing views over the same canonical scene state. They MUST NOT become competing sources of truth.

## Core relationship

SHAPE answers primarily:

> What happens, what is said, what is heard, and what does it mean in the story?

BUILD answers primarily:

> How is that same scene constructed cinematically and spatially for production?

SHAPE and BUILD therefore operate in tandem. A Director may move between them without manually reconciling duplicated scene information.

The permanent rule is:

> SHAPE and BUILD are two working views of the same canonical scene. The Director edits once; Brain propagates the meaningful consequence to the other view when the intended result is unambiguous.

## SHAPE responsibilities

SHAPE primarily manages narrative and performance intent, including:

- scene action;
- dialogue;
- reactions;
- entrances and exits;
- transformations and meaningful state changes;
- narrative order and timing intent;
- emotional/performance intent;
- character voice and dialogue assets;
- sound-effect requirements;
- ambience requirements;
- music/score intent and linked audio cues.

SHAPE is not required to define final camera, lens, framing, lighting, shot breakdown, or other cinematic construction unless the Director explicitly establishes those details there.

## BUILD responsibilities

BUILD primarily translates the established scene into cinematic and production construction, including:

- shot structure;
- storyboard or visual shot representation;
- character placement;
- blocking and movement;
- camera position and movement;
- lens and framing;
- focus;
- lighting;
- environment use;
- props and vehicles;
- accessories, injuries, damage and scene-specific states;
- CGI/VFX requirements;
- timing needed for production execution;
- visual references and anchor frames;
- production dependencies required by downstream PRODUCTION.

BUILD must follow the scene's established narrative intent rather than silently rewriting the story for implementation convenience.

## Bidirectional synchronization

A meaningful narrative or action change made in SHAPE must update the affected BUILD state when the consequence is unambiguous.

Examples:

- changing who enters the room updates affected blocking and shot dependencies;
- removing an explosion removes the corresponding BUILD event/VFX dependency;
- changing a character action updates the affected blocking or movement requirement;
- changing dialogue timing updates affected timing dependencies without rebuilding unrelated scene elements.

A meaningful story/action change made in BUILD must update the affected SHAPE state when it materially changes what happens in the movie.

Examples:

- adding a character entrance that materially occurs in the scene updates the script action;
- changing the order of a physical event updates the narrative action order;
- adding a meaningful object interaction updates the corresponding scene action.

Purely cinematic or presentational changes should not rewrite SHAPE unnecessarily.

Examples that normally remain BUILD-only unless they change story meaning:

- lens choice;
- framing;
- camera height;
- camera movement;
- lighting treatment;
- colour/look intention;
- focus choice;
- minor composition adjustments.

The permanent rule is:

> If it materially happens in the movie, it belongs in the shared scene truth and must remain synchronized. If it only changes how the established event is photographed or presented, it does not automatically rewrite the script.

## Layered scene package

The canonical scene must remain layered beneath SHAPE and BUILD. A visible preview may appear as one composed scene, but the underlying production state must preserve useful separability.

A scene package may contain the following logical layers or linked layer groups:

1. **Narrative layer** — scene action, dialogue, reactions, narrative timing and meaning.
2. **Character layers** — each character identity plus current scene/appearance/performance state.
3. **Environment/base layer** — location, environment and background state.
4. **Object layers** — props, vehicles, movable set pieces and other independently controlled objects.
5. **Attachment/state layers** — accessories, wardrobe, Injury Assets/States, damage, dirt, blood, decals and other non-destructive additions.
6. **Camera layer** — shot, camera position, lens, framing, focus and movement.
7. **Lighting layer** — lights, lighting intent, practicals and scene lighting state.
8. **CGI/VFX layers** — effects, simulations, generated elements and other separately controllable visual effects.
9. **Dialogue audio layers** — voice identity references and line/beat-level dialogue performances.
10. **SFX layers** — sound effects linked to actions, props, events and timing.
11. **Ambience layers** — room tone, environmental beds and location ambience.
12. **Music/score layers** — scene cues, themes, emotional beds and transitions.

Not every scene requires every layer. Nexkosmo should preserve the layers that are materially useful for editing, continuity, targeted regeneration, rerendering, reuse, validation or finishing.

## Layer rules

1. Layers are logical production state, not merely UI tracks. The interface may simplify how many are visible at once without flattening the underlying structure.
2. Independently editable elements must preserve identity, provenance, version history and dependency links.
3. A clean base character or reusable object remains preserved beneath temporary additions and scene-specific states.
4. Audio elements remain separate from one another and from picture until a derived mix/export is intentionally created.
5. Visual effects, object states and attachments must not be baked destructively into the canonical base merely because a preview displays them together.
6. A change to one layer should invalidate or regenerate only the dependent material where practical rather than forcing the whole scene to be recreated.
7. Brain and Continuity must track cross-layer consequences, including character state, wardrobe, injuries, props, entrances/exits, timing, eyelines, environment, camera and audio dependencies.
8. A flattened image, video, audio mix or other preview is a derivative representation. It MUST NOT replace the persistent layered scene package.

The permanent rule is:

> Keep the scene layered underneath. Flatten only for previews, exports or final derived outputs when the editable canonical structure remains preserved.

## SHAPE and BUILD page behaviour

SHAPE and BUILD may present different tools because the Director is solving different problems on each page, but both pages must resolve the same scene identities, characters, assets, states, timing references and approved decisions.

The Director should be able to move from SHAPE to BUILD and back without performing a manual sync step.

When an edit has an obvious consequence, Brain propagates it automatically. When an edit is genuinely ambiguous or would require inventing a material creative decision, the ambiguity remains explicit for the Director rather than being silently guessed.

## Relationship to DISCOVER and Build This Moment

Build This Moment remains an advanced DISCOVER interaction used to develop a scene visually before the global BUILD stage. Its layered assets and approved scene states should flow forward into SHAPE and BUILD rather than being recreated from scratch.

DISCOVER establishes and explores scene moments. SHAPE establishes what happens and what is heard. BUILD turns that same established scene into cinematic construction.

## READY validation

READY validates the SHAPE <-> BUILD relationship before committed full PRODUCTION. It should detect critical inconsistencies such as:

- script action that has no viable production construction where one is required;
- BUILD action that materially contradicts the established script;
- missing or conflicting character state;
- incompatible wardrobe, injury, prop or environment continuity;
- timing contradictions that would force PRODUCTION to invent a creative decision;
- missing critical audio or production dependency when required for the intended production route.

Non-critical incompleteness may remain a warning rather than an artificial blocker.

## Downstream continuity

PRODUCTION consumes the same canonical layered scene package rather than a disconnected copy. The Render Orchestrator may translate supported subsets into renderer-specific instructions while preserving the richer Nexkosmo scene state.

STUDIO receives production results plus useful retained layers, source assets, audio elements, passes, masks, metadata and dependencies so targeted changes can be made without destroying the canonical source structure.

## Permanent summary

> SHAPE defines what happens and what is heard. BUILD defines how that same scene is constructed cinematically. Both operate on one canonical layered scene, synchronize meaningful changes in both directions, preserve independently editable layers underneath, and flatten only for derived output.