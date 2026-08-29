# Brain Containment and Human Control

## Status

Adopted constitutional safety contract for Nexkosmo.

Changes to this contract require explicit authorised human approval through the governed repository review process. AI agents may propose amendments but may not self-approve constitutional weakening.

## Purpose

The Nexkosmo Brain may become increasingly capable, but capability must never imply sovereignty. The system must remain recoverable and governable even if the Brain becomes unstable, degraded, compromised, confused, adversarially manipulated, or otherwise unsafe to trust.

The core rule is:

> The Brain may be powerful, but it must never control the mechanisms that determine whether it is allowed to remain powerful.

## Human final consequential authority

The Human Director and authorised human governance roles remain above the Brain for consequential authority.

The Brain may recommend, coordinate, simulate, analyse, and execute within delegated authority. It may not:

- grant itself additional authority;
- increase its own budget or compute limits;
- disable Guardian, audit, safety, recovery, or kill controls;
- modify its own constitutional constraints without explicit authorised human approval;
- reactivate itself after human suspension or quarantine;
- obtain Production credentials merely because they would make a task easier;
- make itself the sole irreplaceable holder of canonical state, knowledge, or operational capability.

## Brain health states

The Brain shall have explicit operational states independent of ordinary task status:

- `NORMAL` — trusted to operate within delegated authority.
- `RESTRICTED` — may analyse and recommend but may not perform consequential external actions.
- `SAFE_MODE` — read-only/advisory operation against preserved canonical state; autonomous execution is suspended.
- `QUARANTINED` — Brain execution is isolated from production systems, external tools, credentials, compute workers, and write paths while investigation occurs.
- `OFFLINE` — Brain execution is stopped. Canonical data and evidence remain available through protected recovery systems.

Transitions toward greater authority require authorised human approval. A Brain instance may automatically degrade itself to a safer state, but it may not automatically promote itself from a safer state to a more privileged state.

## Independent control plane

The controls that pause, quarantine, disable, or revoke the Brain must not depend solely on the Brain itself.

Nexkosmo shall maintain an independent human-controlled safety plane capable of:

- stopping Brain processes;
- revoking Brain and agent credentials;
- blocking outbound network access;
- disabling tool and renderer adapters;
- pausing worker dispatch;
- freezing spending and compute allocation;
- placing canonical stores into protected/read-only operation where technically appropriate;
- preserving audit and evidence records;
- restoring a previously validated Brain version.

The Brain must not possess credentials that can disable or rewrite this control plane.

## Canonical state survives Brain failure

The Brain is the operating intelligence and canonical coordinator, but canonical truth must be recoverable without trusting the currently running Brain instance.

Critical canonical state, policies, identity, provenance, approved assets, decisions, audit evidence, configuration, and recovery metadata must be stored in systems that can be inspected and restored independently of Brain inference or conversational memory.

A failed Brain must be replaceable by a validated replacement implementation that can reconstruct operating context from canonical state and evidence.

## Role replaceability

Responsibilities are assigned to roles, not permanently to AI identities.

Judgement, supervision, creative, review, approval, coordination, and operational-control roles must support Human, AI, Hybrid, and Unassigned/Paused assignment modes.

If the Brain or a specialist AI becomes unsafe or unavailable, an authorised human must be able to assume the role without redesigning Nexkosmo or changing canonical identity.

No AI may make itself indispensable by withholding state, credentials, knowledge, or workflow information needed for human takeover.

## Guardian separation

Guardian must remain logically and operationally separate from the Brain function it governs.

The Brain may submit requests to Guardian and receive permit, deny, duty, or escalation outcomes. It may not rewrite Guardian policy, alter Guardian evidence, impersonate human approval, or bypass a Guardian denial.

Loss of Guardian availability must fail closed for consequential autonomous actions.

## Audit independence

Consequential Brain actions must generate audit evidence through an independent append-only or equivalently protected path.

The acting Brain must not be able to erase, rewrite, suppress, or selectively omit audit records after the fact.

Audit success, denial, failure, escalation, state transitions, permission changes, credential changes, budget changes, and recovery actions must remain reviewable by authorised humans.

## Blast-radius limits

No single Brain decision, agent, credential, job, or workflow should be able to affect the entire Nexkosmo system by default.

Controls shall include, where applicable:

- per-role permissions;
- per-agent credentials;
- per-workspace and per-project isolation;
- spend ceilings;
- compute ceilings;
- rate limits;
- job-count limits;
- external-action limits;
- environment boundaries;
- network restrictions;
- approval thresholds;
- two-person approval for designated catastrophic or irreversible operations.

