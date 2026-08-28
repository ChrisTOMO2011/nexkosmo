# Architecture Amendment 001: Continuity and Render Orchestration

**Status:** Adopted  
**Applies to:** Nexkosmo Studio and all future visual-production systems  
**Authority:** Nexkosmo Canon  

## 1. Purpose

This amendment separates continuity management from rendering execution.

The Nexkosmo Brain remains the permanent operating system and canonical source of truth. Rendering is treated as a replaceable execution capability. AI models, real-time engines, offline renderers, VFX systems, animation systems, compositors, and future production technologies may be exchanged without changing the canonical project state.

The system must not depend on any renderer to remember a production. The Brain owns truth; renderers consume validated instructions.

## 2. Governing Principle

> The Brain owns truth. The Continuity Engine protects truth. The Render Orchestrator determines how truth is produced visually. Renderers remain replaceable.

## 3. Architectural Separation

```text
Director / Filmmaker
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

## 4. Canonical Creative Hierarchy and Execution Scope

The canonical creative hierarchy is:

```text
Project
  -> Sequence
      -> Scene
          -> Shot
```

Rendering execution is a separate plane:

```text
Validated canonical scope
  -> Render Plan / Batch
      -> Render Job(s)
          -> Render Result(s)
```

A Render Plan, Render Batch, or Render Job may target the smallest or largest valid production scope supported by the chosen route, including:

- one Shot;
- multiple Shots;
- one Scene;
- multiple Scenes;
- one Sequence;
- multiple Sequences;
- a whole Project;
- a renderer/farm batch containing any valid combination of the above.

The execution scope must not redefine the filmmaker's creative hierarchy.

A three-minute Scene may contain many canonical Shots even when an offline renderer or render farm can efficiently submit the entire Scene, Sequence, or Project as one coordinated batch. Conversely, an apparently single Shot may be divided internally into several technical executions when reliability, VFX, layers, frame ranges, hardware limits, or renderer constraints require it.

Therefore:

> **Creative scope and render-execution scope are related but not identical. Nexkosmo may render narrowly or broadly while preserving Project -> Sequence -> Scene -> Shot as canonical creative truth.**

Internal generation segments, frame chunks, tiles, layers, farm tasks and batches are implementation details. They do not replace the filmmaker's Project, Sequence, Scene and Shot structure.

## 5. Brain Responsibilities

The Brain remains authoritative for:

- project identity and ownership;
- story, sequence, scene, and shot structure;
- character identity and state;
- environment and world state;
- asset identity and version history;
- timeline state;
- approved creative intent;
- canonical continuity records;
- renderer-independent production instructions;
- validation evidence and provenance.

No renderer may modify canonical truth directly. Renderer observations or proposed changes must return to the Brain as evidence, suggestions, or candidate state transitions for validation.

## 6. Continuity Engine

### 6.1 Purpose

The Continuity Engine maintains persistent production state across shots, scenes, sequences, revisions, and renderer changes.

### 6.2 Responsibilities

The Continuity Engine shall maintain and validate:

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
- deliberate continuity breaks approved by the filmmaker.

### 6.3 Continuity Snapshot

Every renderable shot shall reference a versioned Continuity Snapshot.

A snapshot records the validated state required to produce that shot without relying on a renderer's memory of previous frames.

Example:

```json
{
  "snapshotId": "continuity-sc024-sh018-v3",
  "sceneId": "scene-024",
  "shotId": "shot-018",
  "characters": [
    {
      "characterId": "char-john",
      "wardrobeId": "wardrobe-black-jacket-v2",
      "position": "warehouse-east-door",
      "heldProps": ["prop-torch-right-hand"],
      "condition": ["cut-left-cheek"]
    }
  ],
  "environmentId": "warehouse-night-v4",
  "cameraStateId": "camera-state-sh018-v2",
  "lightingStateId": "lighting-rain-night-v1",
  "approvedAt": "canonical-revision-reference"
}
```

The schema above is illustrative. The implementation must use formal typed contracts and validation rules.

A broad Scene-, Sequence-, or Project-scope render batch does not eliminate Shot-level Continuity Snapshots. The batch references the set of approved snapshots and shared state required by its contained Shots so that validation and targeted recovery remain granular.

### 6.4 Conflict Handling

When an instruction conflicts with current continuity, the engine must not silently invent a resolution.

It shall classify the conflict as one of:

- intentional creative change;
- unresolved ambiguity;
- continuity error;
- permitted discontinuity;
- state transition requiring approval.

The filmmaker or an authorised production rule determines the accepted resolution.

## 7. Render Orchestrator

### 7.1 Purpose

The Render Orchestrator converts validated creative intent and continuity state into executable render plans.

### 7.2 Responsibilities

The Render Orchestrator shall:

- analyse Shot, Scene, Sequence, and Project execution requirements;
- select one or more compatible renderers;
- choose AI, traditional, real-time, offline, VFX, or hybrid production routes;
- choose the most appropriate execution scope: Shot, multi-Shot, Scene, multi-Scene, Sequence, Project, or another validated batch scope;
- decide whether technical segmentation is required;
- generate Render Manifests and, where useful, coordinated Render Plans/Batches;
- schedule and distribute render jobs;
- manage preview, draft, review, and final quality tiers;
- reuse cached assets, layers, simulations, frames, and intermediate results;
- perform partial re-renders when dependencies permit;
- coordinate compositing and final assembly;
- track cost, compute, duration, renderer version, scope, and evidence;
- validate technical completion before returning results to the Brain.

The best execution scope is not necessarily the smallest scope. A broad RenderMan, Arnold, V-Ray, Cycles, Unreal, farm, or equivalent submission may reduce setup, scene-loading, asset-transfer, scheduling, and orchestration overhead when multiple approved Shots share data.

The best execution scope is also not necessarily the largest scope. A narrow Shot/frame/layer execution may be safer or cheaper when only a small dependency changed or when a renderer has reliability, memory, duration, or capability limits.

### 7.3 Non-responsibilities

The Render Orchestrator shall not:

- own canonical continuity;
- rewrite story or performance intent without approval;
- treat renderer output as automatically authoritative;
- bind the project permanently to one vendor or model;
- hide material failures behind a successful job status;
- treat a broad render submission as permission to collapse Shot/Scene validation or rerender unaffected work.

## 8. Render Manifest and Render Plan

Every render job shall originate from versioned validated execution state.

A single- or narrow-scope Render Manifest may resemble:

```json
{
  "manifestId": "render-sc024-sh018-v5",
  "scopeType": "shot",
  "scopeIds": ["shot-018"],
  "shotId": "shot-018",
  "continuitySnapshotId": "continuity-sc024-sh018-v3",
  "durationSeconds": 8,
  "frameRate": 24,
  "resolution": "3840x2160",
  "camera": {
    "lens": "50mm",
    "movement": "slow-dolly-left"
  },
  "productionRoute": "hybrid",
  "layers": [
    "environment",
    "characters",
    "lighting",
    "effects",
    "colour"
  ],
  "qualityTier": "preview",
  "rendererRequirements": {
    "identityLock": true,
    "deterministicSeedPreferred": true,
    "alphaOutputRequired": false
  }
}
```

A broader Render Plan/Batch may instead reference multiple approved manifests/snapshots:

```json
{
  "renderPlanId": "render-project-001-v2",
  "scopeType": "project",
  "scopeIds": ["project-001"],
  "includedShotIds": ["shot-001", "shot-002", "shot-003"],
  "manifestIds": ["render-sh001-v4", "render-sh002-v3", "render-sh003-v8"],
  "productionRoute": "offline-render-farm",
  "qualityTier": "final"
}
```

The broad plan coordinates execution; it does not erase the individual Shot contracts contained within it.

A Render Manifest or Render Plan is a contract. Renderer-specific adapters may translate it, but may not change its approved creative meaning.

## 9. Renderer Adapter Layer

Every renderer shall integrate through a Renderer Adapter.

The adapter shall translate between canonical Render Manifest/Render Plan state and renderer-specific inputs and outputs.

A renderer adapter should expose capabilities such as:

- supported media and output types;
- supported execution scopes and batching behaviour;
- duration and resolution limits;
- deterministic or stochastic behaviour;
- identity and reference controls;
- camera controls;
- depth, motion, normal, matte, and alpha outputs;
- seed, model, checkpoint, and version metadata;
- CPU/GPU/device requirements and limitations;
- cost and expected completion time;
- cancellation, retry, resume, checkpoint and farm-distribution support;
- provenance and licence information.

The adapter boundary prevents renderer-specific assumptions from entering the Brain.

Different modes of the same renderer may require separate capability profiles when their supported features differ materially. For example, CPU and GPU modes, or different renderer engines under one product family, must not be treated as identical merely because they share a product name.

## 10. Adaptive Shot and Batch Execution

Nexkosmo shall not impose one fixed generation duration or one fixed execution scope across all production work.

The Render Orchestrator may estimate execution confidence and efficiency using factors such as:

- number of characters;
- motion complexity;
- camera movement;
- dialogue and lip-sync requirements;
- physical interaction;
- environmental change;
- VFX density;
- identity sensitivity;
- renderer capabilities;
- requested resolution and frame rate;
- shared assets and scene-loading cost;
- farm/queue overhead;
- memory/VRAM limits;
- checkpoint/resume support;
- dependency boundaries;
- expected acceptance reliability;
- cost and elapsed time per accepted result.

Possible outcomes:

```text
Simple AI dialogue Shot
-> execute as one Shot

