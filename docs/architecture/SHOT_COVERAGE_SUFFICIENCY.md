# Shot Coverage Sufficiency Contract

**Status:** Adopted product/architecture contract  
**Applies to:** SHAPE, BUILD, READY, Brain, Continuity Engine, frontend and backend implementations  
**Related contracts:** `SHAPE_BUILD_TANDEM_AND_LAYERING.md`, `SCENE_SHOT_DATA_CONTRACT.md`, `AUTOMATIC_SYNCHRONIZATION_RULES.md`

## 1. Purpose

This contract defines how Brain/Producer proposes a variable `1..N` Shot structure from an established SHAPE Scene without relying on arbitrary shot-count targets.

Shot count is never a fixed requirement. A Scene may legitimately require one Shot, five Shots, twelve Shots, twenty-seven Shots or another number according to what is needed to express the Scene clearly and in the Director's intended cinematic language.

The governing rule is:

> Shot count is an output of coverage sufficiency, never an input target. Brain proposes the smallest coherent Shot structure that clearly expresses the established Scene in the Director's intended style, adding Shots only when they satisfy a real narrative, spatial, emotional, continuity, editorial or production purpose.

## 2. Coverage obligations before shot generation

Brain MUST identify the Scene's **Coverage Obligations** before proposing individual Shots.

Coverage Obligations describe what the audience must be able to understand, see, hear, track or feel for the Scene to work as intended. They are not themselves mandatory individual Shots.

One Shot may satisfy several obligations. Several Shots may be required to satisfy one complex obligation.

Coverage Obligations may include:

### Dialogue coverage

Brain considers:

- who is speaking;
- who is listening;
- whether a reaction is materially important;
- whether overlap/interruption matters;
- whether performance intimacy or distance matters;
- whether dialogue timing requires distinct coverage;
- whether the Director intends a master, shot/reverse-shot, long take, profile two-shot, moving dialogue coverage or another style.

Dialogue does not automatically create one Shot per line or one Shot per speaker.

### Action readability

Brain considers whether material actions and cause/effect remain understandable.

Examples include:

- character movement;
- fight/action beats;
- object pickup/handoff/use;
- doors opening/closing;
- vehicle movement;
- transformations;
- injuries;
- explosions or other material events.

A Shot is justified when existing coverage would make an important action ambiguous, unreadable or confusing.

### Spatial orientation

Brain considers whether the audience understands:

- where characters are relative to one another;
- where important objects are;
- entrances/exits and travel direction;
- geography of the environment;
- where an action is occurring;
- whether spatial re-establishment is needed after a major movement or change.

An establishing Shot is not mandatory by formula. It exists only when spatial understanding or the Director's style benefits from it.

### Screen direction, eyelines and continuity

Brain considers:

- screen direction;
- eyelines;
- axis/180-degree relationships where applicable;
- movement direction;
- matched action;
- character/object continuity;
- wardrobe, injury, prop and environment state;
- deliberate discontinuity when established by the Director.

Coverage should cut together coherently unless the Director intends a continuity break.

### Entrances and exits

Brain considers whether an entrance, exit or relocation is important enough to require visible coverage.

A character entering the Scene may be covered inside an existing master or moving Shot. A dedicated Shot is created only when needed for clarity, emphasis, timing, emotion or style.

### Inserts and details

Brain considers whether an insert/detail is necessary because it communicates information that other Shots do not make sufficiently readable.

Examples:

- a text message;
- a key turning;
- a weapon changing hands;
- a timer reaching zero;
- a ring, injury or clue;
- a control being activated.

Decorative detail alone does not require an insert unless it serves a deliberate stylistic/editing purpose.

### Emotional and performance beats

Brain considers:

- emotional reversals;
- important reactions;
- pauses/silence;
- revelations;
- decisions;
- changes in power or relationship;
- moments where audience connection depends on seeing a face, body response or interaction clearly.

A reaction Shot is not mandatory merely because a reaction exists. It is justified when that reaction materially contributes to the Scene or Director's style.

