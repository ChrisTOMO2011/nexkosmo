# Nexkosmo Preserved Candidate Migration Register — 2026-08-20

Status: SLICE 1 ACTIVE — DIRECTOR-APPROVED DOCUMENTATION RECONCILIATION ONLY<br>
Owner: Director<br>
Manifest: version 9<br>
Trusted baseline branch: `governance/alignment-system`<br>
Trusted baseline commit: `e34d2aaba4cda1aa9563242edc3df48b230833f7`<br>
Preserved candidate branch: `candidate/preserve-nexkosmo-inspection-2026-08-20`<br>
Preserved candidate tip: `c26ee95fccc34891d514dcb528684698d933f758`<br>
Preservation digest: `585CED3089C167A55A09D01E408C81A2BD668734204F53763EB288E6BB3B59BF`

## Authority and evidence boundary

**CANDIDATE DOES NOT MEAN CANONICAL.**

Presence on the preserved candidate branch does not mean:

- approved architecture;
- approved product behaviour;
- approved migration;
- approved visual identity;
- approved public claims;
- approved provider integration;
- approved database schema; or
- Production readiness.

The candidate is immutable migration evidence and capability source. Candidate
documents, self-declared statuses, tests, mockups, fixtures, migrations and code
remain subordinate to manifest version 9, Director authority, approved decision
records and verified trusted-baseline evidence. Candidate ADRs `0001` through
`0007` remain evidence only even where they label themselves `accepted`.

Slice 1 creates this register and reconciles the trusted current-state projection.
It does not approve or implement Slice 2 or any later slice. No candidate commit is
merged or rebased by this slice.

## Canonical controls preserved

- Director authority and all STOP gates remain unchanged.
- The canonical workflow remains
  `IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`.
- Studio remains a contextual scene/shot deep editor opened from PRODUCTION, not a
  seventh top-level stage.
- The normal entry, screenplay-import entry and Production/Studio deep-edit loop
  remain distinct flows.
- Python/PostgreSQL owns canonical domain authority, persistence, RLS, readiness,
  audit, idempotency and truth.
- Frontend TypeScript may provide UI state, typed DTOs and HTTP clients, but must
  not become a second Brain.
- Retrieval Before Generation remains authoritative.
- Frozen canonical assets remain unchanged.
- The newer brighter Nexkosmo UI direction remains preferred.
- Useful legacy Set, Studio, CGI, VFX, Render, Pre-Production and related
  capability source must be preserved before consolidation or retirement.
- Market & Opportunity Intelligence and Growth Intelligence remain governed
  responsibilities within the existing intelligence architecture, not duplicate
  Brains.

## Migration slice register

Classification values are `PROMOTE`, `PROMOTE_WITH_CHANGES`,
`CAPABILITY_SOURCE_ONLY`, `DEFER`, `REJECT` and `NEEDS_DIRECTOR_REVIEW`.
Every slice after Slice 1 is blocked until the Director separately approves it.

