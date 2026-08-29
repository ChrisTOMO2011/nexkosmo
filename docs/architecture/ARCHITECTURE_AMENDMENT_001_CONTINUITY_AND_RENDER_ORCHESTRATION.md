# Architecture Amendment 001: Continuity and Render Orchestration

**Status:** Adopted  
**Applies to:** Nexkosmo Studio and all future visual/interactive production systems  
**Authority:** Nexkosmo Canon  

## 1. Purpose

This amendment separates continuity/state management from rendering and production execution.

The Nexkosmo Brain remains the permanent operating system and canonical source of truth. Rendering and other production execution are replaceable capabilities. AI models, real-time engines, offline renderers, VFX systems, animation systems, game engines, simulation systems, compositors, and future production technologies may be exchanged without changing canonical project state.

The system must not depend on any renderer or production engine to remember a production. The Brain owns truth; execution tools consume validated instructions.

## 2. Governing Principle

> The Brain owns truth. The Continuity/State Engine protects truth. The Render Orchestrator determines how validated production intent is executed visually or interactively. Execution tools remain replaceable.

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
Continuity / State Engine                    Render Orchestrator
        |                                             |
        +----------------------+----------------------+
                               |
                               v
                       Production Pipeline
                 +-------------+-------------+
                 |             |             |
                 v             v             v
            AI Renderers   3D / Real-Time   VFX / Simulation
                 |             |             |
                 +-------------+-------------+
                               |
                               v
                    Integration / Assembly
                               |
                               v
                         Final Output
```

The Continuity/State Engine and Render Orchestrator are distinct architectural domains. They may cooperate through stable contracts, but neither may assume the responsibilities of the other.

## 4. Canonical Production Hierarchy

Nexkosmo uses a format-general hierarchy:

```text
Project
  -> Format-specific production structure
      -> Production Unit
          -> Execution Task / Render Job
              -> Execution / Render Result
```

For film-oriented work, this commonly resolves to:

```text
Project
  -> Sequence
      -> Scene
          -> Shot
              -> Render Job
                  -> Render Result
