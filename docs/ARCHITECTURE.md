# Architecture

This increment is a modular monolith with one PostgreSQL business transaction
boundary and a separate least-privilege audit transaction boundary.

The permanent kernel areas are represented without creating independent State,
Memory, Graph, World State, Search, Embedding, or Explainability truth stores.

- Domain: dependency-free scientific and semantic rules.
- Application: use-case orchestration through ports.
- Infrastructure: authentication adapter, PostgreSQL, RLS and migrations.
- Interfaces: HTTP and operational endpoints.

## Product intelligence direction

Market & Opportunity Intelligence is an enduring higher-level product-intelligence
responsibility, not a competing source of semantic truth and not a claim of
implementation in this increment. It discovers permitted public market signals,
clusters underlying creator needs, evaluates multi-signal Demand Confidence,
identifies Capability Gaps, and routes strong candidates through Developmental
Intelligence, Steward review, explicit human approval, experimentation, behavioural
validation, and deliberate production promotion.

Visible feedback must never be treated as market size. Silent demand may be inferred
with explicit uncertainty, and consequential opportunity recommendations must retain
provenance and explainability. See `MARKET_OPPORTUNITY_INTELLIGENCE.md` for the
normative product-intelligence contract.

## Growth intelligence direction

Growth Intelligence is an enduring higher-level responsibility connected to Market &
Opportunity Intelligence. It converts validated creator needs that Nexkosmo can
actually satisfy into controlled acquisition, activation, retention, and learning
experiments. It may prepare intent-specific landing experiences, campaign variants,
educational content, onboarding paths, lifecycle interventions, creator-led growth
loops, and budget recommendations, but it must optimise for retained creator value and
sustainable economics rather than clicks or impressions.

Growth attribution remains uncertain and must be represented as evidence and scenario
ranges rather than guaranteed AI-generated customer percentages. Material public
campaigns, marketing claims, spending changes, partnerships, and other consequential
actions remain governed by Steward review, policy limits, and explicit human authority.
The subsystem must respect consent, privacy, provenance, opt-out requirements, and the
prohibition on harvested contact data or deceptive outreach. See
`GROWTH_INTELLIGENCE.md` for the normative growth-intelligence contract.

The preferred product-to-growth learning loop is:

`Market Signal -> Need Cluster -> Demand Confidence -> Capability Match -> Growth Hypothesis -> Human Approval -> Controlled Experiment -> Acquisition -> Activation -> Retention -> Revenue/Creator Outcome -> Evidence Update`

The current increment deliberately stops before claiming full implementation.
Repository adapters, the complete Aiden database fixture, event dispatcher,
consumer worker, API command surface, metrics/traces wiring, and all twenty
integration proofs remain blocking.
