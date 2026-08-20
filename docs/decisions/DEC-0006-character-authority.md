# DEC-0006: Project-owned Character authority

- Status: Approved for Migration Slice 4 implementation
- Date: 2026-08-20
- Manifest: version 9

## Decision

A Character is a canonical Project-owned record in the authority hierarchy
`Workspace -> Project -> Character`. It is reusable by Productions inside the
same Project. Production-specific continuity, costume, version, shot, or other
use state requires a later explicit `ProductionCharacterBinding`; Slice 4 does
not create that binding and the core Character has no `production_id`.

PostgreSQL and the Python domain are authoritative. Frontend state is not
Character truth and no frontend Character Brain, catalogue, compatibility,
pipeline, generation, preview, or asset authority is introduced.

## Minimal aggregate

The Slice 4 Character contains only `id` (also `identity_id`), `workspace_id`,
`project_id`, `created_by_principal_id`, `display_name`, optional `role_label`,
`version`, `created_at`, and `updated_at`.

Workspace, Project, semantic Identity, creation provenance, and creation time
are immutable. Display name is trimmed and 1-160 characters. Role label is
optional free-form metadata of at most 160 characters. Every successful
metadata mutation changes a value and advances the version exactly once.
Character deletion and destructive migration downgrade are prohibited.
Archive/restore remains deferred.

## Authority

Active human Workspace and Project membership are both required. Project Owner,
Admin, and Editor may create and update Character metadata. Project Viewer may
list and read only. Workspace Owner/Admin authority without Project membership
does not grant Character-content access.

An archived Project or an effective authority-remediation lock blocks Character
mutation. Claims can narrow authority but cannot create persisted membership.
There is no Character DELETE route, RLS policy, or application grant.

## Semantic Kernel relationship

Character uses the existing `IdentityKind.CHARACTER`; no new primitive or
Character Context is created. Creation and metadata mutation append Activities
inside the owning Project Context. Each Activity attributes the acting human
principal and agent, and records the Character Identity as output.

## Transaction and API

Writes use the existing transactional idempotency lease and commit Character,
semantic Activity/provenance, completed idempotency response, outbox event, and
audit-delivery intent atomically. Independent audit delivery occurs after the
business commit and cannot reverse it.

Only nested Project routes are exposed:

- `POST /v1/workspaces/{workspaceId}/projects/{projectId}/characters`
- `GET /v1/workspaces/{workspaceId}/projects/{projectId}/characters`
- `GET /v1/workspaces/{workspaceId}/projects/{projectId}/characters/{characterId}`
- `PATCH /v1/workspaces/{workspaceId}/projects/{projectId}/characters/{characterId}`

Writes require an idempotency key. PATCH requires `expected_version`.

## Deferred decisions

Species, body, age, accessory and editor-tab catalogues; asset manifests;
compatibility; readiness; lifecycle; uploads; generation; preview; renderer
state; and Production bindings remain separate Director gates. Candidate seed
data, `brain://` references, generated UUIDs, and legacy pipeline invalidation
rules are not promoted by this decision.
