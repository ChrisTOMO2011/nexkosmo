# Nexkosmo Staging Runbook

Status: ACTIVE STAGING OPERATIONS CONTRACT

Authority: Director

Alignment manifest: version 9

## Environment boundary

This runbook applies only to `https://staging.nexkosmo.com` on Server 1 under
the deployment identity `nexkosmo-deploy`. Production is out of scope. Use the
purpose-scoped `nexkosmo-staging-*` wrappers; direct Docker or unrestricted root
access is neither required nor authorized for normal Staging work.

Canonical loopback port mappings:

- API: host `18000` -> container `8000`.
- Keycloak: host `18080` -> container `8080`.
- Frontend: host `18081` -> container `8080`.

## Release and rollback

1. Confirm the repository is clean, on
   `migration/staging-batch-01-application-readiness`, and the approved commit is
   present on the remote branch.
2. Create the release archive from the exact Git commit, not the mutable worktree.
3. Place it at `/opt/nexkosmo/staging/app/incoming/<sha>.tar.gz`.
4. Run `sudo nexkosmo-staging-release import <sha>` and then
   `sudo nexkosmo-staging-release activate <sha>`.
5. Run `sudo nexkosmo-staging-compose validate`, `build`, `migrate`, and `up`.
6. Require `/api/health/ready` to report `ready`, the exact release SHA, and
   migration `0005_staging_readiness`.
7. Preserve the preceding release directory and container images as the rollback
   target. Rollback uses the same `activate <known-good-sha>`, `build`, and `up`
   sequence and must be followed by readiness verification.

Never place secrets in the release archive, logs, browser evidence, or repository.
Back up before a schema-changing release. This login repair does not change schema.

## Login acceptance

Run `pnpm test:staging-login` from `frontend/` with a clean Playwright browser.
The test is hard-bound to Staging and uses no credentials. It verifies:

- OIDC Authorization Code with PKCE S256, state, client ID, and callback;
- visible username/password fields, labels, validation, and sign-in button;
- computed visibility, focus indication, and WCAG text contrast;
- required versioned Keycloak assets, status, content types, and cache headers;
- `no-store` authorization HTML; and
- no relevant console, page, network, or HTTP failures.

Cloudflare may inject its analytics beacon after origin delivery. Staging CSP is
expected to block that unapproved third-party script; the test excludes only that
specific blocked request. All Nexkosmo and Keycloak errors remain failures.

The reverse proxy must use the path-scoped `/auth/` CSP in
`deploy/staging/nexkosmo-staging.conf`. Keycloak 26 emits trusted inline import maps
and per-flow initialization, so the generic application `script-src 'self'` policy
must not be intersected with the login response. The scoped policy permits inline
Keycloak initialization but retains same-origin script loading, clickjacking
protection, `object-src 'none'`, form/action, base, image, font, and connection
restrictions.

After automated acceptance, the Director opens
`https://staging.nexkosmo.com/` in a private browser window, selects **Continue
securely**, and authenticates without sharing credentials. A hard refresh is not
required in a private window. The Director then confirms the Project directory is
shown and returns control to Codex for authenticated read-only claims and
Project/Character list/read acceptance.

## Read-only authority and data-integrity proof

Before and after interactive acceptance, use the fixed read-only wrappers:

- `sudo nexkosmo-staging-authority-read db`
- `sudo nexkosmo-staging-authority-read keycloak`

Compare the stable Workspace, human agent, active membership, Keycloak subject,
authority attributes, and mapper output. Do not record credentials, access tokens,
cookies, transient authorization codes, or private keys. Project and Character
acceptance uses only list/read routes; no create, update, delete, archive, owner,
membership, or authority mutation is permitted.