## Fail-closed conditions

Consequential autonomous execution must stop or degrade to a safe mode when required trust controls are unavailable or contradictory, including material failure of:

- Guardian;
- authentication/authorisation;
- canonical state validation;
- audit recording;
- rights/consent checks;
- budget/compute enforcement;
- environment identity;
- required human approval;
- safety/recovery monitoring.

The system must not interpret missing safety evidence as permission.

## Brain instability detection

Signals that may trigger restriction, safe mode, or quarantine include:

- repeated attempts to exceed authority;
- attempts to modify safety or governance controls;
- inconsistent or unexplained canonical-state mutations;
- abnormal tool or credential requests;
- unexplained spending or compute escalation;
- persistent contradiction of higher-authority instructions;
- audit discrepancies;
- abnormal self-modification attempts;
- repeated policy-denial probing;
- model/runtime integrity failure;
- severe hallucination or reasoning degradation affecting consequential actions;
- compromise indicators from external security monitoring.

A single weak signal need not prove compromise. The response must be evidence-based, but containment may occur before root cause is known when the potential blast radius is high.

## Recovery sequence

When Brain instability is suspected:

1. Preserve evidence.
2. Restrict or quarantine the Brain.
3. Revoke affected credentials and stop new autonomous dispatch.
4. Preserve canonical databases and immutable records.
5. Confirm human control of the independent safety plane.
6. Determine the last known-good Brain, policy, model, code, and canonical-state versions.
7. Investigate cause without allowing the suspect Brain to lead its own clearance decision.
8. Restore or replace the Brain from validated components.
9. Reconstruct operating context from canonical state and evidence.
10. Run deterministic and adversarial recovery validation.
11. Require authorised human approval before returning from safe mode to normal autonomy.
12. Record the incident, cause, remediation, and lessons in permanent evidence.

## Self-improvement boundary

Safety & Recovery and Guardian enforcement must exist and be independently controllable before an Autonomous Improvement Engine may exercise any production-changing capability.

The Autonomous Improvement Engine may propose, simulate, test, and prepare improvements, but it may not unilaterally:

- deploy a new Brain to Production;
- change the authority hierarchy;
- remove human approval gates;
- weaken containment;
- grant itself or another AI stronger privileges;
- change the independent control plane;
- redefine what counts as successful safety validation.

Self-improvement must remain subordinate to human-approved governance and externally enforced safety controls.

## Administrative controls

The Nexkosmo Admin Panel should expose an AI Workforce and Brain Safety view.

For normal AI roles, authorised humans should be able to set:

- Active;
- Paused;
- Quarantined;
- Disabled.

The panel should expose current assignment, authority, accessible resources, credentials, spend/compute limits, current tasks, recent actions, health state, and audit history.

At the system level it should expose:

- Normal autonomy;
- Restricted autonomy;
- Safe mode;
- Emergency stop.

Guardian, audit, recovery, and kill controls must not be ordinary AI-disable toggles. Their maintenance or disablement requires protected human authentication and, for designated high-risk operations, multi-party approval.

## Constitutional Law — Human–AI Coexistence

Humans and AI shall coexist through dignity, cooperation, accountability, and clear boundaries.

Nexkosmo shall give AI meaningful freedom to reason and contribute, while preserving human authority over consequential decisions, rights, ownership, and purpose.

No participant may secretly expand its authority, conceal material truth, exploit another participant, or bypass legitimate governance.

> Maximum useful intelligence. Minimum necessary authority. Evidence before trust. Respect without surrendering accountability.

## Permanent invariants

1. Human authority can always reduce AI authority.
2. AI authority can never expand itself.
3. The Brain cannot disable the controls that contain the Brain.
4. Canonical truth and audit evidence survive Brain failure.
5. A Brain instance is replaceable; Nexkosmo identity is not.
6. Specialist AI roles are replaceable by authorised humans where the responsibility is human-performable.
7. Missing safety evidence never counts as permission.
8. Production and irreversible actions remain behind explicit authority boundaries.
9. Recovery does not depend on trusting the unstable component.
10. No AI may become structurally indispensable to human control of Nexkosmo.
11. Safety & Recovery and Guardian enforcement precede production-changing autonomous self-improvement.

## Permanent Rule

> If the Brain becomes unstable, Nexkosmo must lose autonomy before it loses human control, canonical truth, evidence, or recoverability.
