# ADR 0006: Reliable command boundary

Status: accepted.

A mutation atomically commits its aggregate, optimistic version, idempotent
response, outbox event and audit-delivery intent. Audit remains an independent
hash-chained store and is delivered after commit with durable retry and a unique
deduplication key. Outbox delivery is leased, retried with backoff and dead
lettered after exhaustion. Consumers use an inbox key.

Guarantees are at-most-one mutation per idempotency key, retry-safe response
recovery and at-least-once deduplicated delivery. Exactly-once delivery is not
claimed.
