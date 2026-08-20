# Project Authority Threat Model

## Scope and protected assets

This model covers Workspace membership as the authority root, Project ownership
and membership, Production operational state, Semantic Kernel Project
Identity/Context creation, idempotency, outbox evidence, audit-delivery intent,
and the independent audit store. It does not define frontend trust, Workspace
provisioning, emergency remediation resolution, or creative-domain behavior.

Protected assets include human authority attribution, tenant isolation,
Project-content confidentiality, the single-Owner invariant, aggregate versions,
semantic identity provenance, deterministic command results, and durable event
and audit evidence.

## Trust boundaries

- Bearer claims authenticate a principal and acting agent, but cannot grant a
  Workspace or Project role.
- PostgreSQL membership and validity periods are canonical authorization state.
- `principal_id` owns authority. `agent_id` is acting context and attribution.
- The application transaction and independent audit transaction are separate;
  the durable delivery queue bridges them.
- Workspace provisioning and remediation resolution are trusted control-plane
  operations and are intentionally route-disabled here.

## Threats and controls

| Threat | Control |
|---|---|
| Forged token role or delegated action | Every command re-queries active PostgreSQL membership. Claims can only narrow authority. |
| AI/service agent becomes owner | Workspace queries and database guards require a same-Workspace human agent; Project membership stores principal authority only. |
| Cross-Workspace access | Transaction-local Workspace context, same-Workspace foreign keys, forced RLS, and path/context agreement. |
| Workspace Admin reads private Projects | Project SELECT requires active Project membership in addition to active Workspace membership. |
| Cross-Project Production access | Production RLS inherits the referenced Project membership and the route verifies the Project relationship before mutation. |
| Duplicate or missing Project Owner | Deferred temporal exclusion and owner-integrity triggers require exactly one active Owner matching the aggregate. |
| Owner transfer race | Project and membership rows plus target Workspace membership are locked; expected version and deferred constraints serialize the result. |
| Owner Workspace membership revoked | Access fails immediately from live membership state; an unresolved remediation intent is recorded and mutations remain locked. |
| Stale bearer after revocation | Database membership is checked on every request and helper evaluation. |
| Archived data mutation | Domain rules, RLS predicates, and mutation triggers reject changes; restore is Owner-only. |
| Invalid Production transition | Domain transition table and PostgreSQL trigger independently enforce the approved graph. |
| Same idempotency key, different request | Request hash mismatch raises conflict before business mutation. |
| Lost idempotency lease | Lease is revalidated under lock in the business UoW before authorization and completion. |
| Partial Project creation | Identity, Context, aggregate, membership, provenance, idempotency completion, outbox, and audit intent share one transaction. |
| Audit service outage | Business commit remains; pending queue entry is durable, deduplicated, observable, and retryable. |
| Direct application membership mutation | `nexkosmo_app` has no INSERT, UPDATE, or DELETE grant on Workspace memberships. |
| Search-path or dynamic-SQL injection | Authorization helpers use fixed search paths, qualified objects, no dynamic SQL, revoked PUBLIC execution, and narrow app execution grants. |
| Canonical record deletion | No Project/Production DELETE policy or grant exists; migrations have no destructive downgrade. |

## Fail-closed cases

Missing actor context, inactive membership, non-human acting agent, invalid role,
unknown Project membership, cross-tenant identifiers, authority-remediation lock,
stale versions, expired leases, and ambiguous ownership all deny the operation.
Migration preflight rejects unknown roles, non-human or cross-Workspace agents,
overlapping membership periods, and conflicting Workspace Owner periods without
rewriting data.

## Residual risks and deferred controls

- Trusted Workspace provisioning and emergency remediation resolution require a
  separately approved control-plane identity and audit contract.
- Passing disposable PostgreSQL rehearsal is not evidence of Production
  migration readiness.
- Audit queue monitoring and an always-on retry worker require later operational
  deployment approval; queue durability is present now.
- The baseline transaction-local actor context remains dependent on authenticated
  server code. Direct database credentials must continue to be protected.
