# Nexkosmo Semantic Kernel — Milestone 1R++ Increment 1

This repository is the first controlled implementation increment for the frozen:

- Science of Enduring Intelligence v1.0
- Permanent Semantic Kernel Specification v1.0
- Science-to-Kernel Traceability Model v1.0

## Increment 1 scope

This increment establishes:

- Domain/Application/Infrastructure/Interfaces separation
- Permanent kernel record vocabulary
- Explicit Alembic migration
- PostgreSQL 16 Docker test harness
- Forced row-level security design
- Transaction-local workspace and principal context
- OIDC/JWKS-ready principal verifier port
- Repository and Unit of Work ports
- Stable Problem Details contract
- Transactional outbox and consumer inbox schema
- Recoverable idempotency lease schema
- Independently committed audit schema and audit writer boundary
- Aiden proof fixture and pure-domain tests
- Blocking integration test suite that requires real PostgreSQL

## Evidence status

The package was syntax-compiled and its pure-domain tests were executed in the
artifact environment. PostgreSQL/Docker evidence could not be executed there
because Docker and PostgreSQL were unavailable.

Under the Milestone 1R++ stopping rule, the STOP GATE therefore remains active.

## Run with Docker

```bash
cp .env.example .env
docker compose up -d postgres
docker compose run --rm migrate
docker compose run --rm test
docker compose run --rm restore-test
```

No blocking PostgreSQL test is marked skipped. If PostgreSQL is unavailable,
the test command fails rather than creating false evidence.

## Service

```bash
docker compose up api
```

- Liveness: `GET /health/live`
- Readiness: `GET /health/ready`
- OpenAPI: `/docs`
