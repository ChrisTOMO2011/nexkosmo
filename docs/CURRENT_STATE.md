# Nexkosmo Current State

Status: CANONICAL CURRENT-STATE SNAPSHOT
Owner: Director
Alignment steward: ChatGPT
Last updated: 2026-08-29

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

A user with existing source material may use an alternate import entry appropriate to the production format. For screenplay-based work, the approved shortcut is:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`

Imported source material must retain provenance and must not be silently rewritten or treated as AI-authored material. The user is not forced through IDEA or DISCOVER merely to import existing source material when a format-specific approved shortcut exists.

## Creative workflow

The canonical shared creative progression is:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

This is the shared creative workflow, not the entire account/onboarding/project lifecycle and not a requirement that every production format use movie-specific terminology internally.

Definitions:

- IDEA: establish what the Director wants to create.
- DISCOVER: explore what the project could become through a visual planning surface appropriate to the format.
- SHAPE: define structure, story, design, interaction, timing, or other project-specific composition requirements.
- BUILD: create and approve the characters, environments, props, wardrobe, vehicles, assets, systems, and other production resources required by the project.
- READY: preflight structure, assets, continuity/state, rights/provenance, and production planning. Production cannot start while mandatory blockers remain.
- PRODUCTION: project-wide control room for making, validating, repairing, comparing, and approving format-appropriate production units.

Film, animation, commercial, and music-video profiles may commonly use Sequence -> Scene -> Shot. Games, interactive experiences, 3D/VFX work, and future production formats may use other approved structures such as levels, encounters, cinematics, clips, assets, simulations, passes, or other production units. Nexkosmo must not force every project into movie-only vocabulary or hierarchy.

The legacy prototype progression `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded as a product-navigation model. It may remain temporarily inside unmerged prototype code for reconciliation evidence, but it must not be treated as current canon or merged unchanged into production UI.

## Production and Studio boundary

Studio is not an additional top-level journey stage.

- PRODUCTION is the project-wide control room. It answers: what is running, what is complete, what is blocked, what needs review, and what decision is required next?
- Studio is the precision editing workspace for the selected format-appropriate production unit. For film-oriented profiles, this is commonly a scene or shot.
- Normal navigation is `READY -> Start Production -> PRODUCTION -> select production unit -> Open in Studio`.
- Studio opens with explicit project, selected production-unit, canonical-state, dependency, and continuity/state context. It must not open as a blank unrelated workspace.
- Returning from Studio must return the edited work to Production for Brain revalidation before approval.

The general production deep-edit loop is:

`PRODUCTION -> select production unit -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

A film-oriented profile may present this as:

`PRODUCTION -> select scene/shot -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

## Production Assurance and render economics

`docs/decisions/DEC-0005-production-assurance-and-render-cost-attribution.md` defines the approved Production Assurance direction.

- READY does not mean production can never change. Approved production state establishes the baseline from which downstream dependency validity is measured.
- Render/compute execution must originate from validated, versioned state and preserve the distinction between a Nexkosmo-caused production failure and a new Director-authorised creative revision.
- Nexkosmo shall not treat every consumed machine cycle as automatically customer-billable.
- Material production accounting must keep **Actual Production Cost**, **Customer-Billable Cost**, and **Nexkosmo Assurance Cost** distinct. Recovered/reused work may be tracked separately when supported by defensible evidence.
- A Nexkosmo-caused failure to conform to the approved production contract basis must not silently become a customer-billable retry merely because compute was consumed.
- A Director change after conforming work is delivered is new authorised production work rather than a Nexkosmo failure.
- The Render Orchestrator must preserve accepted work and identify the smallest valid re-execution scope when dependencies permit.
- Production Assurance is not permission for unbounded retries. Repeated materially similar failures require evidence-based containment, route/renderer/model/task reconsideration, and lower-cost proof where practical before expensive continuation.
- Validation checkpoints may intentionally consume some compute when they reduce expected downstream loss or expose faults before more expensive continuation. The objective is minimum expected wasted production cost, not simply the fewest checkpoints or minimum raw GPU minutes.
- Large productions should be orchestrated as one creative whole but executed in the smallest practical independently validatable and recoverable units appropriate to the production format.
- A project-wide Render/Build/Produce command is an orchestration command, not permission to collapse the whole project into one indivisible execution job.
- Coverage before completion is permitted and encouraged where it reduces risk: obtain enough lower-cost evidence across the relevant production scope to expose systemic faults before committing heavily to deep completion of isolated units.
- The Brain/Orchestrator may reduce or stop delegated execution when risk rises, but cannot increase its own budget, compute ceiling, or material-spend authority.
- Nexkosmo shall not impose an arbitrary architectural render-count limit per production unit. Execution remains subject to credits/resources, project budget, safety/resource ceilings, and Director material-spend authority.
- A public `100% guarantee` remains a planned commercial promise until billing, attribution, ledger, recovery, runtime evidence, customer terms, and applicable legal review support the exact claim. Product truth and claims assurance apply.

