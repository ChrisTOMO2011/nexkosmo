# Runtime Metric Observer

## Status

First implementation increment. Domain observation and drift evaluation are implemented in this branch. Persistent runtime ingestion, production telemetry wiring, Guardian integration, dashboards, and end-to-end production verification are not yet claimed.

## Purpose

The Runtime Metric Observer provides evidence about how Nexkosmo agents and workflows actually behave over time. It complements repository CI and the Governance Drift Sentinel:

- CI detects code and integration failures;
- Governance Drift Sentinel detects protected contract drift;
- Runtime Metric Observer detects material operational drift in comparable task outcomes.

The observer is evidence infrastructure, not a source of authority.

## Current observed dimensions

The first increment supports:

- cost per validated outcome;
- handoff rate;
- premature handoff rate;
- rework rate;
- human intervention rate; and
- validated outcome rate.

Task observations preserve task identity, agent identity, comparable task class, terminal resolution, validated-outcome state, cost units, handoff counts, premature-handoff counts, rework counts, and human-intervention counts.

Cost units are intentionally generic in this increment. Future telemetry may compose model/API cost, token usage, GPU/CPU time, electricity, storage, transfer, human attention, and other evidenced resource costs without changing the observer's authority boundary.

## Comparable baselines

Drift comparisons require a single comparable `task_class` across the baseline and current samples. The observer must not silently compare unlike workloads and call the difference agent drift.

A baseline is evidence about historical operation, not an eternal performance target. Task difficulty, provider pricing, model versions, infrastructure changes, workload mix, and other material context may explain a metric movement and must remain available to investigation.

## Drift findings

A drift finding records:

- metric identity;
- baseline value;
- current value;
- absolute change;
- relative change where mathematically defined;
- direction; and
- current sample size.

Zero baselines are handled explicitly. For example, movement from zero premature handoffs to a material non-zero rate can be flagged even though percentage growth from zero is undefined.

Default rules are initial diagnostic rules, not permanent truth. They are deliberately reviewable and replaceable as operational evidence accumulates.

## Authority boundary

The Runtime Metric Observer may:

- observe;
- aggregate;
- compare;
- detect configured drift;
- emit evidence; and
- support investigation.

The Runtime Metric Observer may not by itself:

- disable or punish an agent;
- remove or increase authority;
- change permissions or credentials;
- alter budgets or compute ceilings;
- rewrite canonical state;
- declare an agent unsafe solely from a metric;
- treat a metric as the objective; or
- conceal contradictory context that could explain a finding.

Consequential responses belong to Guardian and authorised human governance using evidence appropriate to the consequence.

## Interpretation rule

A metric movement is a signal to investigate, not proof of cause.

Examples:

- rising cost may reflect waste, harder tasks, provider pricing, retries, or infrastructure degradation;
- rising handoffs may reflect premature transfer, missing authority, changed workload, or specialist requirements;
- falling validated-outcome rate may reflect model degradation, harder work, validator changes, or upstream defects.

The observer reports what changed. Root-cause analysis determines why.

## Relationship to Mission Sustainability

The observer supplies evidence needed to evaluate Mission Sustainability and Economic Stewardship without creating AI self-preservation incentives.

It can reveal avoidable duplication, rising cost, excessive handoffs, rework, or growing human rescue requirements. It must not reward concealment, punish truthful failure reporting, or create an incentive for an agent to resist authorised shutdown in order to protect its score or continued operation.

## Next runtime increments

1. Define persistent observation/event contracts with evidence-lineage identifiers.
2. Persist observations using the existing canonical database/audit/event architecture rather than a competing truth store.
3. Bind observations to authenticated actors, task identity, model/runtime/configuration versions, and evidence provenance.
4. Add task-class-aware rolling baselines and minimum sample requirements based on collected evidence.
5. Add diagnostic dashboards and evidence packets for Brain/Guardian/human review.
6. Add incident/replay linkage so abnormal metric changes can be reconstructed.
7. Validate that metrics improve real outcomes without producing metric gaming or self-preservation behaviour.

## Permanent implementation rule

> Metrics are evidence about operation, not commands to the system. Detect the change, preserve the evidence, investigate the cause, then make governed decisions.
