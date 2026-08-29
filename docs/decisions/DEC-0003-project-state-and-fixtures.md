# DEC-0003: Project State and Fixtures

Status: APPROVED
Date: 2026-08-19
Authority: Director

## Context

Prototype frontend work currently contains fixed characters, fixed character attributes, local-only state, and workflow assumptions. Those are acceptable as isolated fixtures during prototyping but unsafe if they masquerade as production truth.

## Decision

Project-specific state must come from explicit project/application state contracts and persistence. It must not be hidden in production UI constants.

Examples include characters, attributes, scenes, shots, levels, encounters, clips, assets, simulations, passes, other format-appropriate production units, Producer selection, story/design/interaction state, canonical asset selections, validation results, approvals, continuity/state, render/compute status/cost/time, production progress, and project-specific AI recommendations.

Demo data is permitted only when:

- it is isolated in fixture/demo locations;
- it is clearly labelled as fixture data;
- production code cannot silently treat it as canonical project state;
- tests make the boundary visible.

## Consequences

- Existing prototype values such as fixed character names, default character IDs, age/height/body type, fixed scene/shot assumptions, or local-only additions must not become the real data layer.
- UI work may continue with fixtures while backend contracts are developed, but the fixture boundary must be explicit.
- Codex must not invent fake backend APIs solely to make screens appear complete.
- The first film-oriented vertical slice must not hard-code movie-only semantics into project contracts that are intended to support other production formats.

## Validation

Alignment checks should detect obvious prototype project identifiers or unjustified format-specific constants in production-path frontend source and require an explicit fixture boundary, format-profile contract, or approved exception.
