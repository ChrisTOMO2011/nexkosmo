# DEC-0001: Canonical Product Journey

Status: APPROVED
Date: 2026-08-19
Authority: Director

## Context

Earlier repository guidance documented a five-stage journey ending at READY. Product design subsequently established a distinct project-wide Production control room followed by contextual deep editing in Studio.

Nexkosmo supports multiple production formats. Film-oriented projects commonly use sequence/scene/shot structure, while games, interactive experiences, 3D/VFX, animation, commercials, music videos, asset production, simulations, and future formats may use different production-unit hierarchies. The shared journey must therefore remain format-general even when the first implemented profile is film-oriented.

## Decision

The canonical shared journey is:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

Studio is not a seventh top-level stage.

The six stages describe shared creative responsibility, not mandatory movie-specific internal vocabulary.

## Consequences

- Shared navigation and product documentation must use the six-stage journey.
- Existing frontend code using older `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` assumptions is prototype-era implementation and must be reconciled before production adoption.
- READY ends with a production-readiness decision and `Start Production` action when mandatory blockers pass.
- PRODUCTION owns project-wide orchestration, execution/render/compute status, validation, repair, comparison, and approval flow for format-appropriate production units.
- Precision editing opens contextually in Studio from Production for the selected production unit and its canonical/dependency/continuity-state context.
- Film-oriented profiles may expose scenes and shots; other profiles must be free to expose appropriate units such as levels, encounters, cinematics, clips, assets, simulations, passes, or future approved structures.
- Nexkosmo must not force every production type into movie-only hierarchy merely because a current prototype or first vertical slice is film-oriented.

## Supersedes

Any earlier shared journey definition that ends at READY, treats Studio as an equivalent top-level progression stage, or treats movie-specific scene/shot vocabulary as the universal Nexkosmo production model.

## Validation

Alignment checks must confirm that current-state and agent instructions contain the six-stage journey, preserve the Production/Studio boundary, and retain a format-general production-unit model.
