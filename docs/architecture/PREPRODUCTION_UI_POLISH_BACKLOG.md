# Pre-Production UI polish backlog

Last reviewed: 3 August 2026

## Resolved in the shared foundation pass

- Single-choice identity, style and Character asset cards no longer combine an
  active border with a duplicate checkmark.
- Accessories communicate multi-select membership with a checkmark and retain a
  separate keyboard focus outline.
- Previously selected single-choice cards lose both `aria-pressed` and the
  active-border class after a successful replacement.
- Upload and AI Generate controls explain their deferred phase and create no
  browser-local production record, fake job or fake result.
- Character suggestions are identified as curated presets and do not claim that
  scene analysis or personalised AI generation occurred.
- The lower-left card is producer-aware and uses an honest unassigned fallback.

## Resolved in the Character stabilisation pass

- Replaced the stale local API process that had remained alive across the
  Phase 3 schema/application upgrade. The current readiness response now
  verifies the configured migration head before browser use (currently
  `0008_accessory_categories`).
- Character reload no longer loses the roster when the current species,
  supported-tab or compatible-asset reads are healthy.
- Delayed physical-property saves are buffered per Character rather than in a
  shared pending object. Switching Characters cannot merge slider values into
  another Character.
- A late response for a previously selected Character updates the cached roster
  only; it cannot overwrite the active Character inspector.
- Obsolete supported-tab, editor-asset and accessory requests are ignored after
  their Character or tab changes.
- Human, Elf, Orc, Robot, Dragon and Alien filter pills now show exactly their
  named species; All and More have explicit, non-mutating catalogue projections.
- Accessory categories use their canonical manifest subcategory and an empty
  category no longer falls back to Glasses.
- Character API failures now include a request correlation identifier, and a
  missing manifest returns a controlled 404 problem response.
- Accessory tabs now operate on canonical manifest UUIDs and subcategories,
  preserve cross-category membership, expose pending/error/focus state, and
  support arrow-key navigation. The historical `More` manifest is no longer
  classified as Glasses.

## Deferred product work

- Add a canonical Project or Production producer-profile assignment to the
  backend domain, PostgreSQL migration, repository, application service and API
  before persisting producer selection.
- Connect the producer action only when a real conversation/orchestration phase
  defines ownership, audit, provider availability and failure behavior.
- Map each curated suggestion to explicit Character commands and compatibility
  rules before enabling Apply.
- Implement asset upload/ingestion before enabling local file selection,
  progress, cancellation or retry.
- Implement AI Character generation jobs before exposing generation progress,
  results or retry.
- Add real progress and recovery presentation when upload/generation APIs exist;
  the shared card-state vocabulary is ready, but no progress is fabricated now.

## Visual and accessibility watch list

- Recheck asset-card hover contrast when final thumbnails replace screenshot
  crops; hover must remain weaker than selection.
- Recheck tooltip placement for unsupported assets once compatibility reasons
  are supplied by each domain controller.
- Repeat desktop and tablet screenshot acceptance whenever a future domain adds
  shared CSS. Character-specific dimensions remain the regression baseline.
- Replace the remaining screenshot-derived preview, portrait and accessory
  crops only when approved original assets become available; their present
  crop, brightness and resolution are intentionally retained.
- Add field-level pending, saved and retry feedback when the approved interaction
  design exists. The current global live-region message is accessible but later
  operations can replace an earlier success message.
- Review the seeded API asset order against the approved catalogue order before
  final asset art is connected. The current compatible-asset response order is
  canonical but differs from the fixed mock catalogue ordering.
- Decide the domain rule for a species change when an existing physical profile
  falls outside the new species age or height range. The current command can
  retain an out-of-range value; the stabilisation acceptance record was returned
  to a valid Human age after this was observed.
- Lit, Wireframe, fullscreen, preview-scene, advanced-settings and catalogue
  expansion controls remain explicit placeholders and must not imply completed
  rendering behavior.
- Recheck narrow-tablet inspector focus return and long asset-name wrapping when
  real catalogue names and property schemas replace development seeds.
- Remove the Starlette `TestClient` deprecation warning when the repository's
  framework upgrade is scheduled; it does not affect current Character behavior.
- Bring the legacy migration files under the current Ruff line-length and format
  policy in a dedicated migration-maintenance change. They are executable and
  tested, but remain outside this defect-only pass.

Environment now uses the shared workspace. Its remaining polish items are approved
original preview/thumbnail artwork, final empty-state copy, and field-level saved/retry
feedback. The current seeded imagery is explicitly development-only and deferred
buttons report that no upload, generation job or producer session was created.

Camera Gear, Lighting, Audio, VFX, Props and Vehicles remain unimplemented pending
their approved content and domain controllers.
