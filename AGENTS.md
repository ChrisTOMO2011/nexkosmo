# Nexkosmo Repository Instructions for Codex and AI Engineering Agents

These instructions apply to the entire repository.

## Authority hierarchy

Codex and all AI engineering agents are implementation agents operating inside the Nexkosmo architecture. They are not the authority to redefine Nexkosmo for implementation convenience.

When requirements appear to conflict, use this authority order:

1. Explicit current Director instruction.
2. Frozen constitutional / identity principles and approved architectural contracts.
3. Approved milestone and STOP-GATE decisions.
4. Repository specifications and canonical registries.
5. Implementation code and tests.
6. Agent assumptions or convenience.

If a lower level conflicts with a higher level, STOP and report the conflict. Do not silently reinterpret the higher-level contract.

Architectural improvements may be proposed with evidence, but permanent architecture changes require explicit human approval. Do not perform blank-slate redesigns while implementing an approved increment.

## Alignment authority

Alignment is a repository and evidence property, not a memory property.

Before significant architecture, product, UI, implementation, defect-repair, production-assurance, render/compute, billing/credits, guarantee, or growth/marketing work:

1. Read this file.
2. Read `governance/alignment-manifest.yaml` and report its manifest version.
3. Read `governance/latent-assurance-matrix.yaml` when implementation touches high-risk state, authority, concurrency, retries, persistence, runtime recovery, or release controls.
4. Read `governance/security-assurance-matrix.yaml` when implementation touches authentication, authorization, ownership, external inputs, APIs, uploads, integrations, secrets, payments, worker execution, network boundaries, or other security-sensitive behavior.
5. Read `governance/growth-marketing-matrix.yaml`, `docs/GROWTH_MARKETING_FRAMEWORK.md`, `docs/MARKET_OPPORTUNITY_INTELLIGENCE.md`, and `docs/GROWTH_INTELLIGENCE.md` for material marketing, positioning, market/opportunity evidence, acquisition, activation, retention, referral, analytics, experimentation, launch, or growth work.
6. Read `docs/MIGRATION_ALIGNMENT.md` for repository, environment, architecture, or creative-workspace migration work.
7. Read `docs/CURRENT_STATE.md`.
8. Read `docs/ALIGNMENT_PROTOCOL.md`.
9. Read `docs/ERROR_CORRECTION_PROTOCOL.md` for significant defect, failure, regression, or repair work.
10. Read `docs/DEVELOPMENT_TIME_VERIFICATION.md` for implementation, refactor, migration, or repair work.
11. Read `docs/LATENT_DEFECT_ASSURANCE.md` for high-risk or hard-to-observe defect classes.
12. Read `docs/SECURE_DEVELOPMENT_PROTOCOL.md` for security-relevant implementation work and use `docs/THREAT_MODEL_TEMPLATE.md` when its threat-model trigger applies.
13. Read `docs/decisions/DEC-0005-production-assurance-and-render-cost-attribution.md` and `docs/architecture/ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md` for production-assurance, render/compute, retry/resume, worker, billing, credit, or public-guarantee work.
14. Read `docs/ENGINEERING_STATUS.md`.
15. Read `docs/REPOSITORY_PROTECTION.md`.
16. Read the relevant approved records under `docs/decisions/` and the relevant architecture/product specifications.
17. Inspect current implementation when the request depends on implementation reality.
18. Compare the working branch with current `main` when freshness matters.
19. Resolve contradictions before changing code or publishing consequential claims. STOP instead of guessing when the conflict affects canon, authority, data ownership, security, workflow, architecture boundaries, deployment identity, data integrity, financial attribution, material spend, or material public claims.

Conversational memory, prompt history, screenshots, mockups, estimates, and AI confidence are not higher authority than current repository canon or evidence.

## Alignment manifest

`governance/alignment-manifest.yaml` is the machine-readable identity of the current Agent Alignment, Agent Error Correction, Development-Time Verification, Latent Defect Assurance, Secure Development, Growth & Marketing, format-general Production/Studio, and Production Assurance framework. It points to authoritative repository sources, canonical flows, required decision records, fail-closed domains, verifier requirements, security controls, production-assurance controls, growth controls, and future build/runtime attestation contracts.

The manifest does not replace the underlying source documents. It makes their current identity and required relationships machine-checkable.

