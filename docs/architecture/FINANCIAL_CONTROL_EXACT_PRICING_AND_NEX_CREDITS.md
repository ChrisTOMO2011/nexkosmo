# Financial Control, Exact Pricing, and Nex Credits

## Status

**APPROVED PRODUCT/COMMERCIAL DIRECTION**

**IMPLEMENTATION DEFERRED UNTIL MIGRATION COMPLETION**

**NOT PRODUCTION-AUTHORISED**

**Classification:** Approved architecture decision captured during migration; runtime implementation is `DEFERRED`.

**Authority:** Director.

**Scope:** Future paid creative operations, execution routing, customer pricing, Nex Credits, financial evidence, and pre-commercial acceptance.

This document records approved governing architecture so that it survives the current controlled migration. It does not claim that pricing, wallets, payments, billing, render charging, provider settlement, contributor settlement, or financial-control runtime capabilities exist.

## Relationship to existing Nexkosmo architecture

This direction extends, and does not replace, the existing Brain and Render Orchestrator boundaries:

- the Brain remains Nexkosmo's canonical intelligence and truth architecture;
- the Director remains authoritative for creative intent and approved production state;
- the Render Orchestrator converts validated creative intent into replaceable execution plans;
- renderer and provider adapters preserve technical provenance behind stable boundaries; and
- the Financial Controller adds an independent financial gate before customer or Nexkosmo financial exposure.

This is not a competing Brain, truth store, rendering architecture, or migration path. Implementation remains subordinate to `docs/MIGRATION_ALIGNMENT.md`, the governing security and latent-defect protocols, and explicit future Director acceptance.

## 1. Customer buys the outcome, not the AI model

Normal users buy an approved Nexkosmo production outcome. They do not select the AI model, provider, renderer, GPU, workflow, ComfyUI pipeline, or external inference vendor. Provider or model selection must not be exposed as an advanced-user control.

The user-facing execution identity is **Nexkosmo Brain**.

The Director controls creative intent and approved production state. The Brain and Render Orchestrator select the best qualifying execution route. Underlying models, renderers, providers, workflows, and compute remain replaceable.

Technical provenance must retain the exact provider, model, version, workflow, adapter, relevant configuration, and execution evidence internally where required for audit, reproducibility, cost verification, incident investigation, and debugging.

## 2. Exact price before action

No paid creative operation may begin until Nexkosmo shows the Director the **exact customer price** that will be deducted. The customer's selected supported currency is the primary monetary display, with the exact NXC debit also shown. This is a price, not an estimate.

Illustrative concept only:

```text
Nexkosmo Brain
Production Shot
380 NXC
A$5.72
Price locked
Generate
```

Once the Director accepts a quote:

- the customer price is immutable for that operation;
- the NXC debit is immutable for that operation;
- the approved creative contract is bound to that quote; and
- Nexkosmo absorbs authorised internal execution-cost variance within the bounded exposure approved for that operation.

Changing duration, quality, resolution, creative intent, or another price-affecting requirement invalidates an unaccepted quote and requires a new exact quote. An accepted quote must never be repriced retrospectively.

## 3. Pay for production, not failed attempts

Customer credits are charged for the accepted production contract, not for each internal generation, retry, repair, segment, provider call, or rerouting attempt.

Two cases must remain distinct:

### A. Nexkosmo contract failure

A provider, renderer, worker, system, or Nexkosmo contract failure may trigger bounded internal repair, retry, or rerouting. These attempts must not repeatedly debit the customer. If Nexkosmo cannot fulfil the valid contracted result within authorised recovery limits, the applicable charge must be released or refunded under the future settlement policy.

### B. Director creative revision

A creative revision requested after Nexkosmo has delivered a valid contracted result is a new production action and receives a new exact quote.

Nexkosmo does not promise subjective aesthetic satisfaction. The guarantee concerns fulfilment of the approved production contract and its deterministic acceptance criteria.

## 4. Internal Execution Confidence gate

Each proposed paid execution plan receives an internal **Execution Confidence Score** from 0 to 100.

This score must never be shown to normal users.

The hard execution rule is:

```text
Execution Confidence < 90/100 -> EXECUTION PROHIBITED
```

Below 90, the Brain must rethink the plan. It may find another qualifying renderer, workflow, provider, compute route, strengthen references or continuity evidence, improve validation, or segment and restructure technical execution where that does not alter approved creative meaning. It must then recalculate confidence.

The Brain must not lower the approved creative standard merely to cross the threshold. Rethinking is bounded. If no qualifying plan reaches at least 90, Nexkosmo must stop and must not issue a paid Generate quote for that plan.

The initial score is an evidence-backed confidence score, not a claimed statistical probability. It may be treated as a calibrated probability internally only after historical predicted-versus-actual outcomes demonstrate calibration. Predicted confidence and actual outcomes must therefore be preserved for later calibration analysis.

## 5. Nexkosmo Financial Controller

The **Nexkosmo Financial Controller** is an independent financial decision authority over paid operations, not merely a reporting accountant.

Its permitted decisions are:

- `APPROVE`
- `REPRICE`
- `REROUTE`
- `STOP`

The Brain may not override the Financial Controller's minimum-margin, maximum-exposure, reserve, liquidity, spending, pricing, discount, or circuit-breaker rules.

If a route is creatively excellent but financially unsafe, the Brain must find a safer qualifying route, the exact price must increase through a new unaccepted quote, or the operation must not be sold. The Financial Controller sits before customer and Nexkosmo financial exposure.

## 6. Accounting, Economist, and Financial Controller responsibilities

These responsibilities remain separate.

### Accounting and ledger truth

Accounting records authoritative realised evidence, including:

- actual provider invoices;
- actual provider token and usage reports;
- actual GPU and compute costs;
- actual worker payouts;
- payment fees;
- refunds and releases;
- taxes where applicable;
- storage and network costs;
- failed-render costs;
- realised gross margin; and
- historical price snapshots.

### Economist and market-risk intelligence

The Economist supplies evidence and scenarios concerning:

- provider price trends;
- compute supply and demand;
- GPU capacity trends;
- foreign-exchange movements;
- wholesale inference trends;
- contributor supply;
- demand trends;
- market stress scenarios; and
- provider-dependency risk.

The Economist does not arbitrarily set customer prices.

### Financial Controller

The Financial Controller combines accounting truth, approved economic evidence, authenticated current inputs, and deterministic financial policy. It has the final internal financial gate for paid operations.

Critical financial decisions require deterministic, auditable calculations. An LLM opinion is never proof of cost. If a critical price input is unavailable, stale, or unverifiable, the result is:

```text
NO QUOTE
```

Nexkosmo must not guess.

## 7. Usage and cost ledger facts

The following are distinct ledger facts and must never be conflated:

- actual provider tokens;
- provider credits or usage units;
- GPU or compute consumption;
- estimated metered value;
- actual provider billed cost;
- customer retail price;
- NXC debit; and
- display-currency conversion.

Usage and cost truth uses this source priority:

```text
provider-reported actual
> deterministic measured actual
> UNKNOWN
```

Actual billed money must come from billing, contract, invoice, or credit-ledger evidence where available. It must never be inferred solely from token count.

Pricing data must be effective-dated, versioned, and historically preserved. Every historical transaction retains the pricing policy, rates, source evidence, and conversions that applied when its quote was accepted.

## 8. Nexkosmo Credits

The customer purchasing unit is:

- **Name:** Nexkosmo Credits
- **Short name:** Nex Credits
- **Code:** NXC

Customer credits must not be called tokens.

NXC is initially non-crypto, non-speculative, non-transferable between users unless later explicitly approved, non-redeemable for cash unless later explicitly approved, and usable only as a Nexkosmo service purchasing unit.

NXC must not equal OpenAI tokens, video-model credits, GPU seconds, GPU-hours, or any provider-specific credit system. Provider usage units remain internal. The customer's real selected supported currency remains prominently displayed with NXC.

## 9. Credit packs and bulk discounts

Nexkosmo may sell NXC in packs or lots. Larger packs may receive approved discounts, but the Financial Controller determines the maximum financially safe discount. Marketing has no authority to discount below financial safety controls.

