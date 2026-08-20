# Nexkosmo Current State

Status: CANONICAL CURRENT-STATE SNAPSHOT
Owner: Director
Alignment steward: ChatGPT
Last updated: 2026-08-20

This file is the compact authoritative snapshot of Nexkosmo's current approved direction. It is intentionally smaller than the full architecture documentation. Detailed specifications remain in their dedicated documents.

## Authority order

When sources conflict, use this order:

1. Explicit Director approval recorded in the repository.
2. This current-state snapshot and approved decision records.
3. Verified tests, evidence, and canonical registries.
4. Architecture and product specifications.
5. Current implementation.
6. AI inference, conversational memory, mockups, estimates, and hypotheses.

AI confidence is never authority by itself. The alignment steward is responsible for detecting drift and keeping the repository, ChatGPT, and Codex pointed at the same approved direction, but cannot supersede Director authority or independently approve canon.

## Full user journey

The complete entry journey is distinct from the creative workflow.

Normal new-project entry:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> IDEA`

The selected AI Producer persists as the Director-facing collaborator through the project unless the Director explicitly changes that selection.

A user with an existing screenplay may use the alternate entry:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`

Imported source material must retain provenance and must not be silently rewritten or treated as AI-authored material. The user is not forced through IDEA or DISCOVER simply to import an existing screenplay.

## Creative workflow

The canonical shared creative progression is:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

This is the creative workflow, not the entire account/onboarding/project lifecycle.

Definitions:

- IDEA: establish what the Director wants to create.
- DISCOVER: explore what the story could become through a visual Movie Map.
- SHAPE: define the story and screenplay, with synchronized screenplay and layered scene-timeline views.
- BUILD: create and approve the characters, environments, props, wardrobe, vehicles, and other production assets required by the story.
- READY: preflight story, assets, continuity, rights/provenance, and production planning. Production cannot start while mandatory blockers remain.
- PRODUCTION: movie-wide control room for making, validating, repairing, comparing, and approving scenes and shots.

The legacy prototype progression `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded as a product-navigation model. It may remain temporarily inside unmerged prototype code for reconciliation evidence, but it must not be treated as current canon or merged unchanged into production UI.

## Production and Studio boundary

Studio is not an additional top-level journey stage.

- PRODUCTION is the movie-wide control room. It answers: what is running, what is complete, what is blocked, what needs review, and what decision is required next?
- Studio is the precision scene/shot editing workspace. It answers: what exactly should change in this scene or shot?
- Normal navigation is `READY -> Start Production -> PRODUCTION -> select scene/shot -> Open in Studio`.
- Studio opens with explicit project, scene, shot, canonical asset, timeline, and continuity context. It must not open as a blank unrelated workspace.
- Returning from Studio must return the edited work to Production for Brain revalidation before approval.

The production deep-edit loop is:

`PRODUCTION -> select scene/shot -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

## Human and AI authority

- The human user is the Director and retains final creative and consequential authority unless explicitly delegated.
- The selected AI Producer is the Director-facing collaboration/personality layer.
- Brain is the underlying intelligence, state, evidence, continuity, reasoning, and health layer. Brain must not become a competing chat persona.
- ChatGPT acts as alignment steward for the development process: retrieve current repository state, detect contradictions, challenge drift, and keep Codex work pointed at approved canon. This stewardship does not grant authority to approve or rewrite canon without Director approval.
- Codex is an implementation agent. It implements approved direction and must not infer a new product direction from stale branches, screenshots, or prototype structure.
- AI recommendations may propose, challenge, explain, simulate, or optimize, but cannot silently promote themselves to approved canon.

## Canon and truth

- Retrieve before generate.
- Approved canonical assets and approved project state are retrieved by default.
- New AI-generated material remains draft/proposed until explicitly approved.
- Renderers are replaceable execution tools; they do not own canon.
- Production acceptance requires evidence and validation appropriate to the work.
- Facts, approved decisions, observations, inferences, estimates, hypotheses, and unknowns must remain distinguishable.

## Project data and hard-coding

Production code must not encode project-specific state as if it were canonical state.

Examples of project state that must come from project state/API/fixtures with explicit provenance rather than hidden UI constants include:

- characters and character attributes;
- scenes and shots;
- selected Producer;
- approved canonical assets;
- story state and script state;
- continuity state;
- validation results;
- approvals;
- render cost/time/status;
- production progress;
- AI recommendations tied to a real project.

