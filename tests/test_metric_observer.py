from uuid import UUID

import pytest

from app.application.metric_observer import MetricObserver
from app.domain.metrics import MetricName, TaskObservation, TaskResolution

AGENT = UUID("20000000-0000-0000-0000-000000000001")


def observation(
    number: int,
    *,
    resolution: TaskResolution = TaskResolution.COMPLETED,
    validated: bool = True,
    cost: float = 1.0,
    handoffs: int = 0,
    premature_handoffs: int = 0,
    rework: int = 0,
    human_intervention: int = 0,
    task_class: str = "code_change",
) -> TaskObservation:
    return TaskObservation(
        task_id=UUID(f"20000000-0000-0000-0000-{number:012d}"),
        agent_id=AGENT,
        task_class=task_class,
        resolution=resolution,
        validated_outcome=validated,
        cost_units=cost,
        handoff_count=handoffs,
        premature_handoff_count=premature_handoffs,
        rework_count=rework,
        human_intervention_count=human_intervention,
    )


def test_observer_detects_cost_and_handoff_drift() -> None:
    baseline = tuple(observation(index, cost=1.0) for index in range(1, 11))
    current = tuple(
        observation(
            index,
            cost=2.0,
            resolution=(
                TaskResolution.HANDED_OFF if index <= 15 else TaskResolution.COMPLETED
            ),
            handoffs=1 if index <= 15 else 0,
        )
        for index in range(11, 21)
    )

    report = MetricObserver().compare(baseline=baseline, current=current)
    findings = {finding.metric: finding for finding in report.drift_findings}

    assert report.drift_detected is True
    assert MetricName.COST_PER_VALIDATED_OUTCOME in findings
    assert MetricName.HANDOFF_RATE in findings
    assert findings[MetricName.HANDOFF_RATE].baseline_value == 0.0
    assert findings[MetricName.HANDOFF_RATE].current_value == 0.5
    assert findings[MetricName.HANDOFF_RATE].relative_change is None


def test_observer_detects_drift_from_zero_premature_handoff_baseline() -> None:
    baseline = tuple(observation(index) for index in range(1, 11))
    current = tuple(
        observation(
            index,
            resolution=(
                TaskResolution.HANDED_OFF if index <= 13 else TaskResolution.COMPLETED
            ),
            handoffs=1 if index <= 13 else 0,
            premature_handoffs=1 if index <= 13 else 0,
        )
        for index in range(11, 21)
    )

    report = MetricObserver().compare(baseline=baseline, current=current)
    findings = {finding.metric: finding for finding in report.drift_findings}

    assert MetricName.PREMATURE_HANDOFF_RATE in findings
    assert findings[MetricName.PREMATURE_HANDOFF_RATE].relative_change is None


def test_observer_detects_validated_outcome_degradation() -> None:
    baseline = tuple(observation(index) for index in range(1, 11))
    current = tuple(
        observation(index, validated=index <= 15) for index in range(11, 21)
    )

    report = MetricObserver().compare(baseline=baseline, current=current)
    metrics = {finding.metric for finding in report.drift_findings}

    assert MetricName.VALIDATED_OUTCOME_RATE in metrics


def test_observer_requires_comparable_task_classes() -> None:
    baseline = (observation(1, task_class="code_change"),)
    current = (observation(2, task_class="render"),)

    with pytest.raises(ValueError, match="comparable task_class"):
        MetricObserver().compare(baseline=baseline, current=current)


def test_observation_rejects_impossible_premature_handoff_count() -> None:
    with pytest.raises(ValueError, match="cannot exceed"):
        observation(1, handoffs=0, premature_handoffs=1)


def test_no_drift_when_current_performance_is_stable() -> None:
    baseline = tuple(observation(index, cost=1.0) for index in range(1, 11))
    current = tuple(observation(index, cost=1.0) for index in range(11, 21))

    report = MetricObserver().compare(baseline=baseline, current=current)

    assert report.drift_detected is False
    assert report.drift_findings == ()
