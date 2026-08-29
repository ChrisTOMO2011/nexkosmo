from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.domain.enums import (
    AgentKind,
    AssertionObjectKind,
    EpistemicStatus,
    PolicyEffect,
)
from app.domain.errors import AuthorizationDenied, InvariantViolation
from app.domain.rules import (
    require_authenticated_actor,
    require_human_authority,
    validate_assertion,
    validate_policy_issuance,
)
from app.domain.types import Assertion, Policy, Principal

U = UUID("10000000-0000-0000-0000-000000000001")
OTHER = UUID("10000000-0000-0000-0000-000000000002")
NOW = datetime(2026, 8, 30, tzinfo=UTC)


def principal(
    *,
    kind: AgentKind = AgentKind.HUMAN,
    actions: frozenset[str] = frozenset(),
) -> Principal:
    return Principal(
        principal_id=U,
        workspace_id=U,
        agent_id=U,
        agent_kind=kind,
        delegated_actions=actions,
    )


def test_ai_cannot_exercise_human_approval_authority():
    ai = principal(kind=AgentKind.AI, actions=frozenset({"knowledge.decide"}))
    with pytest.raises(AuthorizationDenied):
        require_human_authority(ai, "knowledge.decide")


def test_claimed_actor_must_match_authenticated_principal():
    human = principal(actions=frozenset({"knowledge.decide"}))
    with pytest.raises(AuthorizationDenied):
        require_authenticated_actor(human, OTHER, "knowledge.decide")


def test_assertion_cannot_start_as_accepted():
    assertion = Assertion(
        id=U,
        workspace_id=U,
        subject_id=U,
        predicate="character.eye_colour",
        object_kind=AssertionObjectKind.LITERAL,
        object_identity_id=None,
        object_value={"value": "blue"},
        context_id=U,
        asserted_by=U,
        epistemic_status=EpistemicStatus.ACCEPTED,
        valid_from=None,
        valid_to=None,
        recorded_at=NOW,
    )
    with pytest.raises(InvariantViolation):
        validate_assertion(assertion)


def test_ai_cannot_issue_policy_even_with_delegated_action():
    ai = principal(kind=AgentKind.AI, actions=frozenset({"policy.issue"}))
    policy = Policy(
        id=OTHER,
        workspace_id=U,
        action="knowledge.read",
        effect=PolicyEffect.PERMIT,
        subject_agent_id=OTHER,
        resource_identity_id=OTHER,
        context_id=U,
        purpose="belief_resolution",
        valid_from=NOW,
        valid_to=None,
        constraints={},
        issued_by=U,
    )
    with pytest.raises(AuthorizationDenied):
        validate_policy_issuance(ai, policy)


def test_policy_issuer_must_match_authenticated_principal():
    human = principal(actions=frozenset({"policy.issue"}))
    policy = Policy(
        id=OTHER,
        workspace_id=U,
        action="knowledge.read",
        effect=PolicyEffect.PERMIT,
        subject_agent_id=OTHER,
        resource_identity_id=OTHER,
        context_id=U,
        purpose="belief_resolution",
        valid_from=NOW,
        valid_to=None,
        constraints={},
        issued_by=OTHER,
    )
    with pytest.raises(AuthorizationDenied):
        validate_policy_issuance(human, policy)


def test_principal_cannot_issue_permit_to_expand_own_authority():
    human = principal(actions=frozenset({"policy.issue"}))
    policy = Policy(
        id=OTHER,
        workspace_id=U,
        action="knowledge.read",
        effect=PolicyEffect.PERMIT,
        subject_agent_id=U,
        resource_identity_id=OTHER,
        context_id=U,
        purpose="belief_resolution",
        valid_from=NOW,
        valid_to=None,
        constraints={},
        issued_by=U,
    )
    with pytest.raises(AuthorizationDenied):
        validate_policy_issuance(human, policy)


def test_authorised_human_can_issue_policy_for_another_agent():
    human = principal(actions=frozenset({"policy.issue"}))
    policy = Policy(
        id=U,
        workspace_id=U,
        action="knowledge.read",
        effect=PolicyEffect.PERMIT,
        subject_agent_id=OTHER,
        resource_identity_id=OTHER,
        context_id=U,
        purpose="belief_resolution",
        valid_from=NOW,
        valid_to=None,
        constraints={},
        issued_by=U,
    )
    validate_policy_issuance(human, policy)