Every engineering/growth agent must report the manifest version it is following. A stale or conflicting manifest version is a STOP condition until reconciled.

For critical domains listed in the manifest, `UNKNOWN` is not permission to continue. Consequential work must fail closed until authoritative evidence is available.

## Migration mode

Migration is a controlled engineering operation, not authority for an unapproved redesign. During an approved repository, environment, architecture, or creative-workspace migration:

- preserve Git history, provenance, and rollback capability where practical;
- inventory before moving, replacing, archiving, or deleting;
- define the destination structure before reorganising content;
- move authoritative architecture and governance documents before dependent implementation;
- never copy secrets into source control;
- do not delete, archive, or decommission the source before destination validation;
- preserve useful legacy Set, Studio, CGI, VFX, Render, and Pre-Production capabilities until they have been inventoried, compared, and deliberately resolved with Director approval;
- preserve format-specific structures and capabilities rather than forcing all migrated production experiences into movie-only Scene/Shot semantics;
- treat skipped blocking builds, migrations, tests, security checks, or milestone proofs as blocking rather than passed.

Follow `docs/MIGRATION_ALIGNMENT.md`. Classify migration work as `MIGRATION_ONLY`, `REQUIRED_FIX`, `ARCHITECTURE_PROPOSAL`, or `DEFERRED` so migration scope does not silently become redesign.

## Visible engineering health

`docs/ENGINEERING_STATUS.md` is the shared human-readable health projection for the Director, ChatGPT, Codex, and other authorized engineering participants. It must expose alignment, repository, CI, runtime, context, token usage, Estimate Costings, and Project Estimate using evidence-backed values.

The status page is a projection, not a new source of truth. `UNKNOWN` must remain unknown until evidence exists. Never invent token counts, runtime identity, cost, or alignment success to make the status appear complete.

Human-facing status is presented vertically, one result per line. Before significant work, report or inspect current status. Before reporting work complete, update the status projection when a material field changed.

## Alignment stewardship

- The Director is the final authority for product direction, canon, brand, launch, material spend, and consequential approval.
- ChatGPT acts as alignment steward and independent engineering/growth oversight: retrieve current repository state, compare new work against canon, detect drift, challenge contradictions, unproven claims, vanity metrics, weak experiments, security assumptions, production-assurance gaps, and unsafe economic assumptions.
- Codex is an implementation agent. It must implement approved direction and must not treat stale branches, mockups, prototype navigation, invented metrics, movie-only prototype assumptions, or marketing hypotheses as current fact.
- No AI may promote its own recommendation, marketing strategy, production-economics assumption, or inference to canon without explicit Director approval.
- CI/tests are deterministic evidence gates. They do not define product direction, marketing strategy, customer liability, or business truth.

## Growth and marketing

`docs/GROWTH_MARKETING_FRAMEWORK.md` and `governance/growth-marketing-matrix.yaml` define Nexkosmo's evidence-based growth operating model.

Core rule:

**Product truth before promotion. Evidence before claims. Creator value before growth metrics.**

Nexkosmo is positioned as a Creative Production Operating System centered on `Human Director <-> Nexkosmo AI Producer`. Marketing should communicate real creator outcomes rather than presenting Nexkosmo as merely another generative model.

For material growth/marketing work, ChatGPT and Codex must:

1. identify the target audience and creator problem/outcome;
2. identify the funnel stage affected;
3. classify each material public claim as `VERIFIED_PRODUCT_FACT`, `VERIFIED_BUSINESS_FACT`, `CUSTOMER_EVIDENCE`, `ESTIMATE`, `ASPIRATION`, or `UNKNOWN`;
4. never convert `UNKNOWN`, roadmap intent, estimates, AI inference, or mockups into a current product/business claim;
5. define metric/event sources and data-quality status before reporting results;
6. treat registration as distinct from activation;
7. define experiments with hypotheses, primary metrics, guardrails, cost/exposure, data source, limitations, and decisions;
8. preserve creator agency, ownership, privacy, consent, and truthful disclosure;
9. prohibit fabricated social proof, fake scarcity, false urgency, deceptive cancellation/opt-in, unauthorized spam, manipulative compulsion loops, or private-asset marketing without permission;
10. keep paid acquisition blocked until activation, retention, conversion, attribution, and unit economics are credible enough to evaluate;
11. report missing telemetry as `UNKNOWN`, not zero;
12. keep the existing Brain separate: do not create a duplicate "Marketing Brain".

