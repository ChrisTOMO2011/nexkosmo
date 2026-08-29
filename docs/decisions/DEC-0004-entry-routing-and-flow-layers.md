# DEC-0004: Entry Routing and Flow Layers

Status: APPROVED
Date: 2026-08-19
Authority: Director

## Context

The six-stage creative workflow was being described as though it were the entire user journey. That creates ambiguity around onboarding, AI Producer selection, project creation, format-specific imports, and the contextual Production/Studio edit loop.

## Decision

Nexkosmo has three distinct flow layers.

### Full user entry journey

Normal new-project entry:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> IDEA`

Existing source material may use an approved import shortcut appropriate to the production format. For screenplay-based work:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`

The selected AI Producer persists as the Director-facing collaborator unless the Director explicitly changes the selection.

Imported source material retains provenance and is not silently rewritten or treated as AI-authored work.

### Creative workflow

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

The shared stages remain format-general. Their internal structures and terminology adapt to the production format rather than requiring every project to use movie-specific semantics.

### Production deep-edit loop

General form:

`PRODUCTION -> select production unit -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

A film-oriented profile may present:

`PRODUCTION -> select scene/shot -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

Other formats use equivalent approved production units such as levels, encounters, cinematics, clips, assets, simulations, passes, or future format-specific structures.

Studio is not a seventh top-level stage.

## Consequences

- Onboarding/account entry, creative progression, and Studio deep editing must not be collapsed into one ambiguous navigation model.
- Users importing existing source material are not forced through IDEA or DISCOVER merely to reach an approved format-specific entry point.
- Screenplay import remains a supported film-oriented shortcut, not a universal requirement for every Nexkosmo project.
- The legacy prototype progression `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded as product-navigation canon.
- Existing prototype code may be preserved for reconciliation and reuse, but obsolete navigation or movie-only architecture assumptions must not be merged unchanged.
- Alignment checks and fresh-context tests must distinguish the full entry journey from the creative workflow and must preserve the format-general Production/Studio boundary.

## Validation

A fresh agent reading the repository should be able to state the normal entry route, explain that imports are format-specific, identify the screenplay-import route as one supported profile, state the six-stage creative workflow, and describe the format-general Production/Studio editing loop without relying on conversation history.