The existing Render Manifest remains the execution contract for renderable work; Production Assurance does not create a competing truth store or duplicate manifest.

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
- Renderers, engines, models, simulators, and other production tools are replaceable execution tools; they do not own canon.
- Production acceptance requires evidence and validation appropriate to the work.
- Facts, approved decisions, observations, inferences, estimates, hypotheses, and unknowns must remain distinguishable.

## Project data and hard-coding

Production code must not encode project-specific state as if it were canonical state.

Examples of project state that must come from project state/API/fixtures with explicit provenance rather than hidden UI constants include:

- characters and character attributes;
- scenes, shots, levels, clips, encounters, assets, simulations, or other format-appropriate production units;
- selected Producer;
- approved canonical assets;
- story, design, interaction, or structure state;
- continuity/state;
- validation results;
- approvals;
- render/compute cost/time/status;
- production progress;
- AI recommendations tied to a real project.

Demo fixtures are allowed only when clearly isolated and labelled as fixtures. Fixtures must not masquerade as production truth.

## Current implementation reality

- The repository contains the Brain/backend foundation, architecture documents, canonical asset enforcement, and CI.
- The existing Studio frontend work remains a draft branch/PR and includes prototype local state and fixtures.
- That frontend predates the current six-stage creative workflow, the full-entry routing clarification, the current Production/Studio boundary, and the format-general production clarification.
- Therefore it must be reconciled with this state before becoming the production UI foundation.
- Preserve reusable layout/components that remain compatible; do not delete useful prototype work merely because its navigation assumptions are obsolete.
- Do not infer that a designed screen, mockup, placeholder route, or documented architecture is already implemented end-to-end.
- Production Assurance, financial attribution, intelligent render checkpoints, format-general granular execution, and bounded assurance recovery are approved design/canon but are not yet verified end-to-end runtime capabilities.

## Current engineering priority

ALIGNMENT STOP GATE.

Before major new feature construction:

1. Reconcile active Codex/frontend work with current `main` and this approved alignment branch once merged.
2. Replace obsolete workflow assumptions with the approved full-entry routing and six-stage creative workflow.
3. Preserve reusable frontend components where they remain compatible.
4. Remove project-specific prototype hard-coding from production data paths.
5. Wire UI state to canonical project contracts incrementally rather than inventing fake backend APIs.
6. Keep canonical asset and alignment checks passing.
7. Prove one end-to-end new-project vertical slice before expanding breadth. The first profile may be film-oriented, but the architecture must preserve format-general production-unit contracts rather than hard-code movie-only semantics.
8. Prove the alternate screenplay-import entry separately for the film-oriented profile:
   `Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`.

## Change rule

Any change that contradicts this file must either:

- be rejected as drift, or
- include an explicit Director-approved decision record that intentionally supersedes the affected section and updates this file in the same reviewed change.

Conversation alone does not supersede repository canon.
