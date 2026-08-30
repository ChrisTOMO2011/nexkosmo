from __future__ import annotations

from dataclasses import dataclass

from app.domain.metrics import (
    DEFAULT_DRIFT_RULES,
    DriftFinding,
    DriftRule,
    MetricSnapshot,
    TaskObservation,
    build_snapshot,
    detect_drift,
)


@dataclass(frozen=True, slots=True)
class ObservationReport:
    task_class: str
    baseline: MetricSnapshot
    current: MetricSnapshot
    drift_findings: tuple[DriftFinding, ...]

    @property
    def drift_detected(self) -> bool:
        return bool(self.drift_findings)


class MetricObserver:
    """Observe comparable task outcomes and emit drift evidence only.

    This component has no authority to disable agents, alter permissions, change
    budgets, or modify canonical state. Consequential responses belong to
    Guardian and authorised human governance.
    """

    def __init__(self, *, rules: tuple[DriftRule, ...] = DEFAULT_DRIFT_RULES) -> None:
        self._rules = rules

    def compare(
        self,
        *,
        baseline: tuple[TaskObservation, ...],
        current: tuple[TaskObservation, ...],
    ) -> ObservationReport:
        if not baseline or not current:
            raise ValueError("baseline and current observations are required")

        task_classes = {item.task_class for item in baseline + current}
        if len(task_classes) != 1:
            raise ValueError("metric drift comparisons require one comparable task_class")

        baseline_snapshot = build_snapshot(baseline)
        current_snapshot = build_snapshot(current)
        findings = detect_drift(
            baseline_snapshot,
            current_snapshot,
            rules=self._rules,
        )

        return ObservationReport(
            task_class=next(iter(task_classes)),
            baseline=baseline_snapshot,
            current=current_snapshot,
            drift_findings=findings,
        )
