# Growth Intelligence

## Status

This document defines an enduring Nexkosmo growth-intelligence responsibility. It is an architectural direction and product contract, not a claim that the capability is implemented in the current increment.

## Purpose

Growth Intelligence turns validated market opportunities into measurable, consent-respecting acquisition and retention experiments.

Its goal is not to maximise impressions, clicks, or the amount of automated marketing. Its goal is to help Nexkosmo acquire and retain creators efficiently while preserving human agency, transparency, brand quality, privacy, consent, and economic discipline.

The system exists to answer:

> Given a validated creator need that Nexkosmo can satisfy, what is the most effective responsible way to reach the right audience, activate them, retain them, and learn whether the opportunity creates durable value?

## Core Principle: Optimise for Retained Creator Value

Growth Intelligence MUST optimise toward durable creator and business outcomes rather than vanity metrics.

Primary economic and product signals may include:

- customer acquisition cost (CAC);
- trial-to-paid conversion;
- activation rate;
- time to first meaningful outcome;
- retention and churn;
- lifetime value (LTV);
- LTV:CAC ratio;
- CAC payback period;
- contribution margin;
- feature adoption;
- project completion;
- creator success and satisfaction; and
- revenue quality over time.

Clicks, impressions, open rates, video views, and page visits are useful diagnostic signals but MUST NOT become the final optimisation objective.

## Relationship to Market & Opportunity Intelligence

Growth Intelligence consumes validated opportunity hypotheses from `MARKET_OPPORTUNITY_INTELLIGENCE.md`.

The preferred flow is:

`Market Signal -> Need Cluster -> Demand Confidence -> Capability Match -> Growth Hypothesis -> Human Approval -> Controlled Experiment -> Acquisition -> Activation -> Retention -> Revenue/Value -> Learning`

When Nexkosmo already satisfies an identified need, Growth Intelligence may propose a campaign or discovery experiment.

When Nexkosmo does not satisfy the need, Growth Intelligence MUST NOT misrepresent the product. The opportunity should remain in the Capability Gap lifecycle until a real capability or approved prototype exists.

## Opportunity-to-Campaign Automation

For an approved opportunity, the system may prepare:

- target problem statement;
- creator segment hypothesis;
- positioning and messaging hypotheses;
- landing-page concepts;
- feature and comparison pages;
- demo scripts;
- educational content;
- ad creative concepts;
- social content concepts;
- SEO content concepts;
- onboarding paths;
- experiment definitions;
- success thresholds;
- budget recommendations; and
- measurement plans.

Preparation may be highly automated. Publishing, paid spend, material brand claims, major budget changes, and other consequential actions remain subject to policy and human approval.

## Official Distribution Channels

Growth Intelligence may prepare channel-specific recommendations for the current official Nexkosmo public accounts defined in `BRAND_GUIDELINES.md`:

- LinkedIn: Nexkosmo company page
- Instagram: `@nexkosmo`
- TikTok: `@nexkosmo`
- Reddit: `u/Nexkosmo`
- Discord: `@Nexkosmo_`
- YouTube: `@NexkosmoOfficial`

These accounts are approved destinations, not blanket authority for autonomous publication. Growth Intelligence may research, draft, adapt, schedule-propose, and measure content for them, but public publishing remains subject to the applicable human-approval and operational-permission boundaries in this document.

### Google and email identities

Nexkosmo currently distinguishes its general company mailbox from its owner/administrator identity:

- `office@nexkosmo.com` — general company/office communications identity and existing Hostinger-managed mailbox unless a future migration explicitly changes that role.
- `chris@nexkosmo.com` — Christopher Tomson's Nexkosmo identity and current Google owner/administrator identity where applicable.

Growth Intelligence MUST NOT assume these addresses use the same provider, licence, billing arrangement, mailbox, or permissions. Sender identity for any email campaign or operational workflow must be explicitly approved and must respect consent, communication preferences, applicable anti-spam requirements, authentication, and domain reputation.

The presence of two identities does not itself justify two paid Google Workspace subscriptions. Before any Google or email account/licence is cancelled, ownership and dependencies must be checked, including Drive files, calendars, YouTube assets, recovery methods, third-party sign-ins, administrator roles, and billing.

Credentials, API keys, access tokens, cookies, and account recovery information MUST remain outside repository source and documentation.

## Controlled Creative Experimentation

The system should be able to generate and compare multiple legitimate ways of communicating the same validated value proposition.

For example, an integrated 3D capability might be framed as:

- `Create and edit 3D assets inside your filmmaking workflow.`
- `Stop switching between your AI movie tool and a separate 3D package.`
- `Direct, model, modify, and animate production assets in one workspace.`

Experiments should identify which underlying problem framing produces qualified creators, not merely which headline generates the most clicks.

Weak variants should be reduced or stopped. Strong variants should gain confidence only when downstream activation, retention, and value remain healthy.

## Intent-Specific Experiences

