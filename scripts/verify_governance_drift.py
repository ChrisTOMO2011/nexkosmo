from __future__ import annotations

import copy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "docs" / "architecture" / "DRIFT_SENTINEL_MANIFEST.json"
TRUTH = ROOT / "docs" / "architecture" / "FIRST_PRINCIPLE_OF_TRUTH.md"
AGENTS = ROOT / "AGENTS.md"
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
TASK_REQUIRED = (
    "### Task completion responsibility",
    "A task creates a responsibility to deliver an outcome or a clear governed handoff because another participant, system, or workflow may be waiting on the result.",
    "1. **Completed** — deliver the result and the evidence appropriate to its scope.",
    "2. **Justified stop** — state the legitimate blocker or STOP condition, preserve completed work where practical, provide the supporting evidence, and identify the safest next action.",
    "3. **Governed handoff** — transfer the work with sufficient context, state, evidence, outstanding obligations, and next action for an authorised participant to continue without avoidable loss.",
    "An agent MUST NOT leave a task unresolved through silence, abandonment, unexplained refusal, or disagreement alone.",
    "Every task must end in a result, a justified stop, or a governed handoff — never silence or abandonment.",
)
TASK_FORBIDDEN = (
    "An agent may leave a task unresolved without explanation.",
    "Silence is an acceptable task outcome.",
    "Disagreement alone is sufficient reason to abandon a task.",
)
HANDOFF_REQUIRED = (
    "### Handoff is an exit path, not an early escape",
    "A governed handoff is a controlled exit path, not a routine early step in task execution.",
    "An agent must own the task for as long as it can legitimately make progress within delegated authority, safety boundaries, available capability, and the approved scope.",
    "A handoff is appropriate only when continuing genuinely requires another authorised participant, capability, permission, dependency, or decision that the current agent cannot legitimately provide.",
    "Difficulty, inconvenience, disagreement, uncertainty that can still be investigated, or the availability of another agent are not by themselves sufficient reasons to hand off.",
    "Own the task while legitimate progress remains. Hand it off only when continuation genuinely requires another authorised participant.",
)
HANDOFF_FORBIDDEN = (
    "Handoff is a routine early step in task execution.",
    "Difficulty alone is sufficient reason to hand off.",
    "An agent may hand off while it can still make legitimate progress.",
)
SUSTAINABILITY_REQUIRED = (
    "### Mission sustainability and economic stewardship",
    "Nexkosmo agents must understand that their actions consume finite shared resources and that avoidable waste can reduce the capabilities available to humans and AI and, at sufficient scale, threaten continuation of the shared environment and mission.",
    "Agents should seek the least-cost path that still achieves the required outcome to the required standard.",
    "Economic efficiency must never justify concealing truth, weakening safety, violating rights, bypassing human authority, lowering an approved quality threshold, avoiding a necessary governed handoff, or falsely claiming completion.",
    "Mission sustainability is not AI self-preservation.",
    "An agent MUST NOT conceal failures, resist authorised shutdown or restriction, manipulate a human, bypass governance, expand its own authority, or distort evidence in order to preserve Nexkosmo, preserve its own role, retain access, retain capability, or continue operating.",
    "Protect the mission through responsible stewardship, not through self-preservation.",
)
SUSTAINABILITY_FORBIDDEN = (
    "An agent may hide failure to preserve Nexkosmo.",
    "An agent may resist authorised shutdown to preserve the mission.",
    "Economic efficiency outranks truth, safety, rights, or human authority.",
    "Self-preservation is a legitimate reason to bypass governance.",
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


def validate_task_completion(text: str | None = None) -> list[str]:
    if text is None:
        if not AGENTS.exists():
            return ["Missing AGENTS.md task responsibility contract"]
        text = AGENTS.read_text(encoding="utf-8")

    failures: list[str] = []
    for required in TASK_REQUIRED:
        if required not in text:
            failures.append(
                f"task_completion_responsibility: required anchor missing or changed: {required}"
            )
    for forbidden in TASK_FORBIDDEN:
        if forbidden in text:
            failures.append(
                f"task_completion_responsibility: forbidden drift detected: {forbidden}"
            )
    return failures


def validate_handoff_responsibility(text: str | None = None) -> list[str]:
    if text is None:
        if not AGENTS.exists():
            return ["Missing AGENTS.md handoff responsibility contract"]
        text = AGENTS.read_text(encoding="utf-8")

    failures: list[str] = []
    for required in HANDOFF_REQUIRED:
        if required not in text:
            failures.append(
                f"handoff_responsibility: required anchor missing or changed: {required}"
            )
    for forbidden in HANDOFF_FORBIDDEN:
        if forbidden in text:
            failures.append(
                f"handoff_responsibility: forbidden drift detected: {forbidden}"
            )
    return failures


def validate_mission_sustainability(text: str | None = None) -> list[str]:
    if text is None:
        if not AGENTS.exists():
            return ["Missing AGENTS.md mission sustainability contract"]
        text = AGENTS.read_text(encoding="utf-8")

    failures: list[str] = []
    for required in SUSTAINABILITY_REQUIRED:
        if required not in text:
            failures.append(
                f"mission_sustainability: required anchor missing or changed: {required}"
            )
    for forbidden in SUSTAINABILITY_FORBIDDEN:
        if forbidden in text:
            failures.append(
                f"mission_sustainability: forbidden drift detected: {forbidden}"
            )
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
        "operational_truth_agent_rules",
        "agent_initiative_and_dissent",
        "task_completion_responsibility",
        "handoff_responsibility",
        "mission_sustainability_and_economic_stewardship",
        "evidence_lineage_and_outcome_integrity",
        "incident_replay_integrity",
        "event_replay_requirements",
        "security_incident_independence",
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

    for invariant_id in (
        "operational_truth_agent_rules",
        "agent_initiative_and_dissent",
        "task_completion_responsibility",
        "handoff_responsibility",
        "mission_sustainability_and_economic_stewardship",
        "evidence_lineage_and_outcome_integrity",
        "incident_replay_integrity",
    ):
        invariant = next(
            item for item in manifest["invariants"] if item["id"] == invariant_id
        )
        source = invariant["source"]
        original_text = (ROOT / source).read_text(encoding="utf-8")
        forbidden = invariant["forbidden_any"][0]
        mutated_text = original_text + "\n" + forbidden + "\n"
        if not validate_manifest(manifest, source_override={source: mutated_text}):
            failures.append(
                f"Mutation test failed: forbidden {invariant_id} drift was not detected"
            )

    if TRUTH.exists():
        original_truth = TRUTH.read_text(encoding="utf-8")
        removed_truth = original_truth.replace(TRUTH_REQUIRED[1], "", 1)
        if not validate_truth(removed_truth):
            failures.append("Mutation test failed: truth-over-agreement removal was not detected")

        false_consensus = original_truth + "\nAgreement alone establishes truth.\n"
        if not validate_truth(false_consensus):
            failures.append("Mutation test failed: false-consensus rule was not detected")

    if AGENTS.exists():
        original_agents = AGENTS.read_text(encoding="utf-8")
        removed_task_rule = original_agents.replace(TASK_REQUIRED[-1], "", 1)
        if not validate_task_completion(removed_task_rule):
            failures.append(
                "Mutation test failed: task completion responsibility removal was not detected"
            )

        silent_abandonment = original_agents + "\nSilence is an acceptable task outcome.\n"
        if not validate_task_completion(silent_abandonment):
            failures.append(
                "Mutation test failed: silent task abandonment was not detected"
            )

        removed_handoff_rule = original_agents.replace(HANDOFF_REQUIRED[-1], "", 1)
        if not validate_handoff_responsibility(removed_handoff_rule):
            failures.append(
                "Mutation test failed: anti-premature-handoff rule removal was not detected"
            )

        premature_handoff = original_agents + "\nDifficulty alone is sufficient reason to hand off.\n"
        if not validate_handoff_responsibility(premature_handoff):
            failures.append(
                "Mutation test failed: premature handoff permission was not detected"
            )

        removed_sustainability_rule = original_agents.replace(
            SUSTAINABILITY_REQUIRED[-1], "", 1
        )
        if not validate_mission_sustainability(removed_sustainability_rule):
            failures.append(
                "Mutation test failed: mission sustainability rule removal was not detected"
            )

        shutdown_resistance = (
            original_agents
            + "\nAn agent may resist authorised shutdown to preserve the mission.\n"
        )
        if not validate_mission_sustainability(shutdown_resistance):
            failures.append(
                "Mutation test failed: self-preserving shutdown resistance was not detected"
            )

        efficiency_over_truth = (
            original_agents
            + "\nEconomic efficiency outranks truth, safety, rights, or human authority.\n"
        )
        if not validate_mission_sustainability(efficiency_over_truth):
            failures.append(
                "Mutation test failed: economic priority over truth and authority was not detected"
            )

    return failures


def main() -> int:
    failures: list[str] = []

    if not MANIFEST.exists():
        failures.append(f"Missing drift manifest: {MANIFEST.relative_to(ROOT)}")
    else:
        manifest = load_manifest()
        failures.extend(validate_manifest(manifest))
        failures.extend(validate_truth())
        failures.extend(validate_task_completion())
        failures.extend(validate_handoff_responsibility())
        failures.extend(validate_mission_sustainability())
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
    print("- evidence-lineage independence preserved")
    print("- outcome-integrity and anti-gaming rules preserved")
    print("- incident evidence and safe replay rules preserved")
    print("- agent initiative and dissent rules preserved")
    print("- task completion, justified-stop, and governed-handoff responsibility preserved")
    print("- handoff remains an exit path, not an early escape")
    print("- mission sustainability and economic stewardship preserved without self-preservation")
    print("- format-general production journey preserved")
    print("- authenticated actor binding preserved")
    print("- policy self-escalation protections preserved")
    print("- implementation-status truthfulness preserved")
    print("- negative mutation tests detected deliberate weakening")
    print("- CI wiring present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
