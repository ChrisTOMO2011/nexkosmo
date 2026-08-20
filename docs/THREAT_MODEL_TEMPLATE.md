# Nexkosmo Threat Model

Status: DRAFT
Owner:
Change/feature:
Commit/PR:
Date:

## Scope

Describe the exact feature/change being assessed and what is out of scope.

## Assets at risk

List sensitive or consequential assets, for example:

- user/project identity;
- private creative assets/IP;
- canonical project state;
- credentials/tokens/keys;
- payment/credit state;
- worker/GPU execution authority;
- database/storage contents;
- audit/provenance evidence.

## Trust boundaries

For each boundary, record:

- source;
- destination;
- authenticated identity;
- authorization decision;
- data crossing the boundary;
- confidentiality/integrity requirements;
- replay/idempotency requirements;
- resource/rate limits;
- audit evidence.

## Attacker-controlled inputs

Identify all inputs an attacker or compromised component can influence.

## Threats and abuse cases

Record concrete abuse cases. Consider:

- spoofing/identity confusion;
- authorization bypass / IDOR;
- tampering/replay;
- injection and unsafe execution;
- information disclosure;
- denial/resource exhaustion;
- privilege escalation;
- SSRF/network pivoting;
- path traversal/file confusion;
- race/idempotency failures;
- dependency/supply-chain compromise;
- unsafe fallback/fail-open behavior.

## Security invariants

List rules that must remain true even under hostile input/failure.

## Controls

For each threat, identify preventive, detective, containment, and recovery controls.

## Security tests

List happy-path, negative/abuse, generated/fuzz, concurrency, mutation, integration, and runtime tests that apply.

## Residual risk / unknowns

Use `UNKNOWN` where evidence is unavailable. Critical security unknowns block consequential progression.

## Evidence

Link tests, CI runs, scanner results, code locations, configuration, staging/runtime observations, or external assessments.

## Decision

- [ ] Security review complete for stated scope
- [ ] Residual risk accepted by authorized owner where required
- [ ] No unresolved critical security unknown

Decision authority/date:
