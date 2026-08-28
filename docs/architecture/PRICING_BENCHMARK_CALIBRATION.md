# Pricing Benchmark and Commercial Calibration Contract

**Status:** Adopted commercial-calibration rule; numerical economics intentionally unfrozen  
**Applies to:** Pricing Engine, BUILD estimates, PRODUCTION quoting, distributed compute economics  
**Related contract:** `PRICING_CREDITS_AND_RENDER_COST_TARGET.md`, `RENDERER_CAPABILITY_AWARE_PREVIEW_ROUTING.md`

## 1. Purpose

Nexkosmo's pricing architecture is established: credits plus understandable money value, pre-execution estimates/quotes, per-asset/per-Shot/per-Scene costing, reuse of existing assets, dependency-aware partial rerendering, and no duplicate charging for the same reusable production work.

What remains intentionally unresolved is the final commercial calibration.

The governing rule is:

> Do not freeze credit conversion, margins, provider markups, node payouts or final price tables until representative real Nexkosmo workloads have been measured end to end.

## 2. Architecture is stable; numbers are not

The following pricing principles are architectural and should remain stable:

- one understandable Nexkosmo credit system;
- money equivalent shown where practical;
- estimate -> quote/reserve -> execute -> reconcile;
- visible maximum charge before materially expensive execution;
- asset cost based on actual work required;
- Shot cost based on actual route and workload;
- Scene cost derived from shared preparation + required assets + Shot work + finishing;
- existing assets reused rather than charged as newly created every time;
- cache/reuse lowers repeated compute cost;
- partial rerender charges only affected work where technically practical;
- user-owned hardware is not billed as if Nexkosmo paid external cloud GPU cost;
- distributed compute pricing accounts for node payout, Nexkosmo cost, failure/retry overhead and sustainable margin;
- guaranteed production pricing must be supported by measured route reliability evidence for the relevant execution scope.

The following remain commercial variables:

- credit-to-currency conversion;
- subscription credit allocations;
- asset price tables;
- per-Shot/per-Scene price bands;
- provider/API markups;
- gross-margin targets;
- node payout percentages;
- retry/refund allowances;
- promotional/free credits;
- numeric reliability thresholds required for QUALIFIED/GUARANTEED production status.

## 3. Benchmark before freeze

Representative workloads must be measured across the actual routes Nexkosmo intends to support.

A benchmark record should capture, where applicable:

- workload identity/type;
- asset/Scene/Shot complexity;
- duration;
- resolution and frame rate;
- renderer/model/engine/version;
- local/Nexkosmo/distributed/third-party execution route;
- GPU model and GPU time;
- CPU time;
- RAM use where material;
- storage/egress;
- licensed software cost where attributable;
- provider/API fees;
- orchestration overhead;
- queue/wall time;
- retry/failure rate;
- first-pass Brain acceptance rate;
- attempts per Brain-accepted result;
- cost per Brain-accepted result;
- elapsed time per Brain-accepted result;
- targeted-repair success rate;
- fallback/reroute success rate;
- unresolved failure rate after approved recovery policy;
- cache hit/reuse rate;
- successful reusable intermediates;
- achieved output quality/fidelity;
- human review/rework requirement where materially attributable;
- actual total internal cost;
- sample size, evidence recency and route/model/provider version.

## 4. Benchmark classes

The benchmark set should include enough variation to avoid calibrating the business around one easy workload.

Representative classes should include, where applicable:

- lightweight 2D asset creation;
- photoreal identity-sensitive character creation;
- reusable 3D asset creation;
- simple locked-camera Shot;
- dialogue/lip-sync Shot;
- multi-character interaction;
- moving-camera Shot;
- action Shot;
- VFX/simulation-heavy Shot;
- hybrid AI + 3D Shot;
- layer/pass/AOV-sensitive Shot;
- preview-quality execution;
- production-quality execution;
- targeted partial rerender;
- full Scene execution;
- local user hardware;
- Nexkosmo-owned compute;
- distributed node execution;
- third-party provider/API execution.

## 5. Film-scale workload guardrail

Nexkosmo must not calibrate pricing only from isolated assets or single-Shot demonstrations. Commercial readiness must also be tested against whole-film workload scale.

