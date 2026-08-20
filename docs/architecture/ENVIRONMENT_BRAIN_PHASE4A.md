# Environment Brain — Phase 4A

## Canonical ownership and persistence

Environment packages follow the existing ownership chain:

`Workspace -> Project -> Production -> Environment`

PostgreSQL is authoritative. The Environment aggregate is loaded and saved through the existing repository and unit-of-work boundary, application service, FastAPI routes, and typed frontend API client. Future scenes should reference `environment_id`; they must not copy Environment package state.

## Reused architecture

- Immutable domain aggregates and explicit mutation methods.
- SQLAlchemy repositories and the established unit of work.
- Workspace-scoped PostgreSQL row-level security.
- Optimistic concurrency through `expected_version`.
- Idempotent mutations, audit records, and transactional outbox events.
- RFC 9457-style Problem Details responses.
- The shared `PreProductionWorkspace` presentation shell and Character workspace geometry.
- The canonical asset-manifest table, extended with an Environment domain discriminator and Environment compatibility metadata.

## Environment model

The Environment aggregate persists identity, ownership, type and location metadata, biome and climate, time and atmosphere, canonical asset selections, cross-domain compatibility profile references, constraints, package/readiness state, validation issues, and version timestamps.

Environment types and capabilities are canonical database records. Supported editor tabs and validation behavior come from type capability metadata rather than React conditionals.

## API surface

- `GET /api/v1/environment-types`
- `POST|GET /api/v1/projects/{project_id}/environments`
- `GET|POST /api/v1/productions/{production_id}/environments`
- `GET /api/v1/environments/{environment_id}`
- `PATCH /api/v1/environments/{environment_id}/properties`
- `PATCH /api/v1/environments/{environment_id}/identity`
- `POST /api/v1/environments/{environment_id}/change-type`
- `PUT /api/v1/environments/{environment_id}/selections/{category}`
- `PUT /api/v1/environments/{environment_id}/collections/{category}`
- `DELETE /api/v1/environments/{environment_id}/selections/{category}`
- `POST /api/v1/environments/{environment_id}/validate-package`
- `POST /api/v1/environments/{environment_id}/validate`
- `GET /api/v1/environments/{environment_id}/readiness`
- `GET /api/v1/environments/{environment_id}/compatible-assets`
- `GET /api/v1/environments/{environment_id}/supported-tabs`

Compatible-assets accepts category and subcategory filters. Those reads do not mutate
the package. Commands require the established idempotency and optimistic-version
headers, and return the canonical package/version after commit.

## Readiness contract

Readiness is one of `incomplete`, `valid`, `processing_required`, `ready_for_scene`
or `blocked`, with warnings, missing requirements, invalid assets, required processing
jobs and the validated aggregate version/time persisted together. Any package mutation
invalidates the prior result. Compatibility evaluates type/category/subcategory,
biome, climate, time, weather, style, status, visibility, capabilities, dependencies
and conflicts in one application policy.

## Source boundaries and future seams

Seeded Environment manifests are development catalogue metadata, not generated media.
No binary upload, storage object, AI result, preview render or Scene is fabricated.
The future Scene Builder seam is the stable Environment UUID and structured readiness;
Scene, Lighting, Camera Gear, Audio, VFX, Props and Vehicles remain separate domains.

## Intentional deferrals

Upload, AI generation, binary storage, preview rendering, Scene Builder, Set, Lighting, Camera Gear, Audio, VFX, Props, Vehicles, Studio, Review, and Render behavior remain outside Phase 4A. Their UI actions provide honest deferred messaging and do not fabricate assets or results.

`Next: Set` remains disabled until the persisted Environment readiness contract reports
`ready_for_scene`. Because preview generation is deferred, a compatible configured
package currently reports `processing_required` rather than falsely claiming readiness.
