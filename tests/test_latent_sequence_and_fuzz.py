from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from hypothesis import given, strategies as st

from app.domain.belief import resolve_belief
from app.domain.enums import AssertionObjectKind, DecisionOutcome, EpistemicStatus
from app.domain.errors import InvariantViolation
from app.domain.rules import validate_assertion
from app.domain.types import Assertion, Decision

BASE = UUID("20000000-0000-0000-0000-000000000001")
TARGET = UUID("20000000-0000-0000-0000-000000000002")
ACTOR = UUID("20000000-0000-0000-0000-000000000003")


def make_assertion(
    *,
    object_kind: AssertionObjectKind,
    identity_value: UUID | None,
    literal_value: dict[str, object] | None,
) -> Assertion:
    return Assertion(
        id=TARGET,
        workspace_id=BASE,
        subject_id=BASE,
        predicate="test.property",
        object_kind=object_kind,
        object_identity_id=identity_value,
        object_value=literal_value,
        context_id=BASE,
        asserted_by=ACTOR,
        epistemic_status=EpistemicStatus.PROPOSED,
        valid_from=None,
        valid_to=None,
        recorded_at=datetime.now(UTC),
    )


@given(
    object_kind=st.sampled_from(list(AssertionObjectKind)),
    identity_present=st.booleans(),
    literal_present=st.booleans(),
)
def test_generated_assertion_object_shape_matches_declared_kind(
    object_kind: AssertionObjectKind,
    identity_present: bool,
    literal_present: bool,
) -> None:
    assertion = make_assertion(
        object_kind=object_kind,
        identity_value=BASE if identity_present else None,
        literal_value={"value": "x"} if literal_present else None,
    )
    valid = (
        object_kind is AssertionObjectKind.IDENTITY
        and identity_present
        and not literal_present
    ) or (
        object_kind is AssertionObjectKind.LITERAL
        and literal_present
        and not identity_present
    )

    if valid:
        validate_assertion(assertion)
    else:
        with pytest.raises(InvariantViolation):
            validate_assertion(assertion)


@given(
    outcomes=st.lists(
        st.sampled_from(
            [
                DecisionOutcome.ACCEPT,
                DecisionOutcome.REJECT,
                DecisionOutcome.WITHDRAW,
                DecisionOutcome.ESCALATE,
            ]
        ),
        min_size=1,
        max_size=50,
    )
)
def test_decision_sequence_resolves_to_last_decisive_outcome(
    outcomes: list[DecisionOutcome],
) -> None:
    assertion = make_assertion(
        object_kind=AssertionObjectKind.LITERAL,
        identity_value=None,
        literal_value={"value": "x"},
    )
    start = datetime(2026, 1, 1, tzinfo=UTC)
    decisions = [
        Decision(
            id=UUID(int=index + 1),
            workspace_id=BASE,
            decision_type="canon.resolve",
            outcome=outcome,
            decided_by=ACTOR,
            context_id=BASE,
            target_ids=(TARGET,),
            policy_ids=(),
            evidence_ids=(),
            reasons=(f"step-{index}",),
            alternatives=(),
            decided_at=start + timedelta(seconds=index),
        )
        for index, outcome in enumerate(outcomes)
    ]

    resolution = resolve_belief([assertion], decisions)
    decisive = [
        outcome
        for outcome in outcomes
        if outcome
        in {DecisionOutcome.ACCEPT, DecisionOutcome.REJECT, DecisionOutcome.WITHDRAW}
    ]

    if not decisive:
        assert TARGET in resolution.proposed
        assert TARGET not in resolution.accepted
        assert TARGET not in resolution.rejected
    elif decisive[-1] is DecisionOutcome.ACCEPT:
        assert TARGET in resolution.accepted
        assert TARGET not in resolution.rejected
        assert TARGET not in resolution.proposed
    else:
        assert TARGET in resolution.rejected
        assert TARGET not in resolution.accepted
        assert TARGET not in resolution.proposed
