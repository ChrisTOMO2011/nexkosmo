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

## 5. Quality-adjusted cost

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

## 6. Cache and reuse economics

Benchmarks must distinguish first-time creation from reuse.

Examples:

- first creation of a reusable character package;
- later use of that character in a new Shot;
- full Shot rerender;
- partial face/dialogue rerender;
- reused environment with a new camera;
- reused simulation/intermediate pass where valid.

Pricing must not be calibrated as though every Shot recreates every reusable asset.

## 7. Local and distributed compute

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

## 8. Calibration process

Commercial calibration should follow:

```text
Measure representative workloads
-> normalize cost evidence
-> identify route-specific cost distributions
-> include failure/retry/reuse behaviour
-> select sustainable margin policy
-> test user-facing credit mapping
-> validate price clarity and competitiveness
-> freeze approved commercial schedule
```

Numerical pricing should remain changeable independently of canonical creative architecture.

## 9. BUILD relationship

BUILD may show estimated credits and money value before final commercial calibration is frozen, but prototype/internal figures must be clearly treated as provisional.

BUILD architecture must not hard-code permanent commercial constants into Scene/Shot creative state.

Pricing configuration should remain a replaceable/versioned commercial policy consumed by the quote engine.

## 10. Versioned price policy

When pricing is eventually launched, each quote should reference the price-policy version used to calculate it.

Historical render evidence should remain traceable to:

- execution route;
- metered work;
- quote/reservation;
- pricing-policy version;
- reconciliation result.

Later pricing-policy changes must not rewrite historical charges.

## 11. No invented certainty

Until benchmarking is sufficient, Nexkosmo documentation and internal planning must not present speculative numerical margins, credit conversions or per-Shot prices as proven economics.

Scenario modelling is allowed, but scenario assumptions must remain distinguishable from measured production evidence.

## 12. Permanent rules

> The pricing architecture is ready before the final price table is ready.

> Measure real workloads before freezing commercial numbers.

> Calibrate against successful-output cost, not theoretical compute cost alone.

> Reuse, caching and partial rerendering must be represented in both cost evidence and user pricing.

> Commercial policy may evolve without redesigning the creative Scene/Shot architecture.