Different creator needs should not be forced through one generic acquisition and onboarding path.

Where appropriate, Growth Intelligence should align:

`Need -> Message -> Landing Experience -> Signup Context -> Onboarding -> First Value -> Relevant Capability`

A creator arriving because of character consistency should see a different first-value path from one arriving because of integrated 3D creation, rendering cost, storyboarding, collaboration, or another validated need.

This context may be used to improve relevance, but it MUST respect consent, privacy, policy, and data minimisation principles.

## Lifecycle and Retention Intelligence

Growth Intelligence extends beyond initial acquisition.

It may identify legitimate lifecycle states such as:

- signed up but not activated;
- created a project but not completed a first scene;
- reached a capability milestone;
- repeatedly encounters workflow friction;
- appears at risk of churn based on permitted first-party behaviour;
- becomes a successful repeat creator; or
- becomes suitable for an opt-in referral or advocacy experience.

The system may propose context-appropriate guidance, education, product assistance, or approved communications.

It MUST NOT use dark patterns, deceptive urgency, manipulative personal profiling, harvested contact data, or unsolicited outreach that violates consent or applicable rules.

## Creator-Led Growth

Nexkosmo should prefer growth loops that also create value for creators.

Examples may include:

- creator-controlled attribution links;
- opt-in referral programs;
- project sharing;
- reusable templates;
- marketplace assets;
- educational showcases;
- published works that voluntarily identify Nexkosmo as part of the production workflow; and
- collaboration invitations.

Growth mechanisms should increase creator agency rather than turn creators into involuntary advertising surfaces.

## Budget Intelligence

The Brain may compare acquisition channels and experiments using economic evidence.

For each channel or campaign it should consider, where available:

- acquisition cost;
- conversion quality;
- activation quality;
- retention;
- contribution margin;
- LTV;
- payback period;
- confidence interval or uncertainty;
- sample sufficiency;
- strategic relevance; and
- creator outcome quality.

The system may recommend reallocating budget toward better-performing opportunities, but significant budget changes require explicit approval under defined policy thresholds.

## Attribution

Growth attribution is inherently uncertain. Nexkosmo MUST NOT pretend every signup has one perfectly knowable cause.

The system should distinguish, where possible:

- direct attribution;
- assisted attribution;
- organic discovery;
- referral;
- creator-content discovery;
- paid acquisition;
- partner acquisition;
- marketplace/network effects; and
- unattributed/unknown acquisition.

Financial forecasts should use scenario ranges rather than assume that a fixed percentage of future customers will be generated by AI marketing.

## Learning Loop

Growth Intelligence should continuously learn which validated problems produce durable creator value.

For example:

- a campaign may generate high traffic but weak retention;
- another may generate fewer signups but much higher conversion and lifetime value.

The second opportunity may be economically and strategically stronger even with lower top-of-funnel volume.

The preferred learning loop is:

`Opportunity -> Hypothesis -> Experiment -> Qualified Signup -> Activation -> Usage -> Retention -> Revenue/Creator Outcome -> Evidence Update -> Next Decision`

Results should feed back into both Growth Intelligence and Market & Opportunity Intelligence so demand confidence and product priorities can improve over time.

## Governance Responsibilities

### Developmental Intelligence

May discover growth hypotheses, generate campaign alternatives, propose experiments, analyse outcomes, and identify improvements.

### Steward Worker

Evaluates whether an experiment or budget recommendation is a worthwhile use of resources and whether it aligns with Nexkosmo's principles, evidence standards, creator value, and opportunity cost.

### Human Authority

Humans retain final authority over consequential marketing claims, material budget changes, public brand campaigns, sensitive targeting decisions, partnerships, and major strategic changes.

### Operational Intelligence

May execute only approved production workflows within defined permissions, budgets, consent rules, rate limits, and policy boundaries.

## Safety, Privacy, and Trust Boundaries

Growth Intelligence MUST:

- use consent-respecting first-party data and legitimately available aggregate/public market intelligence;
- honour opt-out and communication preferences;
- preserve provenance for market-derived claims;
- avoid harvested personal contact databases;
- avoid deceptive claims about capabilities;
- avoid manipulation and dark patterns;
- avoid sensitive-trait targeting unless explicitly lawful, appropriate, and separately governed;
- keep spend authority bounded;
- retain audit trails for consequential automated decisions; and
- provide explainability for material recommendations.

## Success Criteria

The system is successful when it can demonstrate that it helps Nexkosmo:

1. find qualified creators more efficiently;
2. reduce CAC without degrading creator quality;
3. improve activation and time to first value;
4. improve retention and LTV;
5. identify which market needs produce durable value;
6. stop weak campaigns and weak opportunity hypotheses quickly;
7. scale strong opportunities responsibly; and
8. increase human agency for creators while building a sustainable business.

## Permanent Rule

> Do not optimise AI marketing for attention. Optimise the entire growth loop for retained creator value, sustainable economics, evidence, consent, and human agency.
