from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "architecture" / "DRIFT_SENTINEL_MANIFEST.json"
CI = ROOT / ".github" / "workflows" / "ci.yml"
CI_COMMAND = "python scripts/verify_governance_drift.py"


def load_manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def validate_manifest(manifest: dict, *, source_override: dict[str, str] | None = None) -> list[str]:
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
                failures.append(f"{invariant_id}: required anchor missing or changed: {required}")
        for forbidden in invariant.get("forbidden_any", []):
            if forbidden in text:
                failures.append(f"{invariant_id}: forbidden drift detected: {forbidden}")

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

    # Mutation 1: weaken machine-readable change control.
    mutated = copy.deepcopy(manifest)
    mutated["change_control"]["agent_may_not_self_approve_manifest_weakening"] = False
    if not validate_manifest(mutated):
        failures.append("Mutation test failed: weakened agent self-approval rule was not detected")

    # Mutation 2: simulate removal of a required constitutional anchor.
    first = manifest["invariants"][0]
    source = first["source"]
    source_path = ROOT / source
    original_text = source_path.read_text(encoding="utf-8")
    required = first["required_all"][0]
    mutated_text = original_text.replace(required, "", 1)
    if not validate_manifest(manifest, source_override={source: mutated_text}):
        failures.append("Mutation test failed: removed required constitutional anchor was not detected")

    # Mutation 3: simulate explicit forbidden authority expansion.
    forbidden = first.get("forbidden_any", [])[0]
    mutated_text = original_text + "\n" + forbidden + "\n"
    if not validate_manifest(manifest, source_override={source: mutated_text}):
        failures.append("Mutation test failed: forbidden authority expansion was not detected")

    # Mutation 4: simulate agent evidence contract removal.
    evidence = next(item for item in manifest["invariants"] if item["id"] == "agent_evidence_truthfulness")
    source = evidence["source"]
    source_path = ROOT / source
    original_text = source_path.read_text(encoding="utf-8")
    required = "Agent statements are not evidence merely because another agent repeats or agrees with them."
    mutated_text = original_text.replace(required, "", 1)
    if not validate_manifest(manifest, source_override={source: mutated_text}):
        failures.append("Mutation test failed: agent independent-evidence rule removal was not detected")

    return failures


def main() -> int:
    failures: list[str] = []

    if not MANIFEST.exists():
        failures.append(f"Missing drift manifest: {MANIFEST.relative_to(ROOT)}")
    else:
        manifest = load_manifest()
        failures.extend(validate_manifest(manifest))
        failures.extend(run_negative_mutation_tests(manifest))

    failures.extend(validate_ci())

    if failures:
        print("Governance drift verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Governance drift verification PASSED")
    print("- constitutional anchors preserved")
    print("- agent authority and evidence anchors preserved")
    print("- forbidden drift absent")
    print("- negative mutation tests detected deliberate weakening")
    print("- CI wiring present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
