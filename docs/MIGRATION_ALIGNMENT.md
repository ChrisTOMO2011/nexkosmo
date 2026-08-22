# Nexkosmo Migration & Codex Alignment Contract

## Status

This document governs the controlled migration of Nexkosmo into its intended long-term repository and environment structure. It does not itself authorise a production deployment or declare any milestone complete.

## Objective

Move Nexkosmo without losing architectural identity, provenance, working implementation, rollback capability, security boundaries, milestone evidence, or useful unimplemented product concepts.

The migration is a controlled engineering operation, not an opportunity for an unapproved redesign.

## Codex Role

Codex is an engineering agent operating within approved Nexkosmo architecture.

Codex MAY:

- inspect and inventory the repository;
- identify contradictions, risks, duplication, missing tests, and migration hazards;
- propose improvements with evidence;
- implement explicitly approved work;
- run tests and validation;
- prepare commits and pull requests in Development; and
- document discovered implementation facts.

Codex MUST NOT:

- silently redefine constitutional principles or frozen architecture;
- weaken STOP-GATE requirements;
- declare skipped tests successful;
- alter canonical identity-bearing assets without explicit approval;
- expose or commit secrets;
- treat implementation convenience as authority over architecture;
- delete the source before destination validation; or
- deploy to Production without explicit human approval.

## Migration Sequence

### Gate 0 — Baseline

- identify and record the source repository and baseline commit;
- pause unnecessary architecture churn during migration;
- preserve a recoverable source state;
- confirm access and backup/rollback strategy.

### Gate 1 — Inventory

Inventory at minimum:

- source code;
- architecture and product specifications;
- constitutional / governance documents;
- canonical asset registries and canonical assets;
- database schema and migrations;
- automated tests and fixtures;
- CI/CD configuration;
- infrastructure and deployment configuration;
- dependencies and lockfiles;
- scripts and developer tooling;
- model/runtime integrations;
- environment-variable names and secret references, never secret values;
- open milestone work and STOP-GATE state;
- external dependencies or resources required to reproduce the system; and
- legacy, experimental, alternate, or unimplemented product interfaces and their capabilities.

The creative-interface inventory MUST explicitly include all known variants and specialist workspaces, including Set, Studio, CGI, VFX, Render, Pre-Production, and any other historical or experimental production pages discovered during inventory.

These interfaces are not to be treated as obsolete merely because they are older, unimplemented, or not aligned with the latest shell. Their useful capabilities, controls, workflows, and interaction ideas must be catalogued before any consolidation decision.

Unknown or unexplained material must be classified before destructive action.

### Gate 2 — Destination Design

Define the destination before moving content.

The destination should preserve clear responsibility boundaries for governance, architecture/specifications, application code, infrastructure, tests, assets, migrations, operations, documentation, and design concepts.

Legacy or alternative interface concepts should be preserved in a clearly marked design/concepts or archive area until they are evaluated and either promoted, merged, superseded, or deliberately retired by Director approval.

Do not reorganise solely for aesthetics. Every structural change should improve ownership, security, build isolation, deployment, discoverability, or maintainability.

### Gate 3 — Authoritative Knowledge Migration

Move or establish the authoritative documents and registries first so implementation agents have the correct reference frame.

This includes, as applicable:

- Constitution / Charter / North Star;
- permanent Semantic Kernel contracts;
- architecture specifications;
- Guardian and stewardship contracts;
- canonical asset registries;
- Market & Opportunity Intelligence;
- Growth Intelligence;
- security and rights/consent contracts;
- environment and release policy; and
- current milestone / STOP-GATE decision.

### Gate 4 — Implementation Migration

Move implementation only after the destination's authority structure is known.

Preserve behaviour unless a change is separately approved. Avoid combining migration with broad refactoring because that makes failures and regressions harder to attribute.

Before replacing any creative workspace with a newer implementation, compare the old and new versions capability-by-capability. A newer page does not automatically supersede an older one.

The preferred convergence flow is:

`Preserve -> Catalogue -> Compare -> Extract Best Capabilities -> Director Review -> Canonical Workspace -> Implement`