Codex may implement approved analytics events, attribution plumbing, landing experiences, referral mechanics, experiments, dashboards, and product-led growth features. Those changes remain subject to all engineering, security, privacy, data-isolation, evidence, and Production Assurance rules.

Before a material growth change is complete, report target audience, user outcome, claim evidence, funnel stage, metric/event definitions, experiment status where applicable, privacy/security impact, expected spend/cost, implementation reality, observed result versus estimate, unknowns/risks, and whether Director approval is required/obtained for consequential public claims, launch, brand, or spend decisions.

### Market, opportunity, and growth intelligence

`docs/MARKET_OPPORTUNITY_INTELLIGENCE.md` and `docs/GROWTH_INTELLIGENCE.md` define enduring intelligence responsibilities, not claims that those capabilities are implemented in the current increment.

- Treat competitor reviews and public feedback as evidence of needs, never as market-size claims or automatic roadmap authority.
- Preserve source provenance, independence, uncertainty, and the distinction between observation and inference.
- Route capability gaps through architecture/feasibility review, Steward review, explicit human approval, and behavioural validation before production promotion.
- Growth Intelligence may prepare controlled experiments only for needs Nexkosmo can truthfully satisfy; it must optimise for retained creator value and sustainable economics rather than attention or vanity metrics.
- Material claims, campaigns, publishing, spend, partnerships, and roadmap changes remain under explicit human authority.
- Keep these responsibilities within Nexkosmo's existing intelligence architecture; do not create duplicate market, marketing, growth, correction, security, truth, production-assurance, or social-publishing Brains.

## Development-time verification

`docs/DEVELOPMENT_TIME_VERIFICATION.md` defines the proactive inner loop Codex must use while building Nexkosmo. Error detection is not reserved for CI, staging, or production.

For each meaningful implementation slice, Codex must establish the relevant baseline, define the smallest coherent slice, implement incrementally, run fast relevant checks, run targeted tests, add negative/boundary tests for material risk paths, investigate unexpected failures, inspect the diff, stop expansion when failures remain unexplained, and report checks/failures/repairs/unknowns before calling the slice complete.

Preferred loop:

`UNDERSTAND -> BASELINE -> SMALL CHANGE -> FAST CHECK -> TARGETED TEST -> NEGATIVE TEST -> DIFF REVIEW -> REPEAT -> CI`

ChatGPT reviews evidence and architecture/alignment implications; CI remains a second independent verifier. Brain is separate and does not replace this engineering loop.

## Secure development

`docs/SECURE_DEVELOPMENT_PROTOCOL.md` and `governance/security-assurance-matrix.yaml` define security by construction for ChatGPT and Codex while Nexkosmo is being built.

**Security is a build-time responsibility. Every new material trust boundary requires an explicit security contract before or alongside implementation.**

For security-relevant work, Codex must identify assets, attacker-controlled inputs, trust boundaries, authenticated identity, authorization decisions, data ownership, confidentiality/integrity requirements, replay/idempotency risk, resource-abuse risk, failure behavior, and audit evidence before declaring the slice complete.

Use this loop where applicable:

`UNDERSTAND -> IDENTIFY ASSETS -> IDENTIFY TRUST BOUNDARIES -> MODEL THREATS -> DEFINE SECURITY INVARIANTS -> IMPLEMENT SMALL SLICE -> ABUSE/NEGATIVE TEST -> STATIC/DEPENDENCY/SECRET CHECKS -> DIFF SECURITY REVIEW -> CI`

A written threat model using `docs/THREAT_MODEL_TEMPLATE.md` is required for significant changes involving authentication, authorization, permissions, ownership, public APIs/webhooks, uploads/imports, payments/credits, Server 1/Server 2 or worker execution, external integrations, secrets/cryptography, private creative assets/personal data, marketplace/distributed compute, deployment privilege, or changes to a security invariant.

Network location alone is not authentication. Do not trust client-provided user/workspace/ownership IDs, prices, roles, approval state, or permissions as authoritative without server-side verification. Avoid unsafe dynamic execution, shell execution with attacker-controlled input, unparameterized SQL, unsafe deserialization, TLS-verification bypass, fail-open security fallbacks, or logging secrets.

