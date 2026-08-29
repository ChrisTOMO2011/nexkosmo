# Security Model

- Authentication is behind a `PrincipalVerifier` port.
- The production adapter is OIDC/JWKS-ready and permits RS256/ES256.
- Principal claims distinguish human, AI, service and organisation agents.
- Every Unit of Work sets transaction-local workspace, principal and agent IDs.
- Tenant tables use `ENABLE ROW LEVEL SECURITY` and `FORCE ROW LEVEL SECURITY`.
- Application and audit database roles are separate.
- Capability and authority are separate domain concepts.
- Audit success, denial and failure are designed for an independent commit path.
- Claimed assertion and decision actors must match the authenticated principal before persistence.
- Policy issuance is human-authority-only in the domain contract, must bind `issued_by` to the authenticated principal, and must reject self-issued permits that expand the issuer's own authority.
- Merely storing an agent ID is not sufficient provenance; consequential attribution must be bound to authenticated identity and preserved in audit/evidence records.
- Missing permission or missing safety evidence fails closed rather than becoming implicit permission.

Full authorization coverage, policy-issuance persistence flow, Guardian enforcement, and audit sequencing are not yet proven end to end.
