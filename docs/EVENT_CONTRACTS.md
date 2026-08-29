# Event Contracts

Increment 1 registers the event envelope persistence shape:

- event ID
- workspace ID
- aggregate ID
- aggregate sequence
- event type
- event version
- payload
- occurrence and availability time
- lease and delivery state

Initial implemented contract names:

- `kernel.assertion.recorded` v1
- `kernel.decision.recorded` v1

Event payload schemas and compatibility tests remain blocking for Increment 2.

## Operational truth event requirements

The First Principle of Truth requires future event contracts to support evidence lineage and incident reconstruction without creating a competing truth store.

Planned event families include, subject to implementation design and compatibility review:

- evidence source/lineage linked or invalidated;
- claim contradiction detected or resolved;
- independent validation requested/completed/failed;
- agent authority or role changed;
- policy permit/deny/escalation outcome;
- material tool or external action attempted/completed/failed;
- Brain/agent health-state transition;
- Guardian restriction/quarantine/clearance action;
- material agent incident opened/evidence-preserved/closed; and
- replay/root-cause record produced.

These names are requirements for the future event model, not claims that those runtime event schemas already exist.

For material incidents, event design must preserve enough ordered, integrity-protected references to reconstruct the relevant instruction, authenticated actor, authority, evidence lineage, material inter-agent coordination, decisions, tool actions, contradictions, validation outcomes, Guardian response, and resulting state.

Replay records must distinguish reconstruction from live re-execution. Replaying an incident must not automatically repeat dangerous or consequential external side effects.
