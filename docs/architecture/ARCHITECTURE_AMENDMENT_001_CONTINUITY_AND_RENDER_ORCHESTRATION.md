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

## 4. Canonical Production Hierarchy

```text
Project
  -> Sequence
      -> Scene
          -> Shot
              -> Render Job
                  -> Render Result
```

A scene may be any appropriate dramatic duration. A three-minute scene is not treated as one generation request. It is represented as a collection of shots, and each shot may be divided internally into technical generation segments only when required.

Internal generation segments are implementation details. They do not replace the filmmaker's scene and shot structure.

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

- analyse shot complexity;
- select one or more compatible renderers;
- choose AI, traditional, real-time, offline, VFX, or hybrid production routes;
- decide whether technical segmentation is required;
- generate Render Manifests;
- schedule and distribute render jobs;
- manage preview, draft, review, and final quality tiers;
- reuse cached assets, layers, simulations, frames, and intermediate results;
- perform partial re-renders when dependencies permit;
- coordinate compositing and final assembly;
- track cost, compute, duration, renderer version, and evidence;
- validate technical completion before returning results to the Brain.

### 7.3 Non-responsibilities

The Render Orchestrator shall not:

- own canonical continuity;
- rewrite story or performance intent without approval;
- treat renderer output as automatically authoritative;
- bind the project permanently to one vendor or model;
- hide material failures behind a successful job status.

## 8. Render Manifest

Every render job shall originate from a versioned Render Manifest generated from validated Brain state.

Example:

```json
{
  "manifestId": "render-sc024-sh018-v5",
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

A Render Manifest is a contract. Renderer-specific adapters may translate it, but may not change its approved creative meaning.

## 9. Renderer Adapter Layer

Every renderer shall integrate through a Renderer Adapter.

The adapter shall translate between the canonical Render Manifest and renderer-specific inputs and outputs.

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

## 10. Adaptive Shot Execution

Nexkosmo shall not impose one fixed generation duration across all shots.

The Render Orchestrator may estimate execution confidence using factors such as:

- number of characters;
- motion complexity;
- camera movement;
- dialogue and lip-sync requirements;
- physical interaction;
- environmental change;
- VFX density;
- identity sensitivity;
- renderer capabilities;
- requested resolution and frame rate.

Possible outcomes:

```text
Simple locked-camera dialogue -> render as one shot
Walking conversation          -> render using limited internal segments
Complex fight                  -> render using smaller internal segments
Large VFX event                -> split by layer, simulation, and segment
```

The filmmaker continues to see one shot. Internal segmentation exists only to improve reliability and may be revealed through advanced diagnostics when required.

## 11. Hybrid Rendering

The Render Orchestrator may combine multiple production technologies within one shot.

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

## 12. Caching and Partial Re-rendering

Every render result shall record its dependencies.

When a dependency changes, the orchestrator shall identify the smallest valid re-render scope.

Example:

```text
Dialogue changed
  Reuse: environment, static props, approved lighting
  Re-render: voice, face performance, lip sync, affected composite
```

A complete re-render shall occur only when required by dependency changes, renderer limitations, or validation failure.

Caches are accelerators, not sources of truth. Cached data must remain traceable to the manifest, snapshot, renderer, model, version, and asset revisions that produced it.

## 13. Validation Loop

```text
Canonical Brain State
        -> Continuity Snapshot
        -> Render Manifest
        -> Renderer Adapter
        -> Render Result
        -> Technical Validation
        -> Continuity Validation
        -> Human Approval when required
        -> Accepted Result or Targeted Regeneration
```

A technically successful render may still fail continuity or creative validation. These statuses must remain separate.

Only failed shots, layers, frames, or segments should be regenerated when the dependency graph supports it.

## 14. Evidence and Provenance

For every render result, Nexkosmo shall retain sufficient evidence to determine:

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

- retrying a failed render without altering canonical continuity;
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

## 18. Implementation Order

### Phase 1: Contracts

Define typed schemas and invariants for:

- Scene;
- Shot;
- Continuity Snapshot;
- Render Manifest;
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

Support multiple renderer classes and compositing under one manifest.

### Phase 6: Adaptive Orchestration

Introduce confidence-based routing and technical segmentation without changing the filmmaker's scene and shot model.

## 19. Architectural Invariants

The following invariants are mandatory:

1. The Brain is the canonical source of truth.
2. Continuity is independent of rendering.
3. Renderers do not own project state.
4. Every render originates from validated, versioned state.
5. Every result is traceable to its inputs and execution environment.
6. Renderer-specific details remain behind adapter boundaries.
7. Technical segmentation does not replace scenes or shots.
8. Failed rendering does not corrupt canonical continuity.
9. Cached outputs are never treated as canonical truth.
10. New rendering technology must integrate without redesigning the Brain.

## 20. Supersession

This amendment supersedes any architectural assumption that an AI renderer, video model, or rendering engine is responsible for remembering or owning production continuity.

From adoption onward:

- continuity management and rendering execution are separate domains;
- the Brain supplies authoritative state;
- the Render Orchestrator supplies execution plans;
- renderer adapters supply interoperability;
- renderers supply replaceable visual execution;
- accepted results return to the Brain with evidence.

This amendment extends the Nexkosmo Canon without changing its foundational principle: reality, evidence, and validated state govern the system, while implementation technologies remain replaceable.