Demo fixtures are allowed only when clearly isolated and labelled as fixtures. Fixtures must not masquerade as production truth.

## Current implementation reality

- The trusted governance baseline is branch `governance/alignment-system` at commit
  `e34d2aaba4cda1aa9563242edc3df48b230833f7`. It contains the approved governance,
  Brain/backend foundation, architecture documents, canonical asset enforcement and
  CI evidence used for controlled migration review.
- The preserved candidate source is branch
  `candidate/preserve-nexkosmo-inspection-2026-08-20` at commit
  `c26ee95fccc34891d514dcb528684698d933f758`, recorded under preservation digest
  `585CED3089C167A55A09D01E408C81A2BD668734204F53763EB288E6BB3B59BF`.
- The candidate contains substantial frontend, Project, Character, Environment,
  adapter, migration, test and infrastructure capability source. Presence on that
  branch is evidence for review, not proof that those capabilities are implemented,
  approved, migrated or production-ready in the trusted baseline.
- Candidate frontend work includes prototype local state, fixtures, obsolete routing
  assumptions, page-specific branding, and unresolved Production/Studio boundaries.
  Reusable capability may be extracted only through independently approved migration
  slices.
- Candidate migrations `0003-0011` have not been approved or executed wholesale.
  The controlled lineage independently replaced candidate Project/Production work
  with trusted migration `0003_project_authority`; approved Slice 4 now validates a
  new minimal `0004_character_foundation` rather than promoting candidate schema,
  catalogues, seeds, grants, or policies.
- Preserve reusable layout/components and all useful legacy Set, Studio, CGI, VFX,
  Render and Pre-Production capability source. Do not delete useful prototype work
  merely because its navigation assumptions are obsolete.
- Do not infer that a candidate file, designed screen, mockup, placeholder route,
  test, migration or documented architecture is implemented end-to-end in the
  trusted baseline.

## Controlled migration state

Director-approved controlled slices now form this reviewed lineage:

- Slice 1 reconciles governance/current state and records candidate provenance.
- The maintenance checkpoint fixes verifier portability and protection-status docs.
- Slice 2 introduces the canonical shared frontend shell without frontend Brain
  authority.
- Slice 3B implements the canonical Workspace -> Project -> Production authority
  foundation through `DEC-0005` and migration `0003_project_authority`.
- Slice 4 is the active, uncommitted implementation review for the minimal
  Project-owned Character foundation defined by `DEC-0006`.

Slice 4 does not promote candidate catalogues, assets, compatibility/readiness,
frontend Character authority, or Production-specific Character state. All later
slices remain blocked pending separate Director approval. Candidate ADRs, roadmaps,
architecture maps and implementation-status documents remain evidence only.

## Current engineering priority

CONTROLLED MIGRATION STOP GATE. The existing status remains: ALIGNMENT STOP GATE.

Before candidate implementation is extracted:

1. Complete and validate Slice 4 on the approved branch and 20-file allowlist,
   stopping before commit for Director review.
2. Require separate Director approval for the exact files and controls of every
   later migration slice. Do not merge the candidate branch wholesale.
3. Replace obsolete workflow assumptions only inside a separately approved slice,
   preserving the approved full-entry routing, six-stage creative workflow and
   contextual Studio boundary.
4. Preserve reusable frontend and legacy capability source where compatible; compare
   before consolidating or retiring it.
5. Remove project-specific prototype hard-coding from production data paths before
   candidate UI can represent canonical project state.
6. Wire UI state to canonical Python/PostgreSQL contracts incrementally rather than
   inventing fake backend APIs or a frontend Brain.
7. Keep canonical asset, alignment, authority, security, latent-defect and repository
   protection checks passing.
8. Do not execute candidate migrations `0003-0011`; controlled replacements require
   separate domain, security, schema, restore and Director gates.
9. Prove one end-to-end new-project vertical slice before expanding breadth:
   `Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION -> Open in Studio -> edit -> revalidate -> approve`.
10. Prove the alternate screenplay-import entry separately:
   `Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`.

## Change rule

Any change that contradicts this file must either:

- be rejected as drift, or
- include an explicit Director-approved decision record that intentionally supersedes the affected section and updates this file in the same reviewed change.

Conversation alone does not supersede repository canon.
