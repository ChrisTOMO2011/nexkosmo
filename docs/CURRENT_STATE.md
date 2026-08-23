# Nexkosmo Current State

Status: CANONICAL CURRENT-STATE SNAPSHOT
Owner: Director
Alignment steward: ChatGPT
Last updated: 2026-08-19

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

- The repository contains the Brain/backend foundation, architecture documents, canonical asset enforcement, and CI.
- The existing Studio frontend work remains a draft branch/PR and includes prototype local state and fixtures.
- That frontend predates the current six-stage creative workflow, the full-entry routing clarification, and the current Production/Studio boundary.
- Therefore it must be reconciled with this state before becoming the production UI foundation.
- Preserve reusable layout/components that remain compatible; do not delete useful prototype work merely because its navigation assumptions are obsolete.
- Do not infer that a designed screen, mockup, placeholder route, or documented architecture is already implemented end-to-end.

## Current engineering priority

ALIGNMENT STOP GATE.

Before major new feature construction:

1. Reconcile active Codex/frontend work with current `main` and this approved alignment branch once merged.
2. Replace obsolete workflow assumptions with the approved full-entry routing and six-stage creative workflow.
3. Preserve reusable frontend components where they remain compatible.
4. Remove project-specific prototype hard-coding from production data paths.
5. Wire UI state to canonical project contracts incrementally rather than inventing fake backend APIs.
6. Keep canonical asset and alignment checks passing.
7. Prove one end-to-end new-project vertical slice before expanding breadth:
   `Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION -> Open in Studio -> edit -> revalidate -> approve`.
8. Prove the alternate screenplay-import entry separately:
   `Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`.

## Change rule

Any change that contradicts this file must either:

- be rejected as drift, or
- include an explicit Director-approved decision record that intentionally supersedes the affected section and updates this file in the same reviewed change.

Conversation alone does not supersede repository canon.