```

Other production formats may use approved structures such as levels, encounters, cinematics, clips, assets, simulations, passes, interactive sequences, or other format-appropriate production units.

A large production unit must not automatically become one indivisible generation or execution request. A three-minute film scene, a long game cinematic, a complex level bake, a large VFX simulation, or another costly production scope may be divided into smaller independently validatable execution units when reliability, recoverability, cost, or production logic justifies it.

Internal technical segmentation is an execution detail. It does not replace the creator-facing production structure or canonical project semantics.

## 5. Brain Responsibilities

The Brain remains authoritative for:

- project identity and ownership;
- format-specific project and production structure;
- character identity and state;
- environment and world state;
- asset identity and version history;
- timeline, interaction, and state-machine context where applicable;
- approved creative intent;
- canonical continuity/state records;
- renderer/engine-independent production instructions;
- validation evidence and provenance.

No renderer, engine, simulator, or production tool may modify canonical truth directly. Observations or proposed changes return to the Brain as evidence, suggestions, or candidate state transitions for validation.

## 6. Continuity / State Engine

### 6.1 Purpose

The Continuity/State Engine maintains persistent production state across production units, revisions, branches, renderer/engine changes, and format-specific transitions.

### 6.2 Responsibilities

It shall maintain and validate relevant state such as:

- character identity, face, body, hair, and distinguishing features;
- wardrobe, accessories, damage, dirt, ageing, transformation, inventory, and status;
- props, ownership, placement, location, condition, and interaction state;
- blocking, entrances, exits, eyelines, navigation, orientation, and spatial state;
- camera position, lens, framing, movement, and orientation where applicable;
- environment layout, set dressing, weather, time of day, lighting, and world state;
- object persistence and physical changes;
- dialogue, emotional state, performance intent, lip-sync, and interaction references;
- temporal order, branching/state progression, and cause-and-effect state;
- asset, material, level, system, and dependency versions;
- deliberate continuity/state breaks approved by the Director.

### 6.3 Continuity / State Snapshot

Every renderable or executable production unit shall reference versioned validated state sufficient for that unit to execute without relying on a renderer/engine's informal memory.

The implementation must use formal typed contracts and validation rules appropriate to the production format.

### 6.4 Conflict Handling

When an instruction conflicts with current continuity/state, the system must not silently invent a resolution.

It shall classify the conflict as one of:

- intentional creative change;
- unresolved ambiguity;
- continuity/state error;
- permitted discontinuity/state transition;
- state transition requiring approval.

The Director or an authorised production rule determines the accepted resolution.

## 7. Render Orchestrator

### 7.1 Purpose

The Render Orchestrator converts validated creative intent and continuity/state into executable production plans.

### 7.2 Responsibilities

The Render Orchestrator shall:

- analyse production-unit complexity;
- select one or more compatible renderers/engines/tools;
- choose AI, traditional, real-time, offline, VFX, simulation, game-engine, or hybrid production routes;
- decide whether technical segmentation is required;
- generate versioned execution/Render Manifests;
- schedule and distribute jobs/tasks;
- manage preview, draft, review, and final quality tiers where applicable;
- reuse cached assets, layers, simulations, frames, passes, builds, bakes, and intermediate results;
- perform partial re-execution when dependencies permit;
- coordinate compositing, integration, assembly, packaging, or equivalent format-specific output stages;
- track cost, compute, duration, tool/renderer version, and evidence;
- validate technical completion before returning results to the Brain.

### 7.3 Non-responsibilities

The Render Orchestrator shall not:

- own canonical continuity/state;
- rewrite story, gameplay, interaction, performance, or design intent without approval;
- treat renderer/engine output as automatically authoritative;
- bind the project permanently to one vendor, model, engine, or tool;
- hide material failures behind a successful job status.

## 8. Render / Execution Manifest

Every material render/execution job shall originate from a versioned manifest generated from validated Brain state.

A manifest is a contract. Tool-specific adapters may translate it, but may not change its approved creative or production meaning.

## 9. Adapter Layer

Every renderer, engine, simulator, or production tool shall integrate through an adapter boundary appropriate to its capabilities.

Adapters should expose applicable capabilities such as:

- supported media/output/task types;
- duration, resolution, memory, scene, or workload limits;
- deterministic or stochastic behaviour;
- identity/reference/state controls;
- camera and interaction controls;
- depth, motion, normal, matte, alpha, pass, cache, bake, or other evidence outputs;
- seed, model, checkpoint, engine, tool, and version metadata;
- cost and expected completion time;
- cancellation, retry, resume, migration, and partial-execution support;
- provenance and licence information.

The adapter boundary prevents tool-specific assumptions from entering the Brain.

## 10. Adaptive Production-Unit Execution

Nexkosmo shall not impose one fixed execution duration or granularity across all production units.

The Orchestrator may estimate execution confidence using factors such as:

- number of characters/entities;
- motion, simulation, gameplay, or interaction complexity;
- camera movement;
- dialogue and lip-sync requirements;
- physical interaction;
- environmental change;
- VFX or simulation density;
- identity/state sensitivity;
- renderer/engine/tool capabilities;
- requested resolution, frame rate, fidelity, build target, or output quality.

Film example:

```text
Simple locked-camera dialogue -> render as one shot
Walking conversation          -> render using limited internal segments
Complex fight                 -> render using smaller internal segments
Large VFX event                -> split by layer, simulation, and segment
```

Game/interactive example:

```text
Static prop bake             -> one bounded task
Complex cinematic            -> shot/segment execution
Large simulation             -> simulation regions/checkpoints
Level build                  -> dependency-aware task graph
Interactive encounter        -> state-aware assets + logic + validation units
```

The Director continues to see the appropriate creative/production unit. Internal segmentation exists to improve reliability, cost control, recoverability, and validation.

## 11. Hybrid Production

The Orchestrator may combine multiple production technologies within one production unit.

Example:

```text
Environment       -> real-time or offline 3D renderer
Character body    -> animation system
Face performance  -> AI-assisted performance renderer
Explosion         -> VFX simulation
Lighting passes   -> renderer-native output
Logic/state       -> game/interaction engine where applicable
Final integration -> compositor/engine/build pipeline
```

Hybrid execution must preserve the relevant unified timing, camera, colour, depth, motion, identity, state, interaction, and continuity contracts.

## 12. Caching and Partial Re-execution

Every material result shall record its dependencies.

When a dependency changes, the Orchestrator shall identify the smallest valid re-execution scope.

A complete rerun shall occur only when required by dependency changes, tool limitations, validation failure, or an approved production reason.

Caches are accelerators, not sources of truth. Cached data must remain traceable to the manifest, validated state, tool/renderer/model/engine version, and asset revisions that produced it.

## 13. Validation Loop

```text
Canonical Brain State
        -> Validated Continuity / State Snapshot
        -> Execution / Render Manifest
        -> Adapter
        -> Result
        -> Technical Validation
        -> Continuity / State Validation
        -> Human Approval when required
        -> Accepted Result or Targeted Regeneration / Re-execution
