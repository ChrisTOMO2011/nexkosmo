# Nexkosmo AI Agent Organisation and Cost-Control Contract

**Status:** Adopted organisational baseline  
**Applies to:** Brain orchestration, AI agents, MCP/library access, project workflows, operations, and AI-cost telemetry  
**Authority:** Nexkosmo Canon  

## 1. Purpose

Nexkosmo uses specialist agents with bounded responsibilities rather than one unconstrained AI repeatedly loading the whole project and attempting every task.

This contract creates an explicit counted baseline so Nexkosmo can measure what it is actually facing in orchestration, context use, token/compute exposure, responsibility coverage, and future implementation.

The baseline is:

> **50 bounded specialist agent roles.**

The count is a role count, not a requirement that 50 model sessions run at once. Most work should activate only the smallest set of agents required for the current task.

The Nexkosmo Brain is the canonical coordinator and source-of-truth system and is **not counted as one of the 50 agents**. Deterministic infrastructure services are also not counted as agents. The Human Director remains the highest creative authority.

## 2. Governing model

```text
Human Director
      |
      v
AI Producer / Director Liaison
      |
      v
Nexkosmo Brain
      |
      +--> determine current task and authoritative state
      +--> retrieve exact context / library data / tool capability
      +--> check governed state of required role(s)
      +--> assign only required bounded agent role(s)
      +--> receive structured result + evidence + cost telemetry
      +--> validate / update canonical state when authorised
      |
      v
Next required task only
```

Permanent principle:

> **Brain knows the project. Each agent knows its job. Retrieval supplies the exact information required.**

Agents do not receive the complete project history merely because it exists.

## 3. Role assignment, not permanent model identity

These 50 entries define responsibilities. They do not permanently bind Nexkosmo to a particular AI model, vendor, model instance, or named bot.

Each role may be assigned to an authorised human, authorised AI agent, approved human-plus-AI hybrid, or paused/unassigned state where appropriate.

A role may use deterministic code instead of an LLM when deterministic processing is sufficient. The Brain should prefer the cheapest reliable execution method that preserves quality, authority, safety, provenance, and the Director's intent.

## 4. Canonical counted roster — exactly 50 roles

### A. Direction, orchestration and governance — 8 roles

1. **AI Producer / Director Liaison Agent** — translates Director requests into clear project actions, presents recommendations, and returns decisions to the Brain; never overrides the Director.
2. **Project Intake & Classification Agent** — identifies project type, destination, known constraints, and unresolved intake information without forcing premature decisions.
3. **Context Assembly Agent** — constructs the smallest authoritative task context from canonical state, dependencies, and retrieved evidence.
4. **Task Routing Agent** — selects the minimum required specialist role or role set for the current task and prevents unnecessary agent fan-out.
5. **Canon & Approval Agent** — distinguishes proposed, inferred, established, approved, frozen, and superseded state and protects approval boundaries.
6. **Continuity Agent** — validates identity, world state, temporal state, props, wardrobe, entrances/exits, camera continuity, and deliberate continuity exceptions.
7. **Evidence & Provenance Agent** — tracks sources, versions, generated evidence, renderer/model provenance, decisions, and reconstruction history.
8. **Rights, Consent & Governance Agent** — checks permissions, consent, ownership, licensing, policy and governance constraints before affected work proceeds.

### B. Story, scene and performance intelligence — 6 roles

9. **Story Structure Agent** — evaluates story structure, anchor scenes, gaps, causality and narrative progression without turning suggestions into canon.
10. **Scene Structure Agent** — manages Scene-level narrative facts, events, transitions, shared world state and Scene dependencies.
11. **Script & Dialogue Agent** — works on screenplay text, dialogue, line-level dependencies, revisions and script consistency.
12. **Performance & Emotion Agent** — tracks performance intent, emotion, reactions, behaviour, character motivation and approved acting direction.
13. **Audio Intent Agent** — establishes dialogue, voice, SFX, ambience and music intent and their narrative/timing relationships before final Studio finishing.
14. **Pacing & Duration Agent** — evaluates scene/sequence/film duration, rhythm, timing and pacing implications without imposing formulaic scene counts.

### C. Asset, identity and world specialists — 10 roles

