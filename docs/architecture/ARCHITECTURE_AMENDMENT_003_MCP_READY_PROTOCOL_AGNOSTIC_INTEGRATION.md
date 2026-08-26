# Architecture Amendment 003: MCP-Ready, Protocol-Agnostic Integration

**Status:** Adopted as architectural policy  
**Implementation status:** Preparation only; MCP is not yet a production dependency  
**Applies to:** Brain Integration Layer, Studio integrations, workers, external tools, and future interoperability systems  
**Authority:** Nexkosmo Canon

## 1. Purpose

Nexkosmo shall prepare for Model Context Protocol (MCP) and similar interoperability standards without making the Brain, Governance, Canon, identity, project state, or critical production workflows dependent on any external protocol.

## 2. Governing Principle

> Nexkosmo shall be MCP-ready, not MCP-dependent.

The Brain remains the canonical source of truth. Governance and the Nexkosmo Guardian remain authoritative for policy, permissions, human control, and approval boundaries. MCP, native APIs, plugins, CLIs, worker protocols, and future interoperability mechanisms remain replaceable infrastructure.

## 3. Required Boundary

```text
Human Director
      |
      v
Nexkosmo Brain
      |
      v
Governance / Guardian
      |
      v
Orchestration
      |
      v
Brain Integration Layer
      |
      v
Nexkosmo Capability Contract
      |
      v
Adapter Boundary
  +-------+--------+--------+--------+
  | MCP   | Native | Plugin | Worker |
  |       | API    | / CLI  | Proto  |
  +-------+--------+--------+--------+
      |
      v
External tools, renderers, services, and agents
```

No external protocol may bypass this boundary.

## 4. Nexkosmo Capability Contract

Nexkosmo shall define stable, typed, protocol-independent capabilities before binding them to a transport or external system. Examples include GetProjectState, ResolveCanonicalAsset, GetCharacterIdentity, GetShotManifest, ValidateShot, RenderPreview, SubmitRender, GetJobStatus, CancelJob, GenerateAsset, RigCharacter, SimulateEffect, ImportAsset, ExportScene, ValidateResult, and GetCapabilityProfile.

Capability contracts shall use typed schemas, versioning, authorization, idempotency where applicable, and evidence/provenance requirements.

## 5. MCP Status

Current status: **WATCH / PREPARE**.

Allowed now:

- MCP-compatible adapter boundaries;
- protocol-independent capability contracts;
- documentation and interoperability research;
- controlled sandbox experiments;
- explicitly approved non-critical proof-of-concept MCP servers or clients;
- compatibility testing that creates no production dependency.

Not allowed yet:

- critical MCP-only workflows;
- direct MCP writes to canonical Brain state;
- MCP ownership of identity, Governance, permissions, continuity, or Canon;
- unrestricted database, shell, filesystem, infrastructure, or secret access through MCP;
- treating third-party MCP servers as trusted merely because they implement MCP;
- redesigning the Brain around MCP-specific concepts.

## 6. Governance and Human Authority

MCP is not Governance. Every MCP-originated action that can affect Nexkosmo state or external execution must pass through the same policy and authorization controls as every other integration.

```text
MCP request
    -> authentication / caller identity
    -> workspace and project authorization
    -> Guardian / policy evaluation
    -> Director authority or approval check where required
    -> typed Nexkosmo application command
    -> canonical application service / orchestration path
    -> evidence and audit record
```

MCP shall never be able to promote its own output to canonical truth.

## 7. Security Invariants

1. Least privilege is mandatory.
2. Tool scopes must be explicit and reviewable.
3. Sensitive assets and secrets must not be exposed by default.
4. Canonical database writes may occur only through authorised Nexkosmo application services.
5. Arbitrary shell execution, arbitrary filesystem access, and unrestricted database access are prohibited as general-purpose MCP capabilities.
6. Every material action must be attributable to an authenticated principal, service, or agent identity.
7. Material actions require appropriate evidence and audit records.
8. Workspace and project isolation must remain enforced.
9. Human approval gates must remain enforceable regardless of protocol.
10. External MCP servers are replaceable and potentially untrusted infrastructure boundaries.

## 8. Production Adoption Gate

MCP shall not become a production dependency until Nexkosmo has evidence of acceptable protocol stability, security and authorization, long-running job support where required, cancellation/retry/recovery behavior, failure containment, version compatibility, observability and auditability, ecosystem trust, and performance at the required scale.

A failed, stale, incompatible, malicious, or unavailable MCP server must never corrupt canonical state and must not prevent Nexkosmo from using an alternate integration route.

Production adoption requires an explicit future approval decision after these gates are evidenced.

## 9. Adapter Strategy

```text
Nexkosmo Capability
      |
      +-> MCP Adapter
      +-> Native API Adapter
      +-> Plugin Adapter
      +-> CLI Adapter
      +-> Worker/Queue Adapter
      +-> Future Protocol Adapter
```

MCP is an interoperability option, not a universal mandate. Nexkosmo shall choose the implementation that best satisfies reliability, security, performance, licensing, maintainability, deployment, and user-control requirements.

## 10. Creative Tool Integrations

For Blender, ComfyUI, Unreal Engine, Houdini, V-Ray, Arnold, DaVinci Resolve, Substance 3D, and future creative software, Nexkosmo shall first define the capability and governance contract, then select the most appropriate adapter technology.

No application shall be forced through MCP if a native integration is safer, more capable, more reliable, or materially more efficient.

## 11. First MCP Proof Rule

When MCP is ready for implementation testing, the first proof shall remain narrow:

1. one approved MCP server implementation;
2. one non-critical external application or capability;
3. read-only operations first where practical;
4. scoped writes only after read-only validation;
5. full Guardian/policy enforcement;
6. no direct canonical database access;
7. audit and evidence capture;
8. failure and disconnect testing;
9. proof that the same Nexkosmo capability can be fulfilled through another adapter route.

## 12. Architectural Invariants

1. The Brain remains canonical.
2. Governance remains above MCP.
3. MCP never becomes the source of truth.
4. MCP never becomes a required identity or policy authority.
5. External integrations remain behind stable contracts and adapters.
6. Nexkosmo must remain operable if MCP is replaced, unavailable, or rejected.
7. Protocol choice must not leak into canonical domain semantics.
8. Human Director authority remains enforceable across every integration path.
9. Evidence, provenance, isolation, and least privilege apply regardless of protocol.
10. Future MCP adoption is evidence-gated, not assumption-driven.

## 13. Supersession

This amendment does not replace the existing Brain, Governance, continuity, render orchestration, or renderer-adapter architecture. It extends those principles to general interoperability and establishes the rule that MCP may be adopted only as replaceable infrastructure beneath the Brain Integration Layer.