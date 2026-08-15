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

Codex and future UI work must use this canonical logo on all Nexkosmo product pages and shared shells, including Discovery, Shape, Build, Ready, Studio, onboarding, account surfaces, and future production workspaces.

Do not reintroduce the older cyan/blue-heavy X as the default brand mark.

Do not redraw, regenerate, approximate, recolor, or reinterpret the logo independently on individual pages. Reference the shared canonical asset/component so future logo changes propagate consistently.

A page-level redesign or image-generation request is not authority to change a frozen global brand asset.

### Canonical asset enforcement

The repository-level `AGENTS.md` defines the mandatory AI/Codex workflow:

`resolve canon -> retrieve source -> perform requested change -> validate -> accept or reject`

For the frozen logo, validation is a release gate. `python scripts/verify_canonical_assets.py` calculates the Git blob identity of the canonical file and compares it with the registered identity. CI fails if the asset is missing or has drifted without the registry being deliberately updated as part of an explicit brand revision.

This protects canonical identity from conversational forgetting, prompt drift, regenerated approximations, and accidental page-specific substitutions.

## Global Shell Consistency

The product journey uses the shared progression model:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY`

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
