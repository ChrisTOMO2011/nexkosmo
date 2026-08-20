# Nexkosmo Agent Error Correction Protocol

Status: APPROVED GOVERNANCE PROTOCOL
Authority: Director
Scope: ChatGPT, Codex, repository evidence, CI, tests, and engineering defect handling.

## Purpose

This protocol defines how Nexkosmo detects, investigates, repairs, verifies, and learns from software and engineering errors involving ChatGPT and Codex.

It exists to prevent AI engineering agents from hiding, guessing through, repeatedly reintroducing, or incorrectly declaring software defects fixed.

## Permanent scope boundary

This is an **Agent Error Correction Layer** for ChatGPT and Codex.

It is deliberately separate from the Nexkosmo Brain.

- ChatGPT performs engineering oversight, evidence review, error classification, root-cause challenge, alignment review, and verification review.
- Codex performs implementation, reproduction, tests, and approved repairs.
- CI and deterministic tests provide independent engineering evidence.
- The Director remains final authority for consequential product, canon, security, architecture, and release decisions.
- The Brain remains Nexkosmo's separate intelligence architecture and must not become the correction authority for ChatGPT or Codex.

Future Brain integrations may consume defect, test, CI, runtime, and recovery records as **external evidence**. They must not turn this protocol into a duplicate Brain truth, reasoning, Guardian, continuity, or recovery system.

**Agent error correction evidence may inform Brain. Brain does not replace the independent engineering correction path.**

## Core rule

A bug is not fixed because an error message disappeared.

A defect is fixed only when:

1. the failure is detected and evidence is preserved;
2. the affected scope and severity are classified;
3. the failure is reproduced when practical;
4. the causal mechanism is understood to the level justified by evidence;
5. a regression test or equivalent proof exists where practical;
6. the minimum safe repair is implemented;
7. relevant independent checks pass;
8. runtime/staging behavior is verified where the defect reaches runtime;
9. unresolved uncertainty remains explicitly labelled;
10. the defect record can explain what happened, why, how it was fixed, and how recurrence will be detected.

## Error lifecycle

Use this lifecycle for significant defects:

`DETECTED -> EVIDENCE_CAPTURED -> CLASSIFIED -> CONTAINED -> REPRODUCED -> ROOT_CAUSE_SUPPORTED -> REGRESSION_PROOF_ADDED -> FIXED_IN_CODE -> VERIFIED_IN_CI -> VERIFIED_IN_STAGING/RUNTIME -> CLOSED`

A state may be skipped only when it does not apply and the reason is recorded. For example, a documentation-only test defect may not require runtime verification.

If reproduction or root cause is not established, use `UNKNOWN`, `NOT_REPRODUCED`, or `SUPPORTED` rather than claiming certainty.

## Severity

### CRITICAL

Use `CRITICAL` when a defect could cause or has caused one or more of:

- unauthorized canonical or ownership changes;
- security compromise or credential exposure;
- irreversible or widespread data corruption;
- human-authority bypass;
- destructive production behavior;
- material consent/rights violation;
- inability to trust the system's source of truth.

Action: **STOP affected consequential operations, preserve evidence, contain first, repair second.**

### HIGH

Use `HIGH` when the defect blocks a required workflow, causes major incorrect behavior, violates an important invariant, or can materially damage user/project state without meeting CRITICAL criteria.

Action: block affected release/deployment until resolved or explicitly accepted by the Director with documented risk.

### MEDIUM

Use `MEDIUM` for material but contained defects with a safe workaround or limited blast radius.

Action: repair in the normal engineering cycle with regression evidence.

### LOW

Use `LOW` for minor defects with no meaningful integrity, security, canon, workflow, or data risk.

Action: backlog or repair opportunistically, while preserving enough evidence to avoid duplicate investigation.

## Error classes

Classify significant defects using one or more of:

- `CODE_DEFECT`
- `TEST_DEFECT`
- `CONTRACT_DEFECT`
- `CONFIGURATION_DEFECT`
- `DEPENDENCY_DEFECT`
- `DATABASE_DEFECT`
- `MIGRATION_DEFECT`
- `NETWORK_DEFECT`
- `STORAGE_DEFECT`
- `GPU_WORKER_DEFECT`
- `CONCURRENCY_DEFECT`
- `IDEMPOTENCY_DEFECT`
- `AUTHORIZATION_DEFECT`
- `SECURITY_DEFECT`
- `DATA_INTEGRITY_DEFECT`
- `CANON_INTEGRITY_DEFECT`
- `PERFORMANCE_DEFECT`
- `DEPLOYMENT_DEFECT`
- `INTEGRATION_DEFECT`
- `OBSERVABILITY_DEFECT`
- `AI_AGENT_DEFECT`
- `UNKNOWN`

Do not count downstream symptoms as independent root defects until evidence supports that classification.

## Evidence capture

For significant errors, capture the smallest useful evidence set available:

- defect/incident ID;
- detection source;
- timestamp;
- branch and commit SHA;
- environment or service identity;
- CI run/job/test identity where applicable;
- error code/message and relevant stack trace;
- request/job/correlation ID where applicable;
- affected inputs/state identifiers without exposing secrets;
- reproduction steps or reproduction status;
- severity and blast-radius assessment;
- known-good comparison where available;
- evidence supporting root-cause conclusions;
- repair commit;
- regression proof;
- verification evidence;
- remaining unknowns.

Secrets, credentials, unnecessary personal information, and private chain-of-thought must not be stored in defect evidence.

## Reproduction rule

Before broad repair work, reduce the problem to the smallest reliable reproduction practical.

If it cannot be reproduced, state:

`Reproduction: NOT_REPRODUCED`

and continue investigation without inventing a root cause.

Intermittent/concurrency/runtime failures may require statistical or trace-based reproduction rather than a single deterministic test.

## Root-cause rule

ChatGPT and Codex must distinguish:

- **symptom** - what visibly failed;
- **trigger** - the condition that exposed the failure;
- **causal defect** - the code/configuration/contract flaw that allowed it;
- **systemic contributor** - missing test, weak invariant, poor observability, unsafe coupling, or process weakness that allowed escape.

Do not label the first plausible explanation as root cause without evidence.

## Regression-first repair

Where practical, convert every confirmed defect into a failing regression test, invariant test, contract check, static rule, integration test, or controlled fault-injection scenario before or alongside the repair.

Required proof shape:

`broken version -> regression proof FAILS`

`repaired version -> same regression proof PASSES`

If a regression test is impractical, document the equivalent verification mechanism and why it is sufficient.

## Repair rule

Prefer the minimum safe causal repair.

Do not perform an unrelated rewrite to fix a localized defect unless evidence shows the architecture itself is causal.

Repairs must not silently change product canon, authority, ownership, security posture, or architecture boundaries. Those changes require the normal Director-approved governance path.

## ChatGPT correction responsibilities

ChatGPT must:

- retrieve current repository/CI/runtime evidence before making implementation-dependent claims;
- classify facts, evidence, inference, estimate, hypothesis, and unknown distinctly;
- identify likely scope, severity, and blast radius;
- challenge symptom-only fixes;
- require regression evidence where practical;
- review Codex's proposed repair against architecture/canon/invariants;
- inspect CI evidence before declaring verified;
- preserve unresolved uncertainty;
- record significant correction lessons in durable repository evidence rather than relying on conversational memory.

ChatGPT must not:

- claim a defect is fixed solely because Codex says so;
- claim runtime recovery without runtime evidence;
- turn its own hypothesis into canonical root cause;
- bypass Director authority;
- delegate its independent oversight responsibility to Brain.

## Codex correction responsibilities

Codex must:

- reproduce the defect or explicitly report that reproduction failed;
- identify affected code and contracts;
- propose the smallest safe causal repair;
- add or update regression proof;
- run the relevant local checks available in its environment;
- expose known limitations and skipped checks;
- avoid unrelated refactors during defect repair unless separately justified;
- provide branch/commit/test evidence for review.

Codex must not:

- suppress, delete, weaken, skip, or rewrite a failing test merely to obtain green CI unless the test itself is proven defective and the correction preserves or strengthens the intended contract;
- silently downgrade severity;
- redefine canon or architecture to make broken code appear correct;
- treat Brain output as permission to bypass engineering evidence.

## Test-defect rule

Tests can be wrong.

When a test fails because the test contract is stale or incorrect:

1. prove the implementation/authoritative contract it is meant to verify;
2. preserve the failing evidence;
3. update the test to assert the intended behavior rather than merely the latest string/output;
4. where practical, make the test less brittle while retaining its safety value;
5. rerun the corrected test against both expected-good and deliberately-bad cases.

A test may not be weakened simply because it is inconvenient.

## CI rule

CI is an independent evidence producer, not an authority over product direction.

A required failing CI gate blocks the affected merge/release until:

- the defect is repaired and the same gate passes; or
- the gate itself is proven defective and corrected with evidence; or
- the Director explicitly accepts a documented exception where policy allows one.

Independent validation families should eventually report separately so an early failure does not hide unrelated failures. The final aggregate gate must fail when any required family fails.

## Runtime rule

For defects that can manifest after deployment, completion requires runtime or staging evidence appropriate to the risk.

Preferred progression:

`FIXED_IN_CODE -> VERIFIED_IN_CI -> VERIFIED_IN_STAGING -> VERIFIED_IN_RUNTIME -> CLOSED`

Until runtime identity/telemetry is available, use `Runtime verification: UNKNOWN` rather than claiming production success.

## Recovery and rollback

For high-risk runtime changes, maintain a known-good state and a reversible path.

If a repair introduces critical regression:

1. contain affected operations;
2. preserve evidence;
3. roll back to the known-good version when safer than forward repair;
4. verify restored state;
5. investigate the failed repair separately;
6. do not erase the failed deployment from history.

## Defect record

Significant defects should use a durable record with at least:

- `ID`
- `Status`
- `Severity`
- `Class`
- `Detected by`
- `First detected`
- `Affected commit/environment`
- `Symptom`
- `Reproduction`
- `Root cause status`
- `Root cause evidence`
- `Containment`
- `Regression proof`
- `Repair commit`
- `CI verification`
- `Runtime verification`
- `Remaining unknowns`
- `Closed by/date`

## Closure standard

Do not use `CLOSED` when the only evidence is "the code changed."

A defect is normally closed only when the relevant regression and integration evidence passes, the repair is traceable, and applicable runtime behavior is verified.

Use `FIXED_IN_CODE`, `VERIFIED_IN_CI`, or another accurate intermediate state when later evidence is still pending.

## Brain separation

The Brain may later:

- ingest defect records;
- detect recurring patterns;
- reason over failure history;
- recommend architecture or operational improvements;
- correlate engineering failures with wider system evidence.

The Brain must not become the sole detector, sole verifier, sole repair authority, or sole record of ChatGPT/Codex engineering errors.

The independent correction chain remains:

`Director authority -> repository contracts -> ChatGPT oversight -> Codex repair -> CI/tests evidence -> staging/runtime evidence -> closure`

This separation ensures that a Brain fault cannot silently certify its own engineering repair, and an agent error cannot silently redefine Brain truth.