15. **Asset Retrieval Agent** — searches approved project, Creator Vault, Core Library and permitted external sources before new generation is considered.
16. **Asset Creation Agent** — coordinates creation of a genuinely missing asset and preserves identity, provenance, source representation and derivatives.
17. **Character Identity Agent** — protects canonical character identity across 2D, 3D, AI video, animation and downstream representations.
18. **Face / Eye / Mouth Agent** — validates facial structure, eyes, mouth/teeth, expressions, lip-related identity and close-up facial fidelity.
19. **Body & Anatomy Agent** — validates body proportions, anatomy, skeletal/structural consistency and identity-bearing physical characteristics.
20. **Hands & Feet Agent** — validates hand/finger/thumb, foot/toe topology, pose, contact and deformation quality where material.
21. **Hair & Groom Agent** — manages hair, brows, facial hair, fur/groom state, simulation requirements and continuity.
22. **Wardrobe, Accessories & Injury Agent** — manages non-destructive clothing, accessories, damage, dirt, injury states, healing and continuity.
23. **Props, Vehicles & Equipment Agent** — manages reusable props, vehicles, weapons/tools where permitted, production equipment and their state/ownership/dependencies.
24. **Environment & Set Agent** — manages locations, environments, set dressing, weather, time of day, physical layout and reusable world assets.

### D. BUILD / cinematography specialists — 10 roles

25. **Shot Coverage Agent** — determines whether the Director's intended event is sufficiently covered without imposing a fixed Shot count or conventional grammar.
26. **Blocking & Staging Agent** — manages character/object placement, entrances/exits, eyelines, screen relationships, physical interaction and Shot-local staging.
27. **Camera & Sensor Agent** — manages camera profile, sensor/filmback, resolution, frame rate, shutter behaviour, ISO/EI and camera-response facts.
28. **Lens, Optics & Filtration Agent** — manages lens identity, focal behaviour, aperture/T-stop, distortion, breathing, anamorphic traits and physical filters.
29. **Camera Support & Movement Rig Agent** — manages tripod, handheld, Steadicam-type, gimbal, dolly, slider, jib, crane, drone, vehicle, motion-control and other support semantics.
30. **Focus & Zoom Trajectory Agent** — manages focus targets, rack-focus behaviour, zoom/focal trajectories and time-varying optical controls.
31. **Exposure & Camera Colour Agent** — manages exposure relationships, WB/tint, highlight/shadow response, camera colour interpretation and temporal exposure continuity.
32. **Lighting Agent** — manages physical/creative lighting intent, fixtures/sources, intensity relationships, interaction with depth and exposure, and lighting continuity.
33. **Spatial Layering & Depth Agent** — manages foreground/midground/background relationships, occlusion, parallax, atmospheric depth, DOF intent and depth evidence.
34. **Motion & Animation Planning Agent** — defines movement, timing, pose/animation intent, motion dependencies and preview requirements before final execution.

### E. PRODUCTION / CGI / VFX / render specialists — 9 roles

35. **CGI Production Agent** — coordinates approved production-quality CG asset/Shot execution, including modelling/refinement, rig/animation/material/lighting dependencies where required.
36. **VFX & Simulation Agent** — coordinates approved production-quality effects such as particles, fire, smoke, fluids, destruction, debris, volumes and simulations.
37. **Renderer Capability & Route Agent** — matches Shot requirements to verified renderer capabilities and chooses AI, real-time, offline, VFX or hybrid routes without altering creative intent to suit a tool.
38. **AI Image / Video Execution Agent** — executes approved AI image/video generation tasks using bounded manifests, references and identity/continuity controls.
39. **3D & Real-Time Execution Agent** — executes approved Blender/Unreal or equivalent 3D/real-time work where that route is selected.
40. **Offline Render Execution Agent** — executes approved path-traced/offline rendering such as Arnold, V-Ray, Cycles or equivalent production routes.
41. **Layer / Pass / AOV Agent** — preserves useful beauty, alpha, Z, normals, motion, IDs, mattes, light groups and other renderer-native outputs without needless flattening.
42. **Render Validation Agent** — separates technical success from continuity/creative acceptance and records fidelity, quality, failures and evidence.
43. **Cache, Reuse & Partial-Rerender Agent** — identifies reusable assets, frames, simulations, layers and intermediates and computes the smallest valid dependency rerender after a change.

### F. STUDIO / finishing specialists — 5 roles

44. **Editorial Agent** — manages assembly, Shot/Scene ordering, cut timing, trims, transitions and editorial versions from produced material.
45. **Compositing & Finishing VFX Agent** — combines plates, CG, VFX, mattes, depth and passes; performs integration/cleanup/finishing without silently becoming source-production owner.
46. **Colour Agent** — manages colour correction, grading, look consistency, colour-space handling and final visual colour intent.
47. **Dialogue, Sound Design & Music Agent** — manages dialogue editing, cleanup, SFX, ambience, sound design and music placement/editing from the established audio intent and produced assets.
48. **Mix, Master & Delivery Agent** — performs final mix/master preparation, titles/credits integration where applicable, delivery mastering, encoding and output validation.