For planning and stress testing, Nexkosmo adopts the following **provisional worst-case reference**, not a permanent rendering rule:

> **Approximately 15 logical render/generation instances per Scene for a new-user, empty-library, everything-from-scratch workflow.**

A logical render/generation instance means a genuinely independent generation, render, simulation, composite/master or other material compute execution. It does **not** mean one classic renderer invocation per image layer, and it must not encourage unnecessary fragmentation of work that can be produced efficiently in one coordinated execution.

Using that provisional 15-per-Scene stress-test assumption:

| Planning example | Scene count | At 15 logical instances per Scene |
| --- | ---: | ---: |
| 90-minute film | 40-70 | 600-1,050 |
| 120-minute film | 50-90 | 750-1,350 |
| Fast action/thriller | 100+ | 1,500+ |
| Slow drama | 30-50 | 450-750 |
| Short film | 5-20 | 75-300 |

Reference feature-film examples:

```text
60 Scenes x 15 = 900 logical render/generation instances
90 Scenes x 15 = 1,350 logical render/generation instances
100 Scenes x 15 = 1,500 logical render/generation instances
```

These figures are a commercial stress-test reminder. They are not a requirement that every Scene perform 15 jobs and are not permission to generate work that reuse, caching, richer renderer outputs or dependency-aware execution could avoid.

### 5.1 Reuse-efficiency scenarios

The pricing and orchestration architecture should actively drive the effective average downward through asset reuse, cached results, combined outputs/passes, dependency-aware invalidation and partial rerendering.

For a 60-Scene feature-film planning example:

```text
15 effective jobs per Scene -> 900 jobs
10 effective jobs per Scene -> 600 jobs
 7 effective jobs per Scene -> 420 jobs
```

The difference is economically material. Costing must therefore measure both first-time creation and later reuse rather than assuming every Scene starts from nothing.

### 5.2 Reliability compounding at film scale

A route that appears acceptable in isolated demos may become commercially unsafe when its rejection rate is multiplied across hundreds or more than a thousand executions.

Nexkosmo must therefore model how first-pass Brain acceptance and attempts-per-accepted-result compound across the expected film workload.

The costing model must not assume that a low per-attempt price remains economical at scale when repeated rejection, retry and rerouting are required.

Permanent rule:

> **Small reliability losses compound into large token/compute, time and margin losses at film scale. Route qualification must therefore be evaluated against the expected accepted-result workload, not isolated demo success.**

### 5.3 Commercial readiness STOP-GATE

Before Nexkosmo freezes production pricing, the costing model must be capable of estimating and reconciling the cost and elapsed time of film-scale workloads in approximately the **600-1,500+ logical-job range**, with uncertainty bands appropriate to workload complexity.

At minimum, the comparison must cover where technically applicable:

- RTX 3090-class local/owned execution;
- Nexkosmo-owned compute;
- distributed contributor compute;
- third-party/cloud/API execution;
- hybrid routing across those options.

The comparison must account for actual effective successful-output cost, including retries, failures, storage/transfer, licences, orchestration, cache/reuse behaviour, route reliability, fallback behaviour and quality/rework.

If Nexkosmo cannot reliably explain what a 60-, 90- or 100-Scene film could cost under the supported routes, including the effect of reuse and rejection/recovery behaviour, then the commercial pricing schedule is **not ready to be frozen**.

Permanent reminder:

> **A small per-job costing or reliability error becomes a large film-scale business error when multiplied across hundreds or more than a thousand executions. Costing and reliability accuracy are release-level commercial requirements, not cosmetic pricing exercises.**

## 6. Quality-adjusted cost

The cheapest route is not automatically the best economic route if it fails frequently or requires repeated regeneration.

Commercial calibration should consider effective successful-output cost, including:

```text
effective cost
= execution cost
+ expected retry cost
+ failed-work overhead
+ required post-processing
+ material quality/rework cost
```

A route that costs less per attempt but fails identity/continuity repeatedly may be more expensive overall than a higher-cost reliable route.

## 7. Brain-accepted result economics

Nexkosmo must distinguish **generation attempts** from **accepted production results**.

A Render Result that Brain rejects for technical, continuity, identity, creative, output-contract or other required validation failure is not a completed Shot merely because compute was consumed.

