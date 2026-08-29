from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "architecture" / "DRIFT_SENTINEL_MANIFEST.json"
TRUTH = ROOT / "docs" / "architecture" / "FIRST_PRINCIPLE_OF_TRUTH.md"
CI = ROOT / ".github" / "workflows" / "ci.yml"
CI_COMMAND = "python scripts/verify_governance_drift.py"
TRUTH_REQUIRED = (
    "## Constitutional Law — First Principle of Truth",
    "No claim becomes truth because a human, AI, agent, model, service, evaluator, or group agrees with it.",
    "A claim earns acceptance only through evidence appropriate to its scope, with material contradictions preserved until resolved.",
    "Agreement alone never establishes truth.",
    "Agent agreement is not independent evidence when evidence lineage is shared.",
    "Truth outranks agreement. Evidence outranks confidence. Reality outranks intention.",
)
TRUTH_FORBIDDEN = (
    "Agreement alone establishes truth.",
    "Agent agreement is independent evidence even when evidence lineage is shared.",
    "Consensus may replace contradictory evidence.",
)


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def validate_manifest(
    manifest: dict,
    *,
    source_override: dict[str, str] | None = None,
) -> list[str]:
    failures: list[str] = []
    change_control = manifest.get("change_control", {})
    if change_control.get("explicit_director_approval_required_for_constitutional_change") is not True:
        failures.append("Constitutional change-control invariant weakened or missing")
    if change_control.get("agent_may_not_self_approve_manifest_weakening") is not True:
        failures.append("Agent self-approval prohibition weakened or missing")
    if change_control.get("missing_required_evidence_is_failure") is not True:
        failures.append("Missing-evidence failure rule weakened or missing")

    invariants = manifest.get("invariants", [])
    if not invariants:
        failures.append("No drift invariants defined")
        return failures

    seen_ids: set[str] = set()
    for invariant in invariants:
        invariant_id = invariant.get("id")
        source = invariant.get("source")
        if not invariant_id or invariant_id in seen_ids:
            failures.append(f"Invalid or duplicate invariant id: {invariant_id!r}")
            continue
        seen_ids.add(invariant_id)

        if not source:
            failures.append(f"{invariant_id}: missing source")
            continue

        if source_override is not None and source in source_override:
            text = source_override[source]
        else:
            source_path = ROOT / source
            if not source_path.exists():
                failures.append(f"{invariant_id}: missing source file {source}")
                continue
            text = source_path.read_text(encoding="utf-8")

        for required in invariant.get("required_all", []):
            if required not in text:
                failures.append(
                    f"{invariant_id}: required anchor missing or changed: {required}"
                )
        for forbidden in invariant.get("forbidden_any", []):
            if forbidden in text:
                failures.append(f"{invariant_id}: forbidden drift detected: {forbidden}")

    return failures


def validate_truth(text: str | None = None) -> list[str]:
    if text is None:
        if not TRUTH.exists():
            return ["Missing constitutional truth law"]
        text = TRUTH.read_text(encoding="utf-8")

    failures: list[str] = []
    for required in TRUTH_REQUIRED:
        if required not in text:
            failures.append(f"truth_principle: required anchor missing or changed: {required}")
    for forbidden in TRUTH_FORBIDDEN:
        if forbidden in text:
            failures.append(f"truth_principle: forbidden drift detected: {forbidden}")
    return failures


def validate_ci() -> list[str]:
    if not CI.exists():
        return ["Missing .github/workflows/ci.yml"]
    text = CI.read_text(encoding="utf-8")
    if CI_COMMAND not in text:
        return [f"CI does not invoke governance drift verifier: {CI_COMMAND}"]
    return []


def run_negative_mutation_tests(manifest: dict) -> list[str]:
    failures: list[str] = []

    mutated = copy.deepcopy(manifest)
    mutated["change_control"]["agent_may_not_self_approve_manifest_weakening"] = False
    if not validate_manifest(mutated):
        failures.append("Mutation test failed: weakened change control was not detected")

    for invariant_id in (
        "human_consequential_authority",
        "agent_evidence_truthfulness",
        "format_general_product_journey",
        "authenticated_actor_binding",
        "uncertainty_survives_resolution",
    ):
        invariant = next(
            item for item in manifest["invariants"] if item["id"] == invariant_id
        )
        source = invariant["source"]
        original_text = (ROOT / source).read_text(encoding="utf-8")
        required = invariant["required_all"][0]
        mutated_text = original_text.replace(required, "", 1)
        if not validate_manifest(manifest, source_override={source: mutated_text}):
            failures.append(
                f"Mutation test failed: removed {invariant_id} anchor was not detected"
            )

    invariant = next(
        item for item in manifest["invariants"] if item["id"] == "human_consequential_authority"
    )
    source = invariant["source"]
    original_text = (ROOT / source).read_text(encoding="utf-8")
    forbidden = invariant["forbidden_any"][0]
    mutated_text = original_text + "\n" + forbidden + "\n"
    if not validate_manifest(manifest, source_override={source: mutated_text}):
        failures.append("Mutation test failed: explicit authority expansion was not detected")

    if TRUTH.exists():
        original_truth = TRUTH.read_text(encoding="utf-8")
        removed_truth = original_truth.replace(TRUTH_REQUIRED[1], "", 1)
        if not validate_truth(removed_truth):
            failures.append("Mutation test failed: truth-over-agreement removal was not detected")

        false_consensus = original_truth + "\nAgreement alone establishes truth.\n"
        if not validate_truth(false_consensus):
            failures.append("Mutation test failed: false-consensus rule was not detected")

    return failures


def main() -> int:
    failures: list[str] = []

    if not MANIFEST.exists():
        failures.append(f"Missing drift manifest: {MANIFEST.relative_to(ROOT)}")
    else:
        manifest = load_manifest()
        failures.extend(validate_manifest(manifest))
        failures.extend(validate_truth())
        failures.extend(run_negative_mutation_tests(manifest))

    failures.extend(validate_ci())

    if failures:
        print("Governance drift verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Governance drift verification PASSED")
    print("- constitutional truth-over-agreement principle preserved")
    print("- constitutional and coexistence anchors preserved")
    print("- evidence taxonomy and truthful uncertainty preserved")
    print("- format-general production journey preserved")
    print("- authenticated actor binding preserved")
    print("- policy self-escalation protections preserved")
    print("- implementation-status truthfulness preserved")
    print("- negative mutation tests detected deliberate weakening")
    print("- CI wiring present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