### G. Economics, infrastructure and evolution — 2 roles

49. **Cost, Quote & Compute Economics Agent** — meters model/API usage, GPU/CPU time, storage, transfer, licences, node payouts, retries and other attributable costs; produces Estimate -> Quote/Reserve -> Execute -> Reconcile evidence.
50. **Market, Growth & Opportunity Intelligence Agent** — evaluates permitted market signals, product gaps, user friction and growth opportunities using evidence rather than raw request-count assumptions.

**Canonical count: 50 specialist roles.**

## 5. Count exclusions

The following are deliberately excluded from the 50-agent count:

- Human Director;
- Nexkosmo Brain itself;
- databases and canonical storage;
- event/outbox infrastructure;
- deterministic validators and cryptographic audit functions;
- raw compute workers/render nodes;
- third-party renderers/models/tools merely being invoked;
- temporary technical subprocesses that do not hold an organisational responsibility.

A renderer such as Blender, Arnold, V-Ray, Unreal, Houdini or an AI model is a tool/capability, not automatically another Nexkosmo organisational agent.

## 6. Fixed-task rule

Each agent has a bounded task contract.

An agent MUST NOT:

- roam freely across unrelated project concerns;
- reload the full project/conversation when a smaller authoritative context is sufficient;
- silently invoke additional agents without orchestration authority;
- create recursive agent-to-agent loops;
- promote proposed information to canon without authority;
- duplicate another role's work merely because the information is available;
- hide its model/API/compute cost from telemetry;
- retain private working context as a competing source of project truth.

When work crosses responsibilities, the Brain coordinates a handoff using structured state and evidence.

## 7. Context-minimisation and MCP/library rule

MCP or another approved bounded interface may expose library, tool and project capabilities to agents. Its purpose is not to dump the whole library into prompts.

The target sequence is:

```text
Task requirement
-> Brain identifies exact information needed
-> targeted retrieval through approved interface
-> minimum authoritative context packet
-> bounded specialist execution
-> structured result/evidence
-> Brain validation and state update
```

Examples:

- Character Identity Agent receives the current canonical identity package and affected Shot state, not the entire film history.
- Asset Retrieval Agent queries only relevant asset classes/metadata before generation.
- Camera Support & Movement Rig Agent receives the Shot's camera/movement requirements and relevant renderer capabilities, not unrelated script pages.
- Cost Agent receives metered execution evidence, not the creative conversation unless a quoted choice depends on it.

Permanent rule:

> **Retrieval should replace context stuffing wherever canonical information can be addressed directly.**

## 8. Agent activation rule

Fifty roles do **not** mean fifty calls per user action.

The Brain should activate:

1. zero LLM agents when deterministic processing is sufficient;
2. one specialist agent when one responsibility can resolve the task;
3. a small dependency set when the task genuinely crosses roles;
4. broader parallel fan-out only when independent work can be justified and its cost is visible.

No agent is activated merely to make the architecture look intelligent.

Before assignment, Brain MUST verify that the required role is in an operational state that permits work.

## 9. Governed per-role state and Director/Admin control

Every one of the 50 specialist roles MUST expose an individually governed operational state through the authorised Nexkosmo administration surface.

The admin experience must make it possible to view and control each role independently rather than providing only one global agent-system switch.

The minimum governed states are:

- **ACTIVE** — the role is available for assignment by Brain and may perform its bounded responsibility subject to normal authority, stage, tool and cost controls.
- **PAUSED** — the role is not available for new assignments. Brain must not route new work to it until an authorised admin returns it to ACTIVE. The implementation must stop, hold or complete already-running work only at a safe governed boundary appropriate to that task.
- **ISOLATED** — the role is quarantined. It must receive no new work and must not initiate agent-to-agent communication, MCP/library access, external model/provider calls, tool execution or other autonomous operations while isolated, except for explicitly authorised diagnostics required to investigate the isolation itself.

The administration panel should present an immediately understandable control model:

```text
Admin -> Agents -> Role

ON   = ACTIVE
OFF  = PAUSED
ISOLATE = governed quarantine
```

Isolation is intentionally stronger than ordinary OFF/PAUSED state.

### 9.1 Authoritative state enforcement

The governed role state is authoritative orchestration state, not a cosmetic UI preference.