The governing commercial metric is:

> **Cost per Brain-accepted result, not cost per generation attempt.**

Internal attempts may still consume real provider tokens, API charges, GPU time, storage, orchestration and validation resources. Those costs must be measured because Nexkosmo must understand its true COGS. However, a rejected attempt must not automatically create a new customer charge for the same already-approved Shot outcome.

For a supported, quoted Shot or other production outcome:

1. the customer authorises the outcome and the visible maximum charge;
2. Nexkosmo internally meters every attempt required to achieve it;
3. Brain validates each result against the approved acceptance contract;
4. a rejected result remains internal failed/retry work rather than a completed customer deliverable;
5. retries, reroutes, targeted repairs and dependency-aware rerenders remain inside the quoted outcome economics while the approved maximum remains valid;
6. Nexkosmo must stop and obtain new approval rather than silently exceed the approved maximum where the existing quote can no longer support delivery;
7. a user-requested creative change after an accepted result, or an explicitly requested additional variation/alternative, may constitute newly authorised work and may be quoted separately.

Internal accounting should distinguish at least:

- accepted production work;
- expected retry allowance;
- rejected renderer/model attempts;
- infrastructure/provider failure;
- validation/review overhead;
- user-authorised revisions after acceptance;
- user-authorised alternative/variation generation.

This prevents Nexkosmo from hiding unreliable routes inside apparently cheap per-attempt pricing.

Example:

```text
Route A: $1 internal cost per attempt x 3 average attempts to Brain acceptance
         = approximately $3 internal generation cost before other overhead

Route B: $2 internal cost per attempt x 1.1 average attempts to Brain acceptance
         = approximately $2.20 internal generation cost before other overhead
```

Route B may therefore be economically superior even though its single-attempt price is higher.

Permanent rule:

> **Brain rejection is a quality decision; it must also be visible to economics. Rejected attempts are measured as internal cost and reliability evidence, not silently converted into repeated customer charges for the same agreed outcome.**

## 8. Reliability-qualified pricing and guarantee envelope

A technically capable renderer/model/route is not automatically eligible to support guaranteed paid production.

Pricing for a guaranteed production promise must be based on a route that is reliability-qualified for the relevant Shot class and execution scope under `RENDERER_CAPABILITY_AWARE_PREVIEW_ROUTING.md`.

The route/scope should carry a governed state such as:

- `EXPERIMENTAL`;
- `QUALIFIED`;
- `GUARANTEED`;
- `DEGRADED`;
- `QUARANTINED`.

Commercial rules:

1. `EXPERIMENTAL` routes may be benchmarked and tested but must not silently support the same guarantee as a proven production route.
2. `QUALIFIED` routes may enter controlled production according to policy.
3. `GUARANTEED` routes are inside the approved customer guarantee envelope for the declared scope and pricing policy.
4. `DEGRADED` or `QUARANTINED` routes must not be priced as healthy guaranteed capacity.
5. A material provider/model/adapter version change may require requalification before guaranteed status is restored.
6. Guaranteed pricing must include the measured recovery economics of expected targeted repair, retry and qualified fallback use.
7. If no qualified route/fallback exists for a required material capability, READY/pricing must expose a STOP-GATE rather than sell certainty that Nexkosmo has not earned.

### 8.1 Required reliability economics

Before guaranteed pricing is frozen for a route/scope, Nexkosmo must understand at minimum:

- first-pass Brain acceptance rate;
- attempts per Brain-accepted result;
- cost per Brain-accepted result;
- elapsed time per Brain-accepted result;
- targeted-repair success;
- fallback/reroute success;
- unresolved failure rate after the approved recovery policy;
- evidence sample size and recency;
- sensitivity to provider/model/version drift.

No universal numeric threshold is frozen here. Thresholds must be evidence-based and may differ by workload class, but they must be explicit commercial/operational policy before the route supports a guarantee.

### 8.2 Cheap-proof economics

Where a materially risky requirement can be tested cheaply before full-quality execution, costing should include that proof when it lowers expected failed-work cost.

The proof may test identity, multi-character interaction, camera/rig motion, lip-sync, VFX/simulation, layering/passes/AOVs, hybrid alignment or other material uncertainty.

