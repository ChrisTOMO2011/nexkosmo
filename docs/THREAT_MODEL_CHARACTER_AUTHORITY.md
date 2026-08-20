# Character Authority Threat Model

## Scope and protected assets

This model covers the minimal Project-owned Character aggregate, semantic
Identity and Activity provenance, nested HTTP routes, idempotency, outbox and
audit-delivery intent, concurrency, same-Workspace ownership, Project authority
inheritance, and PostgreSQL RLS. It does not approve catalogues, assets,
generation, compatibility, readiness, archive/restore, Production bindings,
frontend authority, or rendering.

## Trust boundaries

- PostgreSQL membership and validity periods are canonical authorization state.
- The Project is the Character ownership and authorization root.
- `principal_id` owns authority; `agent_id` records human acting context.
- Token claims and frontend state may narrow but cannot grant authority.
- Character and semantic provenance commit in one application transaction.
- Independent audit truth is delivered from durable transactional intent.

## Threats and controls

| Threat | Control |
|---|---|
| Cross-Workspace access | Transaction-local actor context, composite same-Workspace foreign keys, path/context agreement, forced RLS, and trigger checks. |
| Cross-Project access | Nested routes verify the Character/Project relationship; RLS inherits live Project membership. |
| Workspace Admin reads private Characters | SELECT requires `can_read_project`, including active Project membership. |
| Viewer mutates Character | Service and `can_mutate_project` allow Owner/Admin/Editor only. |
| Non-human actor mutates Character | Service and live Workspace authority require a human acting agent. |
| Archived or authority-locked Project changes | Service checks plus a Project share lock and database recheck fail closed. |
| Project state race | The Character trigger share-locks the Project before rechecking mutation authority. |
| Character ownership changes | Frozen domain object, narrow SQL UPDATE, immutable-facts trigger, and composite foreign keys. |
| Wrong semantic kind | Trigger requires same-Workspace `IdentityKind.CHARACTER`; `id = identity_id` is constrained. |
| Stale update | Expected-version domain check, version-qualified SQL, and trigger-enforced single increment. |
| Duplicate write | Transactional idempotency request hash and lease; replay returns the committed response. |
| Partial write | Character, Activity/output, idempotency, outbox, and audit intent share one transaction. |
| Audit outage | Durable intent remains retryable; delivery cannot roll back business state. |
| Hard deletion | No DELETE route, policy, or app grant; a trigger rejects direct deletion. |
| Fabricated Character truth | Migration has no seed/backfill; API creates only explicitly requested records with server IDs. |
| Frontend duplicate Brain | Slice 4 has zero frontend scope and promotes no candidate TypeScript authority. |

## Fail-closed cases

Missing context, inactive Workspace membership, missing Project membership,
non-human actor, Viewer mutation, archived Project, remediation lock,
cross-tenant or cross-Project identifiers, wrong Identity kind, stale version,
lost lease, and transactional failure all reject or roll back the operation.

## Residual risks and deferred controls

Character lifecycle, Production binding, catalogues, assets, rights/provenance,
compatibility, and readiness require later decisions. Passing disposable
PostgreSQL tests is not Production migration approval. Audit queue monitoring
and operational delivery remain deployment-gated.
