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
- AI creation of new scene assets when required;
- CGI/VFX requirements;
- timing needed for production execution;
- visual references and anchor frames;
- production dependencies required by downstream PRODUCTION.

BUILD must follow the scene's established narrative intent rather than silently rewriting the story for implementation convenience.

## Seamless SHAPE scene -> BUILD shot workflow

By the time a scene reaches SHAPE, the scene is established narratively enough for BUILD to work from it directly. BUILD MUST NOT require the Director to recreate, re-enter, re-import or manually reconcile the scene.

The SHAPE scene and the BUILD scene are the same canonical scene identity.

Rules:

1. SHAPE establishes the scene's narrative content: what happens, who is present, what is said, meaningful actions and reactions, entrances/exits, important object interactions, narrative timing/intent and relevant audio intent.
2. Entering BUILD opens that same scene state with its existing characters, assets, environment, approved scene states, dialogue/audio references and continuity information already resolved where available.
3. BUILD adds cinematic coverage and production construction to the existing scene rather than creating a disconnected copy.
4. The normal scene hierarchy is **Scene -> 1..N Shots**. A scene may contain one shot or many shots according to what the scene actually requires.
5. **Fifteen shots is not a fixed architectural requirement.** Shot count is variable and must not be used as a mandatory minimum or maximum.
6. Brain/Producer may propose an initial shot structure from the established script scene, but that proposal remains editable by the Director.
7. The Director may add, remove, duplicate, reorder, replace, merge or refine proposed shots while BUILD remains fluid.
8. Each shot must have its own stable identity and version history even though it references the same parent scene.
9. BUILD should make the transition feel like: **Script scene -> open in BUILD -> proposed cinematic shot structure appears -> Director refines it.**
10. No manual synchronization step is required between SHAPE and BUILD. Brain propagates unambiguous changes between the two views.

The permanent rule is:

> SHAPE figures out the scene. BUILD does not rebuild it; BUILD turns that same scene into the shots required to express it cinematically.

## Shared scene assets, 3D structure and shot views

Shots are views and timed constructions of the scene; they are not independent duplicate worlds.

Rules:

1. Reusable scene assets such as characters, props, vehicles, environments, wardrobe, injuries and other persistent scene elements remain linked to their canonical source assets at scene/project level.
2. Where a reusable 3D representation exists or adds lasting value, the scene preserves that 3D source as shared structural state rather than creating a separate duplicate 3D model for every shot.
3. Individual shots reference the shared scene/3D state and add shot-specific information such as camera position, lens, framing, movement, focus, timing, blocking refinements, visibility and other supported overrides.
4. Approved visual identity references remain available alongside 3D structural data where needed. A 3D model alone does not silently replace approved identity.
5. Shot construction should reuse the same canonical character/object/environment identities unless the Director explicitly creates a new version or state.
6. A shot-specific representation, preview image, video or render is a derived view of the canonical scene and shot state; it does not become a new independent source of truth.

The permanent rule is:

> One canonical scene can support many shots. Reuse the same scene identities and 3D source structure; vary the camera, timing and justified shot-specific state rather than duplicating the world for every shot.

## Shot proposal, preview-frame generation and Director control

BUILD may help the Director create the initial coverage, but the Director remains in control of both shot count and shot design.

Rules:

1. Brain/Producer may analyse the established SHAPE scene and propose the number and type of shots that would cover it effectively.
2. The proposal is contextual, not numeric doctrine. A scene may legitimately use a single continuous shot, a small set of shots, or many shots.
3. Shot count remains editable until the relevant production decision is approved. The Director may reorder shots, remove them, add new ones, duplicate one as a variation or replace one coverage idea with another.
4. A shot may be changed from wide to medium, close-up, over-the-shoulder, insert, moving shot or another supported construction without changing the underlying scene identity.
5. BUILD first establishes the shot definition: the scene moment, subject(s), camera, lens/framing, timing, relevant blocking, lighting intent and required scene state.
6. The Render Orchestrator may then create a **derived shot preview frame** using the best supported route for that shot, including traditional 3D/rendering, real-time engines, AI image/video systems or a hybrid route.
7. Where available, the preview route should use the approved scene state, shared 3D structure, visual identity references and shot camera definition together rather than asking a renderer to invent those facts again.
8. The preview frame is evidence and a working visual representation of the shot. It MUST NOT replace the canonical scene, character, asset or shot definition.
9. A changed shot should regenerate only the affected preview/derived material where practical rather than forcing every other shot in the scene to be rebuilt.
10. READY, not the initial AI proposal, is where the chosen shot structure is validated for committed full PRODUCTION.

