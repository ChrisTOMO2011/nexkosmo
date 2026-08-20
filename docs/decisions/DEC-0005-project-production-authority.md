# DEC-0005: Project and Production authority

- Status: Approved for Migration Slice 3B implementation
- Date: 2026-08-20
- Manifest: version 9

## Decision

The canonical ownership hierarchy is `Workspace -> Project -> Production`. This
authority hierarchy is separate from the creative workflow
`IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION`. Studio remains a
contextual deep editor, not a seventh stage.

PostgreSQL and the Python domain are authoritative. Token claims and frontend
state can only narrow persisted authority; they cannot create it.

## Workspace authority

Persisted Workspace roles are stored as `owner`, `admin`, `member`, and
`viewer`, corresponding to Owner, Admin, Member, and Viewer. They are effective
only during the membership validity period and only for a human agent associated
with the human principal.

- Owner and Admin may create Projects.
- Member and Viewer may not create Projects.
- Workspace administrative authority does not imply Project-content access.
- A Workspace Viewer may receive only Project Viewer membership.
- Workspace provisioning and membership mutation remain trusted control-plane
  responsibilities. The normal application role has read-only access to
  `workspace_memberships`.

`principal_id` is the authority identity. `agent_id` records the currently
authenticated human acting context. An AI, service, organization, or machine
agent cannot become a Workspace or Project authority principal in this slice.

## Project authority

Project roles are Owner, Admin, Editor, and Viewer. Every Project member must be
an active human member of the same Workspace. A Project has exactly one active
Owner, and the aggregate's `owner_principal_id` must match that membership.

Ownership transfer is an Owner-only, expected-version, idempotent transaction.
The target must already be an eligible active Project member. The target becomes
Owner, the previous Owner becomes Admin, the Project version increases once,
and the completed idempotency response, outbox event, and audit-delivery intent
commit with the change.

Project lifecycle is limited to `active` and `archived`. Archive and restore are
Owner-only. Archived Projects are retained and read-only. There are no delete
policies for canonical Projects or Productions.

## Production

A Production belongs to one Project and inherits its Workspace and authority.
It has no owner or membership table. The operational states are `planned`,
`active`, `paused`, `completed`, and `archived`. The approved transitions are:

- planned to active or archived;
- active to paused, completed, or archived;
- paused to active or archived;
- completed to active or archived.

Archived is terminal. These operational states do not represent the creative
workflow and do not add a `workflow_stage` field.

## Semantic Kernel relationship

Creating a Project atomically creates the existing Semantic Kernel
`IdentityKind.PROJECT`, a separate context Identity, a `ContextKind.PROJECT`,
the Project aggregate and Owner membership, and a creation Activity with the
Project Identity as output. Frozen Semantic Kernel primitives are unchanged.

## Failure, remediation, and evidence

If the Owner no longer has eligible active human Workspace membership, or an
effective unresolved authority-remediation record exists, consequential
mutations fail closed. No replacement Owner is inferred. Remediation resolution
is schema-supported but has no normal HTTP route in Slice 3B.

The audit delivery queue is durable transaction intent, not audit truth. The
independent append-only audit store remains canonical after delivery. Delivery
failure leaves retryable queue state and does not reverse committed business
state.

## Consequences

This slice intentionally does not introduce Project truth in TypeScript,
Production UI, Character or Environment dependencies, workflow/readiness/render
state, demo owners, hard-coded principals, or destructive downgrade behavior.
