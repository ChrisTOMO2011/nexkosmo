# Nexkosmo Social Automation Protocol

Status: APPROVED DESIGN / RUNTIME IMPLEMENTATION PENDING
Authority: Director
Scope: Nexkosmo-owned social publishing, scheduling, content repurposing, community assistance, provider analytics, and evidence return.

## Purpose

Nexkosmo may automate repetitive social-media production and publishing work, but automation must preserve human authority, product truth, creator rights, security, and platform-specific behavior.

This protocol is an operating and engineering contract. It does not create a separate Marketing Brain. The existing Nexkosmo Brain may consume validated product and market evidence through its existing responsibilities, while the Social Automation Service remains an execution/integration system.

## Core rule

**AI may prepare and execute approved social work; it may not invent truth, rights, authority, or approval.**

The Director retains final authority over brand, consequential public claims, launch decisions, material campaigns, and spend.

## Initial channel set

The initial Nexkosmo-owned channel set is:

- YouTube
- Instagram
- TikTok
- LinkedIn
- Discord
- Reddit

Channel inclusion does not imply that every platform supports the same automation surface. Provider capabilities, permissions, API terms, rate limits, and publishing rules must be verified at implementation time.

## System boundary

The preferred runtime boundary is a Social Automation Service on Server 1, separate from the Brain and separate from renderer/GPU execution.

The service owns:

- content briefs and candidate-post workflow;
- platform-specific adaptation;
- approval state;
- scheduling;
- provider adapters;
- publish receipts and external identifiers;
- retry/idempotency state;
- platform analytics ingestion;
- social automation audit events.

The service does not own Nexkosmo product canon, creator canon, brand canon, or business truth.

## Required pipeline

`VERIFIED EVIDENCE -> CONTENT BRIEF -> CANDIDATE -> CLAIM/RIGHTS/BRAND CHECK -> DIRECTOR/POLICY APPROVAL -> SCHEDULE -> PROVIDER ADAPTER -> PUBLISH RECEIPT -> ANALYTICS EVIDENCE -> REVIEW/LEARNING`

No downstream stage may silently bypass an earlier required gate.

## Content states

A social item must have an explicit state:

- `DRAFT`
- `CHECK_REQUIRED`
- `APPROVAL_REQUIRED`
- `APPROVED`
- `SCHEDULED`
- `PUBLISHING`
- `PUBLISHED`
- `FAILED`
- `CANCELLED`
- `WITHDRAWN`

Only `APPROVED` content may become `SCHEDULED` or `PUBLISHING`.

## Approval model

### Always require explicit Director or authorized-human approval

- launch announcements;
- consequential product/business claims;
- pricing, financial, revenue, creator-income, performance, or comparative claims;
- partnership announcements;
- paid or sponsored campaigns;
- posts using customer/creator work unless the required consent and rights evidence is already present;
- crisis, controversy, legal, safety, security, or sensitive public responses;
- material changes to brand positioning.

### Eligible for future policy-based auto-publishing

Low-risk recurring content may be auto-published only after the Director explicitly creates an approved publishing policy that defines channel, content class, evidence requirements, cadence, expiry, and revocation rules.

A policy is not inferred from past approvals. Absence, expiry, contradiction, or uncertainty fails closed to `APPROVAL_REQUIRED`.

## Claims assurance

Every material claim must use the classifications from `docs/GROWTH_MARKETING_FRAMEWORK.md`:

- `VERIFIED_PRODUCT_FACT`
- `VERIFIED_BUSINESS_FACT`
- `CUSTOMER_EVIDENCE`
- `ESTIMATE`
- `ASPIRATION`
- `UNKNOWN`

`UNKNOWN` cannot be published as fact. A planned feature cannot be presented as live. A generated mockup cannot prove implementation. Provider engagement metrics are evidence only when retrieved from the provider or another documented authoritative source.

## Rights, privacy, and creator control

Before using an asset in social content, the automation must establish permitted use for that purpose.

The system must not:

- publish private creator assets without permission;
- infer public-use consent from upload alone;
- repurpose private prompts, scripts, conversations, or project data into social content;
- expose private workspace/project identifiers;
- manufacture testimonials, endorsements, creators, usage, engagement, or social proof.

Creator-owned work remains creator-owned. Public marketing use requires an appropriate permission/rights basis.

## Brand integrity

Approved canonical brand assets must be retrieved from the repository/asset registry, not redrawn or approximated.

The current canonical logo is `assets/brand/nexkosmo-x-star.svg` and must be used directly where the platform/artifact format permits it.

## Platform adaptation

One source brief may produce multiple platform-specific candidates, but each candidate must preserve the same factual meaning and rights boundary.

Adapters may change:

- length;
- aspect ratio;
- title/caption structure;
- hashtags/tags where appropriate;
- thumbnail/poster crop;
- call-to-action format;
- accessibility metadata;
- scheduling metadata.

Adapters may not alter factual certainty, claim classification, approved meaning, consent, or ownership.