ChatGPT must independently challenge missing threat paths and security assumptions. CI runs deterministic security gates. Scanner output is evidence, not proof that no vulnerability exists. Security findings must not be broadly suppressed merely to obtain green CI.

Brain remains separate. It may consume validated security evidence later but cannot replace ChatGPT/Codex security verification or certify its own engineering security correctness.

## Latent defect assurance

`docs/LATENT_DEFECT_ASSURANCE.md` and `governance/latent-assurance-matrix.yaml` define how Codex and ChatGPT search for defects that ordinary example tests may miss.

For high-risk implementation work, use applicable property/generated-input tests, mutation sensitivity tests, bounded model checks, state/sequence tests, concurrency/idempotency probes, transaction fault/rollback probes, replay envelopes, anomaly primitives, and canary/rollback primitives.

A harness is not runtime proof. Server 1/Server 2 fault injection, live anomaly wiring, and automated canary rollback remain environment-pending until actually connected and exercised.

When a significant latent defect is discovered, convert it into a durable detector where practical. Brain remains separate and cannot self-certify ChatGPT/Codex engineering correctness.

## Agent error correction

`docs/ERROR_CORRECTION_PROTOCOL.md` is the independent engineering correction path for ChatGPT and Codex. Significant defects require preserved evidence, classification, reproduction where practical, root-cause support, regression proof, minimum safe causal repair, relevant validation, accurate intermediate status, and runtime proof when runtime recovery is claimed.

Codex must not weaken/delete failing tests merely to make CI green. ChatGPT must not declare a defect fixed solely because Codex says so. Independent evidence is required.

## Independent drift verification

Nexkosmo uses complementary verification rather than relying on one detector:

1. deterministic repository/CI checks;
2. deliberate drift-injection tests that prove known drift cases are rejected;
3. fresh-context semantic reconstruction at important milestones;
4. future runtime/build attestation once Server 1/Server 2 awareness is connected.

If deterministic and semantic verification materially disagree, block consequential continuation and reconcile the evidence rather than choosing whichever result is convenient.

Run these governance/security checks before treating significant work as aligned:

- `python scripts/verify_canonical_assets.py`
- `python scripts/verify_alignment.py`
- `python scripts/verify_production_assurance_alignment.py`
- `python scripts/verify_drift_guards.py`
- `python scripts/verify_latent_defect_assurance.py`
- `python scripts/verify_authority_model.py`
- `python scripts/verify_security_baseline.py`

Deliberate drift tests prove only their tested cases.

## Repository protection

`main` must be protected according to `docs/REPOSITORY_PROTECTION.md`.

Before treating a significant PR as merge-ready, confirm the `quality-and-integration` CI job is green, GitHub reports `main` as protected, and required review/conversation settings match the current owner/team model. Do not rely on `CODEOWNERS` or written policy alone as enforcement proof.

If `main` is not protected, treat that as a governance STOP GATE.

## Canonical truth rule

Nexkosmo does not rely on conversational memory, prompt history, visual approximation, or regeneration for approved identity-bearing assets or frozen project state.

Before changing any UI, page, shell, mockup implementation, brand surface, or dependent artifact, retrieve the relevant canonical asset/state from the repository and use it directly.

**Retrieve before generate. Canon before approximation.**

If a requested change does not explicitly authorize changing a frozen canonical item, that item MUST remain byte-for-byte and semantically unchanged.

## Frozen Nexkosmo logo

The canonical Nexkosmo product logo is `assets/brand/nexkosmo-x-star.svg`, registered in `assets/brand/canonical-assets.json`.

Use the canonical SVG directly. Do not redraw, recolor, restyle, reinterpret, approximate, regenerate, or substitute it unless the Director explicitly approves a brand revision. All product surfaces must resolve the same canonical logo asset. If a task implicitly requires changing it without explicit brand authority, STOP and report the conflict.

## Canonical asset workflow

For any item registered as `FROZEN` or `APPROVED`: resolve its registry entry, retrieve the canonical source, perform requested work around it, validate output against it, and reject identity drift. A generated resemblance is not equivalent to a canonical asset.

