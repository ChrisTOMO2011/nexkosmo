from itertools import product
from uuid import UUID

from app.domain.enums import AgentKind, DecisionOutcome
from app.domain.errors import AuthorizationDenied
from app.domain.rules import require_human_decision_authority
from app.domain.types import Decision, Principal

U = UUID("30000000-0000-0000-0000-000000000001")
OTHER = UUID("30000000-0000-0000-0000-000000000002")


def main() -> int:
    failures: list[str] = []
    checked = 0

    for kind, delegated, wildcard, attribution_matches in product(
        list(AgentKind),
        (False, True),
        (False, True),
        (False, True),
    ):
        actions: set[str] = set()
        if delegated:
            actions.add("knowledge.decide")
        if wildcard:
            actions.add("*")

        principal = Principal(
            principal_id=U,
            workspace_id=U,
            agent_id=U,
            agent_kind=kind,
            delegated_actions=frozenset(actions),
        )
        decision = Decision(
            id=OTHER,
            workspace_id=U,
            decision_type="canon.resolve",
            outcome=DecisionOutcome.ACCEPT,
            decided_by=U if attribution_matches else OTHER,
            context_id=U,
            target_ids=(OTHER,),
            policy_ids=(),
            evidence_ids=(),
            reasons=("bounded-model-check",),
            alternatives=(),
            decided_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
        )

        should_allow = (
            kind is AgentKind.HUMAN
            and (delegated or wildcard)
            and attribution_matches
        )
        allowed = True
        try:
            require_human_decision_authority(principal, decision)
        except AuthorizationDenied:
            allowed = False

        checked += 1
        if allowed != should_allow:
            failures.append(
                "authority model mismatch: "
                f"kind={kind.value} delegated={delegated} wildcard={wildcard} "
                f"attribution_matches={attribution_matches} expected={should_allow} got={allowed}"
            )

    if failures:
        for failure in failures:
            print(f"AUTHORITY MODEL FAIL: {failure}")
        return 1

    print(f"AUTHORITY MODEL PASS: exhaustively checked {checked} bounded states")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
