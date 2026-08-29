# DEC-0002: Production and Studio Boundary

Status: APPROVED
Date: 2026-08-19
Authority: Director

## Context

Earlier prototypes treated Studio as part of a linear workflow. The approved product model now distinguishes project-wide production orchestration from precision editing of the production unit currently being worked on.

Film, animation, commercial, and music-video projects may commonly use Sequence -> Scene -> Shot. Games, interactive experiences, 3D/VFX work, and future production formats may use other format-appropriate structures such as levels, encounters, cinematics, clips, assets, simulations, passes, or other approved production units. Nexkosmo must not force every production format into movie-only vocabulary or structure.

## Decision

- PRODUCTION is the project-wide production control room.
- Studio is the deep precision editing workspace opened contextually from Production for the selected format-appropriate production unit.
- For film-oriented profiles, that unit is commonly a scene or shot.
- Studio is not a competing top-level product stage.
- Returning from Studio sends the edited production unit back through Brain validation before approval.

## Director-facing responsibilities

PRODUCTION should expose status, progress, the current format-appropriate production unit, validation, compare/repair/approve actions, simplified render/compute route/cost/time/status, and access to Studio.

Studio should expose precision controls appropriate to the active format and unit, including where relevant characters, camera, dialogue, performance, music, sound effects, lighting, VFX, layers, timeline, properties, assets, simulations, interactions, and other specialist production controls.

## Constraints

- Studio must receive project identity plus the explicit format-appropriate production-unit, canonical-state, dependency, and continuity/state context required for the work.
- Studio must not silently own or fork canonical truth.
- Production must not become an infrastructure dashboard for worker/queue internals.
- Infrastructure details may exist behind advanced/render-details surfaces.
- Format-specific terminology and hierarchy may vary, but the authority, validation, provenance, and return-to-Production boundary must remain consistent.

## Validation

For a film-oriented production profile, a user must be able to follow:

`READY -> Start Production -> select scene/shot -> Open in Studio -> edit -> Save & Return -> revalidate -> approve`.

Equivalent format-aware flows must preserve the same boundary:

`READY -> Start Production -> select production unit -> Open in Studio -> edit -> Save & Return -> revalidate -> approve`.
