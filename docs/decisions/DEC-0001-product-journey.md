# DEC-0001: Canonical Product Journey

Status: APPROVED
Date: 2026-08-19
Authority: Director

## Context

Earlier repository guidance documented a five-stage journey ending at READY. Product design subsequently established a distinct movie-wide Production control room followed by contextual deep editing in Studio.

## Decision

The canonical shared journey is:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

Studio is not a seventh top-level stage.

## Consequences

- Shared navigation and product documentation must use the six-stage journey.
- Existing frontend code using older `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` assumptions is prototype-era implementation and must be reconciled before production adoption.
- READY ends with a production-readiness decision and `Start Production` action when mandatory blockers pass.
- PRODUCTION owns movie-wide scene/shot orchestration, rendering status, validation, repair, comparison, and approval flow.
- Precision scene/shot editing opens contextually in Studio from Production.

## Supersedes

Any earlier shared journey definition that ends at READY or treats Studio as an equivalent top-level progression stage.

## Validation

Alignment checks must confirm that current-state and agent instructions contain the six-stage journey and the Production/Studio boundary remains explicit.