### Scene duration and rhythm

Brain considers:

- intended Scene duration;
- dialogue pace;
- action tempo;
- performance breathing room;
- editorial rhythm;
- musical timing where relevant;
- whether the Director wants long takes, measured classical coverage, rapid cutting or another rhythm.

Shot density should follow Scene needs and style rather than a generic cuts-per-minute target.

### Director style and established project language

Brain must use established Director/project style as a major constraint on coverage.

Examples:

- long-take / minimal-cut style;
- classical coverage;
- handheld realism;
- documentary observation;
- fast action cutting;
- intimate drama;
- music-video rhythm;
- symmetrical/formal composition;
- wide-shot storytelling;
- close-up-heavy performance style;
- deliberately fragmented or disorienting grammar.

Style changes how Coverage Obligations are solved. It does not give Brain authority to rewrite established story truth.

### Production viability

Brain considers whether proposed coverage can be produced without silently changing the Scene.

Relevant factors may include:

- available characters/assets;
- shared 3D/spatial state;
- movement/interaction complexity;
- VFX requirements;
- renderer capability limits;
- camera-control capability;
- identity/reference controls;
- duration limits;
- practical/real footage constraints;
- cost/compute implications when materially relevant.

A renderer limitation should not rewrite canonical Scene truth. Brain/Render Orchestrator should prefer a different Shot construction or production route where appropriate.

## 3. Coverage Obligation record

Implementation should represent each material Coverage Obligation as typed state rather than leaving the reasoning only in natural-language model output.

Conceptually:

```text
coverage_obligation_id
scene_id
scene_revision
obligation_type
source_beat_or_event_refs
subjects_or_assets
importance
required_readability
continuity_constraints
style_constraints
satisfied_by_shot_ids[]
status
rationale
```

Exact schemas may vary, but the following invariants apply:

1. Coverage Obligations are traceable to the Scene material that created them.
2. One Shot may satisfy multiple obligations.
3. One obligation may be satisfied by multiple Shots when required.
4. Removing/revising a Shot re-evaluates only the obligations dependent on it.
5. An obligation may be intentionally satisfied by a single continuous Shot.
6. Director-approved omission or unconventional treatment may mark an obligation as deliberately handled rather than forcing automatic Shot creation.

## 4. Minimum justified coverage

Brain should begin from the smallest Shot structure capable of satisfying the obligations in the intended style.

The process is:

```text
SHAPE Scene
-> identify Coverage Obligations
-> apply Director/project style
-> combine compatible obligations
-> propose minimum justified Shots
-> validate readability/continuity/editorial flow
-> add a Shot only when an obligation remains insufficiently served
```

This does NOT mean the visually simplest or cheapest Shot list always wins. A Shot may be added for emotional, stylistic, editorial or production reasons even when raw narrative information could technically be compressed further.

The test is justification, not minimalism for its own sake.

## 5. Redundancy rule

Brain MUST NOT create additional Shots merely because conventional coverage patterns exist.

The permanent rule is:

> Do not create another Shot when an existing proposed Shot already satisfies the same Coverage Obligation adequately, unless the additional Shot has a deliberate narrative, emotional, spatial, continuity, editorial, stylistic or production purpose.

Examples:

- A two-person master may already cover both speakers, reactions and spatial orientation; separate singles are optional unless they improve the intended Scene.
- A close-up of a gun is unnecessary if the handoff is already unmistakably readable in the existing Shot, unless the Director wants emphasis or an editorial insert.
- Repeating essentially identical angles without purpose is not sufficient justification.

## 6. Style-sensitive examples

The same Scene may correctly produce different Shot counts under different established Director styles.

### Long-take style

A conversation with movement, reactions and a prop handoff may be covered in one carefully blocked moving Shot if all obligations remain readable.

### Classical dialogue coverage

The same Scene may use:

- one master/two-shot;
- one Sarah single;
- one Chris single;
- optional reaction/detail coverage where justified.

