# DEC-0005: Production Assurance and Render Cost Attribution

Status: APPROVED
Date: 2026-08-29
Authority: Director

## Context

Nexkosmo is intended to give Directors strong production assurance across supported production formats without transferring Nexkosmo-caused production failure cost to the customer or allowing assurance recovery to become an unbounded spend path for Nexkosmo.

The existing architecture already provides the technical foundation: validated canonical state, versioned continuity/state snapshots, versioned execution/Render Manifests, adapters, dependency-aware partial re-execution, validation, provenance, retry/resume support, human material-spend authority, idempotent financial effects, auditable ledgers, and bounded worker/resource controls.

Film is one production profile, not the definition of Nexkosmo. The same assurance principles apply to animation, commercials, music videos, games, interactive experiences, 3D/VFX work, simulations, asset production, and future supported formats through their own format-appropriate production units.

What was not yet explicit was the commercial and accounting rule that links production-failure evidence to financial responsibility.

## Decision

### 1. Production Assurance principle

Nexkosmo shall distinguish a failure to conform to approved production state from a new or changed Director request.

A Nexkosmo-caused failure to deliver work that conforms to the approved production contract basis must not automatically become a customer-billable retry merely because compute was consumed.

A subsequent Director creative revision to work that satisfied the approved production contract basis is new authorised production work, not a Nexkosmo failure.

The production contract basis is derived from approved canonical state, applicable READY clearance, validated continuity/state snapshots, execution/Render Manifests, dependency state, rights/provenance state, and recorded Director authority. This decision does not create a competing canonical truth or duplicate execution contract.

### 2. Separate economic facts

For every material production operation, Nexkosmo must preserve distinct financial facts:

- **Actual Production Cost** — all authoritative or defensibly estimated production consumption attributable to the operation, including successful work, failed attempts, validation, recovery, compute, storage, transfer, renderer/service/tool cost, and metered AI/model usage where applicable.
- **Customer-Billable Cost** — only the portion legitimately chargeable to the Director/customer under the applicable product and production contract.
- **Nexkosmo Assurance Cost** — production cost absorbed by Nexkosmo because the failure or recovery is attributable to Nexkosmo delivery responsibility rather than a new customer-authorised creative change.
- **Recovered/Reused Value** — measurable work preserved through cache reuse, accepted layers/segments/passes/assets/simulations, compatible checkpoints, resume, or narrow re-execution. This is operational/economic evidence and must not be fabricated as savings when no defensible basis exists.

Compute consumption, customer liability, and future contributor compensation are separate facts and must not be collapsed into one number.

### 3. Fault attribution before billing

A failed or unusable result must be classified from evidence before its recovery cost is treated as customer-billable.

Relevant classifications include, where applicable:

- approved-state or manifest non-conformance;
- technical/render/build/simulation failure;
- continuity/state failure;
- worker/infrastructure failure;
- renderer/provider/engine/tool capability or execution failure;
- Nexkosmo routing/orchestration failure;
- Director creative revision;
- Director-requested experiment/alternative;
- unresolved/unknown attribution.

`UNKNOWN` attribution is not permission to silently charge the customer as though the failure were a Director revision. Financial policy for unresolved attribution must fail safely and remain auditable.

### 4. No arbitrary execution-count limit

Nexkosmo shall not impose an arbitrary creative render/execution-count limit per production unit as an architectural rule.

Execution remains governed by available credits/resources, project budget, material-spend authority, safety/resource ceilings, and approved product policy.

### 5. Economic containment of repeated failure

Production Assurance is not authority for unlimited retries.

When materially similar failures recur, the Orchestrator/Brain must not continue the same expensive strategy merely because retry is technically possible. It must preserve evidence, reduce the blast radius, diagnose or classify the failure to the level supported by evidence, change route/renderer/model/engine/tool/task scope where appropriate, perform a lower-cost proof where practical, and only then resume expensive execution.

No permanent fixed retry count is declared by this decision. Evidence-based thresholds and stop conditions must be versioned and grounded in observed reliability/economics rather than invented constants.

The Brain/Orchestrator may reduce or stop delegated execution when risk rises, but may not raise its own budget, compute ceiling, or material-spend authority.

### 6. Intelligent validation checkpoints

Nexkosmo may deliberately incur checkpoint or validation overhead when doing so is expected to reduce larger downstream loss or expose faults before expensive continuation.

