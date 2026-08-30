# Nexkosmo Brain

## Brain Implementation Status

Status: Living Document
Last reconciled with repository evidence: 30 August 2026

Reality overrides assumptions.
Implementation presence and production verification are different claims.
Only executed evidence may be reported as verified.

## Implemented areas in this repository

The current repository contains implementation for:

- Brain Kernel foundations
- AI Agent identity/runtime foundations
- Assertion and truth-domain foundations
- Confidence-related domain foundations
- Evidence and provenance foundations
- Workflow/event foundations
- Runtime Metric Observer domain and drift-evaluation foundations

These entries mean code or architecture exists. They do **not** mean the area is fully production-verified end to end.

## Verified evidence currently present

Pure-domain evidence demonstrates, within its tested scope:

- AI cannot exercise the human-only approval function used by the current domain test;
- assertions cannot be created directly as `ACCEPTED`;
- contradictory assertions can coexist without erasure;
- human decisions can accept and reject competing assertions while preserving decision reasons.

The Runtime Metric Observer branch adds tests intended to verify, within their narrow scope, snapshot aggregation, configured drift detection, zero-baseline drift handling, comparable-task enforcement, and stable/no-drift behaviour. Those claims become verified only after the branch CI executes successfully at the exact implementation head.

## Not yet verified end to end

The repository's own evidence record and STOP-GATE state mean the following must not be described as production-verified until the required runtime/database proofs have executed successfully:

- complete PostgreSQL-backed Brain Kernel behaviour;
- full Agent Runtime authority and provenance guarantees;
- complete Assertion & Truth Engine behaviour;
- complete Confidence Engine behaviour;
- complete Evidence & Provenance Engine behaviour;
- complete Workflow behaviour;
- persistent Runtime Metric Observer ingestion and storage;
- production telemetry wiring and rolling baselines;
- Guardian-integrated operational-drift response;
- complete authorization coverage;
- complete audit sequencing and independence;
- complete rights/consent handling;
- complete projection/reconstruction behaviour;
- backup/restore and other milestone blocking proofs.

See `docs/INVARIANT_EVIDENCE.md` and `docs/STOP_GATE.md` for the authoritative evidence limits for this increment.

## Permanent status rule

> Implemented is not verified. Authored is not executed. Passing a narrow test is not proof of the whole subsystem. Production verification requires executed evidence for the claimed scope.