## Community interaction

Reply automation is higher risk than scheduled outbound publishing because context is dynamic.

Default behavior:

- AI may draft replies;
- low-risk replies may become policy-eligible only after a separate explicit Director-approved policy exists;
- disputes, criticism, safety/security reports, legal issues, account problems, personal data, harassment, creator-rights disputes, partnership requests, and press inquiries must escalate to a human;
- automated deletion, suppression, argument, impersonation, or retaliatory behavior is prohibited.

Reddit and Discord participation must remain community-appropriate. Automation must not mass-post identical promotional material or behave like spam.

## Paid media

Autonomous ad spend is prohibited by default.

Paid acquisition remains blocked until the prerequisites in the Growth & Marketing Framework are evidenced. Any future paid-media integration requires an explicit spend policy, hard budget ceilings, human approval, provider-side account controls, audit evidence, and a dedicated threat/risk review.

## Credentials and provider security

Provider secrets are Tier 4 / critical credentials.

Requirements:

- never commit provider tokens, refresh tokens, client secrets, signing secrets, or recovery codes to Git;
- use a dedicated secret-management mechanism or protected runtime secret store;
- use least-privilege scopes;
- separate development/staging credentials from production;
- prefer organization/business accounts and delegated roles over shared personal master credentials;
- support token rotation/revocation;
- audit credential use without logging secret values;
- treat provider webhooks and callbacks as untrusted external input until authenticated and validated.

## Publish safety, idempotency, and retries

Publishing is an externally visible side effect.

Each publish attempt must have a stable internal idempotency identity and store the provider receipt/external post identifier where available.

When provider outcome is uncertain, the system must reconcile remote state before retrying where practical. It must not blindly retry an uncertain publish and risk duplicate public posts.

Retry policy must use bounded retries, exponential backoff where appropriate, provider rate-limit handling, dead-letter/manual-review state, and explicit failure evidence.

## Scheduling

Schedules must be stored in UTC with an explicit display timezone.

Editing or cancelling scheduled content must preserve audit history. A stale approval must not survive a material content change; changing claim meaning, asset set, destination, or consequential timing returns the item to approval.

## Evidence and audit

For each published item, retain at minimum:

- internal content ID and version;
- source evidence references;
- claim classifications;
- rights/consent references where applicable;
- platform/account identity;
- candidate content hash;
- approver identity or approved policy identity;
- approval timestamp;
- scheduled time;
- publish attempt history;
- provider receipt/external post ID where available;
- final publish status;
- analytics source and observation timestamps;
- withdrawal/deletion status where applicable.

## Analytics

Provider metrics must retain source, observation timestamp, metric definition, and data-quality limitations.

Missing metrics are `UNKNOWN`, not zero. Cross-platform metrics must not be summed or compared as if definitions are identical unless the normalization is documented and defensible.

The service may recommend future content based on evidence, but recommendations do not become approved strategy or canon automatically.

## Observability

Required operational signals include:

- queue depth;
- scheduled items due/late;
- publish success/failure rate;
- duplicate-prevention events;
- rate-limit events;
- authentication/token failures;
- webhook validation failures;
- provider latency/error rates;
- approval backlog;
- analytics ingestion freshness.

Alerts should prioritize failures that could cause duplicate publishing, unauthorized publishing, credential compromise, or loss of audit evidence.

## Initial infrastructure estimate

These are planning estimates, not measured runtime facts.

For the first production-capable Server 1 implementation:

- CPU: approximately 2-4 vCPU for API/scheduler/adapter work, excluding heavy media encoding;
- RAM: approximately 2-4 GB service budget initially;
- database/storage: approximately 1-5 GB initially for metadata/audit/receipts, growing with retention;
- media staging/cache: approximately 50-200 GB NVMe initially if social derivatives are staged locally;
- long-term media should reuse Nexkosmo's approved asset/object-storage architecture rather than turning the social service into a second canonical asset store.

Heavy video transcoding should use a bounded media worker or existing execution path rather than blocking the social API/scheduler process.

## Implementation sequence

Implementation must not jump ahead of Nexkosmo's current alignment STOP GATE. The current product vertical slice remains the higher engineering priority.

When authorized for implementation, build in this order:

1. provider-neutral domain model and approval state machine;
2. audit/event schema;
3. secret/credential boundary and threat-model controls;
4. scheduler + durable outbox/idempotency;
5. one low-risk provider adapter in development/staging;
6. publish receipt reconciliation and negative tests;
7. analytics ingestion contract;
8. Director approval dashboard;
9. additional provider adapters one at a time;
10. policy-based low-risk auto-publishing only after manual approval workflow is proven.

Do not implement six providers simultaneously as the first slice.

## Completion standard

Social automation is not "implemented" because a post was sent once.

A provider integration is implementation-complete only when its authentication, scopes, approval boundary, idempotency, rate-limit behavior, failure/retry path, audit evidence, security tests, provider receipt reconciliation, and staging/runtime evidence have been demonstrated.
