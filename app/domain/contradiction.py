from collections.abc import Iterable
from dataclasses import dataclass
from uuid import UUID

from app.domain.types import Assertion


@dataclass(frozen=True, slots=True)
class Contradiction:
    left_assertion_id: UUID
    right_assertion_id: UUID
    reason: str


def detect_literal_conflicts(assertions: Iterable[Assertion]) -> tuple[Contradiction, ...]:
    items = list(assertions)
    found: list[Contradiction] = []
    for i, left in enumerate(items):
        for right in items[i + 1 :]:
            same_slot = (
                left.subject_id == right.subject_id
                and left.predicate == right.predicate
                and left.context_id == right.context_id
            )
            different_value = left.object_value != right.object_value
            overlapping = not (
                left.valid_to is not None
                and right.valid_from is not None
                and left.valid_to <= right.valid_from
            ) and not (
                right.valid_to is not None
                and left.valid_from is not None
                and right.valid_to <= left.valid_from
            )
            if same_slot and different_value and overlapping:
                found.append(
                    Contradiction(
                        left_assertion_id=left.id,
                        right_assertion_id=right.id,
                        reason="same subject/predicate/context with incompatible literal values",
                    )
                )
    return tuple(found)
