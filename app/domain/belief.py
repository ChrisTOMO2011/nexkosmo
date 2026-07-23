from collections.abc import Iterable
from uuid import UUID

from app.domain.enums import DecisionOutcome, EpistemicStatus
from app.domain.types import Assertion, BeliefResolution, Decision


def resolve_belief(
    assertions: Iterable[Assertion],
    decisions: Iterable[Decision],
) -> BeliefResolution:
    assertions_by_id = {a.id: a for a in assertions}
    accepted: set[UUID] = set()
    rejected: set[UUID] = set()
    decision_ids: list[UUID] = []
    reasons: list[str] = []

    for decision in sorted(decisions, key=lambda d: d.decided_at):
        decision_ids.append(decision.id)
        reasons.extend(decision.reasons)
        for target_id in decision.target_ids:
            if target_id not in assertions_by_id:
                continue
            if decision.outcome is DecisionOutcome.ACCEPT:
                accepted.add(target_id)
                rejected.discard(target_id)
            elif decision.outcome in {DecisionOutcome.REJECT, DecisionOutcome.WITHDRAW}:
                rejected.add(target_id)
                accepted.discard(target_id)

    proposed = {
        a.id
        for a in assertions_by_id.values()
        if a.id not in accepted
        and a.id not in rejected
        and a.epistemic_status in {EpistemicStatus.PROPOSED, EpistemicStatus.INFERRED}
    }

    return BeliefResolution(
        accepted=tuple(sorted(accepted, key=str)),
        rejected=tuple(sorted(rejected, key=str)),
        proposed=tuple(sorted(proposed, key=str)),
        disputed=(),
        unknown=(),
        decision_ids=tuple(decision_ids),
        explanation=tuple(reasons),
    )
