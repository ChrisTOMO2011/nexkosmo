# Architecture Amendment 001: Continuity and Render Orchestration

**Status:** Adopted  
**Applies to:** Nexkosmo production systems with visual rendering, using format-specific production profiles  
**Authority:** Nexkosmo Canon  

## 1. Purpose

This amendment separates continuity management from rendering execution.

The Nexkosmo Brain remains the permanent operating system and canonical source of truth. Rendering is treated as a replaceable execution capability. AI models, real-time engines, offline renderers, VFX systems, animation systems, compositors, and future production technologies may be exchanged without changing the canonical project state.

The system must not depend on any renderer to remember a production. The Brain owns truth; renderers consume validated instructions.

## 2. Governing Principle

> The Brain owns truth. The Continuity Engine protects truth. The Render Orchestrator determines how truth is produced visually. Renderers remain replaceable.

## 3. Architectural Separation

```text
Director / Creator
        |
        v
Nexkosmo Brain
        |
        +----------------------+----------------------+
        |                                             |
        v                                             v
Continuity Engine                            Render Orchestrator
        |                                             |
        +----------------------+----------------------+
                               |
                               v
                       Rendering Pipeline
                 +-------------+-------------+
                 |             |             |
                 v             v             v
            AI Renderers   3D / Real-Time   VFX / Simulation
                 |             |             |
                 +-------------+-------------+
                               |
                               v
                         Compositing
                               |
                               v
                         Final Output
```

The Continuity Engine and Render Orchestrator are distinct architectural domains. They may cooperate through stable contracts, but neither may assume the responsibilities of the other.

## 4. Format-General Production Hierarchy

The permanent architecture does **not** require every Nexkosmo project to use Sequence, Scene, and Shot.

The shared journey is:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

Inside `PRODUCTION`, each creation format supplies an approved production profile whose units fit that medium.

Examples:

```text
Film profile:
Project -> Sequence -> Scene -> Shot -> Execution Task -> Result

Game profile:
Project -> Level / Encounter / Cinematic / System -> Execution Task -> Result

Music-video profile:
Project -> Section / Clip / Shot -> Execution Task -> Result

Asset-production profile:
Project -> Asset / Variant / Pass -> Execution Task -> Result
```

`Studio` is a contextual precision editor entered from the relevant production unit and returns work to `PRODUCTION`; it is not a seventh top-level stage.

A scene may be any appropriate dramatic duration. A three-minute film scene is not treated as one generation request. It is represented as a collection of shots, and each shot may be divided internally into technical generation segments only when required.

Internal execution segments are implementation details. They do not replace the creator-facing production structure of the selected format.

## 5. Brain Responsibilities

The Brain remains authoritative for:

- project identity and ownership;
- format and production-profile identity;
- format-appropriate structural units and relationships;
- character identity and state;
- environment and world state;
- asset identity and version history;
- timeline or interaction state where applicable;
- approved creative intent;
- canonical continuity records;
- renderer-independent production instructions;
- validation evidence and provenance.

No renderer may modify canonical truth directly. Renderer observations or proposed changes must return to the Brain as evidence, suggestions, or candidate state transitions for validation.

## 6. Continuity Engine

The Continuity Engine maintains persistent production state across production units, revisions, and renderer changes.

For film, this includes shots, scenes, and sequences. Other profiles may define different unit boundaries while preserving the same continuity principles.

The Continuity Engine shall maintain and validate, where applicable:

- character identity, face, body, hair, and distinguishing features;
- wardrobe, accessories, damage, dirt, ageing, and transformation state;
- props, ownership, hand placement, location, and condition;
- character blocking, entrances, exits, eyelines, and screen direction;
- camera position, lens, framing, movement, and orientation;
- environment layout, set dressing, weather, time of day, and lighting state;
- object persistence and physical changes;
- dialogue state, emotional state, performance intent, and lip-sync references;
- temporal order and cause-and-effect state;
- asset and material versions;
- deliberate continuity breaks approved by the Director.

### 6.1 Continuity Snapshot

Every renderable or executable production unit shall reference a versioned Continuity Snapshot or equivalent validated state package appropriate to its profile.

A snapshot records the validated state required to produce that unit without relying on a renderer's memory of previous outputs.

## 7. Render Orchestrator

The Render Orchestrator converts validated creative intent and continuity state into executable render plans.

It shall:

- analyse execution complexity;
- select one or more compatible renderers;
- choose AI, traditional, real-time, offline, VFX, or hybrid production routes;
- decide whether technical segmentation is required;
- generate versioned execution/render manifests;
- schedule and distribute jobs;
- manage preview, draft, review, and final quality tiers;
- reuse cached assets, layers, simulations, frames, and intermediate results;
- perform partial re-renders when dependencies permit;
- coordinate compositing and final assembly;
- track cost, compute, duration, renderer version, and evidence;
- validate technical completion before returning results to the Brain.

The Render Orchestrator shall not:

- own canonical continuity;
- rewrite story, interaction, or performance intent without approval;
- treat renderer output as automatically authoritative;
- bind the project permanently to one vendor or model;
- hide material failures behind a successful job status.

## 8. Render / Execution Manifest

Every render or execution job shall originate from a versioned manifest generated from validated Brain state.

A manifest is a contract. Renderer-specific adapters may translate it, but may not change its approved creative meaning.

## 9. Renderer Adapter Layer

Every renderer shall integrate through a Renderer Adapter.

The adapter shall translate between the canonical manifest and renderer-specific inputs and outputs.

A renderer adapter should expose capabilities such as:

- supported media and output types;
- duration and resolution limits;
- deterministic or stochastic behaviour;
- identity and reference controls;
- camera controls;
- depth, motion, normal, matte, and alpha outputs;
- seed, model, checkpoint, and version metadata;
- cost and expected completion time;
- cancellation, retry, and resume support;
- provenance and licence information.

The adapter boundary prevents renderer-specific assumptions from entering the Brain.

## 10. Adaptive Execution

Nexkosmo shall not impose one fixed generation duration or execution size across all production units.

The Render Orchestrator may estimate execution confidence using factors such as character count, motion complexity, camera movement, dialogue, physical interaction, environmental change, VFX density, identity sensitivity, renderer capabilities, requested resolution, simulation complexity, and profile-specific constraints.

The creator-facing production unit remains stable while internal segmentation exists only to improve reliability and may be revealed through advanced diagnostics when required.

## 11. Hybrid Rendering

The Render Orchestrator may combine multiple production technologies within one production unit.

Hybrid execution must preserve a unified approved contract for timing, state, identity, spatial relationships, colour, depth, motion, and continuity where applicable.

## 12. Caching and Partial Re-rendering

Every render result shall record its dependencies.

When a dependency changes, the orchestrator shall identify the smallest valid re-render scope.

A complete re-render shall occur only when required by dependency changes, renderer limitations, or validation failure.

Caches are accelerators, not sources of truth. Cached data must remain traceable to the manifest, snapshot, renderer, model, version, and asset revisions that produced it.

## 13. Validation Loop

```text
Canonical Brain State
        -> Continuity / State Snapshot
        -> Execution Manifest
        -> Renderer Adapter
        -> Result
        -> Technical Validation
        -> Continuity / State Validation
        -> Human Approval when required
        -> Accepted Result or Targeted Regeneration
```

A technically successful result may still fail continuity, interaction, or creative validation. These statuses must remain separate.

Only failed units, layers, frames, segments, passes, or dependencies should be regenerated when the dependency graph supports it.

## 14. Evidence and Provenance

For every result, Nexkosmo shall retain sufficient evidence to determine:

- what canonical state was used;
- what manifest was executed;
- which renderer, model, engine, and version were used;
- which assets and licences applied;
- what seed and relevant settings were used where available;
- what transformations and compositing operations occurred;
- what validation passed or failed;
- who approved the result;
- whether the result may be reproduced.

Evidence records must be append-only or otherwise protected according to the governing kernel and audit architecture.

## 15. Failure and Recovery

The system shall support:

- retrying failed execution without altering canonical continuity;
- changing renderer while retaining the same approved manifest intent;
- resuming interrupted jobs where supported;
- preserving successful layers or segments;
- rejecting stale results produced from superseded snapshots;
- recording partial and degraded outcomes explicitly;
- preventing silent substitution of incompatible renderer behaviour.

## 16. Security and Isolation

Render jobs shall respect workspace, project, principal, and asset-access boundaries.

Renderer adapters must receive only the minimum authorised data required for the job. Sensitive assets, unreleased scripts, likeness references, voices, and production metadata must be governed by policy, provenance, and audit controls.

External renderers shall be treated as replaceable and potentially untrusted infrastructure boundaries.

## 17. Film Reference Milestone

The earlier one-project / one-30-second-scene / five-shot milestone remains a valid **film-profile reference test**, not a universal Nexkosmo production hierarchy.

The milestone is successful only when a renderer can be replaced or a failed shot regenerated without changing the canonical film scene state.

Equivalent future milestones should be defined for non-film production profiles.

## 18. Implementation Order

### Phase 1: Contracts

Define typed format-general schemas and invariants for production profile, production unit, continuity/state snapshot, execution manifest, execution task, result, renderer capability profile, asset version, dependency record, and validation result.

Film-specific Scene and Shot contracts are specialisations of those permanent concepts.

### Phase 2: Continuity Prototype

Implement deterministic continuity state and conflict detection for a small format-specific production slice.

### Phase 3: Single Renderer Adapter

Connect one renderer through the canonical adapter boundary.

### Phase 4: Caching and Targeted Re-rendering

Add dependency-aware cache reuse and minimal invalidation.

### Phase 5: Hybrid Production

Support multiple renderer classes and compositing under one manifest.

### Phase 6: Adaptive Orchestration

Introduce confidence-based routing and technical segmentation without changing the creator-facing production-unit model.

## 19. Architectural Invariants

1. The Brain is the canonical source of truth.
2. Continuity is independent of rendering.
3. Renderers do not own project state.
4. Every render or execution originates from validated, versioned state.
5. Every result is traceable to its inputs and execution environment.
6. Renderer-specific details remain behind adapter boundaries.
7. Internal technical segmentation does not replace creator-facing production units.
8. Failed rendering does not corrupt canonical continuity.
9. Cached outputs are never treated as canonical truth.
10. New rendering technology must integrate without redesigning the Brain.
11. The permanent production architecture is format-general; Sequence/Scene/Shot is a film specialization, not a universal requirement.
12. `PRODUCTION` is the shared top-level stage; Studio is a contextual precision editor, not a competing stage.

## 20. Supersession

This amendment supersedes any architectural assumption that an AI renderer, video model, rendering engine, or film-only hierarchy is responsible for remembering or owning production continuity.

From adoption onward:

- continuity management and rendering execution are separate domains;
- the Brain supplies authoritative state;
- the selected production profile supplies format-appropriate production units;
- the Render Orchestrator supplies execution plans;
- renderer adapters supply interoperability;
- renderers supply replaceable visual execution;
- accepted results return to the Brain with evidence.

This amendment extends the Nexkosmo Canon without changing its foundational principle: reality, evidence, and validated state govern the system, while implementation technologies remain replaceable.
