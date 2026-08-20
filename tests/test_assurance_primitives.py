from app.assurance.anomaly import (
    AnomalyObservation,
    AnomalyRule,
    Comparison,
    is_anomalous,
)
from app.assurance.release import (
    CanaryEvidence,
    ReleaseIdentity,
    evaluate_canary,
)
from app.assurance.replay import ReplayEnvelope, replay


def test_replay_is_deterministic_for_same_envelope():
    envelope = ReplayEnvelope(
        schema_version=1,
        code_ref="commit-a",
        config_ref="config-a",
        events=(
            {"type": "add", "value": 2},
            {"type": "add", "value": 3},
        ),
    )

    def reducer(state: int, event: dict[str, object]) -> int:
        assert event["type"] == "add"
        return state + int(event["value"])

    first = replay(envelope, initial_state=0, reducer=reducer)
    second = replay(envelope, initial_state=0, reducer=reducer)
    assert first == second
    assert first.final_state == 5


def test_replay_digest_changes_when_order_changes():
    left = ReplayEnvelope(
        1,
        "commit-a",
        "config-a",
        ({"type": "a"}, {"type": "b"}),
    )
    right = ReplayEnvelope(
        1,
        "commit-a",
        "config-a",
        ({"type": "b"}, {"type": "a"}),
    )
    assert left.digest() != right.digest()


def test_anomaly_rule_requires_explicit_threshold_and_sample_floor():
    rule = AnomalyRule(
        metric="duplicate_job_rate",
        threshold=0.01,
        comparison=Comparison.ABOVE,
        minimum_samples=100,
    )
    assert not is_anomalous(
        rule,
        AnomalyObservation("duplicate_job_rate", 0.50, 10),
    )
    assert is_anomalous(
        rule,
        AnomalyObservation("duplicate_job_rate", 0.02, 100),
    )


def test_canary_blocks_on_invariant_failure_and_requests_rollback_when_available():
    candidate = ReleaseIdentity("new", "cfg-2", "mig-2")
    known_good = ReleaseIdentity("old", "cfg-1", "mig-1")
    decision = evaluate_canary(
        candidate=candidate,
        known_good=known_good,
        evidence=CanaryEvidence(
            invariant_failures=1,
            error_rate=0.0,
            error_rate_limit=0.01,
            minimum_observations_met=True,
        ),
    )
    assert not decision.advance
    assert decision.rollback


def test_canary_will_not_advance_without_enough_observations():
    candidate = ReleaseIdentity("new", "cfg-2", "mig-2")
    decision = evaluate_canary(
        candidate=candidate,
        known_good=None,
        evidence=CanaryEvidence(
            invariant_failures=0,
            error_rate=0.0,
            error_rate_limit=0.01,
            minimum_observations_met=False,
        ),
    )
    assert not decision.advance
    assert not decision.rollback
