# ADR 0003: PostgreSQL is canonical

Status: accepted.

PostgreSQL is the permanent source of truth. Frontend TypeScript models are typed
clients/domain helpers, not authoritative persistence. In-memory adapters are
test/development-only and are rejected in production.
