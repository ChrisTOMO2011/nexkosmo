from datetime import UTC, datetime
from uuid import UUID

import pytest
from hypothesis import given, strategies as st

from app.domain.enums import (
    AgentKind,
    AssertionObjectKind,
    DecisionOutcome,
    EpistemicStatus,
)
from app.domain.errors import AuthorizationDenied, InvariantViolation
from app.domain.rules import (
    require_human_authority,
    require_human_decision_authority,
    validate_assertion,
)
from app.domain.types import Assertion, Decision, Principal

U = UUID("10000000-0000-0000-0000-000000000001")
OTHER = UUID("10000000-0000-0000-0000-000000000002")


def test_ai_cannot_exercise_human_approval_authority():
    principal = Principal(
        principal_id=U,
        workspace_id=U,
        agent_id=U,
        agent_kind=AgentKind.AI,
        delegated_actions=frozenset({"knowledge.decide"}),
    )
    with pytest.raises(AuthorizationDenied):
        require_human_authority(principal, "knowledge.decide")


def test_human_cannot_attribute_decision_to_another_identity():
    principal = Principal(
        principal_id=U,
        workspace_id=U,
        agent_id=U,
        agent_kind=AgentKind.HUMAN,
        delegated_actions=frozenset({"knowledge.decide"}),
    )
    decision = Decision(
        id=U,
        workspace_id=U,
        decision_type="canon.resolve",
        outcome=DecisionOutcome.ACCEPT,
        decided_by=OTHER,
        context_id=U,
        target_ids=(OTHER,),
        policy_ids=(),
        evidence_ids=(),
        reasons=("test",),
        alternatives=(),
        decided_at=datetime.now(UTC),
    )
    with pytest.raises(AuthorizationDenied):
        require_human_decision_authority(principal, decision)


def test_authenticated_human_can_author_own_decision_when_delegated():
    principal = Principal(
        principal_id=U,
        workspace_id=U,
        agent_id=U,
        agent_kind=AgentKind.HUMAN,
        delegated_actions=frozenset({"knowledge.decide"}),
    )
    decision = Decision(
        id=OTHER,
        workspace_id=U,
        decision_type="canon.resolve",
        outcome=DecisionOutcome.ACCEPT,
        decided_by=U,
        context_id=U,
        target_ids=(OTHER,),
        policy_ids=(),
        evidence_ids=(),
        reasons=("test",),
        alternatives=(),
        decided_at=datetime.now(UTC),
    )
    require_human_decision_authority(principal, decision)


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
        recorded_at=datetime.now(UTC),
    )
    with pytest.raises(InvariantViolation):
        validate_assertion(assertion)


@given(
    delegated=st.booleans(),
    actor_id=st.uuids(),
    workspace_id=st.uuids(),
)
def test_property_ai_never_gets_human_decision_authority(
    delegated: bool,
    actor_id: UUID,
    workspace_id: UUID,
):
    delegated_actions = frozenset({"knowledge.decide"}) if delegated else frozenset()
    principal = Principal(
        principal_id=actor_id,
        workspace_id=workspace_id,
        agent_id=actor_id,
        agent_kind=AgentKind.AI,
        delegated_actions=delegated_actions,
    )
    with pytest.raises(AuthorizationDenied):
        require_human_authority(principal, "knowledge.decide")


@given(
    actor_id=st.uuids(),
    claimed_decider=st.uuids(),
)
def test_property_human_decision_attribution_must_match_authenticated_actor(
    actor_id: UUID,
    claimed_decider: UUID,
):
    principal = Principal(
        principal_id=actor_id,
        workspace_id=U,
        agent_id=actor_id,
        agent_kind=AgentKind.HUMAN,
        delegated_actions=frozenset({"knowledge.decide"}),
    )
    decision = Decision(
        id=OTHER,
        workspace_id=U,
        decision_type="canon.resolve",
        outcome=DecisionOutcome.ACCEPT,
        decided_by=claimed_decider,
        context_id=U,
        target_ids=(OTHER,),
        policy_ids=(),
        evidence_ids=(),
        reasons=("property-test",),
        alternatives=(),
        decided_at=datetime.now(UTC),
    )

    if claimed_decider == actor_id:
        require_human_decision_authority(principal, decision)
    else:
        with pytest.raises(AuthorizationDenied):
            require_human_decision_authority(principal, decision)
