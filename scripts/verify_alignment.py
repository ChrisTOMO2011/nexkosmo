from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "governance" / "alignment-manifest.yaml",
    ROOT / "governance" / "latent-assurance-matrix.yaml",
    ROOT / "docs" / "CURRENT_STATE.md",
    ROOT / "docs" / "ALIGNMENT_PROTOCOL.md",
    ROOT / "docs" / "ERROR_CORRECTION_PROTOCOL.md",
    ROOT / "docs" / "DEVELOPMENT_TIME_VERIFICATION.md",
    ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md",
    ROOT / "docs" / "ENGINEERING_STATUS.md",
    ROOT / "docs" / "REPOSITORY_PROTECTION.md",
    ROOT / "docs" / "decisions" / "DEC-0001-product-journey.md",
    ROOT / "docs" / "decisions" / "DEC-0002-production-studio-boundary.md",
    ROOT / "docs" / "decisions" / "DEC-0003-project-state-and-fixtures.md",
    ROOT / "docs" / "decisions" / "DEC-0004-entry-routing-and-flow-layers.md",
]

CANONICAL_JOURNEY = "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION"
NORMAL_ENTRY = "Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> IDEA"
IMPORT_ENTRY = "Landing -> Register/Login -> Hire/Select AI Producer -> Choose/Create Project -> Import Script -> SHAPE"
PRODUCTION_LOOP = "PRODUCTION -> select scene/shot -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair"
LEGACY_FLOW = "PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER"


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"missing required alignment file: {path.relative_to(ROOT)}", failures)

    if failures:
        for message in failures:
            print(f"ALIGNMENT FAIL: {message}")
        return 1

    agents = read(ROOT / "AGENTS.md")
    manifest = read(ROOT / "governance" / "alignment-manifest.yaml")
    assurance_matrix = read(ROOT / "governance" / "latent-assurance-matrix.yaml")
    current = read(ROOT / "docs" / "CURRENT_STATE.md")
    protocol = read(ROOT / "docs" / "ALIGNMENT_PROTOCOL.md")
    error_protocol = read(ROOT / "docs" / "ERROR_CORRECTION_PROTOCOL.md")
    development_protocol = read(ROOT / "docs" / "DEVELOPMENT_TIME_VERIFICATION.md")
    latent_protocol = read(ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md")
    status = read(ROOT / "docs" / "ENGINEERING_STATUS.md")
    protection = read(ROOT / "docs" / "REPOSITORY_PROTECTION.md")
    entry_decision = read(ROOT / "docs" / "decisions" / "DEC-0004-entry-routing-and-flow-layers.md")

    for name, content in (
        ("AGENTS.md", agents),
        ("docs/CURRENT_STATE.md", current),
        ("governance/alignment-manifest.yaml", manifest),
    ):
        if CANONICAL_JOURNEY not in content:
            fail(f"{name} does not contain canonical creative workflow: {CANONICAL_JOURNEY}", failures)

    for phrase in (NORMAL_ENTRY, IMPORT_ENTRY):
        if phrase not in current:
            fail(f"docs/CURRENT_STATE.md missing required entry route: {phrase}", failures)
        if phrase not in agents:
            fail(f"AGENTS.md missing required entry route: {phrase}", failures)
        if phrase not in entry_decision:
            fail(f"DEC-0004 missing required entry route: {phrase}", failures)
        if phrase not in manifest:
            fail(f"alignment manifest missing required entry route: {phrase}", failures)

    if PRODUCTION_LOOP not in current:
        fail("docs/CURRENT_STATE.md missing canonical Production/Studio deep-edit loop", failures)
    if PRODUCTION_LOOP not in entry_decision:
        fail("DEC-0004 missing canonical Production/Studio deep-edit loop", failures)
    if PRODUCTION_LOOP not in manifest:
        fail("alignment manifest missing canonical Production/Studio deep-edit loop", failures)

    required_current_phrases = [
        "Studio is not an additional top-level journey stage.",
        "ALIGNMENT STOP GATE.",
        "Conversation alone does not supersede repository canon.",
        "Alignment steward: ChatGPT",
        "The legacy prototype progression `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded as a product-navigation model.",
    ]
    for phrase in required_current_phrases:
        if phrase not in current:
            fail(f"docs/CURRENT_STATE.md missing required rule: {phrase}", failures)

    required_agent_phrases = [
        "governance/alignment-manifest.yaml",
        "governance/latent-assurance-matrix.yaml",
        "docs/CURRENT_STATE.md",
        "docs/ALIGNMENT_PROTOCOL.md",
        "docs/ERROR_CORRECTION_PROTOCOL.md",
        "docs/DEVELOPMENT_TIME_VERIFICATION.md",
        "docs/LATENT_DEFECT_ASSURANCE.md",
        "docs/ENGINEERING_STATUS.md",
        "Alignment is a repository and evidence property, not a memory property.",
        "ChatGPT acts as alignment steward",
        "Codex is an implementation agent",
        "ChatGPT must not declare a defect fixed solely because Codex says so.",
        "Error detection is not reserved for CI, staging, or production.",
        "UNDERSTAND -> BASELINE -> SMALL CHANGE -> FAST CHECK -> TARGETED TEST -> NEGATIVE TEST -> DIFF REVIEW -> REPEAT -> CI",
        "A harness is not runtime proof.",
        "The legacy prototype navigation `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded.",
    ]
    for phrase in required_agent_phrases:
        if phrase not in agents:
            fail(f"AGENTS.md missing alignment/error/development/latent instruction: {phrase}", failures)

    required_protocol_phrases = [
        "Fresh-context reconstruction test",
        "three distinct flow layers",
        "Agent Alignment Layer",
        "It is not a replacement for, redesign of, or duplicate implementation of the Nexkosmo Brain.",
        "The drift controls in this protocol primarily protect ChatGPT and Codex from engineering-agent drift.",
    ]
    for phrase in required_protocol_phrases:
        if phrase not in protocol:
            fail(f"alignment protocol missing required scope/rule: {phrase}", failures)

    required_error_protocol_phrases = [
        "Agent Error Correction Layer",
        "It is deliberately separate from the Nexkosmo Brain.",
        "A bug is not fixed because an error message disappeared.",
        "Codex must not",
        "ChatGPT must not",
        "Brain does not replace the independent engineering correction path.",
        "regression test",
        "Runtime verification: UNKNOWN",
    ]
    for phrase in required_error_protocol_phrases:
        if phrase not in error_protocol:
            fail(f"error correction protocol missing required boundary/rule: {phrase}", failures)

    required_development_phrases = [
        "Development-Time Verification Protocol",
        "while writing Nexkosmo",
        "separate from the Nexkosmo Brain",
        "## Required inner loop",
        "**FAST CHECKS**",
        "**TARGETED TEST**",
        "**NEGATIVE TEST**",
        "## Mandatory stop conditions while coding",
        "CI is a second independent verifier",
        "create smaller changes -> detect defects sooner -> understand the cause -> repair before expansion -> preserve regression proof -> let independent CI challenge the result again.",
    ]
    for phrase in required_development_phrases:
        if phrase not in development_protocol:
            fail(f"development-time verification protocol missing required rule: {phrase}", failures)

    required_latent_phrases = [
        "Latent Defect Assurance Protocol",
        "latent defects",
        "Property-based testing",
        "Mutation testing",
        "State-machine and sequence testing",
        "Concurrency and race testing",
        "Deterministic replay",
        "Fault injection",
        "Runtime invariants",
        "Observability and anomaly detection",
        "A previously unknown defect should surprise us at most once.",
        "separate from the Nexkosmo Brain",
    ]
    for phrase in required_latent_phrases:
        if phrase not in latent_protocol:
            fail(f"latent defect assurance protocol missing required rule: {phrase}", failures)

    required_manifest_phrases = [
        "manifest_version: 6",
        "primary_subjects:",
        "- ChatGPT",
        "- Codex",
        "no_duplicate_brain_truth_engine: true",
        "agent_error_correction_separate_from_brain: true",
        "development_time_verification_separate_from_brain: true",
        "latent_defect_assurance_separate_from_brain: true",
        "error_correction_protocol: docs/ERROR_CORRECTION_PROTOCOL.md",
        "development_time_verification: docs/DEVELOPMENT_TIME_VERIFICATION.md",
        "latent_defect_assurance: docs/LATENT_DEFECT_ASSURANCE.md",
        "latent_assurance_matrix: governance/latent-assurance-matrix.yaml",
        "scripts/verify_latent_defect_assurance.py",
        "scripts/verify_authority_model.py",
        "require_development_time_verification_for_implementation_work: true",
        "require_latent_defect_assurance_for_high_risk_invariants: true",
        "critical_unknowns_block: true",
        "disagreement_policy: BLOCK_AND_RECONCILE",
        "deliberate_injection_tests: REQUIRED",
        "source_commit_sha",
        "deployed_commit_sha",
        "regression_proof_required_where_practical: true",
        "runtime_claim_requires_runtime_evidence: true",
        "symptom_only_fix_prohibited: true",
        "small_verified_slices_required: true",
        "fast_checks_during_implementation_required: true",
        "targeted_tests_during_implementation_required: true",
        "unexplained_failure_blocks_expansion: true",
        "ci_is_second_independent_verifier: true",
        "property_based_testing: IMPLEMENTED",
        "targeted_mutation_testing: IMPLEMENTED",
        "fuzz_testing: INITIAL_IMPLEMENTATION",
        "state_machine_concurrency_campaign: INITIAL_IMPLEMENTATION",
        "deterministic_runtime_replay: HARNESS_IMPLEMENTED_NOT_RUNTIME_CONNECTED",
        "server_fault_injection: PARTIAL_DATABASE_PROBE_SERVER_ENV_PENDING",
        "runtime_anomaly_detection: FRAMEWORK_IMPLEMENTED_NOT_WIRED",
        "canary_and_rollback_automation: DECISION_PRIMITIVE_IMPLEMENTED_NOT_WIRED",
        "formal_methods_selected_invariants: BOUNDED_AUTHORITY_MODEL_IMPLEMENTED",
        "never_report_harness_as_runtime_proof: true",
        "discovered_latent_defect_must_gain_durable_detector: true",
    ]
    for phrase in required_manifest_phrases:
        if phrase not in manifest:
            fail(f"alignment manifest missing required drift/error/development/latent guard: {phrase}", failures)

    required_matrix_phrases = [
        "property_based_testing:",
        "generated_input_fuzzing:",
        "targeted_mutation_testing:",
        "bounded_model_checking:",
        "sequence_state_testing:",
        "concurrency_testing:",
        "fault_injection:",
        "deterministic_replay:",
        "anomaly_detection:",
        "canary_and_rollback:",
        "server_1_server_2_fault_campaign:",
        "A harness is not equivalent to a connected runtime control.",
        "Brain may consume validated assurance evidence later but cannot self-certify ChatGPT/Codex engineering correctness.",
    ]
    for phrase in required_matrix_phrases:
        if phrase not in assurance_matrix:
            fail(f"latent assurance matrix missing required control/rule: {phrase}", failures)

    required_status_phrases = [
        "**Alignment:** `<🟢 PASS|🟠 WARN|🔴 FAIL|⚪ UNKNOWN>`",
        "**Runtime:** `<🟢 MATCH|🔴 DRIFT|⚪ UNKNOWN>`",
        "**Context:** `<used>/<max> tokens | <percent> <icon/state> | <remaining> remaining`",
        "**Estimate Costings (AUD):** `<amount/source|⚪ UNKNOWN>`",
        "**Project Estimate (AUD):** `<range | horizon | confidence|⚪ UNKNOWN>`",
        "Unknown must never be silently converted to pass.",
        "Runtime drift",
        "AI/context drift",
        "AUD is the default human-facing currency",
        "display **Context: ⚪ UNKNOWN**",
    ]
    for phrase in required_status_phrases:
        if phrase not in status:
            fail(f"docs/ENGINEERING_STATUS.md missing required visibility rule: {phrase}", failures)

    required_protection_phrases = [
        "Target branch: `main`",
        "Require a pull request before merging.",
        "Require the `quality-and-integration` status check to pass before merging.",
        "Block force pushes.",
        "Block deletion of `main`.",
        "Do not require a numeric approving review or required CODEOWNER review while the only available approver is also the pull-request author.",
    ]
    for phrase in required_protection_phrases:
        if phrase not in protection:
            fail(f"docs/REPOSITORY_PROTECTION.md missing required rule: {phrase}", failures)

    navigation = ROOT / "frontend" / "src" / "features" / "studio" / "config" / "navigation.ts"
    if navigation.exists():
        nav_text = read(navigation)
        legacy_stage_block = [
            'label: "PRE-PRODUCTION"',
            'label: "SET"',
            'label: "STUDIO"',
            'label: "REVIEW"',
            'label: "RENDER"',
        ]
        if all(item in nav_text for item in legacy_stage_block):
            fail(f"legacy {LEGACY_FLOW} workflow is still encoded in frontend navigation", failures)
        if 'characterId = "christopher"' in nav_text:
            fail("frontend navigation still hard-codes Christopher as the default project character", failures)

    character_page = ROOT / "frontend" / "src" / "features" / "studio" / "pre-production" / "pages" / "CharacterIdentityPage.tsx"
    if character_page.exists():
        page_text = read(character_page)
        for pattern in ('useState("christopher")', "useState(35)", "useState(180)"):
            if pattern in page_text:
                fail(f"prototype project-state hard coding detected in CharacterIdentityPage.tsx: {pattern}", failures)

    if failures:
        for message in failures:
            print(f"ALIGNMENT FAIL: {message}")
        return 1

    print("Alignment verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