Discounts may come from purchasing efficiency, wholesale savings, utilisation improvements, or approved available margin. They must never consume required failure reserve, protected exposure reserve, or required minimum contribution margin.

Buying NXC locks the purchase price of those credits. It does not permanently lock the future NXC amount of every future shot. Future shot prices may require different NXC amounts because complexity, execution route, market/provider costs, or compute economics differ.

Once a specific shot quote is accepted, that shot's NXC debit and customer-currency price are locked.

## 10. User currency

Customer price must be displayed in the user's selected preferred supported currency. Nexkosmo must preserve:

- original or base monetary amount;
- source currency;
- FX source;
- FX timestamp;
- conversion rate; and
- converted customer display amount.

No implementation may hard-code USD or AUD as a universal assumption. If required FX evidence is unavailable or unverifiable, Nexkosmo must not invent a converted value or issue a quote requiring it.

Quote acceptance freezes the customer-facing monetary obligation for that operation.

## 11. Contributor earnings remain separate

Creator/customer credits and Salad-style compute-contributor earnings are separate financial concepts:

### A. Creator/customer NXC wallet

Tracks the customer's Nexkosmo service purchasing units.

### B. Compute-contributor payable earnings ledger

Tracks real payable compensation owed under contributor-governing terms.

Contributor earnings are not NXC and must not share a balance, settlement meaning, or ledger truth with customer NXC.

## 12. Bounded loss

No paid operation may begin without a deterministic upper bound on authorised Nexkosmo financial exposure.

Each paid execution plan must define applicable hard limits for:

- maximum provider spend;
- maximum GPU time or cost;
- maximum contributor payout;
- maximum automatic retries;
- maximum repair passes;
- maximum fallback execution spend; and
- maximum total authorised exposure.

AI failure never authorises unlimited retries or unlimited spending.

## 13. Margin gate

Before Nexkosmo may offer a paid quote, all blocking gates must pass:

1. Execution Confidence is at least 90.
2. The quality and continuity contract passes.
3. Maximum authorised loss exposure is known.
4. Required current cost inputs are verified.
5. The Financial Controller approves.
6. Required margin and reserves survive.
7. Qualifying capacity is available.
8. The exact customer price and NXC debit can be locked.

If any blocking financial gate fails:

```text
NO PAID QUOTE
```

The Brain may replan or reroute and repeat the internal assessment within bounded limits.

## 14. Risk-adjusted pricing

The confidence threshold and financial risk reserve are separate controls. A confidence score of 90 does not mean Nexkosmo automatically adds 10 percent to the price.

Future risk-reserve policy must be grounded in measured Nexkosmo evidence, including first-pass success rate, retry and repair frequency, average recovery cost, refund or release rate, provider failure rate, worker reliability, route-specific loss rate, and realised margin.

Until sufficient evidence exists, financial policy remains conservative, explicit, deterministic, and bounded.

## 15. Economic circuit breakers

The Financial Controller must eventually be able to stop new affected quotes when verified economics leave authorised bounds, including provider price spikes, FX shocks, compute shortages, worker payout increases, abnormal failure or retry rates, margin deterioration, stale or unverifiable billing evidence, and liquidity or reserve breaches.

An economic circuit breaker stops unsafe selling. It must not silently rewrite accepted prices.

Already accepted price-locked operations remain governed by their accepted contract unless a separate safety or failure rule requires cancellation and release or refund.

## 16. Execution routing and Salad-style compute

The Brain and Render Orchestrator may choose among qualifying routes such as:

- Nexkosmo-owned compute;
- Server 2 or future Nexkosmo GPUs;
- an approved contributor or Salad-style GPU network;
- wholesale external compute;
- external specialist models or providers; and
- 3D, real-time, offline, VFX, or hybrid workflows.

The user does not choose the model or provider. Route selection must never be "cheapest wins."

Selection first satisfies the creative contract, identity and continuity, security and trust, capability, reliability, Execution Confidence of at least 90, and required quality. Only then may it optimise expected total execution cost, recovery risk, speed and capacity, and margin.

## 17. Procurement and scale advantage

