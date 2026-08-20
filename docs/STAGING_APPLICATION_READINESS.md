# Staging Batch 1 Application Readiness

Status: implementation under Director review; not deployed.

## Dependency decision

The trusted boot path imports Project and Character routers only. No Environment
domain module, table, migration, client, route, or runtime import is required to
start the API or exercise the approved Project/Character vertical slice. Redis is
not present in Python dependencies, Compose services, configuration, imports, or
the request path. Both are therefore deferred from Batch 1 rather than migrated
speculatively.

## Authentication contract

The API accepts only OIDC access tokens verified by the configured issuer's JWKS.
The required claims are `exp`, `iat`, `iss`, `aud`, `sub`, `jti`, `workspace_id`,
`agent_id`, and `agent_kind`. Claims identify the request context; PostgreSQL
membership and forced RLS remain canonical authorization. Staging and Production
reject placeholder `.invalid` issuer/JWKS URLs and a missing deployment release.
There is no development-auth fallback.

The frontend uses provider-neutral OIDC Authorization Code with PKCE. The actual
authorization endpoint, token endpoint, and client ID are deployment inputs. It
stores the access token for the browser tab only. Decoded claims are routing hints,
never authority decisions; the API verifies every request.

## Outbox and audit operations

Initial Staging has no approved outbox consumer. Its contract is
`durable-storage-only`: events with `delivered_at IS NULL` are pending and must not
be described as published. Authenticated Workspace operational status exposes
pending/delivered counts without payloads.

Audit delivery remains independent and canonical. Delivery keys are unique per
audit stream, automatic retries use bounded exponential backoff, exhausted records
have `failed_at`, and the trusted `scripts/retry_audit_delivery.py` command can
requeue a specific failed record. A failed audit write never rolls back already
committed business state because the durable delivery intent remains in PostgreSQL.

## Control-plane bootstrap

`scripts/bootstrap_staging_workspace.py` is the only Batch 1 Workspace bootstrap
surface. It is not an HTTP route. An operator must provide explicit Workspace,
human owner principal, human owner agent, display name, and reason. The command
creates no synthetic identity and writes a durable audit-delivery intent in the
same transaction as the authority root. It then requires successful independent
audit delivery before reporting full success.

## Readiness contract

`/health/ready` blocks when the business database is unreachable, the current
Alembic revision differs from `EXPECTED_MIGRATION_HEAD`, the independent audit
database is unreachable, or critical Settings validation fails at process start.
The absent outbox consumer is explicitly reported but is not an external
dependency and does not block readiness.

## Deployment boundary

This batch does not authorize Server 1 changes, persistent migration execution,
deployment, DNS, proxy, firewall, Environment, other creative stages, Studio, or
Production changes.
