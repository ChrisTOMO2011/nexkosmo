# ADR 0004: Frontend HTTP client boundary

Status: accepted.

React accesses canonical data only through typed API gateways. Gateways attach
the current bearer token, preserve idempotency keys and map problem responses to
typed errors. No backend APIs are invented in presentation components.