```

A technically successful result may still fail continuity/state or creative validation. These statuses must remain separate.

Only failed production units, layers, frames, passes, simulations, assets, segments, or other affected dependencies should be regenerated/re-executed when the dependency graph supports it.

## 14. Evidence and Provenance

For every material production result, Nexkosmo shall retain sufficient evidence to determine:

- what canonical state was used;
- what manifest was executed;
- which renderer, model, engine, simulator, or tool and version were used;
- which assets and licences applied;
- what seed/settings/state were used where available;
- what transformations, simulations, builds, or compositing/integration operations occurred;
- what validation passed or failed;
- who approved the result;
- whether the result may be reproduced or reconstructed.

Evidence records must be append-only or otherwise protected according to the governing kernel and audit architecture.

## 15. Failure and Recovery

The system shall support, where technically applicable:

- retrying a failed task without altering canonical continuity/state;
- changing renderer/engine/tool while retaining the same approved manifest intent;
- resuming interrupted jobs where supported;
- preserving successful layers, segments, passes, assets, simulations, or other completed dependencies;
- rejecting stale results produced from superseded state;
- recording partial and degraded outcomes explicitly;
- preventing silent substitution of incompatible tool behaviour;
- preventing a failed cheap resume/continuation from silently becoming a materially more expensive full restart without re-evaluating cost, attribution, and authority.

## 16. Coverage Before Completion

For expensive or high-risk production scopes, Nexkosmo may prefer broad lower-cost validation coverage before deep completion of isolated units.

The goal is to expose systemic faults across the relevant scope before committing heavily to final-quality execution.

Examples include:

- lower-cost coverage across all shots in a sequence before final convergence;
- preview validation across a commercial before final render;
- representative level/encounter validation before expensive full-quality bakes;
- broad simulation or asset validation before deep final execution;
- project-wide dependency sanity checks before committing large compute budgets.

Coverage before completion is not mandatory for every task. It is an evidence-based risk-control strategy used when expected avoided loss exceeds the cost of broader early validation.

## 17. Security and Isolation

Production jobs shall respect workspace, project, principal, and asset-access boundaries.

Adapters must receive only the minimum authorised data required for the job. Sensitive assets, unreleased scripts, likeness references, voices, gameplay systems, proprietary logic, and production metadata must be governed by policy, provenance, and audit controls.

External renderers, engines, models, tools, and distributed workers shall be treated as replaceable and potentially untrusted infrastructure boundaries.

## 18. Initial Implementation Milestone

The first controlled implementation may use a film-oriented profile to prove the architecture, but must not hard-code movie-only semantics into permanent contracts.

A valid first milestone can demonstrate:

1. one project;
2. one 30-second scene;
3. five shots;
4. two characters;
5. one environment;
6. one persistent prop;
7. versioned Continuity/State Snapshots;
8. one canonical Render Manifest per shot;
9. one Renderer Adapter;
10. preview-quality results;
11. continuity validation across all five shots;
12. targeted regeneration of only failed shots;
13. complete evidence and provenance records.

The milestone is successful only when a renderer can be replaced or a failed shot regenerated without changing canonical scene state, and when the underlying contracts remain general enough to support non-film production units later without redesigning the Brain.

## 19. Implementation Order

### Phase 1: Contracts

Define typed schemas and invariants for format-general Project Production Structure, Production Unit, Continuity/State Snapshot, Execution/Render Manifest, Job/Task, Result, Capability Profile, Asset Version, Dependency Record, and Validation Result.

Film-specific Scene and Shot contracts may specialize these shared production contracts.

### Phase 2: Continuity/State Prototype

Implement deterministic state and conflict detection for a small multi-unit production.

### Phase 3: Single Adapter

Connect one renderer/engine/tool through the canonical adapter boundary.

### Phase 4: Caching and Targeted Re-execution

Add dependency-aware cache reuse and minimal invalidation.

### Phase 5: Hybrid Production

Support multiple execution classes and integration/compositing under one manifest model.

### Phase 6: Adaptive Orchestration

Introduce confidence-based routing, technical segmentation, coverage-before-completion, and economic containment without changing the Director-facing production structure.

## 20. Architectural Invariants

The following invariants are mandatory:

1. The Brain is the canonical source of truth.
2. Continuity/state is independent of rendering/execution.
3. Renderers/engines/tools do not own project state.
4. Every material execution originates from validated, versioned state.
5. Every result is traceable to its inputs and execution environment.
6. Tool-specific details remain behind adapter boundaries.
7. Technical segmentation does not replace Director-facing production structure.
8. Failed execution does not corrupt canonical continuity/state.
9. Cached outputs are never treated as canonical truth.
10. New production technology must integrate without redesigning the Brain.
11. Large productions are orchestrated as coherent creative wholes but executed in the smallest practical independently validatable and recoverable units appropriate to the production format.
12. A project-wide Render/Build/Produce command is an orchestration command, not one indivisible execution job.
13. A failed continuation must not silently enlarge financial exposure through an unreviewed materially more expensive restart.

## 21. Supersession

This amendment supersedes any architectural assumption that an AI renderer, video model, rendering engine, game engine, simulator, or production tool is responsible for remembering or owning production continuity/state.

From adoption onward:

- continuity/state management and production execution are separate domains;
- the Brain supplies authoritative state;
- the Render Orchestrator supplies execution plans;
- adapters supply interoperability;
- tools/renderers/engines supply replaceable execution;
- accepted results return to the Brain with evidence.

This amendment extends the Nexkosmo Canon without changing its foundational principle: reality, evidence, and validated state govern the system, while implementation technologies remain replaceable.
