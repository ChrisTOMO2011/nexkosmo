# Nexkosmo architecture baseline

Status date: 2026-08-03. This document describes the checked-in and current
working-tree implementation; it is not a promise of future capability.

## Baseline

| Subsystem | Status | Evidence and boundary |
|---|---|---|
| Python domain/application/infrastructure/API modular monolith | implemented | `app/domain`, `app/application`, `app/infrastructure`, `app/interfaces/http` |
| PostgreSQL canonical persistence | development-ready | Alembic revisions through `0011_environment_forest`; local migration and RLS acceptance passed; CI/release acceptance remains |
| Workspace, Project, Production, Character ownership | implemented | aggregate, repository, application service, API and forced-RLS migrations |
| React/Vite Studio frontend | implemented | cinematic root, Studio route, Character Identity and deferred workflow boundaries |
| Transactional outbox | implemented | outbox writes share aggregate transaction |
| Outbox dispatch | development-ready | leased dispatcher, typed registry, retry and dead-letter state; no product consumers registered |
| Independent audit delivery | development-ready | durable business-side intent queue and deduplicated audit-chain delivery |
| OIDC/JWKS authentication | partial | verifier and production fail-fast exist; mocked-provider tests only until a real provider is exercised |
| Semantic kernel repositories | deferred | ports exist; concrete adapters and product activation are intentionally disabled |
| Pre-Production Character Brain | development-ready | canonical identity and physical properties, species capabilities, style profiles, compatible editor assets, accessories and honest package readiness |
| Pre-Production Environment Brain | development-ready | production-owned immutable packages, type/capability registry, compatible manifests and structured readiness through PostgreSQL, FastAPI and the shared workspace |
| Script, upload, AI generation, VFX/CGI, Review, Render product features | missing/deferred | outside Phase 3 |

Environment follows `Workspace -> Project -> Production -> Environment`. Future
Scene records must reference the canonical Environment UUID; the current phase
does not create Scene records or copy Environment package state downstream.

## Governing flow

PostgreSQL is the canonical data source. Commands pass through authenticated
FastAPI dependencies, application services, a unit of work, repositories and
forced row-level security. A successful command atomically commits the aggregate,
outbox event, idempotent response and audit-delivery intent. Audit delivery then
uses its independent database role. The guarantee is at-most-one committed
mutation per idempotency key, retry-safe response recovery, and at-least-once
deduplicated audit/outbox delivery—not exactly once.