Future procurement responsibility includes negotiated provider volume pricing, enterprise inference contracts, reserved capacity where appropriate, bulk compute purchasing, and contributor-network economics.

Verified wholesale savings may improve margin, reduce customer prices, fund safer failure reserves, or be split across those purposes according to Financial Controller policy.

## 18. Customer experience

Normal user experience remains simple. It must not expose:

- Execution Confidence or internal probability;
- provider or model names as choices;
- internal execution cost or margin;
- retry allowance;
- worker payout;
- provider token count; or
- routing logic.

The user sees relevant production identity, the operation, exact NXC debit, exact selected-currency price, price-lock state, and the authorised action. Exact wording and visual design remain a future UX decision.

## 19. Future TestGPT and adversarial acceptance gate

Before real customer money is exposed, a required future adversarial acceptance campaign must attempt to break:

- exact quote locking;
- double charging;
- stale prices and quote expiry;
- FX changes;
- discount abuse and margin-floor bypass;
- confidence-below-90 bypass;
- Brain override of the Financial Controller;
- unlimited retry or spending loops;
- provider and contributor-worker failures;
- interrupted renders;
- refund or release settlement;
- concurrent purchases and insufficient balances;
- repeated callbacks, replay, and idempotency;
- creative-revision versus system-failure classification;
- provider price spikes; and
- wallet and ledger consistency.

The acceptance invariants are:

- the customer is never charged more than the exact accepted amount;
- Nexkosmo never enters unbounded financial exposure;
- an execution plan below 90 confidence never runs;
- the Brain never overrides Financial Controller safety authority;
- internal failed attempts never repeatedly debit customer NXC; and
- discounts never bypass protected financial floors.

TestGPT is not implemented by this decision. This section records a required future pre-commercial gate.

## 20. Legal and accounting review

Before commercial launch, Nexkosmo requires qualified jurisdiction-appropriate review of prepaid-credit accounting, revenue recognition, unused balances, GST/VAT/sales-tax treatment, refunds, any proposed credit expiry, stored-value and payment regulation, consumer law, contributor payouts, and multi-currency treatment.

This architecture makes no legal, tax, regulatory, or accounting conclusion.

## 21. Governing principles

### PRICE BEFORE ACTION

No paid creative operation begins before the Director receives the exact customer charge in their selected supported currency. Once accepted, that operation's customer price and NXC debit are immutable.

### OUTCOME OVER ENGINE

The Director controls the creative outcome. Nexkosmo controls the replaceable execution method.

### CONFIDENCE BEFORE COMMITMENT

No paid execution plan below 90/100 internal Execution Confidence may run. Below the threshold, the Brain must rethink, reroute, or decline without lowering the approved creative standard.

### BOUNDED LOSS

AI failure never authorises unlimited Nexkosmo spending.

### FINANCIAL SURVIVAL AUTHORITY

The Financial Controller has independent authority to `APPROVE`, `REPRICE`, `REROUTE`, or `STOP` paid operations before financial exposure.

### PAY FOR PRODUCTION, NOT FAILED ATTEMPTS

Customers pay the accepted production contract, not repeated charges caused by Nexkosmo's failed internal attempts.

### TRUTHFUL ACCOUNTING

Actual usage, actual billed cost, customer price, NXC debit, and currency conversion are separate facts and must never be falsely inferred from one another.

### DISCOUNTS NEVER CONSUME SAFETY

Bulk-credit discounts may use purchasing efficiency or approved margin, but never required financial safety reserves.

## Migration and implementation discipline

This architecture is approved for future implementation, but implementation remains deferred until the current migration is complete and explicitly accepted.

This decision does not authorise database tables, pricing services, wallet APIs, NXC runtime behavior, UI changes, Stripe or payment-provider integration, render charging, provider adapters, contributor settlement, Server 1 or Server 2 changes, Production changes, or commercial launch.

Future implementation requires its own bounded architecture and security review, threat model, deterministic financial contracts, migration plan, negative and adversarial tests, real evidence, staging acceptance, legal/accounting review, and explicit Director authority.

The historical `docs/STOP_GATE.md` remains unchanged. This record neither weakens nor supersedes the current migration discipline or any existing acceptance boundary.
