# Current system map

```text
Browser
  / -> static cinematic landing
  /studio and /studio/* -> React/Vite application
        |
        | JSON + bearer token + Idempotency-Key
        v
FastAPI routers -> application services -> UnitOfWork
                                      |-> PostgreSQL repositories (forced RLS)
                                      |-> idempotency response
                                      |-> transactional outbox
                                      `-> audit delivery intent

Audit delivery coordinator -> independent audit connection -> hash-chained audit log
Outbox dispatcher -> typed registry -> no product consumers registered in Phase 2C
```

Process liveness is separate from dependency readiness. Readiness reports the
database revision, audit database, dispatcher configuration and the deferred
semantic-kernel state.
