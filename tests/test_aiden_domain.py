from datetime import UTC, datetime
from uuid import UUID

from app.domain.belief import resolve_belief
from app.domain.contradiction import detect_literal_conflicts
from app.domain.enums import (
    AssertionObjectKind,
    DecisionOutcome,
    EpistemicStatus,
)
from app.domain.types import Assertion, Decision

W = UUID("00000000-0000-0000-0000-000000000001")
AIDEN = UUID("00000000-0000-0000-0000-000000000010")
MAYA = UUID("00000000-0000-0000-0000-000000000011")
AI = UUID("00000000-0000-0000-0000-000000000012")
DRAFT = UUID("00000000-0000-0000-0000-000000000020")
BLUE = UUID("00000000-0000-0000-0000-000000000101")
GREEN = UUID("00000000-0000-0000-0000-000000000102")
DECISION = UUID("00000000-0000-0000-0000-000000000201")
NOW = datetime(2026, 7, 13, tzinfo=UTC)


def assertion(id_, by, value, status):
    return Assertion(
        id=id_,
        workspace_id=W,
        subject_id=AIDEN,
        predicate="character.eye_colour",
        object_kind=AssertionObjectKind.LITERAL,
        object_identity_id=None,
        object_value={"value": value},
        context_id=DRAFT,
        asserted_by=by,
        epistemic_status=status,
        valid_from=NOW,
        valid_to=None,
        recorded_at=NOW,
    )


def test_aiden_contradiction_is_preserved_and_contained():
    blue = assertion(BLUE, MAYA, "blue", EpistemicStatus.AUTHORED)
    green = assertion(GREEN, AI, "green", EpistemicStatus.PROPOSED)
    conflicts = detect_literal_conflicts([blue, green])
    assert len(conflicts) == 1
    assert {conflicts[0].left_assertion_id, conflicts[0].right_assertion_id} == {
        BLUE,
        GREEN,
    }


def test_human_decision_accepts_blue_and_rejects_green_without_erasure():
    blue = assertion(BLUE, MAYA, "blue", EpistemicStatus.AUTHORED)
    green = assertion(GREEN, AI, "green", EpistemicStatus.PROPOSED)
    decisions = [
        Decision(
            id=DECISION,
            workspace_id=W,
            decision_type="canon.resolve",
            outcome=DecisionOutcome.ACCEPT,
            decided_by=MAYA,
            context_id=DRAFT,
            target_ids=(BLUE,),
            policy_ids=(),
            evidence_ids=(),
            reasons=("Maya is the creator and the approved brief specifies blue.",),
            alternatives=("Accept green", "Escalate"),
            decided_at=NOW,
        ),
        Decision(
            id=UUID("00000000-0000-0000-0000-000000000202"),
            workspace_id=W,
            decision_type="canon.resolve",
            outcome=DecisionOutcome.REJECT,
            decided_by=MAYA,
            context_id=DRAFT,
            target_ids=(GREEN,),
            policy_ids=(),
            evidence_ids=(),
            reasons=("Green was an image-analysis error.",),
            alternatives=("Accept green",),
            decided_at=NOW,
        ),
    ]
    result = resolve_belief([blue, green], decisions)
    assert result.accepted == (BLUE,)
    assert result.rejected == (GREEN,)
    assert GREEN not in result.proposed
    assert "creator" in " ".join(result.explanation).lower()
