# Pricing, Credits and Render Cost Target

**Status:** Target architecture — not a frozen commercial price schedule

This document defines the intended Nexkosmo pricing and metering direction for assets, AI generation, shot rendering, scene rendering and related compute. Numerical prices remain subject to benchmarking, infrastructure costs, provider/API pricing, node economics, software licensing and approved commercial decisions.

The target is to give the Director a clear, exact quote for the work they are about to run while allowing Nexkosmo's underlying cost model to evolve without changing the creative workflow.

## User-facing credit model

Nexkosmo should expose one simple user-facing credit system for paid creative and production operations rather than asking users to understand unrelated provider token systems, GPU-seconds, API units, render samples or vendor-specific billing models.

Rules:

1. The user-facing unit should be **Nexkosmo Credits** or an equivalent approved Nexkosmo billing unit.
2. The UI should show the credit amount together with an understandable money value in the user's billing currency wherever practical.
3. Raw language-model tokens are not the universal production currency. LLM tokens, image-generation units, video-generation units, GPU time, CPU/RAM usage, storage, data transfer and software/provider charges remain internal metering inputs.
4. A possible simple credit-to-currency mapping may be evaluated for usability, such as making 100 credits approximately equal to one unit of local currency, but no such numeric mapping is frozen by this target document.
5. Pricing presentation should remain simple even when the internal cost model is complex.

The permanent target is:

> One understandable user-facing credit system; many accurately metered cost inputs underneath.

## Cost basis

Nexkosmo's internal pricing engine should calculate the expected cost of an operation from the resources and providers actually required by the selected execution route.

Relevant cost inputs may include:

- AI/model API charges;
- GPU execution time;
- CPU execution time;
- RAM usage where materially billable;
- storage and retained asset cost;
- data transfer/egress where applicable;
- distributed-compute node payout;
- licensed software or renderer cost where attributable;
- orchestration/queue/runtime overhead;
- retry/recovery allowance where commercially appropriate;
- payment/transaction cost where appropriate;
- Nexkosmo operating overhead and approved margin.

Pricing logic must not assume that all renders, assets or shots have the same cost.

## Exact pre-execution quote target

Before a chargeable asset-generation or production-render operation begins, Nexkosmo should show the Director the expected charge clearly enough to make an informed decision.

The target flow is:

`Estimate -> Quote/Reserve -> Execute -> Reconcile`

Rules:

1. Nexkosmo estimates the selected execution route before the job runs.
2. The Director sees the expected credit charge and money equivalent before committing where the operation is materially chargeable.
3. Nexkosmo may reserve the quoted credits before execution to prevent an unexpected insufficient-balance failure mid-job.
4. After completion, Nexkosmo reconciles the reservation against the actual metered execution cost according to the approved billing policy.
5. A job must not silently exceed the Director-visible maximum charge. If the required cost materially exceeds the quoted ceiling, Nexkosmo should stop or request approval rather than surprise-bill the user.
6. Infrastructure failures attributable to Nexkosmo should not result in the user paying for unusable failed work under the intended commercial model. Exact retry/refund rules remain to be defined before launch.
7. The quote must preserve the execution assumptions used to calculate it, including selected quality tier, route, resolution, duration, shot count, required new assets and other material cost drivers.

The permanent target is:

> The Director should know the maximum expected charge before expensive work begins.

## Asset pricing target

Assets should not be priced by a single flat number merely because they share an asset-category name.

A simple isolated 2D prop, a generated texture, a reusable 3D vehicle and a production-ready photoreal character package have materially different production costs.

Rules:

1. Asset pricing should be calculated from the actual production route and resource requirements.
2. The quote may include generation, modelling, conversion, rigging, texturing, reference creation, validation, storage or other required work where applicable.
3. Approved existing assets should be retrieved and reused before generating replacements when suitable, reducing both compute cost and user charge.
4. A reusable source asset must not be charged again as though it were newly created every time it appears in another shot.
5. Derived scene representations, preview renders or shot views may incur only the incremental compute required to create those derivatives.
6. Higher-fidelity or production-ready asset packages may cost more than lightweight concept or preview assets because the underlying work is greater.
7. Asset quotes should expose the useful result being purchased, not force the user to interpret provider-level technical billing units.

## Shot pricing target

BUILD defines a scene as `Scene -> 1..N Shots`. Shot cost should therefore be calculated per required shot execution rather than assuming every scene has the same render price.

A shot quote may depend on:

- duration;
- resolution;
- frame rate;
- renderer/model route;
- quality tier;
- number and complexity of characters;
- scene complexity;
- required AI generation;
- simulation/VFX work;
- lighting/render complexity;
- upscaling or interpolation;
- compositing requirements;
- audio generation where part of the requested operation;
- whether required assets already exist and can be reused;
- cached results and reusable intermediate work.

The same scene may contain a cheap preview shot and an expensive production shot. Nexkosmo should meter each accordingly.

## Scene render pricing target

A scene's user-visible render cost should be derived from the actual work needed for that scene rather than from a fixed arbitrary scene price.

Conceptually:

