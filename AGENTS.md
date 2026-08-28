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

## Non-linear Discover and anchor scenes

The Director does not need to know the whole movie before using DISCOVER. DISCOVER MUST support non-linear story development.

Rules:

1. The Director may create only the scenes they currently know, including a beginning, a middle moment, an ending, or any other isolated scene in any order.
2. Known scenes are treated as **anchor scenes**. Missing story between anchors remains explicitly unresolved rather than being silently invented as decided project truth.
3. Brain may identify the gaps between anchor scenes and may help the Director explore possible connecting scenes, beats, or transitions.
4. AI-generated suggestions for missing material remain proposals. They MUST NOT become canonical Discover cards or approved story events until the Director explicitly accepts, creates, or approves them.
5. The Director may add, remove, reorder, replace, or refine anchor scenes as the story develops.
6. DISCOVER must preserve the distinction between what the Director knows, what has been approved, and what is still unknown or merely suggested.
7. A project may remain intentionally incomplete in DISCOVER while still preserving its known structure and allowing continued development.

Example:

`KNOWN OPENING -> UNRESOLVED GAP -> KNOWN MIDDLE -> UNRESOLVED GAP -> KNOWN ENDING`

Brain may help explore the unresolved gaps, but the gaps remain unresolved until the Director decides what belongs there.

The permanent rule is:

> Unknown story is allowed to remain unknown. Brain may help explore it, but only the Director turns a suggestion into the movie.

## Discover scene minimum and progression

DISCOVER must not force every project type into an arbitrary scene count.

Rules:

1. The hard minimum to establish a DISCOVER project is **one scene**. A Director may begin with only one scene or moment they can clearly imagine.
2. **Three anchor scenes** - typically a beginning, a meaningful middle point, and an ending - are a useful basic story skeleton when that structure fits the project, but they are guidance rather than a mandatory requirement.
3. A Director MUST NOT be blocked from continuing to SHAPE merely because fewer than three scenes exist.
4. Progression from DISCOVER is based on whether the project has enough established structure and intent for meaningful continued development, not on reaching a fixed number of cards.
5. Brain may identify important unresolved structural gaps and explain them to the Director, but unresolved gaps do not become invented canonical scenes merely to satisfy a numeric minimum.
6. The same rule applies across project types and lengths, including commercials, music videos, short films, feature films, game cinematics, and other supported formats.

The permanent rule is:

> One established scene is enough to begin. Story sufficiency, not scene count, determines when the project is ready to continue.

## Ready as the Production gate

READY is the single serious validation gate before full PRODUCTION. Earlier creative stages should remain fluid and should not repeatedly interrupt the Director to reconfirm decisions that have already been made.

Rules:

1. Director edits made in IDEA, DISCOVER, SHAPE, or BUILD may propagate through connected project state without requiring repeated confirmation when the intended consequence is unambiguous.
2. READY validates whether the connected creative state is sufficiently synchronized, complete, and technically usable for full PRODUCTION.
3. READY must distinguish at least three outcomes:
   - **Not Ready** - one or more critical unresolved items remain. Full PRODUCTION is blocked.
   - **Ready with warnings** - only non-critical issues remain. Full PRODUCTION is allowed, with the warnings preserved and visible.
   - **Ready** - required validation has passed. Full PRODUCTION is allowed.
4. Critical blockers include unresolved or conflicting information that would force PRODUCTION to invent a material creative decision, break approved continuity or identity, or proceed without required production information.
5. Non-critical warnings MUST NOT become artificial blockers merely because they exist.
6. Test renders, previews, camera tests, look-development, AI experiments, and other exploratory outputs may be performed before READY passes. These are development activities and do not count as entering committed full PRODUCTION.
7. The system must preserve the reason for every blocking condition so the Director can see what must be fixed rather than encountering an unexplained stop.
8. Once a critical blocker is resolved, READY should re-evaluate automatically rather than forcing the Director through unnecessary duplicate steps.

The permanent rule is:

> Creative work stays fluid until READY. Full PRODUCTION is blocked only when READY finds a critical unresolved condition.
