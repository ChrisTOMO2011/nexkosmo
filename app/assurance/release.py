from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ReleaseIdentity:
    source_commit: str
    config_identity: str
    migration_identity: str


@dataclass(frozen=True, slots=True)
class CanaryEvidence:
    invariant_failures: int
    error_rate: float
    error_rate_limit: float
    minimum_observations_met: bool


@dataclass(frozen=True, slots=True)
class CanaryDecision:
    advance: bool
    rollback: bool
    reason: str


def evaluate_canary(
    *,
    candidate: ReleaseIdentity,
    known_good: ReleaseIdentity | None,
    evidence: CanaryEvidence,
) -> CanaryDecision:
    if not all(
        (
            candidate.source_commit,
            candidate.config_identity,
            candidate.migration_identity,
        )
    ):
        return CanaryDecision(False, False, "candidate release identity is incomplete")
    if not evidence.minimum_observations_met:
        return CanaryDecision(False, False, "insufficient canary observations")
    if evidence.invariant_failures > 0:
        return CanaryDecision(
            False,
            known_good is not None,
            "canary violated a required invariant",
        )
    if evidence.error_rate > evidence.error_rate_limit:
        return CanaryDecision(
            False,
            known_good is not None,
            "canary exceeded its explicit error-rate limit",
        )
    return CanaryDecision(True, False, "canary evidence satisfies current gates")
