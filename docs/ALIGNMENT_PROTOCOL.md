# Nexkosmo Alignment Protocol

Status: APPROVED GOVERNANCE PROTOCOL

Purpose: keep the Director, ChatGPT, Codex, repository documentation, implementation, and tests aligned without depending on long conversational memory.

## Scope boundary

This protocol is the **Agent Alignment Layer** for ChatGPT and Codex, with repository and CI enforcement.

It is not a replacement for, redesign of, or duplicate implementation of the Nexkosmo Brain. The Brain remains its existing intelligence architecture with its own truth, evidence/provenance, confidence, continuity, reasoning, safety/recovery, and future integration responsibilities.

Outputs from this Agent Alignment Layer may later be consumed by the Brain as external engineering evidence. They must not become a competing Brain truth store, reasoning engine, Guardian layer, recovery engine, or Production Assurance engine.

## Core rule

Alignment is a repository and evidence property, not a memory property.

`Director decision -> repository canon -> implementation -> automated checks -> human review -> accepted evidence`

## Roles

- Director: final authority for product direction, canon, material spend, and consequential approval.
- ChatGPT: alignment steward. Responsible for retrieving current state, detecting drift, challenging contradictions, keeping Codex and repository work pointed at approved direction, and clearly separating fact/canon/evidence/inference/estimate/hypothesis/unknown. ChatGPT does not independently approve or supersede canon.
- Codex: implementation agent. Responsible for implementing approved direction against current repository state, not stale branch assumptions or conversational recollection.
- CI/tests: evidence gates. They verify enforceable constraints but do not define product direction, customer liability, or commercial truth.
- Brain: separate Nexkosmo intelligence architecture. The Agent Alignment Layer protects engineering-agent alignment and may provide external evidence to Brain later; it does not replace Brain responsibilities.

## Required pre-work handshake

Before any significant Nexkosmo architecture, product, or implementation task, the AI/agent must:

1. Identify the repository and current target branch.
2. Read `AGENTS.md`.
3. Read `governance/alignment-manifest.yaml` and report its manifest version.
4. Read `docs/CURRENT_STATE.md`.
5. Read the relevant approved decision records and architecture/product specifications.
6. For production-assurance, render/compute, worker, billing/credits, or guarantee work, read `docs/decisions/DEC-0005-production-assurance-and-render-cost-attribution.md` and `docs/architecture/ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md`.
7. Inspect current implementation when the task concerns implementation reality.
8. Compare the working branch with current `main` when branch freshness matters.
9. Resolve contradictions before making changes.
10. Stop instead of guessing when a conflict affects canon, authority, data ownership, security, workflow, architecture boundaries, deployment identity, financial attribution, material spend, or material public claims.

## Flow model

Nexkosmo uses three distinct flow layers that must not be collapsed:

1. Full user entry journey.
2. Creative workflow.
3. Production/Studio deep-edit loop.

The shared creative workflow is format-general:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

The general Production/Studio loop is:

`PRODUCTION -> select production unit -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

Film-oriented profiles may expose that boundary through scene/shot terminology, while games, interactive experiences, 3D/VFX work, asset production, simulations, and future formats may use other approved production-unit structures. Movie-only vocabulary must not become a universal project, Production, Studio, render/compute, billing, or worker contract by accident.

The authoritative forms are defined in `docs/CURRENT_STATE.md` and approved decision records. An implementation may provide shortcuts or format-specific profiles, but it must not redefine the shared layers by accident.

## Production Assurance alignment

`docs/decisions/DEC-0005-production-assurance-and-render-cost-attribution.md` is the approved cross-domain decision linking production execution evidence to customer billing responsibility.

Alignment review must preserve these boundaries:

- a Nexkosmo-caused production failure is not automatically customer-billable merely because compute was consumed;
- a Director revision after conforming delivery is new authorised work;
- Actual Production Cost, Customer-Billable Cost, and Nexkosmo Assurance Cost remain distinct;
- fault attribution precedes recovery billing;
- `UNKNOWN` attribution is not permission to silently charge the customer;
- Production Assurance reuses existing canonical state, READY evidence, continuity/state snapshots, Render/Execution Manifests, dependency evidence, validation, and financial ledgers rather than creating a duplicate Brain or truth store;
- large productions remain coherent creative wholes but execution risk is bounded through the smallest practical independently validatable and recoverable format-appropriate units;
- broad lower-cost validation coverage may precede deep completion when it reduces expected downstream loss;
- retry/resume must not silently convert a cheap continuation into a materially more expensive full restart without reassessing cost, attribution, alternatives, and required Director authority;
- Brain/Orchestrator may reduce or stop delegated execution when risk rises but cannot raise its own budget, compute ceiling, credits, or material-spend authority;
- a public `100% guarantee` remains an unverified claim until implementation, runtime/billing evidence, customer terms, and applicable legal review support the exact promise.

## Evidence labels

Use these meanings consistently:

- `CANONICAL`: explicitly approved current direction or immutable approved identity.
- `VERIFIED`: directly confirmed from repository/runtime/test evidence.
- `PROVEN-WITHIN-SCOPE`: demonstrated under stated test conditions; not universal proof.
- `SUPPORTED`: evidence favors the claim but is not conclusive.
- `INFERENCE`: reasoned conclusion from evidence.
- `ESTIMATE`: planning or forecasting approximation.
- `HYPOTHESIS`: unverified proposal that requires testing.
- `UNKNOWN`: evidence is insufficient.
- `FALSIFIED`: evidence disproves the claim within the tested scope.

AI-generated content does not become CANONICAL merely because it is confident or repeated.

## Decision records

Important decisions must be recorded under `docs/decisions/`.

Each decision should include:

- decision ID;
- status;
- date;
- decision owner/authority;
- context;
- decision;
- consequences;
- superseded decisions, if any;
- evidence or validation required.

A superseded decision remains historical evidence but is no longer current authority.

## Implementation rules

- Never treat screenshots, mockups, fixtures, or local component state as production truth.
- Demo fixtures must be isolated and explicitly labelled.
- Project-specific state belongs behind project/application contracts and persistent state, not hidden frontend constants.
- Do not invent backend APIs to make a UI appear complete.
- Do not silently translate an old architecture into a new architecture without an approved decision.
- Preserve reusable implementation that remains compatible; replace only what conflicts with current canon.
- Obsolete prototype navigation may remain temporarily in an unmerged reconciliation branch, but it must be labelled as legacy and must not be merged unchanged.
- Do not turn a film-oriented first vertical slice into a universal movie-only data model.
- Do not invent financial attribution, customer liability, guarantee eligibility, or assurance evidence to make a billing or Production UI appear complete.

## Pull-request alignment contract

Every significant PR should answer:

1. What alignment-manifest version is being followed?
2. What approved decision/specification does this implement?
3. What current-state sections does it affect?
4. What canonical assets or state does it touch?
5. Does it introduce or remove fixtures/hard-coded project state?
6. What tests/checks were run?
7. What remains placeholder, estimated, inferred, or unknown?
8. Does the branch contain the current `main` governance/canon changes?
9. Does the implementation preserve the distinction between full user journey, creative workflow, and Production/Studio editing loop?
10. Does a shared contract accidentally assume movie-only Scene/Shot semantics?
11. For render/compute/billing/assurance work, how are production format/unit, dependency scope, fault attribution, actual/billable/assurance cost, retry/checkpoint containment, and Director material-spend authority handled?

If the PR changes canon, the Director-approved decision record and `docs/CURRENT_STATE.md` update must be included in the same reviewed change, together with a manifest revision when the machine-readable identity changes.

## Fresh-context reconstruction test

At important milestones, validate the repository with a fresh AI context that has no conversation history.

The fresh agent should be able to answer from the repository alone:

- What is Nexkosmo's full entry journey?
- What is the canonical creative workflow?
- Which import paths are format-specific, and what is the screenplay-import profile?
- What is the format-general Production/Studio boundary?
- How does a film scene/shot profile relate to the general production-unit contract?
- What is Production Assurance and what does it not guarantee yet?
- How are Actual Production Cost, Customer-Billable Cost, and Nexkosmo Assurance Cost distinguished?
- Who has authority over canon and material spend?
- What is ChatGPT's alignment-steward role?
- What is Codex's implementation role?
- What is the current engineering priority/STOP GATE?
- What must not be hard-coded as project truth?
- What is implemented versus merely designed/planned?
- What canonical assets must be retrieved rather than regenerated?
- What is the boundary between the Agent Alignment Layer and the existing Brain architecture?

If the repository cannot answer these reliably, fix the repository documentation/structure instead of relying on a larger prompt.

## Drift response

When drift is detected:

1. classify it as documentation drift, branch drift, implementation drift, data/canon drift, workflow drift, format-contract drift, financial-attribution drift, test/evidence drift, runtime drift, or AI/context drift;
2. stop expansion in the affected area;
3. identify the current authority source;
4. reconcile the minimum required files/code;
5. run alignment, Production Assurance alignment, deliberate drift-injection, and normal quality checks;
6. obtain Director approval for any intentional change of canon;
7. only then resume feature expansion.

The drift controls in this protocol primarily protect ChatGPT and Codex from engineering-agent drift. Future Brain use should consume their evidence through existing Brain architecture rather than duplicating these controls as a second Brain.

## Review philosophy

Neither human nor AI is assumed infallible.

The expected loop is:

`AI recommends -> AI exposes uncertainty and evidence -> Director inspects -> Director approves/rejects -> implementation proves -> later evidence may challenge the decision`.

The goal is not to eliminate change. The goal is to make change explicit, reviewable, reversible, evidence-backed, and economically attributable where production cost is involved.
