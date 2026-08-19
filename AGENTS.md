# Nexkosmo Repository Instructions for Codex and AI Engineering Agents

These instructions apply to the entire repository.

## Alignment authority

Alignment is a repository and evidence property, not a memory property.

Before significant architecture, product, UI, implementation, or defect-repair work:

1. Read this file.
2. Read `governance/alignment-manifest.yaml` and report its manifest version.
3. Read `docs/CURRENT_STATE.md`.
4. Read `docs/ALIGNMENT_PROTOCOL.md`.
5. Read `docs/ERROR_CORRECTION_PROTOCOL.md` for significant defect, failure, regression, or repair work.
6. Read `docs/ENGINEERING_STATUS.md`.
7. Read `docs/REPOSITORY_PROTECTION.md`.
8. Read the relevant approved records under `docs/decisions/` and the relevant architecture/product specifications.
9. Inspect current implementation when the request depends on implementation reality.
10. Compare the working branch with current `main` when freshness matters.
11. Resolve contradictions before changing code. STOP instead of guessing when the conflict affects canon, authority, data ownership, security, workflow, architecture boundaries, deployment identity, or data integrity.

Conversational memory, prompt history, screenshots, mockups, estimates, and AI confidence are not higher authority than current repository canon.

## Alignment manifest

`governance/alignment-manifest.yaml` is the machine-readable identity of the current Agent Alignment and Agent Error Correction contract. It points to authoritative repository sources, canonical flows, required decision records, fail-closed domains, verifier requirements, error-correction rules, and future build/runtime attestation contracts.

The manifest does not replace the underlying source documents. It makes their current identity and required relationships machine-checkable.

Every engineering agent must report the manifest version it is following. A stale or conflicting manifest version is a STOP condition until reconciled.

For critical domains listed in the manifest, `UNKNOWN` is not permission to continue. Consequential work must fail closed until authoritative evidence is available.

## Visible engineering health

`docs/ENGINEERING_STATUS.md` is the shared human-readable health projection for the Director, ChatGPT, Codex, and other authorized engineering participants. It must expose alignment, repository, CI, runtime, context, token usage, Estimate Costings, and Project Estimate using evidence-backed values.

The status page is a projection, not a new source of truth. `UNKNOWN` must remain unknown until evidence exists. Never invent token counts, runtime identity, cost, or alignment success to make the status appear complete.

Human-facing status is presented vertically, one result per line. Before significant work, report or inspect current status. Before reporting work complete, update the status projection when a material field changed.

## Alignment stewardship

- The Director is the final authority for product direction, canon, and consequential approval.
- ChatGPT acts as alignment steward: retrieve current repository state, compare new work against canon, detect drift, challenge contradictions, and keep Codex and documentation pointed in the same approved direction.
- Codex is an implementation agent. It must implement approved direction and must not treat stale branches, mockups, or prototype navigation as current canon.
- No AI may promote its own recommendation to canon without explicit Director approval.
- CI/tests are deterministic evidence gates. They do not define product direction and must not certify themselves as authority.

## Agent error correction

`docs/ERROR_CORRECTION_PROTOCOL.md` is the independent engineering correction path for ChatGPT and Codex.

This path is separate from the Nexkosmo Brain:

- ChatGPT provides independent engineering oversight, evidence review, defect classification, root-cause challenge, and verification review.
- Codex reproduces, implements, tests, and repairs against current repository contracts.
- CI/tests provide independent deterministic evidence.
- Brain may later consume validated defect/recovery records as external evidence, but Brain is not the sole detector, verifier, repair authority, or correction record for ChatGPT/Codex defects.

For significant defects:

1. preserve evidence before repair;
2. classify severity and defect class;
3. reproduce when practical or explicitly report `NOT_REPRODUCED`;
4. separate symptom, trigger, causal defect, and systemic contributor;
5. add regression proof where practical;
6. make the minimum safe causal repair;
7. run all relevant validation families;
8. do not claim runtime recovery without runtime evidence;
9. use accurate intermediate states such as `FIXED_IN_CODE` or `VERIFIED_IN_CI` until later proof exists.

Codex must not weaken/delete failing tests merely to make CI green. A failing test may be corrected only when the test itself is proven defective and the intended contract remains preserved or strengthened.

