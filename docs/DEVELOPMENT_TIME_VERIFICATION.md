# Nexkosmo Development-Time Verification Protocol

Status: APPROVED GOVERNANCE PROTOCOL
Authority: Director
Scope: Codex and ChatGPT engineering work while Nexkosmo is being written, changed, refactored, migrated, or repaired.

## Purpose

This protocol is proactive. It is not limited to defects discovered after code is complete.

Its purpose is to make Codex continuously look for defects **while writing Nexkosmo**, reduce the size of mistakes before they spread, and provide ChatGPT with independent evidence for engineering review.

This protocol is part of the Agent Error Correction Layer and remains separate from the Nexkosmo Brain.

The Brain may later consume validated engineering evidence, but it is not the sole development-time detector, verifier, or repair authority for ChatGPT/Codex engineering work.

## Core development rule

Codex must not use this workflow:

`write a large feature -> hope it works -> wait for CI`

The required engineering pattern is:

`understand contract -> establish baseline -> make a small change -> run fast checks -> run targeted tests -> inspect the diff -> continue`

CI is a second independent verifier. It does not replace development-time checking.

## Required inner loop

For each meaningful implementation slice, Codex should perform the smallest applicable version of this loop:

1. **UNDERSTAND** - identify the approved requirement, affected contracts, invariants, state boundaries, and likely failure modes.
2. **BASELINE** - run or inspect the relevant existing test/check before changing behavior when practical.
3. **CHANGE SMALL** - make the smallest coherent implementation change rather than accumulating unrelated edits.
4. **FAST CHECKS** - run syntax/lint/type/static checks applicable to the changed code.
5. **TARGETED TEST** - run the narrowest tests that should prove or falsify the changed behavior.
6. **NEGATIVE TEST** - where risk justifies it, test invalid input, unauthorized use, missing state, duplicate/retry behavior, boundary values, or another likely failure path.
7. **DIFF REVIEW** - inspect the resulting diff for accidental scope expansion, hard-coded state, hidden fallback behavior, weakened tests, stale interfaces, and architecture/canon drift.
8. **REPAIR OR CONTINUE** - if evidence fails, stop expansion, classify the failure, repair it, and rerun the same evidence before continuing.
9. **SLICE COMPLETE** - only then proceed to the next meaningful slice.

## Proactive defect search

Codex is expected to actively search for defects introduced by the current change and obvious defects exposed in directly affected code.

This includes looking for:

- syntax/import errors;
- type mismatches;
- incorrect assumptions about optional/null values;
- broken API or repository contracts;
- authorization/permission gaps;
- invariant violations;
- unsafe default values;
- hidden hard-coded project/user state;
- concurrency/idempotency mistakes;
- transaction-boundary mistakes;
- stale schema/migration assumptions;
- unhandled failure paths;
- broad exception handling that hides real failures;
- retry loops that can duplicate work;
- resource leaks or missing cleanup where visible;
- frontend state/route mismatches;
- test code that no longer proves the intended contract;
- changes that conflict with approved architecture or canon.

Codex does not need to repair unrelated defects merely because it notices them. Significant unrelated defects should be reported and recorded rather than silently expanding scope.

## Change-impact review

Before changing a shared contract, Codex must identify likely dependents.

Examples include:

- domain type -> services, repositories, tests, migrations, API schemas;
- API contract -> frontend/client, tests, auth, persistence, worker integration;
- database schema -> models, repositories, migrations, fixtures, backup/restore assumptions;
- job schema -> Server 1 scheduler, queue, Server 2 worker, retries, idempotency, monitoring;
- frontend route/state contract -> navigation, deep links, tests, project persistence;
- authorization rule -> callers, policies, audit evidence, negative tests.

A local compile/test pass is not proof that all dependents remain correct.

## Mandatory stop conditions while coding

Codex must stop the affected implementation slice instead of continuing through uncertainty when:

- a required baseline test unexpectedly fails;
- a new failure cannot be explained;
- current code conflicts with approved canon or architecture;
- a migration or state change may destroy or corrupt data;
- authorization/security behavior is uncertain;
- a test must be weakened merely to continue;
- the implementation would require inventing a backend/API contract that does not exist;
- the working branch is materially stale for the task;
- evidence indicates the change is broader than the approved scope.

The correct status is `UNKNOWN`, `BLOCKED`, or `NOT_REPRODUCED` until evidence resolves the issue.

## Check families during development

Use the checks applicable to the current slice rather than waiting for final CI.

### Python/backend

- syntax/import execution;
- Ruff/static analysis;
- mypy/type checking;
- targeted pytest tests;
- domain/invariant tests;
- repository/service contract tests;
- database/integration tests when persistence behavior changes.

### Frontend

When the frontend toolchain is present on the working branch:

- TypeScript type checking;
- lint/static analysis;
- targeted unit/component tests;
- route/state tests;
- production build for meaningful integration changes;
- browser/E2E tests when the affected flow has them.

### Database/migrations

- migration compilation;
- upgrade against a disposable/test database;
- schema/model compatibility;
- constraints/invariants;
- rollback/recovery reasoning where migration risk is material.

### API/integration

- request/response contract tests;
- invalid-input tests;
- authorization tests;
- idempotency/retry tests where applicable;
- integration tests across the directly affected boundary.

### Worker/GPU pipeline

When the worker test environment exists:

- job-schema validation;
- timeout/cancellation behavior;
- retry/idempotency behavior;
- worker disconnect/error paths;
- resource/OOM handling where testable;
- result/provenance integrity.

## Test integrity

Codex must not change a test merely because it fails after an implementation change.

First determine whether:

- the implementation is wrong;
- the test is wrong/stale;
- the approved contract changed;
- the test is exposing a previously hidden defect;
- evidence is insufficient.

If the test itself is defective, preserve or strengthen the intended safety contract when correcting it.

## No silent error suppression

Codex must not treat these as acceptable repairs without evidence:

- swallowing exceptions;
- returning success after a failed operation;
- replacing an error with a default value that changes semantics;
- disabling validation;
- skipping tests;
- weakening assertions;
- adding broad retries without idempotency analysis;
- adding TODO/fake implementations that masquerade as production completion.

## Development evidence handoff

For a meaningful completed implementation slice, Codex should be able to report:

- requirement/contract followed;
- files/contracts changed;
- checks run during development;
- tests added/changed;
- failures encountered and their disposition;
- unresolved unknowns;
- branch/commit identity;
- what still requires CI, staging, Server 1, Server 2, or runtime evidence.

ChatGPT reviews this evidence independently before treating consequential work as verified.

## Relationship to CI

Development-time verification and CI are complementary.

`Codex inner loop` catches defects quickly while the change is small.

`CI` reruns independent repository-defined evidence in a clean environment.

A Codex local pass cannot override CI failure. A CI pass also does not prove untested runtime behavior.

## Desired engineering behavior

The objective is not that Codex never creates a defect.

The objective is:

**create smaller changes -> detect defects sooner -> understand the cause -> repair before expansion -> preserve regression proof -> let independent CI challenge the result again.**

This is the default development posture for building Nexkosmo.