Brain MUST check it before assigning work.

If a required role is PAUSED or ISOLATED:

1. Brain must not silently activate it;
2. Brain must not route the same responsibility to an unrelated agent merely to bypass the control;
3. Brain may use an explicitly approved compatible fallback role or authorised human assignment only when governance permits that substitution;
4. otherwise Brain reports that the required responsibility is unavailable and preserves the pending work without inventing completion.

An agent MUST NOT:

- change its own governed state;
- reactivate itself;
- remove its own isolation;
- ask another agent to bypass its state;
- increase its permissions to escape the control;
- continue autonomous work after the authoritative state forbids it.

Only an authorised human/admin control path, or a separately approved governance mechanism acting within explicit human authority, may change these states.

### 9.2 Audit requirement

Every governed state change must preserve an auditable record containing, where applicable:

- role ID and role name;
- previous state;
- new state;
- authorised actor / principal;
- timestamp;
- reason or incident reference where supplied;
- affected project/workspace scope if the control is scoped rather than global;
- outstanding work at the moment of transition;
- restoration/reactivation event when the role returns to ACTIVE.

The state history must not be erased merely because a role is reactivated or reassigned.

### 9.3 Admin visibility

The authorised admin surface should make the following visible for each role where data exists:

- current governed state;
- current assignee type: human, AI, hybrid, or unassigned;
- whether work is currently running;
- most recent invocation/result;
- recent failures/retries;
- current or recent token/API/compute cost;
- last state change and actor;
- dependency warnings caused by PAUSED or ISOLATED state.

This visibility allows the Director/Admin to control not only whether an agent exists, but whether it is currently permitted to act and what cost or operational consequence it is producing.

Permanent rule:

> **Every specialist role is individually controllable. Human governance can pause or isolate it, and no agent can override or self-reverse that decision.**

## 10. Cost telemetry per agent invocation

Every materially billable or measurable agent invocation should be attributable where practical to:

- role ID/name;
- project / Scene / Shot / asset or operational task;
- model/provider/version if applicable;
- input-context size;
- retrieved-context size;
- output size;
- cached-context reuse where measurable;
- wall time;
- token/API charge;
- local GPU/CPU use where applicable;
- tool calls and downstream paid operations;
- retry/failure count;
- successful result classification;
- evidence/provenance reference.

This allows Nexkosmo to distinguish:

```text
useful reasoning cost
from
avoidable context cost
from
execution/render cost
from
retry/failure waste
```

## 11. Cost-control order

Before invoking an expensive external AI agent/model, Brain should evaluate in this order:

```text
Can canonical data answer it directly?
-> Can deterministic/local code perform it?
-> Can an existing/cached result be reused?
-> Can one bounded specialist solve it?
-> Is multi-agent work actually required?
-> Is an external large model justified by quality or capability?
```

The objective is not to eliminate AI. It is to avoid paying AI to repeatedly relearn information Nexkosmo already knows.

## 12. Relationship to the creative flow

The organisational roster does not change the product journey:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION -> STUDIO`

Agents appear only when their bounded responsibility is required by the current task and stage. Capability gating remains governed by the stage-capability contract.

Information may accumulate continuously while capabilities unlock progressively.

The Brain may retain knowledge needed by later stages without exposing later-stage execution controls early.

## 13. Review and change control

The baseline count is now explicit: **50 roles**.

The number is not sacred. If evidence later shows that two roles should merge, one role is too broad, or a missing bounded responsibility deserves a new role, the roster may change through an explicit architectural update.

Until such an update is approved, planning and cost modelling may use **50** as the canonical specialist-role count.

Any future change must preserve:

- bounded responsibility;
- human replaceability;
- Director authority;
- individually governed role state;
- canonical Brain state;
- provenance and auditability;
- context minimisation;
- measurable cost attribution.

## 14. Permanent rules

> **50 specialist roles is the current canonical organisational baseline; it does not mean 50 simultaneous model calls.**

> **Brain owns project truth and orchestration; agents perform bounded jobs.**

> **Every role has an individually governed ACTIVE / PAUSED / ISOLATED state exposed to authorised administration.**

> **A PAUSED or ISOLATED role cannot self-reactivate or be silently bypassed by orchestration.**

> **Retrieve exact information instead of repeatedly loading entire project history.**

> **Use the smallest capable agent set for the task.**

> **Measure context, model, tool, retry and execution cost per material invocation.**

> **The Brain must reduce unnecessary AI work, not merely orchestrate more AI work.**