ChatGPT must not declare a defect fixed solely because Codex says so. Independent evidence is required.

## Independent drift verification

Nexkosmo uses complementary verification rather than relying on one detector:

1. deterministic repository/CI checks;
2. deliberate drift-injection tests that prove known drift cases are rejected;
3. fresh-context semantic reconstruction at important milestones;
4. future runtime/build attestation once Server 1/Server 2 awareness is connected.

If deterministic and semantic verification materially disagree, block consequential continuation and reconcile the evidence rather than choosing whichever result is convenient.

Run these governance checks before treating significant work as aligned:

- `python scripts/verify_canonical_assets.py`
- `python scripts/verify_alignment.py`
- `python scripts/verify_drift_guards.py`

Deliberate drift tests are proof of detection only for their tested cases. They must not be described as universal or bulletproof proof.

## Repository protection

`main` must be protected according to `docs/REPOSITORY_PROTECTION.md`.

Before treating a significant PR as merge-ready:

- confirm the `quality-and-integration` CI job is green;
- confirm GitHub reports `main` as protected;
- confirm required review/conversation settings match the current owner/team model;
- do not rely on `CODEOWNERS` or written policy alone as proof that GitHub is enforcing the rule.

If `main` is not protected, treat that as a governance STOP GATE rather than silently merging around it.

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
6. Discovery, Shape, Build, Ready, Production, Studio, onboarding, account, collaboration, and future product surfaces must resolve the same canonical logo asset.
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

When an intentional canonical revision is approved, update the canonical asset, its registry/hash, documentation, shared component references, affected decision/current-state records, the alignment manifest where applicable, and affected tests in the same reviewed change.

## Required validation

Before completing any UI or brand-affecting change:

- confirm the canonical logo resolves from `assets/brand/nexkosmo-x-star.svg`;
- run `python scripts/verify_canonical_assets.py`;
- run `python scripts/verify_alignment.py`;
- run `python scripts/verify_drift_guards.py` for significant governance/canon changes;
- confirm no page-specific replacement logo was introduced;
- confirm only explicitly requested canonical changes were made;
- confirm the implementation does not contradict `docs/CURRENT_STATE.md` or `governance/alignment-manifest.yaml`.

CI treats failed canonical, alignment, drift-guard, repository-protection, or integration checks as release blockers, not warnings.

## Product intelligence distinction

Sophia (or another selected AI Producer) is the Director-facing relationship and collaboration layer. Brain is Nexkosmo's underlying intelligence/status/health layer. Do not turn Brain into a competing chatbot.

## Product entry and creative workflow

Do not collapse onboarding/account entry, creative workflow, and Production/Studio deep editing into one ambiguous flow.

Normal new-project entry:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> IDEA`

Alternate screenplay-import entry:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`

Canonical creative workflow:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

Studio is not another top-level stage. Production is the movie-wide control room; Studio is the contextual precision scene/shot editor opened from Production. Returning from Studio sends edited work back through Brain validation before production approval.

The legacy prototype navigation `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded. It may remain temporarily in an unmerged prototype branch for reconciliation, but it is not current product canon and must not be merged unchanged.

Preserve this shared shell and canonical brand identity unless an explicit Director-approved decision supersedes them.

## Project state and fixtures

Do not hard-code project-specific state into production UI/data paths as though it were canonical truth. Characters, scenes, shots, Producer selection, canonical asset selections, approvals, continuity, validation results, render state, production progress, and project-specific AI recommendations must resolve from explicit project/application state contracts and persistence.

Demo fixtures are allowed only when isolated and clearly labelled. Do not invent backend APIs merely to make a prototype appear complete.

## Pull-request contract

Significant PRs must use the repository PR template and identify:

- the alignment-manifest version followed;
- the approved decision/specification implemented;
- affected current-state sections;
- canonical assets/state touched;
- fixture/hard-coded project data added or removed;
- deterministic and drift-injection validation performed;
- for defect repairs: defect ID/status, reproduction status, root-cause evidence, regression proof, repair commit, CI verification, runtime verification where applicable;
- known placeholders, estimates, inferences, unknowns, or conflicts.

If a change intentionally modifies canon, include the Director-approved decision record, `docs/CURRENT_STATE.md` update, and any necessary manifest revision in the same reviewed change.
