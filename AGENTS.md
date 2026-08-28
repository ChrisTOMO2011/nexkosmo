# Nexkosmo Repository Instructions for Codex and AI Engineering Agents

These instructions apply to the entire repository.

## Authority hierarchy

Codex and all AI engineering agents are implementation agents operating inside the Nexkosmo architecture. They are not the authority to redefine Nexkosmo for implementation convenience.

When requirements appear to conflict, use this authority order:

1. Explicit current Director instruction.
2. Frozen constitutional / identity principles and approved architectural contracts.
3. Approved milestone and STOP-GATE decisions.
4. Repository specifications and canonical registries.
5. Implementation code and tests.
6. Agent assumptions or convenience.

If a lower level conflicts with a higher level, STOP and report the conflict. Do not silently reinterpret the higher-level contract.

Architectural improvements may be proposed with evidence, but permanent architecture changes require explicit human approval. Do not perform blank-slate redesigns while implementing an approved increment.

## Human-replaceable role rule

Nexkosmo responsibilities belong to named roles, not permanently to a specific AI model, vendor, agent identity, or service.

Where a responsibility represents judgement, supervision, creative decision-making, review, approval, coordination, or operational control, that role MUST support assignment to:

- an authorised human;
- an authorised AI agent;
- an approved human-plus-AI hybrid; or
- an unassigned/paused state in which no autonomous action occurs.

AI agents MUST NOT be architecturally indispensable merely because they currently occupy a role. A human must be able to assume the responsibility without redesigning canonical Nexkosmo state or authority relationships.

Deterministic infrastructure services such as databases, event dispatchers, cryptographic audit mechanisms, and compute workers are not treated as human employees. Humans must nevertheless be able to supervise, pause, isolate, override, replace, or recover those services through governed operational controls.

A role assignment change MUST preserve identity, provenance, permissions, audit history, outstanding obligations, and canonical project state.

No agent may assign itself to a more privileged role, increase its own authority, reactivate itself after human suspension, or make itself the sole irreplaceable holder of a Nexkosmo responsibility.

## Migration mode

During an approved repository or environment migration:

- preserve Git history and provenance where practical;
- inventory before moving or deleting;
- define the destination structure before reorganising content;
- move authoritative architecture and governance documents before dependent implementation;
- never copy secrets into source control;
- do not delete, archive, or decommission the source until the destination has passed validation;
- preserve rollback capability;
- treat the migration as incomplete until required builds, migrations, tests, security checks, and milestone proofs pass in the destination environment.

See `docs/MIGRATION_ALIGNMENT.md` for the migration contract.

## Canonical truth rule

Nexkosmo does not rely on conversational memory, prompt history, visual approximation, or regeneration for approved identity-bearing assets or frozen project state.

Before changing any UI, page, shell, mockup implementation, brand surface, or other dependent artifact, retrieve the relevant canonical asset/state from the repository and use it directly.

**Retrieve before generate. Canon before approximation.**

If a requested change does not explicitly authorize changing a frozen canonical item, that item MUST remain byte-for-byte and semantically unchanged.

## Frozen Nexkosmo logo

The canonical Nexkosmo product logo is:

`assets/brand/nexkosmo-x-star.svg`

Its canonical registration is:

`assets/brand/canonical-assets.json`

Rules:

1. Use the canonical SVG directly through a shared logo component or asset reference.
2. Do not redraw, recolor, restyle, reinterpret, approximate, or regenerate the logo per page.
3. Do not substitute an older cyan/blue-heavy logo.
4. Do not change the X silhouette, violet/lilac palette, white-violet centre star, or progression-inspired light streak unless the Director explicitly requests a brand revision.
5. Page-specific work must preserve the canonical logo even when surrounding layout, imagery, theme, or controls change.
6. Discovery, Shape, Build, Ready, Production, Studio, onboarding, account, collaboration, and future product surfaces must resolve the same canonical logo asset.
7. If a task would require changing the canonical logo but the task is not explicitly a brand-change task, STOP and report the conflict instead of modifying it.

## Canonical asset workflow

For any item registered as `FROZEN` or `APPROVED`:

1. Resolve its registry entry.
2. Retrieve the canonical source asset/state.
3. Perform the requested operation around that source of truth.
4. Validate the output against the canonical reference.
5. Reject the result if canonical identity drifted.

A generated resemblance is not equivalent to a canonical asset.

## Change scope

Treat explicit Director approval as the authority required to supersede a frozen canonical item. A casual page-edit request is not permission to alter global brand identity.

When an intentional canonical revision is approved, update the canonical asset, its registry/hash, documentation, shared component references, and affected tests in the same reviewed change.

## Required validation

Before completing any UI or brand-affecting change:

- confirm the canonical logo resolves from `assets/brand/nexkosmo-x-star.svg`;
- run `python scripts/verify_canonical_assets.py`;
- confirm no page-specific replacement logo was introduced;
- confirm only explicitly requested canonical changes were made.

CI also runs the canonical-asset verifier. A failed canonical check is a release blocker, not a warning.

## Product intelligence distinction

Sophia (or another selected AI Producer) is the Director-facing collaboration/personality layer. Brain is the underlying intelligence/status/health layer. Do not turn Brain into a competing chat persona.

## Product journey

The shared stage model is:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION -> STUDIO`

Preserve this shared shell and canonical brand identity unless an explicit product decision supersedes them.

## Discover scene snapshots and Build This Moment

DISCOVER represents each scene with a visible snapshot frame. The snapshot may look like a single image to the Director, but its editable scene state must not be flattened when the scene contains assets the Director can manipulate.

Rules:

1. The environment or background may be used as the base layer and does not require transparency merely because it is the scene background.
2. Any asset that can be dragged, dropped, moved, scaled, replaced, reordered in front of or behind another asset, reused, or independently adjusted in **Build This Moment** MUST remain an isolated element with alpha/transparency or an equivalent persistent isolation mask.
3. This applies to characters, creatures, vehicles, props, movable set pieces, and effects whenever independent manipulation is intended.
4. The visible Discover snapshot is a composite of the base environment plus the isolated scene assets. A flattened preview is a derived view and must not replace the underlying editable composition.
5. **Build This Moment** is an advanced DISCOVER interaction. It may add, remove, reposition, resize, replace, and reorder isolated assets and may create additional ordered scene-moment frames while preserving the identity of the underlying assets.
6. Flattening is permitted for previews, exports, or other derived media only when it does not destroy the persistent editable scene structure.
7. If a source asset does not already contain alpha/transparency, Nexkosmo may create an equivalent isolation mask, but the isolated derivative must remain traceable to its source and must be validated before it is treated as an editable scene asset.

The permanent rule is:

> If the Director can manipulate an asset independently in Build This Moment, Nexkosmo must preserve that asset independently beneath the visible scene snapshot.
