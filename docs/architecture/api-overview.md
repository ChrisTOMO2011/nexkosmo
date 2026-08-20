# API overview

FastAPI exposes versioned Project, Production, Character, Environment, Species and compatible
asset endpoints under `/api/v1`. Mutation endpoints require `Idempotency-Key` and
optimistic versions where applicable. Domain errors map to problem responses:
authorization 403, missing data 404, validation 422 and concurrency/idempotency
conflicts 409.

The Character API includes identity and physical-property commands, species changes,
generic scalar selections, accessory replacement, compatible-asset projections,
species-supported tabs and package validation. Character write responses return the
new optimistic version and a structured change summary. Package validation records
structured readiness issues; it does not claim that deferred preview assembly ran.

The Environment API provides Project- and Production-scoped list/create operations,
identity and property updates, type changes, single and collection selection commands,
selection removal, compatible asset and supported-tab projections, and structured
readiness validation. Filters are query projections only and never increment an
Environment version. All Environment writes remain idempotent and version-checked.

`GET /health/live` reports process liveness. `GET /health/ready` checks both
database connections and the Alembic head, and reports deferred/disabled runtime
subsystems without implying they are operational.
