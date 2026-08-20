# Architecture

This increment is a modular monolith with one PostgreSQL business transaction
boundary and a separate least-privilege audit transaction boundary.

The permanent kernel areas are represented without creating independent State,
Memory, Graph, World State, Search, Embedding, or Explainability truth stores.

- Domain: dependency-free scientific and semantic rules.
- Application: use-case orchestration through ports.
- Infrastructure: authentication adapter, PostgreSQL, RLS and migrations.
- Interfaces: HTTP and operational endpoints.

The current foundation includes Character and Project/Production repository and
HTTP slices, a transactional outbox dispatcher foundation, a durable audit
delivery queue and a unified frontend route surface. Product consumers and the
semantic-kernel runtime are deliberately not activated.

The maintained baseline and status are in
[`architecture/master-architecture-baseline.md`](architecture/master-architecture-baseline.md)
and [`roadmap/phase-status.md`](roadmap/phase-status.md).
