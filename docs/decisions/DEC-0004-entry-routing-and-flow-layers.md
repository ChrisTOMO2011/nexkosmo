# DEC-0004: Entry Routing and Flow Layers

Status: APPROVED
Date: 2026-08-19
Authority: Director

## Context

The six-stage creative workflow was being described as though it were the entire user journey. That creates ambiguity around onboarding, AI Producer selection, project creation, screenplay import, and the contextual Production/Studio edit loop.

## Decision

Nexkosmo has three distinct flow layers.

### Full user entry journey

Normal new-project entry:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> IDEA`

Alternate screenplay-import entry:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`

The selected AI Producer persists as the Director-facing collaborator unless the Director explicitly changes the selection.

Imported scripts retain source provenance and are not silently rewritten or treated as AI-authored work.

### Creative workflow

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

### Production deep-edit loop

`PRODUCTION -> select scene/shot -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

Studio is not a seventh top-level stage.

## Consequences

- Onboarding/account entry, creative progression, and Studio deep editing must not be collapsed into one ambiguous navigation model.
- Users importing an existing screenplay are not forced through IDEA or DISCOVER simply to reach SHAPE.
- The legacy prototype progression `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded as product-navigation canon.
- Existing prototype code may be preserved for reconciliation and reuse, but obsolete navigation assumptions must not be merged unchanged.
- Alignment checks and fresh-context tests must distinguish the full entry journey from the creative workflow.

## Validation

A fresh agent reading the repository should be able to state the normal entry route, the screenplay-import route, the six-stage creative workflow, and the Production/Studio editing loop without relying on conversation history.
