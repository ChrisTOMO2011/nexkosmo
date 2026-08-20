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
    ROOT / "governance" / "social-automation-matrix.yaml",
    ROOT / "docs" / "CURRENT_STATE.md",
    ROOT / "docs" / "ALIGNMENT_PROTOCOL.md",
    ROOT / "docs" / "ERROR_CORRECTION_PROTOCOL.md",
    ROOT / "docs" / "DEVELOPMENT_TIME_VERIFICATION.md",
    ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md",
    ROOT / "docs" / "SECURE_DEVELOPMENT_PROTOCOL.md",
    ROOT / "docs" / "THREAT_MODEL_TEMPLATE.md",
    ROOT / "docs" / "GROWTH_MARKETING_FRAMEWORK.md",
    ROOT / "docs" / "MARKET_OPPORTUNITY_INTELLIGENCE.md",
    ROOT / "docs" / "GROWTH_INTELLIGENCE.md",
    ROOT / "docs" / "SOCIAL_AUTOMATION_PROTOCOL.md",
    ROOT / "docs" / "MIGRATION_ALIGNMENT.md",
    ROOT / "docs" / "ARCHITECTURE.md",
    ROOT / "docs" / "BRAND_GUIDELINES.md",
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
    social_matrix = read(ROOT / "governance" / "social-automation-matrix.yaml")
    current = read(ROOT / "docs" / "CURRENT_STATE.md")
    alignment_protocol = read(ROOT / "docs" / "ALIGNMENT_PROTOCOL.md")
    error_protocol = read(ROOT / "docs" / "ERROR_CORRECTION_PROTOCOL.md")
    development_protocol = read(ROOT / "docs" / "DEVELOPMENT_TIME_VERIFICATION.md")
    latent_protocol = read(ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md")
    security_protocol = read(ROOT / "docs" / "SECURE_DEVELOPMENT_PROTOCOL.md")
    threat_template = read(ROOT / "docs" / "THREAT_MODEL_TEMPLATE.md")
    growth_framework = read(ROOT / "docs" / "GROWTH_MARKETING_FRAMEWORK.md")
    market_intelligence = read(ROOT / "docs" / "MARKET_OPPORTUNITY_INTELLIGENCE.md")
    growth_intelligence = read(ROOT / "docs" / "GROWTH_INTELLIGENCE.md")
    social_protocol = read(ROOT / "docs" / "SOCIAL_AUTOMATION_PROTOCOL.md")
    migration_alignment = read(ROOT / "docs" / "MIGRATION_ALIGNMENT.md")
    architecture = read(ROOT / "docs" / "ARCHITECTURE.md")
    brand_guidelines = read(ROOT / "docs" / "BRAND_GUIDELINES.md")
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

    for name, content in (
        ("docs/CURRENT_STATE.md", current),
        ("DEC-0004", entry_decision),
        ("alignment manifest", manifest),
    ):
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
            "treat registration as distinct from activation",
            "keep paid acquisition blocked until activation, retention, conversion, attribution, and unit economics are credible enough to evaluate",
            "report missing telemetry as `UNKNOWN`, not zero",
            "do not create a duplicate \"Marketing Brain\"",
            "ChatGPT must not declare a defect fixed solely because Codex says so.",
            "UNDERSTAND -> BASELINE -> SMALL CHANGE -> FAST CHECK -> TARGETED TEST -> NEGATIVE TEST -> DIFF REVIEW -> REPEAT -> CI",
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
            "does not create a parallel \"Marketing Brain\"",
        ],
        failures,
    )

    require(
        "docs/SOCIAL_AUTOMATION_PROTOCOL.md",
        social_protocol,
        [
            "# Nexkosmo Social Automation Protocol",
            "Status: APPROVED DESIGN / RUNTIME IMPLEMENTATION PENDING",
            "AI may prepare and execute approved social work; it may not invent truth, rights, authority, or approval.",
            "Only `APPROVED` content may become `SCHEDULED` or `PUBLISHING`.",
            "Provider secrets are Tier 4 / critical credentials.",
            "Publishing is an externally visible side effect.",
            "Missing metrics are `UNKNOWN`, not zero.",
            "Do not implement six providers simultaneously as the first slice.",
        ],
        failures,
    )

    require(
        "governance/alignment-manifest.yaml",
        manifest,
        [
            "manifest_version: 9",
            "- ChatGPT",
            "- Codex",
            "agent_error_correction_separate_from_brain: true",
            "development_time_verification_separate_from_brain: true",
            "latent_defect_assurance_separate_from_brain: true",
            "secure_development_separate_from_brain: true",
            "growth_marketing_framework_separate_from_brain: true",
            "social_automation_separate_from_brain: true",
            "growth_marketing_framework: docs/GROWTH_MARKETING_FRAMEWORK.md",
            "growth_marketing_matrix: governance/growth-marketing-matrix.yaml",
            "market_opportunity_intelligence: docs/MARKET_OPPORTUNITY_INTELLIGENCE.md",
            "growth_intelligence: docs/GROWTH_INTELLIGENCE.md",
            "social_automation_protocol: docs/SOCIAL_AUTOMATION_PROTOCOL.md",
            "social_automation_matrix: governance/social-automation-matrix.yaml",
            "migration_alignment: docs/MIGRATION_ALIGNMENT.md",
            "architecture: docs/ARCHITECTURE.md",
            "brand_guidelines: docs/BRAND_GUIDELINES.md",
            "require_growth_framework_for_material_marketing_or_growth_work: true",
            "require_social_automation_protocol_for_social_publishing_or_provider_integration_work: true",
            "critical_unknowns_block: true",
            "- material_public_claims",
            "- social_publishing_authority",
            "- creator_marketing_rights",
            "every_material_trust_boundary_requires_security_contract: true",
            "security_unknowns_fail_closed: true",
            "activation_metric: UNKNOWN_PENDING_USER_EVIDENCE",
            "paid_acquisition: BLOCKED_UNTIL_ECONOMICS_AND_RETENTION_EVIDENCED",
            "claims_assurance: REQUIRED",
            "dark_patterns: PROHIBITED",
            "missing_marketing_telemetry_is_unknown_not_zero: true",
            "director_controls_brand_launch_material_spend_and_consequential_public_claims: true",
            "runtime_implementation: PENDING",
            "manual_approval_first: REQUIRED",
            "provider_credentials: TIER_4_CRITICAL",
            "publish_idempotency: REQUIRED",
        ],
        failures,
    )

    require(
        "docs/MARKET_OPPORTUNITY_INTELLIGENCE.md",
        market_intelligence,
        [
            (
                "architectural direction and product contract, not a claim that "
                "the capability is implemented"
            ),
            "Visible Feedback Is Not Market Size",
            (
                "A public review, feature request, forum post, or comment is "
                "evidence of a need. It is not a population count."
            ),
            "A Capability Gap is not synonymous with `build`.",
            "Human Approval",
            "Never equate visible feedback with market size.",
        ],
        failures,
    )

    require(
        "docs/GROWTH_INTELLIGENCE.md",
        growth_intelligence,
        [
            (
                "architectural direction and product contract, not a claim that "
                "the capability is implemented"
            ),
            "Optimise for Retained Creator Value",
            "Growth Intelligence MUST NOT misrepresent the product.",
            (
                "Clicks, impressions, open rates, video views, and page visits are "
                "useful diagnostic signals"
            ),
            "significant budget changes require explicit approval",
            "Do not optimise AI marketing for attention.",
        ],
        failures,
    )

    require(
        "docs/MIGRATION_ALIGNMENT.md",
        migration_alignment,
        [
            (
                "The migration is a controlled engineering operation, not an "
                "opportunity for an unapproved redesign."
            ),
            "Set, Studio, CGI, VFX, Render, Pre-Production",
            (
                "Preserve -> Catalogue -> Compare -> Extract Best Capabilities -> "
                "Director Review -> Canonical Workspace -> Implement"
            ),
            "Skipped blocking tests remain blocking.",
            "the Director explicitly accepts the cutover",
        ],
        failures,
    )

    require(
        "docs/ARCHITECTURE.md",
        architecture,
        [
            "Market & Opportunity Intelligence",
            "Visible feedback must never be treated as market size or automatic roadmap authority.",
            "Growth Intelligence",
            "This direction does not create a duplicate Market, Growth, Marketing, Truth,",
        ],
        failures,
    )

    require(
        "docs/BRAND_GUIDELINES.md",
        brand_guidelines,
        [
            "## Current Product Color Direction",
            "newer, brighter cinematic color concept",
            (
                "The brighter direction does not authorise arbitrary recoloring "
                "of frozen canonical assets."
            ),
            CANONICAL_JOURNEY,
        ],
        failures,
    )

    require(
        "governance/latent-assurance-matrix.yaml",
        latent_matrix,
        [
            "property_based_testing:",
            "targeted_mutation_testing:",
            "concurrency_testing:",
            "fault_injection:",
            "deterministic_replay:",
            "A harness is not equivalent to a connected runtime control.",
        ],
        failures,
    )

    require(
        "governance/security-assurance-matrix.yaml",
        security_matrix,
        [
            "current_tree_secret_scan:",
            "dependency_vulnerability_scan:",
            "python_static_security_scan:",
            "authentication:",
            "human_authority_boundary:",
            "server_1_server_2_security:",
            "Critical security UNKNOWN blocks consequential progression.",
        ],
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
        "governance/social-automation-matrix.yaml",
        social_matrix,
        [
            "status: APPROVED_DESIGN_RUNTIME_PENDING",
            "initial_channels:",
            "manual_approval_first:",
            "claim_assurance:",
            "rights_and_consent:",
            "credentials:",
            "status: TIER_4_CRITICAL",
            "publish_idempotency:",
            "audit_evidence:",
            "analytics:",
            "paid_media:",
            "implementation_priority:",
            "Social automation runtime implementation is pending until code, tests, CI, staging, and provider evidence exist.",
        ],
        failures,
    )

    require(
        "docs/ENGINEERING_STATUS.md",
        status,
        [
            "**Alignment:** `<🟢 PASS|🟠 WARN|🔴 FAIL|⚪ UNKNOWN>`",
            "**Runtime:** `<🟢 MATCH|🔴 DRIFT|⚪ UNKNOWN>`",
            "display **Context: ⚪ UNKNOWN**",
        ],
        failures,
    )

    require(
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
