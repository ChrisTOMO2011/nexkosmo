# Nexkosmo Secure Development Protocol

Status: APPROVED GOVERNANCE PROTOCOL
Authority: Director
Scope: ChatGPT, Codex, CI, repository, development, staging, deployment, and runtime security evidence.

## Purpose

Security is a build-time responsibility. Nexkosmo must not wait until a feature is finished, deployed, or exposed to users before asking whether it is safe.

This protocol requires ChatGPT and Codex to apply **security by construction** while Nexkosmo is being designed and implemented.

It remains separate from the Nexkosmo Brain. Brain may later consume validated security evidence, but Brain is not the sole security reviewer, scanner, verifier, incident authority, or certification path for ChatGPT/Codex engineering work.

## Core rule

**Every new trust boundary must have an explicit security contract before or alongside implementation.**

Codex must not rely on "remembering security". Security-sensitive assumptions must be represented in code, tests, configuration, CI checks, threat models, or other durable evidence where practical.

## Secure implementation loop

For meaningful work that introduces or changes a trust boundary, sensitive asset, authority decision, external integration, privileged operation, or security control, use:

`UNDERSTAND -> IDENTIFY ASSETS -> IDENTIFY TRUST BOUNDARIES -> MODEL THREATS -> DEFINE SECURITY INVARIANTS -> IMPLEMENT SMALL SLICE -> ABUSE/NEGATIVE TEST -> STATIC/DEPENDENCY/SECRET CHECKS -> DIFF SECURITY REVIEW -> CI -> STAGING/RUNTIME PROOF WHEN APPLICABLE`

Security review happens during implementation, not only at the end.

## Mandatory security questions while coding

Codex and ChatGPT must consider, as applicable:

- Who is authenticated?
- Who is authorized to perform this exact action on this exact resource?
- Is authorization derived from trusted server-side state rather than client claims?
- What data is sensitive, private, proprietary, personal, financial, canonical, or security-critical?
- What crosses a trust boundary?
- What input is attacker-controlled?
- What happens with malformed, oversized, duplicated, reordered, stale, replayed, or intentionally hostile input?
- Can one user or workspace read, modify, enumerate, infer, or delete another user's data?
- Can an AI/service identity exercise human-only authority?
- Can a retry or race cause duplicate effects?
- Can a failure leave partially committed or insecure state?
- Are secrets or credentials exposed in source, logs, telemetry, URLs, exceptions, artifacts, images, prompts, or test fixtures?
- Are external requests constrained against SSRF, redirect abuse, unsafe schemes, and internal-network access where relevant?
- Can files escape intended storage paths, masquerade as another type, exceed resource limits, or execute unexpectedly?
- Are dependencies and container/runtime components trustworthy and vulnerability-scanned?
- Is encryption/TLS verification being weakened?
- Is a dangerous default or fallback converting a security failure into success?
- Is the action independently auditable?
- Is rollback/recovery safe if the change is compromised or fails?

If a relevant answer is `UNKNOWN` in a critical security domain, consequential implementation must fail closed until evidence resolves it.

## Security invariants

High-value security rules should be expressed as executable invariants where practical. Current examples include:

- non-human agents cannot exercise human decision authority;
- authenticated decision attribution must match the human principal exercising authority;
- workspace isolation must not rely only on UI filtering;
- authentication tokens must be cryptographically verified with intended issuer/audience and required claims;
- database transactions must not leave partial state after failure;
- duplicate logical operations must not silently create duplicate protected effects;
- canonical state must not be overwritten by unapproved generated output;
- authorization failure must fail closed.

As new systems are introduced, add explicit invariants for uploads, payments, worker execution, storage, marketplace actions, distributed compute, publishing, and rights/consent.

## Trust-boundary contracts

A trust-boundary contract should identify at minimum:

- boundary name;
- assets/data crossing it;
- authenticated identity;
- authorization decision;
- accepted input/schema;
- confidentiality requirements;
- integrity requirements;
- replay/idempotency requirements;
- resource/rate limits where relevant;
- failure behavior;
- audit/telemetry evidence;
- security tests;
- remaining unknowns.

Important Nexkosmo boundaries include or will include:

- browser/client -> public API;
- Cloudflare/edge -> Server 1;
- Server 1 -> PostgreSQL/Redis/storage;
- Server 1 -> Server 2 GPU worker;
- worker -> renderer/model/tool;
- upload/import -> asset pipeline;
- Stripe/payment provider -> billing/ledger;
- external model/tool/provider -> Nexkosmo services;
- future distributed worker -> control plane;
- marketplace participant -> creator/asset/project state.

Network location alone is not authentication. Internal services still require appropriate identity, authorization, integrity, and least-privilege controls.

## Authentication and authorization

- Authenticate identities at trusted boundaries.
- Authorize every consequential action against server-side policy/state.
- Prefer least privilege and explicit allow rules.
- Treat user IDs, workspace IDs, ownership IDs, prices, roles, approval states, and permissions supplied by clients as untrusted claims until verified.
- Human-only actions require authenticated human authority; AI/service identities may not self-promote into human authority.
- Avoid authorization decisions based only on route hiding, frontend state, network source, or possession of an object identifier.

## Input and output handling

- Validate structure, type, size, range, encoding, and allowed values at trust boundaries.
- Use parameterized database operations; do not construct SQL from untrusted input.
- Avoid shell execution with attacker-controlled data. `shell=True`, `eval`, `exec`, unsafe deserialization, and equivalent dynamic execution require explicit security justification and targeted tests.
- Escape or encode output for its destination context.
- Do not return internal stack traces, secrets, credentials, raw tokens, private filesystem paths, or unnecessary internal implementation detail to untrusted clients.