| # | Slice | Candidate sources | Classification | Dependencies | Director decision state | Canon impact | Database impact | Routing impact | Security impact | Duplicate-Brain risk | Migration risk | Validation requirement | Rollback strategy | Current status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Governance / current-state reconciliation | Candidate ADRs `0001-0007`; architecture maps; roadmaps; Phase 2C inventory; trusted/candidate Git comparison | `PROMOTE_WITH_CHANGES` | None | **APPROVED for the three-file documentation-only slice** | Records authority; does not change canon | None | None | Low; evidence classification only | None | Low | Canon, alignment, drift, latent, authority and security verifiers; focused tests; Ruff; mypy; migration compilation; diff checks | Revert the isolated documentation commit | **ACTIVE — implementation and validation review; no staging/commit/push authorised yet** |
| 2 | Canonical branding and shared shell | `frontend/src/app/**`; `components/**`; `layouts/**`; shared styles/tokens; `assets/branding/**`; `public/landing/**` | `PROMOTE_WITH_CHANGES` | 1 | NOT APPROVED | High: shell and brand usage must resolve trusted canon | None | High | Medium: session and public-surface behaviour | Low in shell; landing state can imitate product truth | High | Canonical asset identity, accessibility, route/deep-link, visual and claims review | Revert isolated shell changes; retain canonical SVG/registry | BLOCKED — candidate evidence only |
| 3 | Project foundation | Python Project/Production aggregate, service, repository, schemas/routes; frontend Project DTO/client portions | `PROMOTE_WITH_CHANGES` | 1, 18, 19 | NOT APPROVED | High: ownership model | Migration `0004` | Medium | High: roles, membership, RLS, audit, idempotency | High if frontend in-memory gateway becomes authoritative | High | Domain/application/API tests; PostgreSQL repository, RLS, concurrency and role tests | Revert code; restore rehearsed DB backup if schema ran | BLOCKED — candidate evidence only |
| 4 | Character domain + API + persistence | Character Python vertical slice; Character workspace; frontend Character clients, services and registries | `PROMOTE_WITH_CHANGES` | 2, 3, 18, 19 | NOT APPROVED | High: species, compatibility and readiness rules | Migrations `0003`, `0007`, `0008` | High | High: tenant access, versions, audit/outbox | **Critical** in frontend schema, registry, compatibility, pipeline, preview and in-memory repository | High | Domain/API/client/UI tests plus real PostgreSQL/RLS and reload evidence | Revert per layer; restore DB backup | BLOCKED — candidate evidence only |
| 5 | Environment domain + API + persistence | Environment aggregate, service, repository, schemas/routes; Environment workspace and client | `PROMOTE_WITH_CHANGES` | 2, 3, 18, 19 | NOT APPROVED | High: type/capability/readiness catalogue | Migrations `0009-0011` | High | High: tenant and asset visibility | Medium: client must remain DTO/API projection only | High | Domain/API/repository/controller tests; PostgreSQL/RLS; readiness evidence | Revert per layer; restore DB backup | BLOCKED — candidate evidence only |
| 6 | IDEA stage | `IdeaPage`; Idea styles/test; Sophia runtime image | `PROMOTE_WITH_CHANGES` | 2, 3 | NOT APPROVED | Medium: canonical stage presentation | None in candidate | High | Medium: future voice/file/script inputs | Low currently | Medium | Component, route, accessibility, visual and persistence-boundary tests | Revert route/component | BLOCKED — candidate evidence only |
| 7 | DISCOVER stage | `DiscoveryPage`; Discovery styles/reference imagery; Movie Map fixtures | `CAPABILITY_SOURCE_ONLY` | 2, 3, 6; future Story model | NOT APPROVED | High: story/Movie Map behaviour | Missing | High | High for future uploads/AI/collaboration | High if browser state becomes story authority | High | Story-domain/API/persistence, state restoration, accessibility, visual and e2e tests | Keep source preserved; do not activate route | BLOCKED — candidate evidence only |
| 8 | SHAPE stage | `ShapePage`; script styles/reference imagery; screenplay/timeline fixtures | `CAPABILITY_SOURCE_ONLY` | 2, 3, 7; future Script/Scene model | NOT APPROVED | High: screenplay authority and provenance | Missing | High | High for import/collaboration | High if local screenplay becomes canonical | High | Script domain/API, import provenance, concurrency, accessibility, visual and e2e tests | Preserve design source only | BLOCKED — candidate evidence only |
| 9 | BUILD / Pre-Production | Shared Pre-Production presentation components; Character and Environment workspaces | `PROMOTE_WITH_CHANGES` | 2-5, 8 | NOT APPROVED | High: BUILD workspace and domain projection | Through approved domain slices only | High | High: canonical readiness and denied actions | High while Character frontend services own rules | High | Shared/UI/domain integration, API failure, accessibility, visual and e2e tests | Revert shared shell and adapters independently | BLOCKED — candidate evidence only |
| 10 | READY stage | `ReadyPage`; tests/styles; project and scene imagery | `CAPABILITY_SOURCE_ONLY` | 3-9; future authoritative readiness service | NOT APPROVED | Critical: production readiness | Missing for whole-project readiness | High | Critical: READY must fail closed and be auditable | **Critical** if client constants decide readiness | Critical | Server-authoritative blockers, provenance, permissions, audit and e2e tests | Retain visual source; do not activate decisions | BLOCKED — fixture state is not authoritative |
| 11 | PRODUCTION dashboard | Candidate `StudioPage`; Production styles/test/shot imagery | `NEEDS_DIRECTOR_REVIEW` | 2, 3, 10, 12 | NOT APPROVED | Critical: Production control behaviour | Missing | Critical | Critical: approve/repair/render actions need authority and audit | **Critical** for fixture validations and route choice | Critical | Production domain/API, authorization, audit, concurrency, provider and e2e tests | Preserve as prototype; activate no action | BLOCKED — implemented under conflicting Studio identity |
| 12 | Studio deep-editor boundary | `Open in Studio`; static landing Studio surface; Moment Workspace editing concepts | `NEEDS_DIRECTOR_REVIEW` | 7, 8, 11 | NOT APPROVED | Critical: Production/Studio boundary | Future Scene/Shot state | Critical | Critical: contextual authorization and audit | High if editing forks canonical state | Critical | Explicit context contract and full return/revalidation loop tests | Preserve all source; expose no operational boundary | BLOCKED — boundary unresolved |
| 13 | Set | `SetPage`; generic workflow scaffold; known legacy capability source outside this candidate slice | `CAPABILITY_SOURCE_ONLY` | 9, 12 | NOT APPROVED | Medium: capability placement | None implemented | High | Unknown | None implemented | High | Capability comparison, routing and workspace tests | Preserve scaffold and legacy source | BLOCKED — placeholder only |
| 14 | CGI | CGI navigation metadata; known legacy CGI source must remain inventoried | `DEFER` | 12; asset/render pipeline | NOT APPROVED | Medium | None implemented | Future | High: providers, generated binaries and provenance | None implemented | High/unknown | Capability inventory, threat model, provider and artifact tests | No promotion; preserve source | BLOCKED — no CGI implementation in candidate tip |
| 15 | VFX | VFX navigation/marketplace references; known legacy VFX source must remain inventoried | `DEFER` | 12; shot/asset/render pipeline | NOT APPROVED | Medium | None implemented | Future | High: plates, providers and generated artifacts | None implemented | High/unknown | Capability inventory, threat model, provider and artifact tests | No promotion; preserve source | BLOCKED — no VFX implementation in candidate tip |
| 16 | Render | `RenderPage`; generic workflow scaffold | `CAPABILITY_SOURCE_ONLY` | 11, 12, 18, 22 | NOT APPROVED | High: render/approval boundary | None implemented | High | Critical: provider credentials, jobs and artifacts | None implemented | High | Render contract, provider, provenance, authorization and e2e tests | Preserve placeholder; do not activate | BLOCKED — placeholder only |
| 17 | Finish / Delivery | No candidate implementation; legacy/future delivery capability remains an inventory obligation | `DEFER` | 10, 11, 16 | NOT APPROVED | High: rights, approvals and delivery | Missing | Future | Critical: signed delivery, retention and access | None | Unknown | Architecture, rights/provenance, authorization and delivery tests | No implementation to promote | BLOCKED — design/authority absent |
| 18 | Backend adapters / UoW / audit / outbox | `operational_adapters`; `outbox_dispatcher`; UoW/ports/config/auth/dependencies; deferred semantic-kernel boundary | `PROMOTE_WITH_CHANGES` | 1; required by 3-5 | NOT APPROVED | High: authority implementation | Migrations `0005`, `0006` and shared tables | API wiring | Critical: transaction, audit role, RLS, replay/idempotency | Low if semantic-kernel boundary remains honestly deferred | Critical | Reliability, transaction-fault, audit, outbox/inbox, RLS, idempotency and observability tests | Revert code; restore DB backup | BLOCKED — candidate evidence only |
| 19 | Candidate migrations `0003-0011` | Nine Alembic revisions covering Character, Project/Production, reliability, least privilege and Environment | `NEEDS_DIRECTOR_REVIEW` | Approved 3-5 and 18 designs | NOT APPROVED; **execution prohibited** | High: seed/catalogue decisions | **Critical and forward-only** | Indirect | Critical: grants, revokes, FORCE RLS and ownership | None | Critical | Per-revision review; upgrade from trusted snapshot; RLS/grants; backup/restore rehearsal; head verification | Restore verified backup; downgrades are intentionally unavailable | BLOCKED — not executed |
| 20 | Tests / contract / e2e / visual evidence | Candidate Python/frontend tests; route and component tests; reference/runtime imagery | `PROMOTE_WITH_CHANGES` | Every implementation slice | NOT APPROVED | Evidence only; may not redefine canon | Integration tests may exercise schema | Route tests | High: negative authorization/RLS must remain | Must assert frontend is non-authoritative | Medium | Preserve trusted assurance tests; add focused, contract, e2e and visual evidence without weakening gates | Revert only additive tests; never delete trusted detectors | BLOCKED — candidate test files are evidence, not current passes |
| 21 | Infrastructure / CI / Docker / routing | Candidate CI, Dockerfile, requirements, env templates, Vite/Vercel routing and migration-head verifier | `PROMOTE_WITH_CHANGES` | 2, 18-20 | NOT APPROVED | Medium: enforcement and release evidence | Can execute migrations | Critical | Critical: permissions, secrets, protection and dependency scanning | None | Critical | Preserve all trusted canon/security/authority/latent/repository gates; validate deep links and build isolation | Revert isolated infrastructure changes | BLOCKED — candidate CI would remove trusted gates if copied wholesale |
| 22 | External-service registry and integrations | No canonical registry; candidate landing simulates collaboration, rewards, marketplace, presence and activity | `DEFER` | Approved registry, security model and Director policy | NOT APPROVED | High: provider and public-behaviour claims | Future | High | Critical: Tier-4 credentials, webhooks, consent, receipts and replay | High if a new integration/marketing/social Brain is created | Critical | Registry, threat model, provider contract, idempotency, receipt and consent tests | Activate nothing; preserve UI evidence only | BLOCKED — no canonical registrations |

