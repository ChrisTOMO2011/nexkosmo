# Security model

Production requires OIDC mode, HTTPS issuer/JWKS endpoints, a configured audience
and no example identity endpoints. Tokens require issuer, audience, signature,
expiry, issued-at, subject, token ID, workspace, agent and agent-kind claims.

The application resolves a `Principal`, applies Owner/Admin/Editor/Viewer rules,
and sets workspace/principal/agent transaction context. Tenant tables use forced
PostgreSQL row-level security. The application role has only the grants required
for API work. The audit role is separate and the audit log is hash chained.

Development header authentication is restricted to non-production settings.
The current test state is mocked-provider validated; real-provider validation is
not claimed. Frontend access tokens are held in memory and cleared on logout.
