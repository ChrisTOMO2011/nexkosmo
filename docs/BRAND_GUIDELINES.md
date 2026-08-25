# Nexkosmo Brand Guidelines

## Canonical Logo

The canonical Nexkosmo logo mark is `assets/brand/nexkosmo-x-star.svg`.

This mark is now the frozen visual reference for the Nexkosmo Studio product family unless a future explicit brand decision supersedes it.

The canonical asset is also registered in `assets/brand/canonical-assets.json` and protected by `scripts/verify_canonical_assets.py` in CI.

### Visual intent

- Preserve the distinctive four-arm Nexkosmo X silhouette.
- Use a violet/lilac identity palette rather than cyan-heavy branding.
- The centre contains a bright white-violet star/glint with a restrained horizontal light streak inspired by the active progression-stage marker.
- The centre star represents Nexkosmo intelligence coming alive.
- The glow must remain premium and restrained; it must not overpower page content.
- The logo should remain readable at header scale and have a reduced-bloom treatment at favicon/app-icon scale if required.

### Product-wide usage

Codex and future UI work must use this canonical logo on all Nexkosmo product pages and shared shells, including Discovery, Shape, Build, Ready, Production, Studio, onboarding, account surfaces, and future production workspaces.

Do not reintroduce the older cyan/blue-heavy X as the default brand mark.

Do not redraw, regenerate, approximate, recolor, or reinterpret the logo independently on individual pages. Reference the shared canonical asset/component so future logo changes propagate consistently.

A page-level redesign or image-generation request is not authority to change a frozen global brand asset.

### Canonical asset enforcement

The repository-level `AGENTS.md` defines the mandatory AI/Codex workflow:

`resolve canon -> retrieve source -> perform requested change -> validate -> accept or reject`

For the frozen logo, validation is a release gate. `python scripts/verify_canonical_assets.py` calculates the Git blob identity of the canonical file and compares it with the registered identity. CI fails if the asset is missing or has drifted without the registry being deliberately updated as part of an explicit brand revision.

This protects canonical identity from conversational forgetting, prompt drift, regenerated approximations, and accidental page-specific substitutions.

## Current Product Color Direction

The current Nexkosmo product UI uses the newer, brighter cinematic color concept as the preferred visual direction.

This supersedes the older, darker and more muted interface treatment as the default reference for future page consolidation and migration decisions.

The current direction should preserve:

- dark cinematic foundations for focus and contrast;
- brighter violet, lilac, electric-purple and controlled blue highlights;
- clearer illuminated active states and progression markers;
- stronger separation between panels, controls, cards and the primary creative viewport;
- higher perceived energy and clarity without becoming neon-heavy or visually noisy;
- readable text and accessible contrast across all production workspaces;
- consistent color language across Pre-Production, Set, Studio, CGI, VFX, Render, Finish/Delivery and future creative surfaces.

When comparing older and newer interface concepts during migration, the **newer brighter color treatment is the visual baseline** unless the Director explicitly approves a different direction.

Older interfaces may still contain valuable layout, controls, workflows or interaction ideas. Those capabilities should be preserved and modernised into the current brighter visual system rather than retaining an outdated color treatment merely because the functionality originated there.

The brighter direction does not authorise arbitrary recoloring of frozen canonical assets. The canonical logo and other registered assets remain governed separately by the canonical asset rules above.

## Global Shell Consistency

The product journey uses the shared progression model:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

Studio remains a specialist/deep-edit workspace within the production system, not a seventh top-level stage.

The active stage may use the same violet/lilac star-glow language as the canonical logo.

Global controls belong in the persistent top-right shell and should remain visually quiet until relevant:

- Project selector
- Search
- Brain
- Credits
- Collaboration
- Alerts / notifications
- Messages
- Achievements
- Profile

The icons remain available at all times. Attention states such as unread messages, collaborators coming online, approval requests, or Brain warnings may add badges, presence indicators, or restrained temporary emphasis. The creative workspace remains the visual priority.

## BUILD Workspace UX Contract

BUILD is a visual creation workspace backed by a machine-readable Render Specification. The Director should not experience it as an engineering dashboard or a wall of permanent controls.

The governing UX principle is:

> What the Director sees in BUILD must be what the rendering system receives.

The simple Director-facing flow is:

`SEE -> SELECT -> ADJUST -> PREVIEW -> APPROVE`

The interface must support that flow while the system captures structured Scene/Shot state underneath.

### Visual hierarchy

BUILD should:

- make the active character, asset, or assembled Scene/Shot preview the primary visual focus;
- avoid large empty decorative panels that overpower useful creative content;
- minimise permanent borders, nested boxes, and inspector clutter;
- use violet/lilac emphasis for selected states, active workflow markers, important warnings, and primary actions rather than outlining everything;
- preserve enough breathing room that the workspace feels cinematic rather than administrative;
- remain usable at ordinary laptop heights without hiding core creative controls below the fold.

### Progressive disclosure

BUILD should not display every possible parameter simultaneously.

Controls should appear contextually based on the selected creative object or task. For example:

- selecting Eyes reveals eye-related controls;
- selecting a Hat reveals hat-related controls;
- selecting Camera reveals camera/framing controls;
- selecting Environment reveals environment and set controls.

Advanced technical state may be inspected when needed, but beginners should not be forced to navigate renderer terminology for ordinary creative work.

### Visual selection

Where practical, BUILD should prefer visual choices, thumbnails, previews, and direct manipulation over dense forms.

Character preparation may expose categories such as:

- Identity
- Style
- Face
- Hair
- Eyes
- Beard
- Age
- Expression
- Accessories

The exact categories may evolve, but the interaction model should remain visual and contextual.

### Scope clarity

BUILD must make scope understandable before consequential edits are committed.

The user must be able to distinguish:

`Canonical Asset -> Scene Override -> Shot Override`

A Shot-specific injury, expression, pose, wardrobe state, placement, or local environment condition must not silently rewrite the canonical reusable asset.

Broader-scope changes must be deliberate and auditable.

### Preview and approval

BUILD's preview is creative evidence, not decoration.

When the Director approves a Scene/Shot configuration, the accepted preview must be bound to the exact versioned Render Specification that represents the visible state.

The interface should provide a clear preview/approve path and should not present multiple ambiguous apply actions that obscure whether a change targets the canonical asset, Scene, or Shot.

### AI Producer presence

The selected AI Producer may assist, explain, propose, compare, or warn without taking visual priority away from the Director's creative workspace.

AI may propose broad alternatives before approval. Approved state must not be silently reinterpreted afterward.

See `docs/architecture/BUILD_RENDER_SPECIFICATION_CONTRACT.md` for the canonical machine-readable and approval rules governing BUILD.

## Intelligence distinction

- The selected AI Producer (for example Sophia) is the Director-facing relationship and collaboration layer.
- Brain is Nexkosmo's underlying intelligence/status/health layer and must not be presented as a competing chatbot.
