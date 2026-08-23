from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


class Comparison(StrEnum):
    ABOVE = "above"
    BELOW = "below"


@dataclass(frozen=True, slots=True)
class AnomalyRule:
    metric: str
    threshold: float
    comparison: Comparison
    minimum_samples: int = 1


@dataclass(frozen=True, slots=True)
class AnomalyObservation:
    metric: str
    value: float
    sample_count: int


def is_anomalous(rule: AnomalyRule, observation: AnomalyObservation) -> bool:
    if observation.metric != rule.metric:
        return False
    if observation.sample_count < rule.minimum_samples:
        return False
    if rule.comparison is Comparison.ABOVE:
        return observation.value > rule.threshold
    return observation.value < rule.threshold
