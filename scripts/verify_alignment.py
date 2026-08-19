from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "governance" / "alignment-manifest.yaml",
    ROOT / "governance" / "latent-assurance-matrix.yaml",
    ROOT / "governance" / "security-assurance-matrix.yaml",
    ROOT / "governance" / "growth-marketing-matrix.yaml",
    ROOT / "docs" / "CURRENT_STATE.md",
    ROOT / "docs" / "ALIGNMENT_PROTOCOL.md",
    ROOT / "docs" / "ERROR_CORRECTION_PROTOCOL.md",
    ROOT / "docs" / "DEVELOPMENT_TIME_VERIFICATION.md",
    ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md",
    ROOT / "docs" / "SECURE_DEVELOPMENT_PROTOCOL.md",
    ROOT / "docs" / "THREAT_MODEL_TEMPLATE.md",
    ROOT / "docs" / "GROWTH_MARKETING_FRAMEWORK.md",
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


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(name: str, content: str, phrases: list[str], failures: list[str]) -> None:
    for phrase in phrases:
        if phrase not in content:
            failures.append(f"{name} missing required rule/control: {phrase}")


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            failures.append(f"missing required alignment file: {path.relative_to(ROOT)}")

    if failures:
        for message in failures:
            print(f"ALIGNMENT FAIL: {message}")
        return 1

    agents = read(ROOT / "AGENTS.md")
    manifest = read(ROOT / "governance" / "alignment-manifest.yaml")
    latent_matrix = read(ROOT / "governance" / "latent-assurance-matrix.yaml")
    security_matrix = read(ROOT / "governance" / "security-assurance-matrix.yaml")
    growth_matrix = read(ROOT / "governance" / "growth-marketing-matrix.yaml")
    current = read(ROOT / "docs" / "CURRENT_STATE.md")
    alignment_protocol = read(ROOT / "docs" / "ALIGNMENT_PROTOCOL.md")
    error_protocol = read(ROOT / "docs" / "ERROR_CORRECTION_PROTOCOL.md")
    development_protocol = read(ROOT / "docs" / "DEVELOPMENT_TIME_VERIFICATION.md")
    latent_protocol = read(ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md")
    security_protocol = read(ROOT / "docs" / "SECURE_DEVELOPMENT_PROTOCOL.md")
    threat_template = read(ROOT / "docs" / "THREAT_MODEL_TEMPLATE.md")
    growth_framework = read(ROOT / "docs" / "GROWTH_MARKETING_FRAMEWORK.md")
    status = read(ROOT / "docs" / "ENGINEERING_STATUS.md")
    protection = read(ROOT / "docs" / "REPOSITORY_PROTECTION.md")
    entry_decision = read(ROOT / "docs" / "decisions" / "DEC-0004-entry-routing-and-flow-layers.md")

    for name, content in (
        ("AGENTS.md", agents),
        ("docs/CURRENT_STATE.md", current),
        ("governance/alignment-manifest.yaml", manifest),
    ):
        if CANONICAL_JOURNEY not in content:
            failures.append(f"{name} does not contain canonical creative workflow: {CANONICAL_JOURNEY}")

    for phrase in (NORMAL_ENTRY, IMPORT_ENTRY):
        for name, content in (
            ("docs/CURRENT_STATE.md", current),
            ("AGENTS.md", agents),
            ("DEC-0004", entry_decision),
            ("alignment manifest", manifest),
        ):
            if phrase not in content:
                failures.append(f"{name} missing required entry route: {phrase}")

    for name, content in (("docs/CURRENT_STATE.md", current), ("DEC-0004", entry_decision), ("alignment manifest", manifest)):
        if PRODUCTION_LOOP not in content:
            failures.append(f"{name} missing canonical Production/Studio deep-edit loop")

    require(
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

    require(
        "AGENTS.md",
        agents,
        [
            "Alignment is a repository and evidence property, not a memory property.",
            "ChatGPT acts as alignment steward",
            "Codex is an implementation agent",
            "docs/DEVELOPMENT_TIME_VERIFICATION.md",
            "docs/LATENT_DEFECT_ASSURANCE.md",
            "docs/SECURE_DEVELOPMENT_PROTOCOL.md",
            "docs/GROWTH_MARKETING_FRAMEWORK.md",
            "governance/growth-marketing-matrix.yaml",
            "Product truth before promotion. Evidence before claims. Creator value before growth metrics.",
            "Missing marketing telemetry is `UNKNOWN`, not zero",
            "Registration is not equivalent to activation",
            "keep paid acquisition blocked until activation, retention, conversion, attribution, and unit economics are credible enough to evaluate",
            "do not create a duplicate \"Marketing Brain\"",
            "ChatGPT must not declare a defect fixed solely because Codex says so.",
            "UNDERSTAND -> BASELINE -> SMALL CHANGE -> FAST CHECK -> TARGETED TEST -> NEGATIVE TEST -> DIFF REVIEW -> REPEAT -> CI",
            "The legacy prototype navigation `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded",
        ],
        failures,
    )

    require(
        "docs/ALIGNMENT_PROTOCOL.md",
        alignment_protocol,
        [
            "Fresh-context reconstruction test",
            "three distinct flow layers",
            "Agent Alignment Layer",
            "It is not a replacement for, redesign of, or duplicate implementation of the Nexkosmo Brain.",
        ],
        failures,
    )

    require(
        "docs/ERROR_CORRECTION_PROTOCOL.md",
        error_protocol,
        [
            "Agent Error Correction Layer",
            "It is deliberately separate from the Nexkosmo Brain.",
            "A bug is not fixed because an error message disappeared.",
            "regression test",
            "Runtime verification: UNKNOWN",
        ],
        failures,
    )

    require(
        "docs/DEVELOPMENT_TIME_VERIFICATION.md",
        development_protocol,
        [
            "Development-Time Verification Protocol",
            "while writing Nexkosmo",
            "separate from the Nexkosmo Brain",
            "**FAST CHECKS**",
            "**TARGETED TEST**",
            "**NEGATIVE TEST**",
            "CI is a second independent verifier",
        ],
        failures,
    )

    require(
        "docs/LATENT_DEFECT_ASSURANCE.md",
        latent_protocol,
        [
            "Latent Defect Assurance Protocol",
            "Property-based testing",
            "Mutation testing",
            "State-machine and sequence testing",
            "Concurrency and race testing",
            "Deterministic replay",
            "Fault injection",
            "A previously unknown defect should surprise us at most once.",
        ],
        failures,
    )

    require(
        "docs/SECURE_DEVELOPMENT_PROTOCOL.md",
        security_protocol,
        [
            "Secure Development Protocol",
            "Security is a build-time responsibility.",
            "Every new trust boundary must have an explicit security contract before or alongside implementation.",
            "Network location alone is not authentication.",
            "## Threat modelling trigger",
            "## Abuse and negative testing",
            "## Brain separation",
        ],
        failures,
    )

    require(
        "docs/THREAT_MODEL_TEMPLATE.md",
        threat_template,
        ["# Nexkosmo Threat Model", "## Assets at risk", "## Trust boundaries", "## Attacker-controlled inputs", "## Security invariants", "## Residual risk / unknowns"],
        failures,
    )

    require(
        "docs/GROWTH_MARKETING_FRAMEWORK.md",
        growth_framework,
        [
            "# Nexkosmo Growth & Marketing Framework",
            "Product truth before promotion. Evidence before claims. Creator value before growth metrics.",
            "Creative Production Operating System",
            "Human Director <-> Nexkosmo AI Producer",
            "Registration is not success.",
            "The exact activation event is currently `UNKNOWN`",
            "Missing metrics are `UNKNOWN`, not zero.",
            "## Experiment protocol",
            "## Growth guardrails",
            "## Claims assurance",
            "## Launch stages",
            "Avoid material paid acquisition.",
            "do not create a parallel \"Marketing Brain\"",
        ],
        failures,
    )

    require(
        "governance/alignment-manifest.yaml",
        manifest,
        [
            "manifest_version: 8",
            "- ChatGPT",
            "- Codex",
            "growth_marketing_framework_separate_from_brain: true",
            "growth_marketing_framework: docs/GROWTH_MARKETING_FRAMEWORK.md",
            "growth_marketing_matrix: governance/growth-marketing-matrix.yaml",
            "require_growth_framework_for_material_marketing_or_growth_work: true",
            "critical_unknowns_block: true",
            "- material_public_claims",
            "every_material_trust_boundary_requires_security_contract: true",
            "security_unknowns_fail_closed: true",
            "activation_metric: UNKNOWN_PENDING_USER_EVIDENCE",
            "paid_acquisition: BLOCKED_UNTIL_ECONOMICS_AND_RETENTION_EVIDENCED",
            "claims_assurance: REQUIRED",
            "dark_patterns: PROHIBITED",
            "missing_marketing_telemetry_is_unknown_not_zero: true",
            "director_controls_brand_launch_material_spend_and_consequential_public_claims: true",
        ],
        failures,
    )

    require(
        "governance/latent-assurance-matrix.yaml",
        latent_matrix,
        ["property_based_testing:", "targeted_mutation_testing:", "concurrency_testing:", "fault_injection:", "deterministic_replay:", "A harness is not equivalent to a connected runtime control."],
        failures,
    )

    require(
        "governance/security-assurance-matrix.yaml",
        security_matrix,
        ["current_tree_secret_scan:", "dependency_vulnerability_scan:", "python_static_security_scan:", "authentication:", "human_authority_boundary:", "server_1_server_2_security:", "Critical security UNKNOWN blocks consequential progression."],
        failures,
    )

    require(
        "governance/growth-marketing-matrix.yaml",
        growth_matrix,
        [
            "positioning_foundation:",
            "audience_segmentation:",
            "activation_metric:",
            "UNKNOWN_PENDING_USER_EVIDENCE",
            "funnel_measurement:",
            "analytics_event_contracts:",
            "creator_research:",
            "share_referral_loop:",
            "paid_acquisition:",
            "BLOCKED_UNTIL_ECONOMICS_AND_RETENTION_EVIDENCED",
            "claims_assurance:",
            "experiment_protocol:",
            "dark_pattern_prohibition:",
            "marketing_brain:",
            "Product truth before promotion. Evidence before claims. Creator value before growth metrics.",
            "Missing marketing telemetry is UNKNOWN, not zero.",
        ],
        failures,
    )

    require(
        "docs/ENGINEERING_STATUS.md",
        status,
        [
            "**Alignment:** `<🟢 PASS|🟠 WARN|🔴 FAIL|⚪ UNKNOWN>`",
            "**Runtime:** `<🟢 MATCH|🔴 DRIFT|⚪ UNKNOWN>`",
            "**Context:** `<used>/<max> tokens | <percent> <icon/state> | <remaining> remaining`",
            "**Estimate Costings (AUD):** `<amount/source|⚪ UNKNOWN>`",
            "**Project Estimate (AUD):** `<range | horizon | confidence|⚪ UNKNOWN>`",
            "display **Context: ⚪ UNKNOWN**",
        ],
        failures,
    )

    require(
        "docs/REPOSITORY_PROTECTION.md",
        protection,
        ["Target branch: `main`", "Require a pull request before merging.", "Require the `quality-and-integration` status check to pass before merging.", "Block force pushes.", "Block deletion of `main`."],
        failures,
    )

    navigation = ROOT / "frontend" / "src" / "features" / "studio" / "config" / "navigation.ts"
    if navigation.exists():
        nav_text = read(navigation)
        legacy_stage_block = ['label: "PRE-PRODUCTION"', 'label: "SET"', 'label: "STUDIO"', 'label: "REVIEW"', 'label: "RENDER"']
        if all(item in nav_text for item in legacy_stage_block):
            failures.append(f"legacy {LEGACY_FLOW} workflow is still encoded in frontend navigation")
        if 'characterId = "christopher"' in nav_text:
            failures.append("frontend navigation still hard-codes Christopher as the default project character")

    character_page = ROOT / "frontend" / "src" / "features" / "studio" / "pre-production" / "pages" / "CharacterIdentityPage.tsx"
    if character_page.exists():
        page_text = read(character_page)
        for pattern in ('useState("christopher")', "useState(35)", "useState(180)"):
            if pattern in page_text:
                failures.append(f"prototype project-state hard coding detected in CharacterIdentityPage.tsx: {pattern}")

    if failures:
        for message in failures:
            print(f"ALIGNMENT FAIL: {message}")
        return 1

    print("Alignment verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