## Secrets and credentials

Secrets must not be committed to source control.

Required practices:

- use environment/secret-management mechanisms rather than source literals;
- commit examples/placeholders only, never working credentials;
- redact tokens, passwords, signing material, payment secrets, API keys, and private keys from logs/evidence;
- rotate a secret if repository exposure is suspected; deleting the source line is not sufficient remediation;
- never use production secrets in tests;
- keep `.env` ignored and use `.env.example` only for non-secret configuration shape.

CI includes deterministic current-tree secret-pattern checks. This is defence in depth, not proof that repository history has never contained a secret.

## Dependency and supply-chain security

- Keep dependencies minimal and intentional.
- Audit Python dependencies for known vulnerabilities in CI.
- Run package consistency checks.
- Do not add a dependency merely to avoid implementing a small safe primitive.
- Review major new dependencies for maintenance, provenance, permissions, transitive risk, and licensing.
- Before production maturity, move from broad compatible ranges to a reproducible lock/pinning strategy with controlled update/audit workflow.
- Pin third-party CI actions to reviewed immutable revisions where practical as the workflow matures.

A vulnerability scanner result is evidence for known published vulnerabilities at scan time, not proof that a dependency is safe.

## Static security analysis

CI must run security-focused static analysis over security-relevant Python code. Findings are triaged by evidence and severity rather than suppressed merely to make CI green.

If a scanner finding is a false positive, document the reason and use the narrowest justified suppression. Broad exclusions require review.

## Files and uploads

When file/asset ingestion is implemented:

- server-generated storage identifiers should be preferred over trusting client filenames;
- prevent path traversal and unintended overwrite;
- enforce size/type/content constraints appropriate to the feature;
- isolate untrusted uploads from executable/application paths;
- do not trust MIME type or extension alone;
- scan/quarantine where threat model requires it;
- enforce ownership/workspace access at retrieval as well as upload;
- use signed/expiring access where private-object delivery requires it;
- preserve provenance without exposing private storage topology.

## Server 1 and Server 2

Server 2 must remain a restricted execution worker, not an implicitly trusted general-purpose remote execution target.

The eventual Server 1 -> Server 2 security contract must include:

- authenticated control-plane identity;
- message/job integrity;
- strict job schema and allow-listed operations;
- replay/idempotency controls;
- resource/time/VRAM/storage limits;
- no unrestricted arbitrary shell execution from user-supplied content;
- isolated temporary working data;
- validated result metadata;
- least-privilege network access;
- audit/correlation identity;
- safe failure on malformed/expired/unauthorized jobs.

These runtime controls remain unverified until the actual Server 1/Server 2 path is connected and tested.

## Payments and financial state

When billing is implemented:

- never trust client-provided price/credit entitlement as authoritative;
- verify provider signatures/events;
- use idempotency for financial effects;
- keep a durable auditable ledger;
- reconcile provider state with internal state;
- separate estimate costings from actual financial evidence;
- test duplicate, reordered, delayed, forged, and replayed events.

## Logging, telemetry, and error handling

Security-relevant events should be attributable without exposing secrets.

Capture where applicable:

- correlation/request/job identity;
- authenticated actor/service identity;
- action and target identity;
- allow/deny/failure outcome;
- security error code/category;
- relevant deployment/configuration identity.

Do not log bearer tokens, passwords, signing keys, payment secrets, private keys, unnecessary personal data, or private chain-of-thought.

## Threat modelling trigger

A written threat model is required for significant changes involving any of:

- authentication/session/token behavior;
- authorization/permissions/ownership;
- public API or webhook exposure;
- file upload/import or user-controlled media;
- payment/credits/billing;
- Server 1/Server 2 or worker execution;
- network boundary or external integration;
- secrets/cryptography/key handling;
- private creative assets or personal data;
- marketplace/distributed compute;
- deployment privilege or production administration;
- changes to a security invariant.

Use `docs/THREAT_MODEL_TEMPLATE.md`. A trivial change need not generate paperwork merely because it touches the same directory.

## Abuse and negative testing

For security-relevant changes, test how the feature fails, not only how it succeeds.

Examples:

- unauthenticated request;
- wrong workspace/user;
- missing/expired/invalid token;
- unauthorized role/action;
- forged ownership/resource ID;
- malformed/oversized input;
- duplicate/replayed request;
- concurrent operation;
- stale state;
- injection/path traversal attempts;
- denied external destination;
- invalid webhook signature;
- worker message tampering;
- security control unavailable.

## Security completion rule

A security-sensitive slice is not complete merely because its happy path works.

Before completion, Codex must report:

- assets/trust boundaries affected;
- security invariants applied;
- abuse/negative tests run;
- static/dependency/secret checks run;
- threat model status where required;
- security findings introduced/resolved;
- controls not tested and why;
- remaining security unknowns.

ChatGPT reviews the security evidence and challenges missing threat paths. CI independently executes available deterministic security gates.

## Security failure handling

Security findings use `docs/ERROR_CORRECTION_PROTOCOL.md` for evidence, severity, containment, causal repair, regression proof, verification, and closure.

Do not silently downgrade, suppress, or work around a security failure merely to continue feature development.

## Brain separation

The security chain remains independent engineering assurance:

`Director authority -> security contracts/policy -> ChatGPT oversight -> Codex secure implementation -> security tests/scanners -> CI evidence -> staging/runtime security evidence -> release decision`

Brain may later consume validated security evidence for reasoning and recommendations, but cannot self-certify ChatGPT/Codex security correctness or replace independent security controls.
