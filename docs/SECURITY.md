# Security Model

- Authentication is behind a `PrincipalVerifier` port.
- The production adapter is OIDC/JWKS-ready and permits RS256/ES256.
- Principal claims distinguish human, AI, service and organisation agents.
- Every Unit of Work sets transaction-local workspace, principal and agent IDs.
- Tenant tables use `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY`.
- Application and audit database roles are separate.
- Capability and authority are separate domain concepts.
- Audit success, denial and failure use a durable delivery queue and an independent
  audit-role commit path.
- The application role cannot read or mutate the immutable audit ledger.

The OIDC adapter is validated with a mocked provider. A real production identity
provider has not been exercised and remains an explicit release gate. See
[`architecture/security-model.md`](architecture/security-model.md).
