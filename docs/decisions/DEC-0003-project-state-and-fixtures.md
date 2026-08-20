# DEC-0003: Project State and Fixtures

Status: APPROVED
Date: 2026-08-19
Authority: Director

## Context

Prototype frontend work currently contains fixed characters, fixed character attributes, local-only state, and workflow assumptions. Those are acceptable as isolated fixtures during prototyping but unsafe if they masquerade as production truth.

## Decision

Project-specific state must come from explicit project/application state contracts and persistence. It must not be hidden in production UI constants.

Examples include characters, attributes, scenes, shots, Producer selection, story state, canonical asset selections, validation results, approvals, continuity state, render status/cost/time, production progress, and project-specific AI recommendations.

Demo data is permitted only when:

- it is isolated in fixture/demo locations;
- it is clearly labelled as fixture data;
- production code cannot silently treat it as canonical project state;
- tests make the boundary visible.

## Consequences

- Existing prototype values such as fixed character names, default character IDs, age/height/body type, and local-only additions must not become the real data layer.
- UI work may continue with fixtures while backend contracts are developed, but the fixture boundary must be explicit.
- Codex must not invent fake backend APIs solely to make screens appear complete.

## Validation

Alignment checks should detect obvious prototype project identifiers in production-path frontend source and require an explicit fixture boundary or approved exception.
