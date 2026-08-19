from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "governance" / "alignment-manifest.yaml",
    ROOT / "governance" / "latent-assurance-matrix.yaml",
    ROOT / "governance" / "security-assurance-matrix.yaml",
    ROOT / "docs" / "CURRENT_STATE.md",
    ROOT / "docs" / "ALIGNMENT_PROTOCOL.md",
    ROOT / "docs" / "ERROR_CORRECTION_PROTOCOL.md",
    ROOT / "docs" / "DEVELOPMENT_TIME_VERIFICATION.md",
    ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md",
    ROOT / "docs" / "SECURE_DEVELOPMENT_PROTOCOL.md",
    ROOT / "docs" / "THREAT_MODEL_TEMPLATE.md",
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


def require_phrases(name: str, content: str, phrases: list[str], failures: list[str]) -> None:
    for phrase in phrases:
        if phrase not in content:
            fail(f"{name} missing required rule/control: {phrase}", failures)


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
    security_matrix = read(ROOT / "governance" / "security-assurance-matrix.yaml")
    current = read(ROOT / "docs" / "CURRENT_STATE.md")
    protocol = read(ROOT / "docs" / "ALIGNMENT_PROTOCOL.md")
    error_protocol = read(ROOT / "docs" / "ERROR_CORRECTION_PROTOCOL.md")
    development_protocol = read(ROOT / "docs" / "DEVELOPMENT_TIME_VERIFICATION.md")
    latent_protocol = read(ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md")
    security_protocol = read(ROOT / "docs" / "SECURE_DEVELOPMENT_PROTOCOL.md")
    threat_template = read(ROOT / "docs" / "THREAT_MODEL_TEMPLATE.md")
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

    require_phrases(
        "docs/CURRENT_STATE.md",
        current,
        [
            "Studio is not an additional top-level journey stage.",
            "ALIGNMENT STOP GATE.",
            "Conversation alone does not supersede repository canon.",
            "Alignment steward: ChatGPT",
            "The legacy prototype progression `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded as a product-navigation model.",
        ],
        failures,
    )

    require_phrases(
        "AGENTS.md",
        agents,
        [
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
        ],
        failures,
    )

    require_phrases(
        "docs/ALIGNMENT_PROTOCOL.md",
        protocol,
        [
            "Fresh-context reconstruction test",
            "three distinct flow layers",
            "Agent Alignment Layer",
            "It is not a replacement for, redesign of, or duplicate implementation of the Nexkosmo Brain.",
            "The drift controls in this protocol primarily protect ChatGPT and Codex from engineering-agent drift.",
        ],
        failures,
    )

    require_phrases(
        "docs/ERROR_CORRECTION_PROTOCOL.md",
        error_protocol,
        [
            "Agent Error Correction Layer",
            "It is deliberately separate from the Nexkosmo Brain.",
            "A bug is not fixed because an error message disappeared.",
            "Codex must not",
            "ChatGPT must not",
            "Brain does not replace the independent engineering correction path.",
            "regression test",
            "Runtime verification: UNKNOWN",
        ],
        failures,
    )

    require_phrases(
        "docs/DEVELOPMENT_TIME_VERIFICATION.md",
        development_protocol,
        [
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
        ],
        failures,
    )

    require_phrases(
        "docs/LATENT_DEFECT_ASSURANCE.md",
        latent_protocol,
        [
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
        ],
        failures,
    )

    require_phrases(
        "docs/SECURE_DEVELOPMENT_PROTOCOL.md",
        security_protocol,
        [
            "Secure Development Protocol",
            "Security is a build-time responsibility.",
            "Every new trust boundary must have an explicit security contract before or alongside implementation.",
            "security by construction",
            "Network location alone is not authentication.",
            "## Threat modelling trigger",
            "## Abuse and negative testing",
            "## Brain separation",
        ],
        failures,
    )

    require_phrases(
        "docs/THREAT_MODEL_TEMPLATE.md",
        threat_template,
        [
            "# Nexkosmo Threat Model",
            "## Assets at risk",
            "## Trust boundaries",
            "## Attacker-controlled inputs",
            "## Security invariants",
            "## Residual risk / unknowns",
        ],
        failures,
    )

    require_phrases(
        "governance/alignment-manifest.yaml",
        manifest,
        [
            "manifest_version: 7",
            "primary_subjects:",
            "- ChatGPT",
            "- Codex",
            "no_duplicate_brain_truth_engine: true",
            "agent_error_correction_separate_from_brain: true",
            "development_time_verification_separate_from_brain: true",
            "latent_defect_assurance_separate_from_brain: true",
            "secure_development_separate_from_brain: true",
            "secure_development_protocol: docs/SECURE_DEVELOPMENT_PROTOCOL.md",
            "security_assurance_matrix: governance/security-assurance-matrix.yaml",
            "scripts/verify_security_baseline.py",
            "require_secure_development_for_security_relevant_work: true",
            "require_threat_model_for_new_material_trust_boundary: true",
            "critical_unknowns_block: true",
            "disagreement_policy: BLOCK_AND_RECONCILE",
            "property_based_testing: IMPLEMENTED",
            "targeted_mutation_testing: IMPLEMENTED",
            "fuzz_testing: INITIAL_IMPLEMENTATION",
            "never_report_harness_as_runtime_proof: true",
            "every_material_trust_boundary_requires_security_contract: true",
            "threat_model_high_risk_changes: REQUIRED",
            "python_static_security_scan: IMPLEMENTED_IN_CI",
            "dependency_vulnerability_scan: IMPLEMENTED_IN_CI",
            "security_unknowns_fail_closed: true",
            "scanner_findings_cannot_be_broadly_suppressed_for_green_ci: true",
        ],
        failures,
    )

    require_phrases(
        "governance/latent-assurance-matrix.yaml",
        assurance_matrix,
        [
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
        ],
        failures,
    )

    require_phrases(
        "governance/security-assurance-matrix.yaml",
        security_matrix,
        [
            "secure_development_protocol:",
            "current_tree_secret_scan:",
            "dependency_vulnerability_scan:",
            "python_static_security_scan:",
            "dangerous_pattern_guard:",
            "authentication:",
            "human_authority_boundary:",
            "server_1_server_2_security:",
            "Security is a build-time responsibility.",
            "Network location alone is not authentication.",
            "Critical security UNKNOWN blocks consequential progression.",
            "Brain may consume validated security evidence later but cannot self-certify ChatGPT/Codex security correctness.",
        ],
        failures,
    )

    require_phrases(
        "docs/ENGINEERING_STATUS.md",
        status,
        [
            "**Alignment:** `<🟢 PASS|🟠 WARN|🔴 FAIL|⚪ UNKNOWN>`",
            "**Runtime:** `<🟢 MATCH|🔴 DRIFT|⚪ UNKNOWN>`",
            "**Context:** `<used>/<max> tokens | <percent> <icon/state> | <remaining> remaining`",
            "**Estimate Costings (AUD):** `<amount/source|⚪ UNKNOWN>`",
            "**Project Estimate (AUD):** `<range | horizon | confidence|⚪ UNKNOWN>`",
            "Unknown must never be silently converted to pass.",
            "AUD is the default human-facing currency",
            "display **Context: ⚪ UNKNOWN**",
        ],
        failures,
    )

    require_phrases(
        "docs/REPOSITORY_PROTECTION.md",
        protection,
        [
            "Target branch: `main`",
            "Require a pull request before merging.",
            "Require the `quality-and-integration` status check to pass before merging.",
            "Block force pushes.",
            "Block deletion of `main`.",
        ],
        failures,
    )

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
