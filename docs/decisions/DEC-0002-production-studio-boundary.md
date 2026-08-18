# DEC-0002: Production and Studio Boundary

Status: APPROVED
Date: 2026-08-19
Authority: Director

## Context

Earlier prototypes treated Studio as part of a linear workflow. The approved product model now distinguishes movie-wide production orchestration from precision scene/shot editing.

## Decision

- PRODUCTION is the movie-wide control room.
- Studio is the deep scene/shot editing workspace opened contextually from Production.
- Studio is not a competing top-level product stage.
- Returning from Studio sends the edited shot/scene back through Brain validation before approval.

## Director-facing responsibilities

PRODUCTION should expose status, progress, current shot/scene, validation, compare/repair/approve actions, simplified render route/cost/time/status, and access to Studio.

Studio should expose precision controls such as characters, camera, dialogue, performance, music, sound effects, lighting, VFX, layers, timeline, and properties.

## Constraints

- Studio must receive project/scene/shot/canonical/continuity context.
- Studio must not silently own or fork canonical truth.
- Production must not become an infrastructure dashboard for worker/queue internals.
- Infrastructure details may exist behind advanced/render-details surfaces.

## Validation

A user must be able to follow:

`READY -> Start Production -> select scene/shot -> Open in Studio -> edit -> Save & Return -> revalidate -> approve`.
