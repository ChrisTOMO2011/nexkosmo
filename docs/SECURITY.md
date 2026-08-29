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

## Operational truth security requirements

- Material evidence used for consequential decisions must preserve provenance and evidence-lineage references sufficient to distinguish independent corroboration from repeated use of the same source.
- Consequential success must not be self-certified solely by the actor whose work or behavior is being evaluated.
- Independent validation evidence should be protected from alteration by the claimant when the validation is used to approve, release, canonise, pay, promote, restore authority, or clear an incident.
- Material agent/Brain incidents must preserve protected evidence sufficient for later reconstruction without trusting the component under investigation.
- Incident evidence should include authenticated actor, authority, material instructions, relevant evidence-lineage references, policy decisions, tool/external actions, contradictions, validation results, state transitions, and Guardian/control-plane responses where applicable.
- Audit/event integrity should make missing, reordered, or altered material records detectable through sequence, hash chaining, append-only storage, signatures, or equivalent controls appropriate to the implementation.
- Replay or root-cause tooling must default to reconstruction/simulation and must not automatically repeat consequential external side effects.
- A suspect agent or Brain instance must not be the sole authority that clears its own incident, restores its own privileges, or certifies its own evidence record as complete.
- Privacy, consent, rights, retention, and least-privilege requirements still apply to incident evidence; observability is not permission for unrestricted logging.

Full authorization coverage, policy-issuance persistence flow, Guardian enforcement, independent audit sequencing, evidence-lineage enforcement, protected incident replay, and outcome-integrity validation are not yet proven end to end.
