# Nexkosmo Repository Instructions for Codex and AI Engineering Agents

These instructions apply to the entire repository.

## Alignment authority

Alignment is a repository and evidence property, not a memory property.

Before significant architecture, product, UI, or implementation work:

1. Read this file.
2. Read `docs/CURRENT_STATE.md`.
3. Read `docs/ALIGNMENT_PROTOCOL.md`.
4. Read `docs/ENGINEERING_STATUS.md`.
5. Read `docs/REPOSITORY_PROTECTION.md`.
6. Read the relevant approved records under `docs/decisions/` and the relevant architecture/product specifications.
7. Inspect current implementation when the request depends on implementation reality.
8. Resolve contradictions before changing code. STOP instead of guessing when the conflict affects canon, authority, data ownership, workflow, or architecture boundaries.

Conversational memory, prompt history, screenshots, mockups, estimates, and AI confidence are not higher authority than current repository canon.

## Visible engineering health

`docs/ENGINEERING_STATUS.md` is the shared human-readable health projection for the Director, ChatGPT, Codex, and other authorized engineering participants. It must expose alignment, repository, CI, runtime, context, and AUD cost state using evidence-backed values.

The status page is a projection, not a new source of truth. `UNKNOWN` must remain unknown until evidence exists. Never invent token counts, runtime identity, cost, or alignment success to make the status appear complete.

Before significant work, report or inspect the current status line. Before reporting work complete, update the status projection when a material field changed.

## Alignment stewardship

- The Director is the final authority for product direction, canon, and consequential approval.
- ChatGPT acts as alignment steward: retrieve current repository state, compare new work against canon, detect drift, challenge contradictions, and keep Codex and documentation pointed in the same approved direction.
- Codex is an implementation agent. It must implement approved direction and must not treat stale branches, mockups, or prototype navigation as current canon.
- No AI may promote its own recommendation to canon without explicit Director approval.

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

When an intentional canonical revision is approved, update the canonical asset, its registry/hash, documentation, shared component references, affected decision/current-state records, and affected tests in the same reviewed change.

## Required validation

Before completing any UI or brand-affecting change:

- confirm the canonical logo resolves from `assets/brand/nexkosmo-x-star.svg`;
- run `python scripts/verify_canonical_assets.py`;
- run `python scripts/verify_alignment.py`;
- confirm no page-specific replacement logo was introduced;
- confirm only explicitly requested canonical changes were made;
- confirm the implementation does not contradict `docs/CURRENT_STATE.md`.

CI treats failed canonical, alignment, repository-protection, or integration checks as release blockers, not warnings.

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

- the approved decision/specification implemented;
- affected current-state sections;
- canonical assets/state touched;
- fixture/hard-coded project data added or removed;
- validation performed;
- known placeholders, estimates, inferences, unknowns, or conflicts.

If a change intentionally modifies canon, include the Director-approved decision record and `docs/CURRENT_STATE.md` update in the same reviewed change.
