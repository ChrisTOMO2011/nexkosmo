# Pricing Benchmark and Commercial Calibration Contract

**Status:** Adopted commercial-calibration rule; numerical economics intentionally unfrozen  
**Applies to:** Pricing Engine, BUILD estimates, PRODUCTION quoting, distributed compute economics  
**Related contract:** `PRICING_CREDITS_AND_RENDER_COST_TARGET.md`

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
- distributed compute pricing accounts for node payout, Nexkosmo cost, failure/retry overhead and sustainable margin.

The following remain commercial variables:

- credit-to-currency conversion;
- subscription credit allocations;
- asset price tables;
- per-Shot/per-Scene price bands;
- provider/API markups;
- gross-margin targets;
- node payout percentages;
- retry/refund allowances;
- promotional/free credits.

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
- cache hit/reuse rate;
- successful reusable intermediates;
- achieved output quality/fidelity;
- human review/rework requirement where materially attributable;
- actual total internal cost.

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

### 5.2 Commercial readiness STOP-GATE

Before Nexkosmo freezes production pricing, the costing model must be capable of estimating and reconciling the cost and elapsed time of film-scale workloads in approximately the **600-1,500+ logical-job range**, with uncertainty bands appropriate to workload complexity.

At minimum, the comparison must cover where technically applicable:

- RTX 3090-class local/owned execution;
- Nexkosmo-owned compute;
- distributed contributor compute;
- third-party/cloud/API execution;
- hybrid routing across those options.

The comparison must account for actual effective successful-output cost, including retries, failures, storage/transfer, licences, orchestration, cache/reuse behaviour and quality/rework.

If Nexkosmo cannot reliably explain what a 60-, 90- or 100-Scene film could cost under the supported routes, including the effect of reuse, then the commercial pricing schedule is **not ready to be frozen**.

Permanent reminder:

> **A small per-job costing error becomes a large film-scale business error when multiplied across hundreds or more than a thousand executions. Costing accuracy is therefore a release-level commercial requirement, not a cosmetic pricing exercise.**

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

## 7. Cache and reuse economics

Benchmarks must distinguish first-time creation from reuse.

Examples:

- first creation of a reusable character package;
- later use of that character in a new Shot;
- full Shot rerender;
- partial face/dialogue rerender;
- reused environment with a new camera;
- reused simulation/intermediate pass where valid.

Pricing must not be calibrated as though every Shot recreates every reusable asset.

## 8. Local and distributed compute

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

## 9. Calibration process

Commercial calibration should follow:

```text
Measure representative workloads
-> normalize cost evidence
-> identify route-specific cost distributions
-> include failure/retry/reuse behaviour
-> stress-test whole-film workload scale
-> select sustainable margin policy
-> test user-facing credit mapping
-> validate price clarity and competitiveness
-> freeze approved commercial schedule
```

Numerical pricing should remain changeable independently of canonical creative architecture.

## 10. BUILD relationship

BUILD may show estimated credits and money value before final commercial calibration is frozen, but prototype/internal figures must be clearly treated as provisional.

BUILD architecture must not hard-code permanent commercial constants into Scene/Shot creative state.

Pricing configuration should remain a replaceable/versioned commercial policy consumed by the quote engine.

## 11. Versioned price policy

When pricing is eventually launched, each quote should reference the price-policy version used to calculate it.

Historical render evidence should remain traceable to:

- execution route;
- metered work;
- quote/reservation;
- pricing-policy version;
- reconciliation result.

Later pricing-policy changes must not rewrite historical charges.

## 12. No invented certainty

Until benchmarking is sufficient, Nexkosmo documentation and internal planning must not present speculative numerical margins, credit conversions or per-Shot prices as proven economics.

Scenario modelling is allowed, but scenario assumptions must remain distinguishable from measured production evidence.

The 15-per-Scene film-scale reference in this contract is explicitly a **stress-test scenario**, not measured production truth and not a frozen commercial constant.

## 13. Permanent rules

> The pricing architecture is ready before the final price table is ready.

> Measure real workloads before freezing commercial numbers.

> Test the costing model at whole-film scale, not only per asset or per Shot.

> Treat approximately 15 logical jobs per Scene as a provisional empty-vault stress-test baseline until measured evidence replaces it.

> A pricing schedule is not ready to freeze if Nexkosmo cannot model the cost and elapsed time of approximately 600-1,500+ logical film-production jobs across supported compute routes.

> Calibrate against successful-output cost, not theoretical compute cost alone.

> Reuse, caching and partial rerendering must be represented in both cost evidence and user pricing.

> Commercial policy may evolve without redesigning the creative Scene/Shot architecture.