## Candidate evidence inventory coverage

The register explicitly preserves and evaluates the following candidate or legacy
capability source without promoting it:

- Project, Character and Environment;
- IDEA, DISCOVER, Moment Workspace, SHAPE, BUILD / Pre-Production, READY and
  PRODUCTION;
- Studio deep editor, Set, CGI, VFX, Render and Finish / Delivery;
- backend adapters, unit of work, audit, outbox, migrations `0003-0011`, tests,
  contracts, CI, Docker and routing;
- the cinematic landing, alternate shell/routing concepts and all runtime reference
  imagery; and
- external-service, collaboration, marketplace, rewards and social/integration
  concepts.

Absence of a complete CGI, VFX, Render, Finish/Delivery or Studio implementation in
the candidate tip is not permission to delete older capability source elsewhere.
Those sources remain protected by the migration inventory and Director-review gates.

## Recorded candidate conflicts — not repaired by Slice 1

1. Candidate deletion of governance files.
2. Candidate deletion of canonical assets.
3. Candidate deletion of assurance tests and verifier scripts.
4. Candidate ADRs labelled `accepted` without Director approval.
5. Stale or overstated candidate architecture and validation claims.
6. Page-specific noncanonical logos.
7. The PRODUCTION dashboard currently implemented as `StudioPage`.
8. Duplicate `/studio` and `/production` behaviour.
9. DISCOVER Moment Workspace and Studio responsibility overlap.
10. Placeholder Set and Render pages.
11. Missing CGI and VFX implementation in the candidate tip.
12. READY fixture state presented as authoritative.
13. PRODUCTION fixture validation presented as authoritative.
14. Frontend Character/Project Brain duplication risks.
15. Candidate migrations containing product catalogue and seed decisions.
16. Unsupported public landing claims and simulated product/business state.
17. Candidate status documents that do not describe the trusted baseline.
18. External services not represented by an approved canonical registry.