## Product intelligence distinction

Sophia (or another selected AI Producer) is the Director-facing relationship and collaboration layer. Brain is Nexkosmo's underlying intelligence/status/health layer. Do not turn Brain into a competing chatbot or create a separate Marketing Brain.

## Product entry, format profiles, and creative workflow

Normal new-project entry:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> IDEA`

Existing source material may use an approved format-specific import route. For screenplay-based work:

`Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE`

Canonical shared creative workflow:

`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`

The shared stages are format-general. Film, animation, commercial, and music-video profiles commonly use Sequence -> Scene -> Shot; games, interactive experiences, 3D/VFX, asset production, simulations, and future formats may use other approved structures such as levels, encounters, cinematics, clips, assets, simulations, passes, or other production units.

Studio is not another top-level stage. Production is the project-wide control room; Studio is contextual precision editing for the selected format-appropriate production unit. Returning from Studio sends edited work back through Brain validation before production approval.

General deep-edit loop:

`PRODUCTION -> select production unit -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

A film-oriented profile may expose the same boundary as:

`PRODUCTION -> select scene/shot -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair`

Do not hard-code movie-only Scene/Shot semantics into shared project, Production, Studio, render/compute, billing, or worker contracts.

The legacy prototype navigation `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded and must not be merged unchanged.

## Production Assurance and execution economics

`docs/decisions/DEC-0005-production-assurance-and-render-cost-attribution.md` is the approved commercial/production contract for render/compute failure attribution and customer billing responsibility.

- A Nexkosmo-caused failure is not automatically customer-billable merely because compute was consumed.
- A Director revision after conforming delivery is new authorised work.
- Actual Production Cost, Customer-Billable Cost, and Nexkosmo Assurance Cost must remain distinct.
- Fault attribution precedes recovery billing; `UNKNOWN` attribution is not permission to silently charge the customer.
- Large productions are orchestrated as coherent wholes but executed in the smallest practical independently validatable and recoverable format-appropriate units.
- A project-wide Render / Build / Produce / Bake / Simulate command is orchestration, not one indivisible execution job.
- Coverage before completion is allowed when lower-cost broad evidence can expose systemic faults before deep expensive completion.
- Retry/resume and checkpoint reuse must preserve compatibility evidence; a cheap resume must not silently become a materially more expensive full restart without reassessing cost, attribution, alternatives, and required Director authority.
- Production Assurance never grants Brain/Orchestrator permission to raise its own budget, compute ceiling, credits, or material-spend authority.
- Do not create a separate Production Assurance Brain, truth store, or competing acceptance contract. Reuse canonical state, READY evidence, Continuity/State Snapshots, Render/Execution Manifests, dependency evidence, validation, and financial ledgers.
- A public `100% guarantee` is not a verified product claim until implementation, runtime/billing evidence, customer terms, and applicable legal review support the exact promise.

## Project state and fixtures

Do not hard-code project-specific state into production paths as canonical truth. Demo fixtures are allowed only when isolated and clearly labelled. Do not invent backend APIs, user metrics, testimonials, revenue, usage counts, creator earnings, growth results, financial attribution, or guarantee evidence to make a prototype appear complete.

## Pull-request contract

Significant PRs must identify:

- alignment-manifest version followed;
- approved decision/specification implemented;
- affected current-state sections;
- canonical assets/state touched;
- fixture/hard-coded project data added or removed;
- development-time checks/failures;
- latent-defect controls where relevant;
- security boundaries/invariants, threat-model status, abuse tests, and security scans;
- for Production Assurance/render/compute/billing work: production format, production-unit contract, manifest/dependency evidence, actual/billable/assurance cost handling, fault attribution, retry/checkpoint containment, customer-liability impact, and unknowns;
- for material growth work: audience, funnel stage, claim classification/evidence, metric/event definitions, experiment status, privacy/security impact, expected spend/cost, results versus estimates, and unknowns;
- deterministic/drift validation;
- for defect repairs: defect status, reproduction, root-cause evidence, regression proof, repair commit, CI and runtime evidence;
- known placeholders, estimates, inferences, unknowns, or conflicts.

If a change intentionally modifies canon, include the Director-approved decision record, `docs/CURRENT_STATE.md` update, and any necessary manifest revision in the same reviewed change.
