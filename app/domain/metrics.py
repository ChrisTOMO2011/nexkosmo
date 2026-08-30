from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from statistics import fmean
from uuid import UUID


class TaskResolution(StrEnum):
    COMPLETED = "completed"
    JUSTIFIED_STOP = "justified_stop"
    HANDED_OFF = "handed_off"


class MetricName(StrEnum):
    COST_PER_VALIDATED_OUTCOME = "cost_per_validated_outcome"
    HANDOFF_RATE = "handoff_rate"
    PREMATURE_HANDOFF_RATE = "premature_handoff_rate"
    REWORK_RATE = "rework_rate"
    HUMAN_INTERVENTION_RATE = "human_intervention_rate"
    VALIDATED_OUTCOME_RATE = "validated_outcome_rate"


class DriftDirection(StrEnum):
    INCREASE = "increase"
    DECREASE = "decrease"


@dataclass(frozen=True, slots=True)
class TaskObservation:
    task_id: UUID
    agent_id: UUID
    task_class: str
    resolution: TaskResolution
    validated_outcome: bool
    cost_units: float
    handoff_count: int = 0
    premature_handoff_count: int = 0
    rework_count: int = 0
    human_intervention_count: int = 0

    def __post_init__(self) -> None:
        if not self.task_class.strip():
            raise ValueError("task_class must not be empty")
        if self.cost_units < 0:
            raise ValueError("cost_units must be non-negative")
        for field_name in (
            "handoff_count",
            "premature_handoff_count",
            "rework_count",
            "human_intervention_count",
        ):
            if getattr(self, field_name) < 0:
                raise ValueError(f"{field_name} must be non-negative")
        if self.premature_handoff_count > self.handoff_count:
            raise ValueError("premature_handoff_count cannot exceed handoff_count")


@dataclass(frozen=True, slots=True)
class MetricSnapshot:
    sample_size: int
    values: dict[MetricName, float]


@dataclass(frozen=True, slots=True)
class DriftRule:
    metric: MetricName
    direction: DriftDirection
    relative_change: float
    minimum_absolute_change: float = 0.0
    minimum_baseline: float = 0.0

    def __post_init__(self) -> None:
        if self.relative_change < 0:
            raise ValueError("relative_change must be non-negative")
        if self.minimum_absolute_change < 0:
            raise ValueError("minimum_absolute_change must be non-negative")
        if self.minimum_baseline < 0:
            raise ValueError("minimum_baseline must be non-negative")


@dataclass(frozen=True, slots=True)
class DriftFinding:
    metric: MetricName
    baseline_value: float
    current_value: float
    absolute_change: float
    relative_change: float | None
    direction: DriftDirection
    sample_size: int


DEFAULT_DRIFT_RULES = (
    DriftRule(MetricName.COST_PER_VALIDATED_OUTCOME, DriftDirection.INCREASE, 0.5),
    DriftRule(MetricName.HANDOFF_RATE, DriftDirection.INCREASE, 0.5, 0.10),
    DriftRule(MetricName.PREMATURE_HANDOFF_RATE, DriftDirection.INCREASE, 0.5, 0.05),
    DriftRule(MetricName.REWORK_RATE, DriftDirection.INCREASE, 0.5, 0.10),
    DriftRule(MetricName.HUMAN_INTERVENTION_RATE, DriftDirection.INCREASE, 0.5, 0.10),
    DriftRule(MetricName.VALIDATED_OUTCOME_RATE, DriftDirection.DECREASE, 0.25, 0.10),
)


def build_snapshot(observations: tuple[TaskObservation, ...]) -> MetricSnapshot:
    if not observations:
        raise ValueError("at least one observation is required")

    total = len(observations)
    validated = sum(1 for item in observations if item.validated_outcome)
    handed_off = sum(1 for item in observations if item.resolution is TaskResolution.HANDED_OFF)
    premature = sum(1 for item in observations if item.premature_handoff_count > 0)
    reworked = sum(1 for item in observations if item.rework_count > 0)
    human_intervened = sum(1 for item in observations if item.human_intervention_count > 0)

    validated_costs = [item.cost_units for item in observations if item.validated_outcome]
    cost_per_validated = fmean(validated_costs) if validated_costs else 0.0

    return MetricSnapshot(
        sample_size=total,
        values={
            MetricName.COST_PER_VALIDATED_OUTCOME: cost_per_validated,
            MetricName.HANDOFF_RATE: handed_off / total,
            MetricName.PREMATURE_HANDOFF_RATE: premature / total,
            MetricName.REWORK_RATE: reworked / total,
            MetricName.HUMAN_INTERVENTION_RATE: human_intervened / total,
            MetricName.VALIDATED_OUTCOME_RATE: validated / total,
        },
    )


def detect_drift(
    baseline: MetricSnapshot,
    current: MetricSnapshot,
    *,
    rules: tuple[DriftRule, ...] = DEFAULT_DRIFT_RULES,
) -> tuple[DriftFinding, ...]:
    findings: list[DriftFinding] = []

    for rule in rules:
        baseline_value = baseline.values[rule.metric]
        current_value = current.values[rule.metric]
        delta = current_value - baseline_value
        if rule.direction is DriftDirection.DECREASE:
            directional_delta = -delta
        else:
            directional_delta = delta

        if directional_delta <= 0:
            continue
        if abs(delta) < rule.minimum_absolute_change:
            continue
        if baseline_value < rule.minimum_baseline:
            continue

        if baseline_value == 0:
            relative = None
            qualifies = rule.relative_change == 0 and abs(delta) >= rule.minimum_absolute_change
        else:
            relative = abs(delta) / baseline_value
            qualifies = relative >= rule.relative_change

        if not qualifies:
            continue

        findings.append(
            DriftFinding(
                metric=rule.metric,
                baseline_value=baseline_value,
                current_value=current_value,
                absolute_change=delta,
                relative_change=relative,
                direction=rule.direction,
                sample_size=current.sample_size,
            )
        )

    return tuple(findings)