These conflicts are migration gates. Recording them is not approval to repair them
and does not change the classification of any later slice.

## Public-claim publication block

The following candidate claims or representations are **BLOCKED FROM PUBLICATION**
unless independently evidenced and Director-approved:

- Disney, Netflix, Sony Pictures, Universal Pictures and Epic Games names or implied
  trust/affiliation;
- creator counts, generated-asset counts and uptime claims;
- creator earnings, marketplace balances, prices or sales;
- simulated production budgets, credits, rendering costs or completion times;
- fake live presence, membership state, collaboration activity, achievements,
  publications or sales; and
- any other fixture, estimate, mockup or candidate statement presented as current
  product or business fact.

Slice 1 does not modify those candidate surfaces. It records the publication block.

## Slice status and STOP rules

- Only Slice 1 has Director approval.
- Slice 1 permits changes only to this register, `docs/CURRENT_STATE.md` and
  `docs/ENGINEERING_STATUS.md`.
- A later slice may begin only after its exact files, boundaries, tests, security
  implications, rollback and Director decision are reviewed.
- Candidate migrations `0003-0011` must not execute during Slice 1.
- Candidate branches, commits, assets, documents and tests remain unchanged.
- No merge, deployment, Production action, branch-protection change or canon/frozen
  asset change is authorised by this register.
