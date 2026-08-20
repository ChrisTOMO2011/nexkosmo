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

Studio is not a seventh top-level progression stage. Production is the movie-wide control room, while Studio is the contextual deep-edit workspace opened from Production for a selected scene or shot. See `docs/CURRENT_STATE.md` and the approved decision records for the authoritative current product model.

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

## Intelligence distinction

- The selected AI Producer (for example Sophia) is the Director-facing relationship and collaboration layer.
- Brain is Nexkosmo's underlying intelligence/status/health layer and must not be presented as a competing chatbot.
