from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID

from app.domain.enums import (
    AgentKind,
    AssertionObjectKind,
    ContextKind,
    DecisionOutcome,
    EpistemicStatus,
    IdentityKind,
    PolicyEffect,
)


@dataclass(frozen=True, slots=True)
class Principal:
    principal_id: UUID
    workspace_id: UUID
    agent_id: UUID
    agent_kind: AgentKind
    memberships: frozenset[UUID] = frozenset()
    delegated_actions: frozenset[str] = frozenset()


@dataclass(frozen=True, slots=True)
class Identity:
    id: UUID
    workspace_id: UUID
    kind: IdentityKind
    canonical_key: str
    created_at: datetime
    revision: int = 1


@dataclass(frozen=True, slots=True)
class Agent:
    identity_id: UUID
    kind: AgentKind
    display_name: str


@dataclass(frozen=True, slots=True)
class Context:
    identity_id: UUID
    workspace_id: UUID
    kind: ContextKind
    parent_context_id: UUID | None


@dataclass(frozen=True, slots=True)
class Assertion:
    id: UUID
    workspace_id: UUID
    subject_id: UUID
    predicate: str
    object_kind: AssertionObjectKind
    object_identity_id: UUID | None
    object_value: dict[str, Any] | None
    context_id: UUID
    asserted_by: UUID
    epistemic_status: EpistemicStatus
    valid_from: datetime | None
    valid_to: datetime | None
    recorded_at: datetime
    supersedes_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class EvidenceLink:
    assertion_id: UUID
    evidence_identity_id: UUID
    relation: str
    recorded_at: datetime


@dataclass(frozen=True, slots=True)
class Activity:
    id: UUID
    workspace_id: UUID
    activity_type: str
    performed_by: UUID
    context_id: UUID
    started_at: datetime
    ended_at: datetime | None
    inputs: tuple[UUID, ...] = ()
    outputs: tuple[UUID, ...] = ()
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class Policy:
    id: UUID
    workspace_id: UUID
    action: str
    effect: PolicyEffect
    subject_agent_id: UUID
    resource_identity_id: UUID
    context_id: UUID
    purpose: str
    valid_from: datetime
    valid_to: datetime | None
    constraints: dict[str, Any]


@dataclass(frozen=True, slots=True)
class Decision:
    id: UUID
    workspace_id: UUID
    decision_type: str
    outcome: DecisionOutcome
    decided_by: UUID
    context_id: UUID
    target_ids: tuple[UUID, ...]
    policy_ids: tuple[UUID, ...]
    evidence_ids: tuple[UUID, ...]
    reasons: tuple[str, ...]
    alternatives: tuple[str, ...]
    decided_at: datetime


@dataclass(frozen=True, slots=True)
class BeliefResolution:
    accepted: tuple[UUID, ...]
    rejected: tuple[UUID, ...]
    proposed: tuple[UUID, ...]
    disputed: tuple[UUID, ...]
    unknown: tuple[str, ...]
    decision_ids: tuple[UUID, ...]
    explanation: tuple[str, ...]
