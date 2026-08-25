# Architecture

This increment is a modular monolith with one PostgreSQL business transaction
boundary and a separate least-privilege audit transaction boundary.

The permanent kernel areas are represented without creating independent State,
Memory, Graph, World State, Search, Embedding, or Explainability truth stores.

- Domain: dependency-free scientific and semantic rules.
- Application: use-case orchestration through ports.
- Infrastructure: authentication adapter, PostgreSQL, RLS and migrations.
- Interfaces: HTTP and operational endpoints.

## BUILD and render preparation direction

BUILD is the Director-facing preparation layer that converts visible Scene and Shot decisions into a complete, machine-readable, versioned Render Specification.

The governing rule is:

`What the Director sees in BUILD must be what the rendering system receives.`

Material visible edits must map to structured state. Canonical asset identity/version, scoped Scene/Shot overrides, character state, spatial placement, environment, camera, lighting, materials, CGI/VFX/audio references, uploaded guidance, masks/depth/control data, positive instructions, explicit exclusions, continuity, generation metadata, provenance, and accepted preview evidence must be represented when applicable.

Director approval freezes an immutable Render Specification version. AI may propose creative alternatives before approval, but approved state must not be silently reinterpreted by BUILD, Studio, orchestration, renderer adapters, or rendering models. Variations branch from existing state rather than mutating approved state.

Studio may enrich approved BUILD preparation with performance and timing, but it must not silently change frozen identity, composition, canonical assets, camera preparation, environment preparation, wardrobe, continuity, or other material approved state.

The Render Orchestrator converts approved Render Specifications and Continuity Snapshots into executable Render Manifests. Renderer adapters translate those manifests into provider-specific controls without changing approved creative meaning.

See `architecture/BUILD_RENDER_SPECIFICATION_CONTRACT.md` and `architecture/ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md` for the normative contracts.

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
