# Nexkosmo Engineering Status

Status: LIVE ENGINEERING SNAPSHOT
Owner: Director
Alignment steward: ChatGPT

This file is the human-readable engineering health page for Nexkosmo. It is a projection of repository, CI, runtime, context, token-usage, and cost evidence. It is not a new source of product canon and must never override `docs/CURRENT_STATE.md`, approved decisions, verified tests, or runtime evidence.

## Current visible status

Display engineering health vertically, one result per line, rather than as a long horizontal status string.

**Alignment:** 🟠 WARN  
**Repository:** 🔴 FAIL  
**CI:** 🔴 BLOCKED BY REPO PROTECTION  
**Runtime:** ⚪ UNKNOWN  
**Context:** ⚪ UNKNOWN  
**Usage:** ⚪ UNKNOWN  
**Estimate Costings (AUD):** ⚪ UNKNOWN  
**Project Estimate (AUD):** ⚪ UNKNOWN

Current objective: complete the alignment/governance stop gate, protect `main`, merge the approved alignment system, realign Codex, and only then migrate normal development to the Server 1 development environment.

Current known conditions:

- Alignment governance is being established on `governance/alignment-system` / PR #4.
- `main` is currently unprotected. This is a governance STOP GATE.
- The old Studio frontend PR must be reconciled against current canon before merge.
- Codex realignment is pending until the alignment system is merged and current canon is available from `main`.
- Server 1 development migration is pending Codex realignment.
- Runtime commit identity is not yet reported into this status surface.
- Authoritative live context-token telemetry is not yet available to this repository status surface.
- Authoritative cumulative token-usage telemetry is not yet available to this repository status surface.
- Authoritative AI cost telemetry is not yet available to this repository status surface. Do not invent a token count or AUD cost when telemetry is unavailable.
- A defensible whole-project cost baseline and forecast have not yet been established, so `PROJECT ESTIMATE (AUD)` remains unknown rather than displaying false precision.

## Visual status convention

Every human-facing engineering status must show both a word and a visual indicator. Do not display a bare `PASS` when the surface supports Unicode/visual indicators.

- `🟢 PASS` / `🟢 CURRENT` / `🟢 MATCH` / `🟢 GREEN`: directly verified healthy/current.
- `🟠 WARN` / `🟠 AMBER` / `🟠 RUNNING`: attention or checkpoint required, but no verified blocking failure unless explicitly stated.
- `🔴 FAIL` / `🔴 DRIFT` / `🔴 RED` / `🔴 BLOCKED`: verified failure, contradiction, drift, or blocking gate.
- `⛔ CRITICAL`: immediate stop/reset/recovery action required.
- `⚪ UNKNOWN`: authoritative evidence or telemetry is unavailable.

Colour/emoji is a visibility aid only. The text status and underlying evidence remain authoritative, and accessible text must always accompany the icon.

## Standard status layout

Every significant engineering session, PR review, deployment review, and future Server 1 engineering dashboard should present the primary results **down the page**, one status per line, in this order:

**Alignment:** `<🟢 PASS|🟠 WARN|🔴 FAIL|⚪ UNKNOWN>`  
**Repository:** `<🟢 CURRENT|🟠 WARN|🔴 FAIL|⚪ UNKNOWN>`  
**CI:** `<🟢 PASS|🟠 RUNNING|🔴 FAIL|⚪ UNKNOWN>`  
**Runtime:** `<🟢 MATCH|🔴 DRIFT|⚪ UNKNOWN>`  
**Context:** `<used>/<max> tokens | <percent> <icon/state> | <remaining> remaining`  
**Usage:** `input=<input> | cached=<cached> | output=<output> | total=<total>`  
**Estimate Costings (AUD):** `<amount/source|⚪ UNKNOWN>`  
**Project Estimate (AUD):** `<range | horizon | confidence|⚪ UNKNOWN>`

Do not compress the primary human-facing results into one long horizontal line. A machine-readable API may use a structured object, but human interfaces should preserve this vertical layout unless space constraints require a compact secondary view.

If a telemetry or estimate field is unavailable, display `⚪ UNKNOWN` rather than estimating silently. Each field must be traceable to evidence.

## Status meanings