`Scene Cost = Shared Scene Preparation + Required New Assets + Sum(Shot Costs) + Required Scene-Level Finishing/Processing`

Rules:

1. Shared work must not be duplicated across shots merely for billing convenience.
2. Existing canonical characters, 3D assets, props, environments and other reusable project assets should be reused rather than recreated per shot.
3. Cached work should reduce repeated compute where technically valid.
4. A scene with three shots should not automatically cost the same as a scene with twenty-five shots.
5. A one-shot scene may legitimately be cheaper or more expensive than a multi-shot scene depending on duration, complexity and route.
6. The Director should be able to see the estimated total scene cost as well as useful shot-level breakdowns before committing a full-scene render.
7. If only one shot is changed, Nexkosmo should rerender and charge only the affected dependencies where practical rather than forcing the whole scene to be regenerated.

The permanent target is:

> Charge for the work actually required, reuse what already exists, and avoid making the Director pay twice for the same reusable production asset.

## BUILD pricing visibility

BUILD should make cost visible at the point where the Director is deciding what to create or render.

The target UI may show, as appropriate:

- current credit balance;
- money equivalent;
- estimated new-asset cost;
- per-shot preview cost;
- per-shot production-render cost;
- estimated scene total;
- assets being reused at no new creation charge;
- quality/route choices that materially change price;
- the maximum charge before the Director confirms.

A Director should be able to understand the cost consequence of adding shots, increasing quality, creating new assets or changing render routes before execution.

## Preview versus production pricing

Nexkosmo should support lower-cost exploratory work before full production quality where the selected renderer/route permits it.

Examples include:

- lightweight shot preview frames;
- lower-resolution motion previews;
- proxy 3D or simplified simulation;
- draft audio;
- test renders;
- look-development samples.

The Director can therefore validate creative intent before paying for full-quality production execution.

Preview pricing must not imply that preview output is equivalent to approved final production output.

## Quality and route choices

Where multiple valid production routes exist, Nexkosmo may present meaningful trade-offs such as:

- faster / lower cost;
- balanced;
- higher fidelity / higher cost;
- local user hardware;
- Nexkosmo-owned compute;
- distributed compute;
- approved third-party API/provider route.

The Brain/Render Orchestrator should select or recommend routes based on capability, quality, continuity, time and cost, while preserving Director authority.

The user should not need to understand every internal provider, but advanced users may be given additional detail where useful.

## User-owned hardware

When a user elects to render on approved local hardware, Nexkosmo should distinguish platform/service charges from external compute charges that Nexkosmo is not incurring.

The pricing target should not pretend Nexkosmo paid cloud GPU cost when the user supplied the hardware.

Any future local-execution pricing must still account transparently for services Nexkosmo actually provides, such as orchestration, AI/API calls, storage, licensed capabilities or other billable infrastructure.

## Distributed compute economics

When external Nexkosmo compute nodes execute work, the pricing engine should preserve enough margin and auditability to support:

- node contributor payout;
- Nexkosmo operating cost;
- failure/retry risk;
- payment and infrastructure overhead;
- sustainable platform margin.

Node payout and user price are related but are not the same number.

Exact payout percentages and gross-margin targets remain commercial variables and are not frozen by this document.

## Benchmark before freezing numerical prices

Exact numerical price schedules must be based on measured production costs rather than assumptions.

Before commercial rates are frozen, Nexkosmo should benchmark representative workloads across the actual supported routes, including where applicable:

- local RTX-class GPUs;
- Nexkosmo-owned GPU workers;
- distributed compute nodes;
- AI image providers;
- AI video providers;
- Blender/Cycles;
- Unreal Engine;
- Arnold;
- V-Ray;
- Houdini/simulation workloads;
- upscaling/interpolation;
- voice/audio generation;
- storage and transfer;
- hybrid workflows.

Benchmarks should record wall time, GPU/CPU/RAM usage, provider fees, output quality, failure/retry rate and reusable/cached work where applicable.

The numerical price schedule may then be calibrated from measured cost plus the approved commercial margin and updated as underlying costs change.

## Target status versus frozen canon

This document intentionally defines a **target** rather than freezing commercial numbers.

The following are targets now:

- one understandable Nexkosmo credit system;
- visible money equivalent;
- exact pre-execution quote target;
- estimate/reserve/execute/reconcile flow;
- asset pricing based on actual work;
- shot-level metering;
- scene cost aggregated from shared work plus 1..N shot costs;
- reuse/caching reduces cost;
- no duplicate charge for recreating already-existing canonical assets;
- partial rerender should charge only affected work where practical;
- benchmark real execution routes before freezing numerical rates.

The following are **not frozen by this document**:

- credit-to-currency conversion;
- asset price tables;
- per-shot prices;
- per-scene prices;
- provider markups;
- gross-margin percentage;
- node payout percentage;
- subscription inclusion amounts;
- promotional/free credit allocations.

## Permanent target summary

> Nexkosmo should tell the Director what an asset, shot or scene will cost before expensive work begins, meter the real execution route underneath, reuse existing assets and cached work, show credits beside understandable money value, and only freeze numerical pricing after representative production workloads have been benchmarked.