Walking conversation
-> one canonical Shot using limited internal segments

Complex fight
-> one canonical Shot using smaller technical segments

Large VFX event
-> split by layer, simulation, frame range, and segment

Offline-rendered Scene with shared environment/assets
-> submit multiple Shots as one Scene batch when efficient

Sequence sharing stable assets/lookdev
-> submit as coordinated multi-Scene or Sequence batch when efficient

Feature project prepared for a compatible render farm
-> submit the whole Project as a coordinated batch while preserving per-Shot manifests, results and validation
```

The filmmaker continues to see the real creative hierarchy and meaningful checkpoints. Internal segmentation or batching exists to improve reliability, efficiency and cost and may be revealed through advanced diagnostics when required.

Permanent rule:

> **Nexkosmo may batch broadly for efficiency and validate narrowly for control.**

## 11. Hybrid Rendering

The Render Orchestrator may combine multiple production technologies within one shot or across a broader render plan.

Example:

```text
Environment       -> real-time or offline 3D renderer
Character body    -> animation system
Face performance  -> AI-assisted performance renderer
Explosion         -> VFX simulation
Lighting passes   -> renderer-native output
Final integration -> compositor
```

Hybrid execution must preserve a unified camera, timing, colour, depth, motion, and continuity contract.

A whole-Scene, Sequence, or Project render plan may contain multiple renderer classes while still preserving the canonical Shot-level dependency and acceptance boundaries.

## 12. Caching and Partial Re-rendering

Every render result shall record its dependencies.

When a dependency changes, the orchestrator shall identify the smallest valid re-render scope.

Example:

```text
Dialogue changed
  Reuse: environment, static props, approved lighting
  Re-render: voice, face performance, lip sync, affected composite
