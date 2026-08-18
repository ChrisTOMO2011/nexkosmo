# Nexkosmo Alignment Protocol

Status: APPROVED GOVERNANCE PROTOCOL

Purpose: keep the Director, ChatGPT, Codex, repository documentation, implementation, and tests aligned without depending on long conversational memory.

## Core rule

Alignment is a repository and evidence property, not a memory property.

`Director decision -> repository canon -> implementation -> automated checks -> human review -> accepted evidence`

## Required pre-work handshake

Before any significant Nexkosmo architecture, product, or implementation task, the AI/agent must:

1. Identify the repository and current target branch.
2. Read `AGENTS.md`.
3. Read `docs/CURRENT_STATE.md`.
4. Read the relevant approved decision records and architecture/product specifications.
5. Inspect current implementation when the task concerns implementation reality.
6. State or internally resolve any contradiction before making changes.
7. Stop instead of guessing when a conflict affects canon, authority, data ownership, or architecture boundaries.

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

## Pull-request alignment contract

Every significant PR should answer:

1. What approved decision/specification does this implement?
2. What current-state sections does it affect?
3. What canonical assets or state does it touch?
4. Does it introduce or remove fixtures/hard-coded project state?
5. What tests/checks were run?
6. What remains placeholder, estimated, inferred, or unknown?
7. Does the branch contain the current `main` governance/canon changes?

If the PR changes canon, the Director-approved decision record and `docs/CURRENT_STATE.md` update must be included in the same reviewed change.

## Fresh-context reconstruction test

At important milestones, validate the repository with a fresh AI context that has no conversation history.

The fresh agent should be able to answer from the repository alone:

- What is Nexkosmo's current product journey?
- What is the Production/Studio boundary?
- Who has authority over canon?
- What is the current engineering priority/STOP GATE?
- What must not be hard-coded as project truth?
- What is implemented versus merely designed/planned?
- What canonical assets must be retrieved rather than regenerated?

If the repository cannot answer these reliably, fix the repository documentation/structure instead of relying on a larger prompt.

## Drift response

When drift is detected:

1. classify it as documentation drift, branch drift, implementation drift, data/canon drift, or test/evidence drift;
2. stop expansion in the affected area;
3. identify the current authority source;
4. reconcile the minimum required files/code;
5. run alignment and normal quality checks;
6. obtain Director approval for any intentional change of canon;
7. only then resume feature expansion.

## Review philosophy

Neither human nor AI is assumed infallible.

The expected loop is:

`AI recommends -> AI exposes uncertainty and evidence -> Director inspects -> Director approves/rejects -> implementation proves -> later evidence may challenge the decision`.

The goal is not to eliminate change. The goal is to make change explicit, reviewable, reversible, and evidence-backed.
