# Database overview

Alembic is the only schema migration mechanism. PostgreSQL roles separate schema
ownership, application access and independent audit writes. Canonical ownership
is Workspace -> Project -> Production -> Character or Environment, enforced by foreign keys,
repository checks and forced RLS.

Current source head: `0011_environment_forest`.

Environment schema is introduced forward-only by `0009_environment_domain`,
`0010_environment_readiness` and `0011_environment_forest`. It includes canonical
packages, type capabilities, manifest compatibility, selections, structured readiness,
optimistic versions, RLS policies, audit intent and outbox-compatible mutation state.

Development migration:

```sh
alembic upgrade head
alembic current
```

Development backup/restore rehearsal:

```sh
./scripts/backup_restore_rehearsal.sh
```

The rehearsal must restore into a separate database and validate canonical rows,
versions, audit-chain links, outbox state and RLS. A successful local rehearsal is
development evidence only, not a production disaster-recovery guarantee.
