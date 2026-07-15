# Architecture

This increment is a modular monolith with one PostgreSQL business transaction
boundary and a separate least-privilege audit transaction boundary.

The permanent kernel areas are represented without creating independent State,
Memory, Graph, World State, Search, Embedding, or Explainability truth stores.

- Domain: dependency-free scientific and semantic rules.
- Application: use-case orchestration through ports.
- Infrastructure: authentication adapter, PostgreSQL, RLS and migrations.
- Interfaces: HTTP and operational endpoints.

The current increment deliberately stops before claiming full implementation.
Repository adapters, the complete Aiden database fixture, event dispatcher,
consumer worker, API command surface, metrics/traces wiring, and all twenty
integration proofs remain blocking.
