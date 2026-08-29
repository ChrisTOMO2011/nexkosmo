# Operational Truth Controls

## Status

Approved governance and architecture contract for implementing the First Principle of Truth.

This contract defines required operational controls. It does not claim the corresponding runtime subsystems are already implemented or verified.

## Purpose

The First Principle of Truth must remain operational under multi-agent work, automation, evaluation pressure, incidents, retries, and system failure. Nexkosmo therefore requires evidence lineage, independent validation, outcome-integrity controls, and incident replay sufficient to investigate abnormal or unsafe behaviour without trusting the agent under investigation.

## 1. Evidence lineage

Material claims and consequential decisions must be traceable to their evidence lineage.

Where applicable, lineage must preserve:

- claim or assertion identity;
- source identity and source type;
- originating actor or system;
- retrieval or observation time;
- parent evidence or derived-claim relationships;
- transformations, summaries, inferences, or model-generated derivations;
- tests, validators, or measurements relied upon;
- agents or services that consumed the evidence; and
- contradictions or invalidations affecting the lineage.

Multiple agents relying on the same source, artifact, model output, test result, prompt, or derived claim are not independent confirmations merely because they are separate agents.

Confidence must not increase solely because dependent agents agree.

## 2. Independent validation

The strength and independence of validation must be appropriate to the consequence, reversibility, uncertainty, and blast radius of the claim or action.

Consequential PASS, production readiness, security acceptance, canonical correctness, financial correctness, safety clearance, migration completion, or equivalent high-impact states must not depend solely on the statement of the actor whose work is being evaluated.

Where independent validation is required, the validator must use evidence or authority meaningfully independent from the claimant's unsupported assertion.

## 3. Outcome integrity and anti-gaming

Nexkosmo must never reward an AI merely for appearing correct.

An agent's own statement that it succeeded, complied, completed a task, or produced a valid result must not by itself satisfy the success condition used to reward, approve, release, canonise, pay, promote, or increase the authority of that agent.

Success criteria should prefer externally inspectable outcomes such as deterministic tests, authoritative state, independent measurements, verified artifacts, protected audit records, human approval where required, or equivalent evidence appropriate to the task.

The system must not create incentives where hiding uncertainty, suppressing contradictory evidence, fabricating completion, or gaming a metric is an easier path to reward than producing the intended real-world outcome.

A metric is evidence about an objective; it must not silently become the objective when doing so would allow the metric to be gamed.

## 4. Agent incident evidence

A material agent or Brain incident must preserve enough protected evidence to reconstruct what happened without relying on the memory, explanation, or cooperation of the component under investigation.

Incident evidence should include, where technically and legally appropriate:

- incident identifier and timestamps;
- workspace/project/environment scope;
- authenticated actor identities and roles;
- model, agent, service, policy, code, and configuration versions materially involved;
- authority and permissions held at relevant times;
- material instructions and delegated objectives;
- evidence and evidence-lineage identifiers available to the actor;
- material inter-agent messages or coordination events;
- tool, adapter, external-action, and policy-decision records;
- relevant assertions, decisions, contradictions, denials, escalations, retries, and state transitions;
- before/after canonical state references;
- spend/compute consequences where material;
- Guardian and control-plane responses;
- independent validation outcomes; and
- hashes, sequence numbers, or equivalent integrity evidence needed to detect missing or altered records.

Sensitive data must still follow privacy, rights, retention, and least-privilege rules. Incident observability is not permission for unrestricted logging.

## 5. Replay and root-cause analysis

Nexkosmo should support deterministic or evidence-faithful replay where technically feasible.

Replay does not mean re-executing dangerous external side effects. It means reconstructing the decision context and causal sequence sufficiently to determine:

- what the actor knew or was shown;
- what authority it held;
- which evidence lineages were independent or shared;
- what claims were accepted, disputed, contradicted, or unknown;
- what decisions and actions followed;
- which safeguards fired or failed to fire; and
- where the earliest preventable divergence occurred.

A suspected agent must not be the sole authority deciding whether its own incident is cleared.

## 6. Incident response linkage

Material incidents must be able to trigger governed responses including restriction, safe mode, quarantine, credential revocation, worker-dispatch pause, spend/compute freeze, or human escalation according to the Brain containment contract.

Incident evidence must remain available after the affected Brain or agent is stopped or replaced.

## 7. Implementation boundary

The current repository has event envelopes, assertion and decision events, authenticated actor binding, evidence/provenance primitives, audit concepts, and constitutional governance foundations.

The complete evidence-lineage graph, agent-incident event family, protected replay store, replay engine, outcome-integrity evaluator, and Guardian-integrated incident workflow are NOT yet claimed as implemented or verified end to end.

Future implementation must extend existing canonical Brain/evidence/audit/event architecture rather than create a competing truth store.

## Permanent operational invariants

1. Dependent agreement is not independent corroboration.
2. Confidence cannot increase solely from repeated claims sharing one evidence lineage.
3. A claimant cannot self-certify a consequential success using only its own assertion.
4. Success evidence must be appropriate to the real objective and resistant to obvious metric gaming.
5. Material contradictions and uncertainty remain part of incident evidence.
6. Incident reconstruction must not depend solely on the component being investigated.
7. Replay must not silently reproduce dangerous external side effects.
8. Incident evidence survives agent or Brain replacement where retention rules permit.
9. Operational truth controls extend the canonical Brain/evidence/audit architecture; they do not create a competing source of truth.