The permanent rule is:

> AI may propose the coverage and Render Orchestration may create the preview, but the Director controls the shot list and every shot remains editable until approved for Production.

## Scene-level inheritance and shot-level overrides

BUILD must distinguish a scene-wide decision from a change that belongs only to one shot.

Rules:

1. **Scene-level state** is inherited by every relevant shot unless a valid shot-specific override exists.
2. Examples of scene-level state may include character identity, base wardrobe for that scene, a scene-wide injury state, environment, persistent props, time/weather state and other continuity-bearing facts.
3. If the Director changes a scene-level fact, all dependent shots must update or be marked for revalidation as appropriate.
4. **Shot-level state** applies only to the specified shot when the Director's intention is local to that shot.
5. Examples may include camera/lens/framing, a temporary composition adjustment, object placement required only for a specific angle, visibility, foreground staging or other shot-specific construction.
6. A shot-level override MUST NOT silently mutate the shared scene-wide source state.
7. The Director may explicitly promote a useful shot-level change to scene-level state when they intend that change to persist across the scene.
8. Brain/Continuity must track inheritance, overrides and dependencies so later edits do not create hidden contradictions.

The permanent rule is:

> Scene decisions flow down to the shots. Shot-specific decisions stay local unless the Director promotes them to the scene.

## BUILD target-aware drag and drop

The global BUILD page is the detailed scene-construction surface. It SHOULD use target-aware drag and drop as a primary interaction for adding, removing and modifying scene contents.

Rules:

1. The Director may select or highlight a character, object, vehicle, prop, set element or open scene space as a target.
2. **Drag into open scene space = place the asset in the scene.**
3. **Drag onto a character or object = apply, attach or place the dragged asset on that target when the relationship is valid.**
4. Character-targeted examples include glasses, hats, jewellery, clothing, weapons, backpacks, pimples, makeup, scars, Injury Assets, bruises, dirt, blood, damage and other approved additions or states.
5. Object-targeted examples include placing an item on a table or box, attaching an element to a vehicle, adding a decal or damage state, or placing one reusable object on another.
6. The Director may remove, replace, reposition, resize or otherwise adjust an applied or attached addition without destroying the clean underlying character or object.
7. Accessories, injuries, damage and other temporary additions remain separate linked assets, modifiers or states wherever independent editing, reuse or continuity tracking is useful.
8. Injury remains a distinct asset class. An Injury Asset defines the injury concept; an Injury State records how that injury currently exists on a specific character, including body location, severity, healing stage and other relevant continuity state.
9. Core identity-bearing changes such as replacing the defining face, fundamental body proportions or species are identity revisions, not ordinary drag-and-drop appearance edits.
10. BUILD must preserve the layered scene package beneath the composed view so a target-aware drop does not destructively bake the addition into the canonical base asset.
11. When a BUILD edit materially changes what happens in the story, the affected SHAPE state must synchronize. Purely presentational or cosmetic additions do not automatically rewrite the script.

The permanent rule is:

> In BUILD, drag into scene space to place an asset; drag onto a valid target to apply or attach it. Keep the clean base asset underneath and preserve the addition as a separate non-destructive layer or state.

## BUILD in-place asset creation

The Director must be able to create a required asset with AI directly from the global BUILD page without leaving the current scene-construction workflow.

Rules:

1. Asset creation may begin from open scene space, the currently selected target, a search/create control, Director text or voice instruction, or another clear BUILD interaction.
2. The Director may create characters, creatures, props, vehicles, accessories, wardrobe, set pieces, Injury Assets, effects and other supported production assets needed by the scene.
3. When the Director creates an asset for a selected target, BUILD should preserve the target context so the new asset can be immediately applied or attached where appropriate. Example: selecting a character and requesting black sunglasses creates the sunglasses as an asset and makes them immediately available to apply to that character.
4. When the Director creates an asset for open scene space, the new asset may be placed directly into the current scene after creation while remaining a reusable project asset.
5. Nexkosmo should retrieve a suitable approved existing asset before generating a new one unless the Director explicitly requests a new or different asset.
6. AI-created assets must receive identity, provenance, generation/source information, version history and dependency links appropriate to their asset class.
7. If the asset benefits from reusable 3D structure, Nexkosmo should preserve or create the richer 3D source and may provide a lightweight 2D isolated representation for fast scene interaction. The 2D representation must not replace the richer source.
8. Assets intended for independent scene manipulation must remain isolated through alpha/transparency, masks, geometry or another appropriate representation rather than being destructively baked into the scene.
9. A newly created asset must be available for later reuse in the same project and, where permissions/ownership allow, the appropriate Creator Vault or library context.
10. Creating an asset in BUILD does not automatically make it part of the story. Only if its placement or use materially changes what happens in the movie should the affected SHAPE state synchronize.
11. Asset creation should not force the Director through a separate creation page merely to complete a BUILD task.

The permanent rule is:

> In BUILD, the Director can create a missing asset in place, preserve it as a reusable canonical project asset, and immediately place, apply or attach it while keeping the scene layered and non-destructive.

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

Build This Moment remains an advanced DISCOVER interaction used to compose and explore a scene moment visually before the global BUILD stage. It may add, remove, reposition, resize, replace and reorder whole isolated scene assets and may create additional ordered scene-moment frames.

**Build This Moment does not provide the global BUILD page's deep target-aware attachment/editing function.** It does not need to support dropping glasses onto a face, placing a bruise on a body location, attaching a weapon to a hand, or placing an object onto another object as its detailed editing model.

Its layered assets and approved scene states should flow forward into SHAPE and BUILD rather than being recreated from scratch. Once the project reaches global BUILD, the Director can use the richer target-aware drag-and-drop and in-place AI asset-creation tools against those same characters, objects and layers.

DISCOVER establishes and explores scene moments. Build This Moment composes those moments. SHAPE establishes what happens and what is heard. BUILD performs detailed cinematic construction, target-aware scene modification and in-place creation of missing production assets.

The permanent rule is:

> Build This Moment composes the Discover moment with whole scene assets. Global BUILD performs the deeper target-aware modifications and can create missing production assets directly inside the scene-construction workflow.

## READY validation

READY validates the SHAPE <-> BUILD relationship before committed full PRODUCTION. It should detect critical inconsistencies such as:

- script action that has no viable production construction where one is required;
- BUILD action that materially contradicts the established script;
- missing or conflicting character state;
- incompatible wardrobe, injury, prop or environment continuity;
- timing contradictions that would force PRODUCTION to invent a creative decision;
- missing critical audio or production dependency when required for the intended production route;
- unresolved conflicts between scene-level inherited state and shot-level overrides;
- a proposed shot structure that cannot represent the established scene without inventing a material creative decision.

Non-critical incompleteness may remain a warning rather than an artificial blocker.

## Downstream continuity

PRODUCTION consumes the same canonical layered scene package and approved shot definitions rather than disconnected copies. The Render Orchestrator may translate supported subsets into renderer-specific instructions while preserving the richer Nexkosmo scene state.

STUDIO receives production results plus useful retained layers, source assets, audio elements, passes, masks, metadata and dependencies so targeted changes can be made without destroying the canonical source structure.

## Permanent summary

> SHAPE defines what happens and what is heard. BUILD takes that same established scene, proposes and refines a variable 1..N shot structure, reuses the scene's canonical identities and shared 3D/source assets, supports deep target-aware scene modification, and can create missing production assets in place. Scene-level decisions flow to dependent shots; shot-specific decisions remain local unless promoted. Build This Moment remains a Discover composition tool. SHAPE and BUILD operate on one canonical layered scene, synchronize meaningful changes in both directions, preserve independently editable layers underneath, and flatten only for derived output.