```

A broad initial render submission does **not** imply a broad rerender requirement.

For example:

```text
Whole Project initially submitted to render farm
-> Shot 47 fails identity validation
-> preserve accepted Project/Sequence/Scene/Shot results
-> rerender only Shot 47 or the smallest affected layer/frame/segment set
-> revalidate affected dependencies
```

A complete Scene, Sequence, or Project re-render shall occur only when required by dependency changes, renderer limitations, shared-state invalidation, or validation failure that genuinely affects that scope.

Caches are accelerators, not sources of truth. Cached data must remain traceable to the manifest, plan, snapshot, renderer, model, version, and asset revisions that produced it.

## 13. Validation Loop

```text
Canonical Brain State
        -> Continuity Snapshot(s)
        -> Render Manifest(s) / Render Plan
        -> Renderer Adapter
        -> Render Result(s)
        -> Technical Validation
        -> Continuity Validation
        -> Human Approval when required
        -> Accepted Result or Targeted Regeneration
```

A technically successful render may still fail continuity or creative validation. These statuses must remain separate.

A broad Render Plan can succeed operationally while one contained Shot, layer, pass, frame range, or segment fails acceptance. Operational batch completion must never be confused with canonical acceptance.

Only failed shots, layers, frames, passes, or segments should be regenerated when the dependency graph supports it.

## 14. Evidence and Provenance

For every render result, Nexkosmo shall retain sufficient evidence to determine:

- what canonical state was used;
- what manifest and/or Render Plan was executed;
- what execution scope was selected and why;
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

- retrying a failed render without altering canonical continuity;
- changing renderer while retaining the same approved manifest intent;
- resuming interrupted jobs where supported;
- preserving successful Shots, layers, frames, passes or segments from a larger batch;
- rejecting stale results produced from superseded snapshots;
- recording partial and degraded outcomes explicitly;
- preventing silent substitution of incompatible renderer behaviour;
- shrinking a failed Scene/Sequence/Project batch to the smallest valid recovery scope;
- expanding execution scope again when batching is demonstrably more efficient and safe.

## 16. Security and Isolation

Render jobs shall respect workspace, project, principal, and asset-access boundaries.

Renderer adapters must receive only the minimum authorised data required for the job. Sensitive assets, unreleased scripts, likeness references, voices, and production metadata must be governed by policy, provenance, and audit controls.

External renderers shall be treated as replaceable and potentially untrusted infrastructure boundaries.

A Project-scope render submission must not automatically disclose unrelated private data merely because the execution batch is broad. Input assembly remains bounded to the authorised production dependencies required by that render plan.

## 17. Initial Implementation Milestone

The first controlled implementation should demonstrate:

1. one project;
2. one 30-second scene;
3. five shots;
4. two characters;
5. one environment;
6. one persistent prop;
7. versioned Continuity Snapshots;
8. one canonical Render Manifest per shot;
9. one Renderer Adapter;
10. preview-quality render results;
11. continuity validation across all five shots;
12. targeted regeneration of only failed shots;
13. complete evidence and provenance records.

The milestone is successful only when a renderer can be replaced or a failed shot regenerated without changing the canonical scene state.

A later orchestration milestone should additionally prove that the same canonical manifests can be submitted both as narrow Shot-level jobs and as a broader Scene/Sequence/Project batch, with equivalent accepted creative results and targeted recovery when only part of the batch fails.

## 18. Implementation Order

### Phase 1: Contracts

Define typed schemas and invariants for:

- Scene;
- Shot;
- Continuity Snapshot;
- Render Manifest;
- Render Plan / Batch;
- Render Job;
- Render Result;
- Renderer Capability Profile;
- Asset Version;
- Dependency Record;
- Validation Result.

### Phase 2: Continuity Prototype

Implement deterministic continuity state and conflict detection for a small multi-shot scene.

### Phase 3: Single Renderer Adapter

Connect one renderer through the canonical adapter boundary.

### Phase 4: Caching and Targeted Re-rendering

Add dependency-aware cache reuse and minimal invalidation.

### Phase 5: Hybrid Production

Support multiple renderer classes and compositing under one manifest/plan architecture.

### Phase 6: Adaptive Orchestration

Introduce confidence-based routing, execution-scope selection, batching and technical segmentation without changing the filmmaker's Project/Sequence/Scene/Shot model.

## 19. Architectural Invariants

The following invariants are mandatory:

1. The Brain is the canonical source of truth.
2. Continuity is independent of rendering.
3. Renderers do not own project state.
4. Every render originates from validated, versioned state.
5. Every result is traceable to its inputs and execution environment.
6. Renderer-specific details remain behind adapter boundaries.
7. Technical segmentation or broad batching does not replace Projects, Sequences, Scenes or Shots.
8. Failed rendering does not corrupt canonical continuity.
9. Cached outputs are never treated as canonical truth.
10. New rendering technology must integrate without redesigning the Brain.
11. Execution scope is adaptive and must not be confused with creative scope.
12. A Scene-, Sequence-, or Project-scope batch never removes Shot-level continuity, dependency, validation, acceptance, evidence or targeted-recovery boundaries.
13. Broad batching may reduce overhead, but failure must be recoverable at the smallest valid dependency scope wherever the selected route supports it.

## 20. Supersession

This amendment supersedes any architectural assumption that an AI renderer, video model, or rendering engine is responsible for remembering or owning production continuity.

It also supersedes any assumption that one canonical Shot or Scene must map one-to-one to one render job, or that every renderer must execute only at Scene level.

From adoption onward:

- continuity management and rendering execution are separate domains;
- the Brain supplies authoritative state;
- the Render Orchestrator supplies adaptive execution plans;
- renderer adapters supply interoperability;
- renderers supply replaceable visual execution at the valid scope they support;
- accepted results return to the Brain with evidence;
- broad renderer/farm batches and narrow targeted renders are both valid when selected from measured capability, reliability, dependency, cost and time evidence.

This amendment extends the Nexkosmo Canon without changing its foundational principle: reality, evidence, and validated state govern the system, while implementation technologies remain replaceable.