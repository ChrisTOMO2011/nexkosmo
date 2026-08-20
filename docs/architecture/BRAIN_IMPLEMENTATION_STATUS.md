# Nexkosmo Brain implementation status

Last verified: 3 August 2026

Reality overrides assumptions. Only behavior supported by repository and validation
evidence is described as implemented.

| Capability | Status | Current boundary |
|---|---|---|
| Domain and application layers | development-ready | Character and Project/Production aggregates and services |
| PostgreSQL persistence | development-ready | Forward migrations through `0008_accessory_categories` |
| Workspace isolation | development-ready | Forced RLS and membership checks; production acceptance remains a release gate |
| Audit delivery | development-ready | Transactional intent queue, separate audit role, retry and deduplication |
| Outbox dispatch | foundation only | Leasing, ordering, retry, dead-letter and inbox primitives; no product consumers |
| Authentication | mocked-provider validated | OIDC/JWKS adapter and production fail-fast; real provider not yet validated |
| Semantic kernel | deferred | Explicit boundary; no AI runtime is activated |
| Character Brain | development-ready | Canonical identity, physical profile, species, style, editor selections, accessories and readiness validation |
| Environment Brain | development-ready | Canonical Production ownership, type capabilities, compatible selections, constraints and structured readiness |
| Frontend | development-ready | Unified landing and Studio routes with typed Character HTTP client |
| Later product workflows | deferred | Script, uploads, AI generation, preview, Set, Studio, Review and Render features |

## Character acceptance checkpoint

The final Character workspace checkpoint ran against PostgreSQL migration
`0008_accessory_categories`. Fresh-process API reads, ten browser reloads,
optimistic conflict handling, Viewer reads, cross-workspace denial, relationship
round trips, RLS and migration tests passed. The stale worker responsible for the
reload HTTP 500 was replaced; no migration or persisted Character repair was needed.

The accepted frontend keeps upload, generation and producer actions explicitly
deferred. They display explanatory messages and create no files, assets, jobs,
conversations or synthetic Character state. No later Pre-Production domain is part
of this checkpoint.

## Known limitations

- The historical detached worker did not retain stderr, so its complete traceback,
  database statement and parameters cannot be recovered after process replacement.
  Current unexpected failures are correlated and logged to prevent that evidence gap.
- The producer assignment domain, asset ingestion, AI-generation jobs and preview
  assembly remain deliberately unimplemented.
- Legacy migrations execute successfully but are not yet formatted to the current
  Ruff line-length policy; that cleanup is separate from this defect-only task.

The accessory-category correction is forward-only. It reclassifies the historical
`More` catalogue sentinel from `glasses` to `more`; no Character selections are
deleted or rewritten.

See the [master architecture baseline](master-architecture-baseline.md),
[current system map](current-system-map.md), and [phase status](../roadmap/phase-status.md).

## Environment Phase 4A checkpoint

Environment now follows the permanent PostgreSQL -> repository/unit-of-work ->
application service -> FastAPI -> typed frontend flow. Forest compatibility includes
terrain, building, nature, material and detail assets. Browser acceptance persisted
the selected Forest package across ten reloads and readiness honestly returned
`processing_required` because preview assembly is deferred.
