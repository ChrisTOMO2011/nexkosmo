from datetime import UTC, datetime
from uuid import UUID

import pytest

from app.domain.enums import (
    AgentKind,
    AssertionObjectKind,
    EpistemicStatus,
)
from app.domain.errors import AuthorizationDenied, InvariantViolation
from app.domain.rules import require_human_authority, validate_assertion
from app.domain.types import Assertion, Principal

U = UUID("10000000-0000-0000-0000-000000000001")


def test_ai_cannot_exercise_human_approval_authority() -> None:
    principal = Principal(
        principal_id=U,
        workspace_id=U,
        agent_id=U,
        agent_kind=AgentKind.AI,
        delegated_actions=frozenset({"knowledge.decide"}),
    )
    with pytest.raises(AuthorizationDenied):
        require_human_authority(principal, "knowledge.decide")


def test_assertion_cannot_start_as_accepted() -> None:
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
