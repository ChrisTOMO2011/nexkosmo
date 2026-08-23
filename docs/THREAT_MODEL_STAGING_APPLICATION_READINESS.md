# Staging Application Readiness Threat Model

## Scope and assets

This model covers OIDC-to-API authentication, browser token handling, Project
rediscovery, Workspace bootstrap, request logging, readiness, audit redelivery,
and durable-only outbox visibility. PostgreSQL authority, audit integrity,
credentials, access tokens, tenant data, and human ownership are protected assets.

## Trust boundaries and controls

| Threat | Control |
|---|---|
| Placeholder or missing Staging IdP | Staging configuration rejects non-HTTPS, `.invalid`, empty, and development release values. |
| Forged authority claim | JWKS signature, issuer, audience, time, and required-claim validation precede live PostgreSQL membership and forced-RLS checks. |
| Browser claim treated as authority | Frontend claims select request context only; server token verification, route/context agreement, membership, and RLS decide access. |
| Authorization-code interception | OIDC Authorization Code with random state and PKCE S256; no password or implicit-flow fallback. |
| Token leakage in logs | Structured request logs exclude headers, tokens, query payloads, and bodies. |
| Generic proxy CSP blocks Keycloak initialization | `/auth/` replaces duplicate upstream/proxy security headers with a scoped same-origin CSP that permits Keycloak's required trusted inline initialization while retaining frame, object, base, form, image, font, and connection restrictions. |
| Workspace Admin enumerates Project content | Project list joins active Project membership and remains guarded by forced RLS. |
| Public Workspace provisioning | No bootstrap route exists; the privileged command requires explicit human IDs and reason. |
| Synthetic or hard-coded owner | Bootstrap has required owner parameters and fails on existing identifiers. |
| Audit outage loses business state | Transactional queue intent survives; bounded retry, failed state, explicit requeue, and deterministic delivery-key deduplication. |
| Duplicate canonical audit entry | Unique stream/delivery-key index plus advisory-lock precheck makes redelivery idempotent. |
| Pending outbox represented as published | Staging contract is durable-storage-only and status reports pending separately from delivered. |
| False-positive readiness | Readiness checks business DB, exact migration head, independent audit connectivity, and validated critical configuration. |
| Backup secret disclosure | Credentials are injected through environment and never embedded or echoed. |

## Fail-closed cases

Missing or invalid OIDC configuration, callback state mismatch, malformed token,
missing authority claims, inactive Workspace membership, missing Project membership,
cross-Workspace path, migration mismatch, database failure, and audit database
failure deny the operation or readiness result.

## Residual risks and deferred controls

- The Staging IdP and client registration are deployment inputs and remain unknown
  until the Director approves the provider configuration.
- Session storage remains exposed to same-origin script. The deployed proxy keeps
  frontend scripts same-origin and uses a separately tested Keycloak-compatible CSP
  only for `/auth/`; browser acceptance must fail on any relevant CSP, console,
  asset, or network error.
- There is no outbox consumer by design. A consumer requires a real integration,
  separate contract, and approval.
- The audit retry command is operator-triggered in Batch 1; scheduler/service
  installation is a deployment concern.