For Set, Studio, CGI, VFX, Render, Pre-Production, and similar surfaces, determine whether each capability should remain a dedicated workspace, become a specialist mode inside another workspace, move to Finish/Delivery, or be shared across multiple stages. Do not discard useful functionality simply to simplify navigation.

### Gate 5 — Secrets and Security

- no credentials, tokens, private keys, passwords, production connection strings, or sensitive environment values may be committed;
- use environment-specific secret management;
- review history and configuration for accidental exposure;
- rotate credentials if exposure is discovered or reasonably suspected;
- apply least privilege to CI, Development, Staging, and Production;
- keep Production approval human-controlled.

### Gate 6 — Destination Validation

A copied repository is not a completed migration.

Validation should include the checks applicable to the current milestone, including:

- dependency installation/build reproducibility;
- canonical asset verification;
- database startup and migration;
- automated tests;
- integration tests;
- security and permission checks;
- required PostgreSQL/RLS/audit/outbox/inbox/idempotency/consent/rights/projection tests;
- backup/restore proof where required;
- observability/health checks where required; and
- the current milestone's formal acceptance contract.

Creative-workspace validation should also confirm that no approved or still-under-review capability from legacy Set, Studio, CGI, VFX, Render, Pre-Production, or other inventoried interfaces was accidentally lost during consolidation.

Skipped blocking tests remain blocking.

The existing `docs/STOP_GATE.md` remains an accurate historical rejection for its
earlier environment. `docs/STOP_GATE_ACCEPTANCE_2026-08-22.md` supersedes that
rejection only for the exact accepted commit and database increment identified in
the acceptance record.

### Gate 7 — Cutover

Cutover may occur only after destination validation passes and a human approves the transition.

After cutover:

- verify repository permissions;
- verify Development/Staging/Production separation;
- verify CI/CD targets the intended environments;
- preserve the source as a rollback/reference point until the Director explicitly authorises archive or removal;
- document the final migration commit and validation evidence.

## Environment Policy

Nexkosmo uses separate Development, Staging, and Production responsibilities.

- **Development:** AI/Codex may implement approved changes, run tests, and prepare reviewed changes.
- **Staging:** release candidates are integrated and verified against production-like expectations.
- **Production:** protected environment; deployment requires explicit human review and approval until a future governance decision deliberately changes that policy.

Secrets, data, permissions, and infrastructure must remain appropriately separated between environments.

### Agent, database, and MCP validation

Database-affecting migration evidence must prove the actual Development or Staging
PostgreSQL state. Record the environment, code commit/version, Alembic migration
head, expected state, actual state, and acceptance evidence. Apply the relevant
schema, constraint, RLS, permission, transaction/concurrency, audit,
outbox/inbox, idempotency, rights/consent, projection, and backup/restore checks.

AI, database, and MCP access must use least privilege. Agent reasoning, MCP output,
mocks, or generated SQL cannot replace required deterministic validation against
the real target state. These rules add evidence requirements and do not weaken any
existing STOP gate.

## Change Discipline

During migration, classify proposed work as one of:

- `MIGRATION_ONLY` — required to reproduce the existing system in the destination;
- `REQUIRED_FIX` — necessary to make validation pass or correct a demonstrated defect;
- `ARCHITECTURE_PROPOSAL` — potentially valuable but requires separate approval;
- `DEFERRED` — useful but unnecessary for safe migration.

This prevents migration scope from silently expanding into a redesign.

## Completion Standard

Migration is complete only when:

1. authoritative architecture is present and internally coherent;
2. implementation is reproducible in the destination;
3. required tests and milestone proofs pass rather than being skipped;
4. canonical assets and identity are preserved;
5. secrets and environment boundaries are secure;
6. provenance and rollback capability are retained;
7. Codex/AI agent authority is bounded by repository instructions;
8. inventoried legacy and experimental creative-workspace capabilities have been deliberately preserved, merged, superseded, or retired rather than accidentally lost; and
9. the Director explicitly accepts the cutover.

## Permanent Rule

> Align authority first, inventory second, design the destination third, migrate fourth, prove it works fifth, and only then cut over. Never sacrifice identity, evidence, useful capability, security, or rollback capability for migration speed.
