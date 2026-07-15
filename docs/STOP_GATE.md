# STOP-GATE Decision

## Decision

REJECTED FOR MILESTONE COMPLETION.

## Reason

The artifact environment did not provide Docker or PostgreSQL. Mandatory
PostgreSQL, concurrency, RLS, audit, outbox/inbox, idempotency recovery,
consent, rights, projection rebuild, backup/restore and load tests could not
execute.

The agreed rules state that skipped or unexecuted blocking tests do not count.

## Authorised next increment

Increment 2 may begin only in an environment with PostgreSQL 16 and Docker,
starting by running:

```bash
docker compose up -d postgres
docker compose run --rm migrate
docker compose run --rm test
docker compose run --rm restore-test
```

Any failure returns the work to this gate.