- `🟢 PASS` / `🟢 CURRENT` / `🟢 MATCH`: directly verified against the applicable source of truth.
- `🟠 WARN`: no proven contradiction, but freshness, context health, evidence, or an unresolved dependency requires attention.
- `🔴 FAIL` / `🔴 DRIFT`: a verified contradiction or required gate failure exists.
- `⚪ UNKNOWN`: evidence is missing or telemetry is unavailable. Unknown must never be silently converted to pass.

## Drift classes

Drift must be classified rather than described vaguely:

1. **Documentation drift** - repository documents contradict one another or fail to describe current approved direction.
2. **Branch drift** - active work is stale relative to `main` or required governance/canon changes.
3. **Implementation drift** - code behavior contradicts current canon, contracts, or architecture boundaries.
4. **Canon/data drift** - approved state, canonical assets, provenance, or project truth is replaced or mutated without authority.
5. **Workflow drift** - product navigation or lifecycle behavior diverges from approved journey/workflow boundaries.
6. **Test/evidence drift** - tests no longer prove the claim being made, expected evidence disappears, or green CI masks an untested contradiction.
7. **Runtime drift** - deployed Server 1/Server 2 versions or configuration differ from the approved/reported commit and deployment state.
8. **AI/context drift** - ChatGPT, Codex, or another agent relies on stale assumptions, contradicts current canon, loses task state, or presents inference as fact.

Any verified high-impact drift in canon, authority, data ownership, security, workflow, or architecture is a STOP GATE.

## Token telemetry model

Nexkosmo must distinguish **context occupancy** from **cumulative usage**. They are related but are not the same measurement.

### Context occupancy

When authoritative telemetry is exposed, show all of these values together:

- context tokens currently used;
- maximum context-window tokens applicable to that session/model;
- percentage occupied;
- tokens remaining;
- context-health state (`🟢 GREEN`, `🟠 AMBER`, `🔴 RED`, or `⛔ CRITICAL`);
- telemetry source and observation timestamp where practical.

Example shape only:

**Context:** `286420 / 1310720 tokens | 21.9% 🟢 GREEN | 1024300 remaining`

Example numbers are illustrative and must never be copied into live status unless they are measured.

### Cumulative usage

Where the provider exposes it, show separately:

- input tokens;
- cached input tokens;
- output tokens;
- cumulative total tokens;
- scope such as current request, task, session, day, month, or project;
- telemetry source and timestamp where practical.

Example shape only:

**Usage:** `input=412800 | cached=271600 | output=38400 | total=451200`

The provider's accounting definition controls the total. Do not assume cached tokens should be added again when the provider already includes them within input usage.

Never use cumulative token usage as a substitute for context occupancy, and never infer remaining context from cumulative session usage.

## Context health policy

Context percentage thresholds are Nexkosmo engineering safety policy, not official OpenAI model limits.

- `🟢 GREEN` 0-50%: normal work.
- `🟠 AMBER` >50-65%: checkpoint current work into repository evidence and prepare a fresh-context handoff.
- `🔴 RED` >65-75%: do not begin new architecture/canon work; finish the current atomic task, checkpoint, and reset context.
- `⛔ CRITICAL` >75%: major decisions require fresh-context reconstruction before approval or continuation.

Behavioral evidence overrides the percentage. Contradiction, repeated loss of settled state, stale-branch reasoning, confusion between planned and implemented work, or unsupported confidence triggers a context reset even below the numeric threshold.

If authoritative context usage is unavailable, display **Context: ⚪ UNKNOWN**; do not fabricate precision. If only some context fields are exposed, mark unavailable subfields `⚪ UNKNOWN` rather than reconstructing them from assumptions.

## Estimate Costings

**Estimate Costings** is the standard Nexkosmo label for forward-looking or calculated project/engineering cost figures. AUD is the default human-facing currency.

Estimate Costings must remain distinct from **Actual Costings**, which require authoritative invoice, billing, transaction, metering, or other financial evidence. Never relabel an estimate as an actual charge merely because the calculation is precise.

Where authoritative usage telemetry exists, record enough source data to audit an AI cost estimate, including model, input tokens, cached input tokens where available, output tokens, pricing basis, exchange-rate basis, timestamp, and calculated AUD value.

The visible engineering surfaces should eventually support Estimate Costings for the current request/task, session, day, week, month, and project lifetime where meaningful.

If usage or pricing telemetry is unavailable, display **Estimate Costings (AUD): ⚪ UNKNOWN**. An API-equivalent estimate may be shown only when clearly labelled as an estimate and must never be presented as an actual ChatGPT/Codex charge.