### Intimate drama

The same Scene may use more selective close-ups because subtle reaction/emotional beats are central to the intended experience.

### Action sequence

More Shots may be required to preserve action readability, geography, screen direction, impact and cause/effect.

### Documentary/observational style

Coverage may prefer longer observational Shots and avoid conventional shot/reverse-shot grammar.

### Music video

Musical beats, rhythm, performance emphasis and image progression may legitimately justify a higher Shot density than narrative dialogue alone would require.

None of these styles creates a fixed numeric quota.

## 7. Shot rationale

Every AI-proposed Shot SHOULD have an internal, explainable rationale linked to the obligations it satisfies.

Conceptually:

```text
shot_id
coverage_obligation_ids[]
rationale
style_reason
continuity_reason
production_reason
```

Example:

```text
Shot 04 - Sarah close-up
Reason: Covers Sarah's emotional reversal after Chris reveals the truth; the master preserves dialogue but does not make the reaction sufficiently readable for the established intimate-drama style.
```

Example:

```text
Shot 07 - pistol insert
Reason: Establishes the pistol changing ownership before later Shots depend on Chris holding it; existing wide coverage makes the handoff ambiguous.
```

The normal BUILD UI does not need to display all rationale continuously. Brain/Producer should be able to explain why a Shot exists when asked, and advanced views may surface this evidence.

## 8. Coverage sufficiency test

A proposed Shot structure is **coverage-sufficient** when:

1. every material Coverage Obligation is satisfied by at least one viable Shot or deliberately combined into another Shot;
2. material dialogue/action remains readable at the intended level;
3. spatial relationships and screen direction are coherent where the Scene/style requires them;
4. entrances/exits and meaningful object interactions are represented when necessary;
5. important emotional/performance beats are represented according to Director style;
6. continuity-bearing state can be resolved across the proposed Shots;
7. the Shot structure supports the intended Scene duration/rhythm;
8. each additional Shot has a justified purpose rather than arbitrary redundancy;
9. the proposed coverage remains consistent with the Director's established cinematic language;
10. production viability can be achieved through an approved route without changing canonical Scene meaning.

The permanent rule is:

> Coverage is sufficient when every materially required narrative, performance, spatial, continuity and Director-style obligation is represented by at least one viable Shot or deliberately combined into another Shot, with no unexplained gaps and no unnecessary duplicate coverage.

## 9. Determinism across models

Different AI models may propose different creative coverage, but they MUST evaluate the same canonical Coverage Obligations and governing constraints.

Therefore variation is allowed in the artistic solution, but not in the underlying reason for coverage.

A model proposing five Shots and a model proposing fifteen Shots must be able to show which obligations each Shot satisfies and why the additional coverage is justified.

If the fifteen-Shot proposal cannot identify additional legitimate obligations/style/editorial reasons, it is over-coverage and should be reduced.

If the five-Shot proposal leaves material obligations unresolved, it is under-coverage and should be expanded.

This creates explainable variation rather than arbitrary variation.

## 10. Director authority

The Director owns the final Shot list.

Brain/Producer proposes coverage; it does not impose coverage doctrine.

Rules:

1. The Director may keep, remove, merge, split, duplicate, reorder or redesign proposed Shots.
2. The Director may deliberately choose one Shot where Brain would normally propose several.
3. The Director may deliberately add stylistic/reaction/detail coverage beyond the minimum proposal.
4. Brain may explain consequences or unresolved obligations, but it MUST NOT override a deliberate Director decision merely because another coverage pattern is more conventional.
5. A deliberate Director choice should be preserved as project intent and used when evaluating future coverage.

## 11. No-roadblock rule

Coverage sufficiency guides proposal and validation; it is not an approval obstacle course.

BUILD remains fluid.

The Director may continue refining a Scene with incomplete, experimental or unconventional coverage.

Brain should:

- propose missing coverage when useful;
- identify why it matters;
- preserve the Director's existing work;
- avoid auto-creating excessive Shots solely to satisfy internal heuristics;
- avoid blocking ordinary BUILD exploration.

READY is the serious downstream validation point.

A missing coverage item should become a critical READY blocker only when committed PRODUCTION would otherwise be unable to express an established material event or continuity state without inventing a consequential creative decision.

Other coverage concerns remain warnings or creative recommendations.

## 12. Relationship to automatic synchronization

When SHAPE changes, only affected Coverage Obligations and dependent Shots should be re-evaluated.

Examples:

```text
Dialogue line changes
-> re-evaluate dialogue/performance/timing obligations
-> preserve unrelated action/environment coverage
```

```text
Sarah now picks up gun
-> add/update action/object-transition obligation
-> re-evaluate Shots covering that beat and later continuity
-> preserve unrelated earlier coverage
```

```text
Director changes style from classical coverage to continuous long takes
-> re-evaluate obligation grouping/Shot design
-> obligations remain; proposed solution may consolidate into fewer Shots
```

Shot proposal updates therefore follow dependency-aware targeted change rather than regenerating the entire Scene blindly.

## 13. Relationship to Scene -> Shot data contract

Coverage Obligations do not own canonical story truth.

They reference Scene/SHAPE state and help Brain construct Shot coverage.

Shots remain canonical children of the Scene according to `SCENE_SHOT_DATA_CONTRACT.md`.

A Coverage Obligation is planning/evidence state explaining why coverage is needed; it MUST NOT become a competing Scene or Shot source of truth.

## 14. Relationship to preview generation

After a Shot definition exists, Render Orchestration may create a derived preview using the best supported production route.

Preview generation is downstream of the coverage decision:

```text
Scene truth
-> Coverage Obligations
-> proposed Shot definitions
-> Shot refinement
-> derived previews
```

A renderer MUST NOT create arbitrary additional canonical Shots because its generation limits require segmentation. Technical generation segments remain internal execution details.

## 15. READY validation

READY should evaluate whether the chosen Shot structure can represent established Scene truth for committed PRODUCTION.

Potential critical conditions include:

- an established material event has no viable coverage and Production would need to invent how it occurs;
- incompatible screen-direction/spatial state makes required continuity unresolvable;
- a required entrance/exit/object transition is absent in a way that breaks later continuity;
- a necessary production dependency cannot be expressed by any approved Shot/route.

Warnings may include:

- optional reaction coverage absent;
- potentially weak spatial orientation that remains technically producible;
- stylistic inconsistency that does not make the Scene unproducible;
- redundant coverage that increases cost but does not break Production.

READY must not convert taste into an unnecessary production blocker.

## 16. Implementation decision order

For AI-generated coverage proposals, Brain/Producer should evaluate in this order:

```text
1. Resolve established/proposed SHAPE Scene state.
2. Identify material Coverage Obligations.
3. Resolve Director/project style constraints.
4. Identify continuity/spatial/screen-direction constraints.
5. Group compatible obligations into candidate Shots.
6. Prefer the smallest justified coherent Shot set.
7. Add Shots only for unresolved obligations or deliberate style/editorial/production reasons.
8. Validate timing, continuity and production viability.
9. Store rationale linking each proposed Shot to its obligations.
10. Present editable coverage to the Director.
```

No numeric Shot target is used in this decision order.

## 17. Permanent rules

> Shot count is an output of coverage sufficiency, never an input target.

> Brain first determines what the audience must understand, see, track or feel; only then does it determine how many Shots are required to express that in the Director's cinematic language.

> One Shot may satisfy many Coverage Obligations. Do not split obligations into separate Shots unless the Scene, style, edit or production genuinely benefits.

> Every AI-proposed Shot should have an explainable reason for existing.

> Different models may make different artistic choices, but they must evaluate the same canonical obligations and justify any additional or omitted coverage.

> Coverage guidance must improve the Scene without turning BUILD into a roadblock. The Director controls the final Shot list; READY blocks only production-critical gaps.