A small proof cost is economically preferred when it avoids a materially larger expected failure cost later.

### 8.3 Circuit-breaker economics

Route health must be monitored continuously.

If observed acceptance/reliability materially degrades, Brain/Render Orchestrator must be able to stop assigning new guaranteed work and downgrade/quarantine the affected scope before failure compounds across a film-scale workload.

Costing must treat a circuit breaker as margin protection and customer protection, not as an optional monitoring feature.

## 9. Cache and reuse economics

Benchmarks must distinguish first-time creation from reuse.

Examples:

- first creation of a reusable character package;
- later use of that character in a new Shot;
- full Shot rerender;
- partial face/dialogue rerender;
- reused environment with a new camera;
- reused simulation/intermediate pass where valid.

Pricing must not be calibrated as though every Shot recreates every reusable asset.

## 10. Local and distributed compute

Benchmarking must keep execution routes economically distinct.

### User-owned hardware

Measure Nexkosmo services actually consumed separately from hardware electricity/compute supplied by the user.

### Nexkosmo-owned compute

Measure:

- electricity;
- hardware utilization;
- depreciation/replacement allowance;
- maintenance;
- orchestration overhead;
- storage/networking;
- software licences where attributable.

### Distributed compute

Measure:

- node payout;
- platform orchestration cost;
- failure/retry risk;
- verification/validation overhead;
- transfer/storage;
- payment overhead;
- sustainable Nexkosmo margin.

## 11. Calibration process

Commercial calibration should follow:

```text
Measure representative workloads
-> normalize cost evidence
-> identify route-specific cost distributions
-> measure first-pass Brain acceptance and attempts per accepted result
-> measure targeted repair / fallback behaviour
-> qualify route for explicit production scope
-> include failure/retry/reuse behaviour
-> stress-test whole-film workload scale
-> establish circuit-breaker thresholds
-> select sustainable margin policy
-> test user-facing credit mapping
-> validate price clarity and competitiveness
-> freeze approved commercial schedule
```

Numerical pricing should remain changeable independently of canonical creative architecture.

## 12. BUILD relationship

BUILD may show estimated credits and money value before final commercial calibration is frozen, but prototype/internal figures must be clearly treated as provisional.

BUILD architecture must not hard-code permanent commercial constants into Scene/Shot creative state.

Pricing configuration should remain a replaceable/versioned commercial policy consumed by the quote engine.

## 13. Versioned price policy

When pricing is eventually launched, each quote should reference the price-policy version used to calculate it.

Historical render evidence should remain traceable to:

- execution route;
- reliability qualification/version;
- metered work;
- quote/reservation;
- pricing-policy version;
- reconciliation result.

Later pricing-policy changes must not rewrite historical charges.

## 14. No invented certainty

Until benchmarking is sufficient, Nexkosmo documentation and internal planning must not present speculative numerical margins, credit conversions, reliability percentages or per-Shot prices as proven economics.

Scenario modelling is allowed, but scenario assumptions must remain distinguishable from measured production evidence.

The 15-per-Scene film-scale reference in this contract is explicitly a **stress-test scenario**, not measured production truth and not a frozen commercial constant.

## 15. Permanent rules

> The pricing architecture is ready before the final price table is ready.

> Measure real workloads before freezing commercial numbers.

> Test the costing model at whole-film scale, not only per asset or per Shot.

> Treat approximately 15 logical jobs per Scene as a provisional empty-vault stress-test baseline until measured evidence replaces it.

> A pricing schedule is not ready to freeze if Nexkosmo cannot model the cost and elapsed time of approximately 600-1,500+ logical film-production jobs across supported compute routes.

> Calibrate against successful-output cost, not theoretical compute cost alone.

> **Cost per Brain-accepted result is the primary production-economics metric; failed attempts remain measured internal cost and do not automatically become repeated customer charges for the same approved outcome.**

> **Guaranteed paid production requires reliability-qualified routes for the relevant scope; experimental, degraded or quarantined routes do not silently inherit the guarantee.**

> **Use cheap proofs and circuit breakers where they reduce expected failure cost before it compounds at film scale.**

> Reuse, caching and partial rerendering must be represented in both cost evidence and user pricing.

> Commercial policy may evolve without redesigning the creative Scene/Shot architecture.