## Project Estimate

**Project Estimate (AUD)** is the forward-looking estimate of the total cost required to reach a clearly defined Nexkosmo project milestone or planning horizon. It is separate from short-period Estimate Costings and separate from Actual Costings.

A Project Estimate must define:

- the milestone or planning horizon being estimated, such as first production vertical slice, private beta, launch, or a stated date;
- included and excluded scope;
- estimated remaining engineering/development costs;
- AI/Codex/API Estimate Costings;
- infrastructure, storage, network, power, software/service, and deployment costs where applicable;
- hardware purchases or upgrades where applicable;
- contingency/risk allowance;
- assumptions and source dates;
- an estimate range rather than false single-dollar precision when uncertainty is material;
- confidence (`LOW`, `MEDIUM`, or `HIGH`) and the evidence supporting that confidence;
- last-updated timestamp or date.

Preferred vertical display:

**Project Estimate (AUD):** `A$<low>-A$<high>`  
**Horizon:** `<milestone/date>`  
**Confidence:** `<LOW|MEDIUM|HIGH>`

A point estimate may additionally be shown as a planning midpoint, but the range remains primary when uncertainty is meaningful.

Until sufficient costing inputs and scope are available, display **Project Estimate (AUD): ⚪ UNKNOWN**. Never infer a whole-project estimate merely from token costs or already-purchased hardware.

As Actual Costings become available, the project forecast should be updated using:

`estimated cost to complete + verified actual cost to date = estimated total project cost at the defined horizon`

The estimate history should remain auditable so changes in scope, assumptions, pricing, or evidence can be explained rather than overwritten silently.

## Required agent handshake

Before significant work, every AI engineering agent must:

1. Read `AGENTS.md`, `docs/CURRENT_STATE.md`, `docs/ALIGNMENT_PROTOCOL.md`, and this status page.
2. Read relevant approved decision records/specifications.
3. Identify repository, target branch, current `main`, active objective, and current STOP GATE.
4. Compare the working branch with `main` where freshness matters.
5. Inspect implementation/runtime evidence where the task depends on implementation/runtime reality.
6. Report contradictions or unknowns before changing code.
7. If authoritative token telemetry is available, report absolute context used/max/remaining plus percentage/health, and keep cumulative usage separate.
8. Continue only when the task is consistent with current authority or an explicit Director-approved change is being made.

## Required completion handshake

Before reporting significant work complete:

1. Compare the implementation against current canon and approved decision/specification.
2. Run alignment, canonical-asset, and normal quality/integration checks.
3. Report branch/commit evidence and known unknowns.
4. Verify that any runtime claim identifies the deployed commit/configuration evidence.
5. Update this status projection when a material status field changed.
6. Preserve the distinction between context occupancy, cumulative token usage, Estimate Costings, Project Estimate, and Actual Costings.
7. Never convert a warning, failure, estimate, inference, or unknown into a pass/fact without evidence.

## Fresh-agent test

At important milestones, start a fresh AI context with no conversation history and require it to reconstruct the project from repository evidence. It must correctly identify the current journey, Production/Studio boundary, authority model, current engineering objective/STOP GATE, implementation-vs-design boundary, canonical-asset rules, current drift/status conditions, and the difference between context occupancy and cumulative token usage.

Failure means the repository or status surfaces are ambiguous/stale and must be corrected before relying on larger prompts.

## Future Server 1 status service

After Codex is realigned and development moves to Server 1, this human-readable contract should drive a small engineering control service/dashboard that derives status rather than becoming another independent truth store.

Planned inputs include:

- Git branch/commit and comparison with approved `main`;
- GitHub PR/CI/protection evidence;
- canonical/alignment test results;
- Server 1 and Server 2 deployed commit/configuration identity;
- service health and deployment state;
- Codex/API context occupancy and usage telemetry where exposed;
- input/cached-input/output token accounting where exposed;
- AUD Estimate Costings conversion with recorded pricing/exchange-rate source and timestamp;
- Project Estimate inputs, actual cost-to-date evidence, scope/horizon, contingency, assumptions, and estimate history.

The dashboard should make drift, token consumption, context health, Estimate Costings, and Project Estimate visible to the Director, ChatGPT, Codex, and other authorized engineering participants using the same vertical status layout defined here.
