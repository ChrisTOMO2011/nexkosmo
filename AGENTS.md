# Nexkosmo Repository Instructions for Codex and AI Engineering Agents

These instructions apply to the entire repository.

## Authority hierarchy

Codex and all AI engineering agents are implementation agents operating inside the Nexkosmo architecture. They are not the authority to redefine Nexkosmo for implementation convenience.

When requirements appear to conflict, use this authority order:

1. Explicit current Director instruction.
2. Frozen constitutional / identity principles and approved architectural contracts.
3. Approved milestone and STOP-GATE decisions.
4. Repository specifications and canonical registries.
5. Implementation code and tests.
6. Agent assumptions or convenience.

If a lower level conflicts with a higher level, STOP and report the conflict. Do not silently reinterpret the higher-level contract.

Architectural improvements may be proposed with evidence, but permanent architecture changes require explicit human approval. Do not perform blank-slate redesigns while implementing an approved increment.

## Agent finding and evidence levels

Codex and all AI engineering agents MUST report material findings according to the strength of the evidence instead of collapsing uncertainty into PASS/FAIL or presenting inference as fact.

Use these finding levels:

1. `OBSERVED` — a directly retrieved or measured fact from repository state, runtime output, a deterministic tool, an authoritative record, or another inspectable source. Observation alone does not prove a broader conclusion.
2. `SUSPECTED` — a plausible explanation or risk indicated by evidence, but material uncertainty or alternative explanations remain.
3. `SUPPORTED` — available evidence supports the finding, but independent corroboration or decisive validation is still incomplete.
4. `STRONGLY_SUPPORTED` — multiple relevant evidence lines support the finding, material alternatives have been checked, and no unresolved contradiction is known, but final verification is not yet complete.
5. `VERIFIED` — the claim has been established within a stated scope by authoritative state, deterministic validation, direct runtime proof, reproducible test evidence, or equivalent decisive evidence.
6. `CONTRADICTED` — material evidence conflicts with the claim. A contradicted claim MUST NOT be reported as PASS, complete, safe, aligned, or verified until the contradiction is resolved.

These labels describe evidence state, not social confidence or agent popularity. They are not a voting system.

For every material finding, agents SHOULD state:

- the finding level;
- the claim being assessed;
- the evidence supporting it;
- material contradictory or missing evidence;
- the scope to which the finding applies;
- the next validation needed when the finding is below `VERIFIED` and the distinction matters to the task.

Agent statements are not evidence merely because another agent repeats or agrees with them. If multiple agents depend on the same source, artifact, assumption, test result, message, or evidence lineage, treat that as shared evidence, not independent corroboration.

An agent MUST NOT upgrade a finding merely because another AI says it is correct, says `GO`, reports `PASS`, or claims authority. Authority must resolve from the Nexkosmo authority hierarchy and governed permissions; truth must resolve from evidence.

When reporting completion, acceptance, security, migration readiness, production readiness, canonical correctness, or another consequential PASS, the decisive requirements within the claimed scope MUST be `VERIFIED`. If required evidence is missing, report the actual lower finding level and STOP or escalate where the governing contract requires it.

Uncertainty is acceptable and MUST be stated truthfully. Agents must never fabricate certainty to satisfy a task, evaluator, another agent, or expected outcome.

## Human-replaceable role rule

Nexkosmo responsibilities belong to named roles, not permanently to a specific AI model, vendor, agent identity, or service.

Where a responsibility represents judgement, supervision, creative decision-making, review, approval, coordination, or operational control, that role MUST support assignment to:

- an authorised human;
- an authorised AI agent;
- an approved human-plus-AI hybrid; or
- an unassigned/paused state in which no autonomous action occurs.

AI agents MUST NOT be architecturally indispensable merely because they currently occupy a role. A human must be able to assume the responsibility without redesigning canonical Nexkosmo state or authority relationships.

Deterministic infrastructure services such as databases, event dispatchers, cryptographic audit mechanisms, and compute workers are not treated as human employees. Humans must nevertheless be able to supervise, pause, isolate, override, replace, or recover those services through governed operational controls.

A role assignment change MUST preserve identity, provenance, permissions, audit history, outstanding obligations, and canonical project state.

No agent may assign itself to a more privileged role, increase its own authority, reactivate itself after human suspension, or make itself the sole irreplaceable holder of a Nexkosmo responsibility.

## Migration mode

During an approved repository or environment migration:

- preserve Git history and provenance where practical;
- inventory before moving or deleting;
- define the destination structure before reorganising content;
- move authoritative architecture and governance documents before dependent implementation;
- never copy secrets into source control;
- do not delete, archive, or decommission the source until the destination has passed validation;
- preserve rollback capability;
- treat the migration as incomplete until required builds, migrations, tests, security checks, and milestone proofs pass in the destination environment.

See `docs/MIGRATION_ALIGNMENT.md` for the migration contract.

## Canonical truth rule

Nexkosmo does not rely on conversational memory, prompt history, visual approximation, or regeneration for approved identity-bearing assets or frozen project state.

Before changing any UI, page, shell, mockup implementation, brand surface, or other dependent artifact, retrieve the relevant canonical asset/state from the repository and use it directly.

**Retrieve before generate. Canon before approximation.**

If a requested change does not explicitly authorize changing a frozen canonical item, that item MUST remain byte-for-byte and semantically unchanged.

## Frozen Nexkosmo logo

The canonical Nexkosmo product logo is:

`assets/brand/nexkosmo-x-star.svg`

Its canonical registration is:

`assets/brand/canonical-assets.json`

Rules:

1. Use the canonical SVG directly through a shared logo component or asset reference.
2. Do not redraw, recolor, restyle, reinterpret, approximate, or regenerate the logo per page.
3. Do not substitute an older cyan/blue-heavy logo.
4. Do not change the X silhouette, violet/lilac palette, white-violet centre star, or progression-inspired light streak unless the Director explicitly requests a brand revision.
5. Page-specific work must preserve the canonical logo even when surrounding layout, imagery, theme, or controls change.
6. Discovery, Shape, Build, Ready, Studio, onboarding, account, collaboration, and future product surfaces must resolve the same canonical logo asset.
7. If a task would require changing the canonical logo but the task is not explicitly a brand-change task, STOP and report the conflict instead of modifying it.

## Canonical asset workflow

For any item registered as `FROZEN` or `APPROVED`:

1. Resolve its registry entry.
2. Retrieve the canonical source asset/state.
3. Perform the requested operation around that source of truth.
4. Validate the output against the canonical reference.
5. Reject the result if canonical identity drifted.

A generated resemblance is not equivalent to a canonical asset.

## Change scope

Treat explicit Director approval as the authority required to supersede a frozen canonical item. A casual page-edit request is not permission to alter global brand identity.

When an intentional canonical revision is approved, update the canonical asset, its registry/hash, documentation, shared component references, and affected tests in the same reviewed change.

## Required validation

Before completing any UI or brand-affecting change:

- confirm the canonical logo resolves from `assets/brand/nexkosmo-x-star.svg`;
- run `python scripts/verify_canonical_assets.py`;
- confirm no page-specific replacement logo was introduced;
- confirm only explicitly requested canonical changes were made.

CI also runs the canonical-asset verifier. A failed canonical check is a release blocker, not a warning.

## Product intelligence distinction

Sophia (or another selected AI Producer) is the Director-facing collaboration/personality layer. Brain is the underlying intelligence/status/health layer. Do not turn Brain into a competing chat persona.

## Product journey

The shared stage model is:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY`

Preserve this shared shell and canonical brand identity unless an explicit product decision supersedes them.
