# Security Model

- Authentication is behind a `PrincipalVerifier` port.
- The production adapter is OIDC/JWKS-ready and permits RS256/ES256.
- Principal claims distinguish human, AI, service and organisation agents.
- Every Unit of Work sets transaction-local workspace, principal and agent IDs.
- Tenant tables use `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY`.
- Application and audit database roles are separate.
- Capability and authority are separate domain concepts.
- Audit success, denial and failure are designed for an independent commit path.

Full authorization coverage and audit sequencing are not yet proven.
