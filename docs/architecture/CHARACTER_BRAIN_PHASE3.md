# Character Brain Phase 3

Last verified: 3 August 2026

## Architecture reused

The Character capability remains one vertical slice of the permanent Nexkosmo Brain:

`PostgreSQL -> repositories and unit of work -> application service -> FastAPI -> typed frontend client`

Phase 3 extends the existing immutable `Character` aggregate, SQLAlchemy repositories,
transactional unit of work, idempotency boundary, optimistic version checks, outbox,
audit delivery, forced RLS, FastAPI problem responses and TypeScript gateway. It does
not add a second store or a parallel backend architecture.

## Canonical package

The Character package now persists:

- identity name, role, identity type and gender presentation;
- age, apparent age, height, body type, skin tone and physical-profile version;
- species and species-specific ranges, supported editor tabs and surface terminology;
- visual style profile with render, shader, texture, material, geometry and preview metadata;
- Face, Hair, Skin, Eyes, Beard, Age and Expression selections;
- grouped multi-select accessories with compatibility metadata;
- rig, skeleton, material, texture, animation, voice, preview and source references;
- readiness state, structured validation issues, validated version and validation time.

Asset identity is UUID-based. Filenames and UI labels are not identifiers. The
existing upload, AI generation and preview buttons remain honest deferred handlers;
they do not fabricate durable asset or job records.

The frontend also prevents browser-local identity previews from being presented
as production uploads. Deferred controls return explicit accessible notices,
and static appearance recommendations are labelled as curated presets rather
than dynamically generated AI output.

## Species behavior

Supported tabs and physical ranges are returned by the canonical species registry.
Unsupported tabs disappear. Robot and creature surface controls use species-specific
labels while retaining the approved page geometry.

Species changes continue to use the compatibility service. Invalid selections are
cleared, compatible selections are preserved, defaults are applied, downstream stages
are invalidated and one durable change event is emitted.

## Readiness

Package validation returns one of:

- `incomplete`
- `invalid`
- `processing-required`
- `ready-for-set`

Missing or incompatible selections are structured blockers. When core selections are
valid but no preview assembly exists, readiness is `processing-required`; Phase 3 does
not claim that rendering occurred.

## Validation evidence

Local PostgreSQL acceptance reached migration head
`0007_character_brain_completion`. The full Python suite passed 58 tests, including
repository, migration, RLS, audit, outbox, idempotency, API and new Phase 3 coverage.
Live API acceptance persisted identity, physical, style and face changes across reload,
returned HTTP 409 for a stale write, hid cross-workspace reads and writes, and confirmed
that a semantic no-op produced no new version or outbox event.

Frontend lint, type checking, 44 tests and the production build passed. Browser
acceptance used HTTP API mode at the approved Character Identity route: an identity
rename and Face selection were written through FastAPI, reloaded from PostgreSQL and
reappeared after a full navigation reload. The manifest-backed Hats category also
returned Upload and AI Generate first, followed by its compatible canonical assets.

## Deferred boundaries

Uploads, AI generation, preview assembly, CGI, VFX, Set, Studio, Review and Render
execution remain outside Phase 3. Existing interfaces may expose deferred status, but
they must not invent files, jobs, previews or rendering results.

The lower-left producer panel has a typed optional Project-profile seam. The
canonical Project and Production backend currently store no producer/director
assignment, so the UI reports `Producer not assigned`; it does not fabricate a
Sophia profile or an AI conversation.

## Final Character workspace acceptance

The reload HTTP 500 was caused by a stale FastAPI worker that pre-dated the
Phase 3 application and migration state while PostgreSQL had already advanced to
`0007_character_brain_completion`. The detached process returned the old readiness
shape and failed the species, supported-tab and compatible-asset reads used during
reload. Replacing it with a worker loaded from the current checkout restored those
reads without a schema or data repair.

HTTP requests now carry a correlation identifier. A safe incoming
`X-Request-Id` is echoed, otherwise the API creates one. Unexpected exceptions are
logged with that identifier, method, path and traceback, and the canonical problem
response includes the same trace identifier. A missing manifest is a controlled 404,
not an unclassified 500.

Final acceptance used the live PostgreSQL Character through ten full browser reloads.
Identity, style, species, all seven single-select editor surfaces, physical properties
and the two selected accessories remained stable. Species filters now project only
their named species (with All and More behaving explicitly), accessory categories no
longer inherit Glasses results, and category changes do not mutate Character state.
The final suites passed 63 backend tests and 53 frontend tests, plus lint, type checking,
Python compilation, migration-head verification and the API-mode production build.

## Accessory catalogue correction

The forward-only `0008_accessory_categories` revision corrects the canonical
subcategory of the historical `More` manifest. Accessory presentation now retains
manifest UUIDs throughout filtering and mutation, while the active category remains
independent frontend navigation state. Cross-category membership is preserved by the
existing collection replacement command and PostgreSQL relationship table.
