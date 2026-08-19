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

The current increment deliberately stops before claiming full implementation.
Repository adapters, the complete Aiden database fixture, event dispatcher,
consumer worker, API command surface, metrics/traces wiring, and all twenty
integration proofs remain blocking.