The optimisation objective is not the fewest checkpoints or the minimum raw GPU minutes. It is the reduction of total expected wasted production cost while preserving required quality, evidence, and fault-detection capability.

Checkpoint placement should consider supported factors such as remaining execution cost, recoverable work, production-unit complexity, failure history, renderer/engine/tool/worker reliability, expensive simulations/builds, Director inspection needs, quality milestones, and compatibility with continuation.

A mandatory safety, continuity/state, rights, technical, or production validation checkpoint must not be suppressed merely to make an estimate appear cheaper.

### 7. Granular execution and coverage before completion

Large productions shall be orchestrated as coherent creative wholes but executed in the smallest practical independently validatable and recoverable units appropriate to the production format.

A project-wide `Render`, `Build`, `Produce`, `Bake`, `Simulate`, or equivalent command is an orchestration command. It must not be interpreted as authority to collapse the entire project into one indivisible execution job.

Where risk justifies it, Nexkosmo may prefer broad lower-cost validation coverage before deep completion of isolated units. The purpose is to expose systemic faults across the relevant production scope before committing heavily to final-quality execution.

Examples include broad preview coverage across a film sequence, representative game level/encounter validation before expensive final bakes, wide asset or simulation validation before deep final execution, and project-wide dependency sanity checks before large compute expenditure.

### 8. Checkpoint compatibility and continuation

A checkpoint or partial result may be reused or resumed only when compatibility is established for the relevant execution path. Compatibility may include renderer/engine/tool version, integrator or production mode, canonical state, scene/level/geometry/material/texture/camera/lighting revisions, resolution, sampling or simulation state, output/pass configuration, colour pipeline, device constraints, and checkpoint format.

Preview-to-final continuation is capability-gated. Preview work must not be promoted into final production merely because reuse would be cheaper.

If a cheap resume or continuation path becomes invalid, Nexkosmo must not silently convert it into a materially more expensive full restart. It must re-evaluate cost, fault attribution, available alternatives, and required Director/material-spend authority before expanding financial exposure.

### 9. Marketing/guarantee boundary

This decision authorises the architecture and policy direction for Production Assurance. It does not, by itself, prove that a public `100% guarantee` is operationally or legally ready to advertise.

Any public guarantee must accurately define scope, conditions, exclusions, and remedy; must be supported by implemented billing/ledger/runtime evidence; and must follow Nexkosmo claims assurance and applicable law.

The intended product principle is: customers should not be charged for Nexkosmo-caused production failure as though it were new customer-requested creative work.

## Consequences

- Billing/payment implementation must support separate actual, billable, and assurance amounts and preserve attribution evidence.
- Production operations and recovery must remain traceable to canonical state, manifests/contracts, dependencies, attempts, validation, and cost evidence.
- Retry/resume logic must include economic containment and cannot become an unbounded assurance-spend loop.
- Reliability becomes part of true route cost: a nominally cheap renderer, engine, tool, provider, or worker can be more expensive when failure/recovery cost is included.
- Contributor-compute settlement rules must later distinguish consumed compute, valid reusable work, contributor responsibility, Nexkosmo orchestration responsibility, and customer liability.
- Public claims must not describe the assurance as unconditional satisfaction or unlimited free creative revision unless a separately approved contract explicitly supports that promise.
- Format-specific production hierarchies may vary, but granular execution, narrow invalidation, evidence-based recovery, and bounded financial exposure remain shared Nexkosmo rules.

## Validation required before public Production Assurance launch

Before Nexkosmo publicly advertises a production guarantee based on this decision, evidence must demonstrate at minimum:

1. server-authoritative price/credit policy;
2. durable auditable financial ledger;
3. idempotent billing and duplicate-completion protection;
4. production attempt/result/dependency/validation evidence;
5. fault-attribution states and dispute/review path;
6. separate Actual Production Cost, Customer-Billable Cost, and Nexkosmo Assurance Cost;
7. bounded retry/economic stop controls;
8. worker/provider/tool failure handling appropriate to the active execution routes;
9. reconciliation between provider/compute evidence and internal ledger;
10. clear customer-facing guarantee terms reviewed for applicable legal requirements.

Until those controls are implemented and evidenced, the public guarantee remains a planned product promise, not a verified current capability.
