from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = {
    "manifest": ROOT / "governance" / "alignment-manifest.yaml",
    "current": ROOT / "docs" / "CURRENT_STATE.md",
    "decision1": ROOT / "docs" / "decisions" / "DEC-0001-product-journey.md",
    "decision2": ROOT / "docs" / "decisions" / "DEC-0002-production-studio-boundary.md",
    "decision3": ROOT / "docs" / "decisions" / "DEC-0003-project-state-and-fixtures.md",
    "decision4": ROOT / "docs" / "decisions" / "DEC-0004-entry-routing-and-flow-layers.md",
    "decision5": ROOT / "docs" / "decisions" / "DEC-0005-production-assurance-and-render-cost-attribution.md",
    "render": ROOT / "docs" / "architecture" / "ARCHITECTURE_AMENDMENT_001_CONTINUITY_AND_RENDER_ORCHESTRATION.md",
    "native_assets": ROOT / "docs" / "architecture" / "ARCHITECTURE_AMENDMENT_002_ASSET_RESOLUTION_AND_ENHANCEMENT.md",
    "security": ROOT / "docs" / "SECURE_DEVELOPMENT_PROTOCOL.md",
    "latent": ROOT / "docs" / "LATENT_DEFECT_ASSURANCE.md",
    "marketing": ROOT / "docs" / "GROWTH_MARKETING_FRAMEWORK.md",
}

GENERAL_LOOP = (
    "PRODUCTION -> select production unit -> Open in Studio -> edit -> "
    "return to PRODUCTION -> Brain revalidate -> approve or repair"
)
FILM_LOOP = (
    "PRODUCTION -> select scene/shot -> Open in Studio -> edit -> "
    "return to PRODUCTION -> Brain revalidate -> approve or repair"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def require(label: str, text: str, phrases: list[str], failures: list[str]) -> None:
    for phrase in phrases:
        if phrase not in text:
            failures.append(f"{label} missing required Production Assurance rule: {phrase}")


def main() -> int:
    failures: list[str] = []
    for label, path in REQUIRED_FILES.items():
        if not path.exists():
            failures.append(f"missing required Production Assurance cross-reference file: {path.relative_to(ROOT)}")

    if failures:
        for failure in failures:
            print(f"PRODUCTION ASSURANCE ALIGNMENT FAIL: {failure}")
        return 1

    docs = {label: read(path) for label, path in REQUIRED_FILES.items()}

    require(
        "manifest",
        docs["manifest"],
        [
            "manifest_version: 10",
            "docs/decisions/DEC-0005-production-assurance-and-render-cost-attribution.md",
            GENERAL_LOOP,
            FILM_LOOP,
            "format_general_production_required: true",
            "movie_only_semantics_prohibited_as_universal_contract: true",
            "execute_smallest_practical_validatable_recoverable_units: true",
            "coverage_before_completion_supported: true",
            "nexkosmo_caused_failure_not_automatically_customer_billable: true",
            "actual_production_cost_separate_from_customer_billable_cost: true",
            "fault_attribution_before_recovery_billing: true",
            "repeated_failure_requires_economic_containment: true",
            "materially_more_expensive_restart_requires_reassessment: true",
            "brain_cannot_raise_own_budget_compute_or_material_spend_authority: true",
        ],
        failures,
    )

    require(
        "CURRENT_STATE",
        docs["current"],
        [
            "Nexkosmo must not force every project into movie-only vocabulary or hierarchy.",
            GENERAL_LOOP,
            "Large productions should be orchestrated as one creative whole but executed in the smallest practical independently validatable and recoverable units appropriate to the production format.",
            "Coverage before completion",
            "Actual Production Cost",
            "Customer-Billable Cost",
            "Nexkosmo Assurance Cost",
        ],
        failures,
    )

    require(
        "DEC-0001",
        docs["decision1"],
        [
            "project-wide Production control room",
            "The six stages describe shared creative responsibility, not mandatory movie-specific internal vocabulary.",
            "Nexkosmo must not force every production type into movie-only hierarchy",
        ],
        failures,
    )

    require(
        "DEC-0002",
        docs["decision2"],
        [
            "PRODUCTION is the project-wide production control room.",
            "format-appropriate production unit",
            "Equivalent format-aware flows must preserve the same boundary",
        ],
        failures,
    )

    require(
        "DEC-0003",
        docs["decision3"],
        [
            "levels, encounters, clips, assets, simulations, passes",
            "must not hard-code movie-only semantics",
        ],
        failures,
    )

    require(
        "DEC-0004",
        docs["decision4"],
        [
            GENERAL_LOOP,
            "The shared stages remain format-general.",
            "Screenplay import remains a supported film-oriented shortcut",
        ],
        failures,
    )

    require(
        "DEC-0005",
        docs["decision5"],
        [
            "Actual Production Cost",
            "Customer-Billable Cost",
            "Nexkosmo Assurance Cost",
            "Fault attribution before billing",
            "Economic containment of repeated failure",
            "Intelligent validation checkpoints",
            "Coverage before completion",
            "materially more expensive full restart",
        ],
        failures,
    )

    require(
        "Render Amendment 001",
        docs["render"],
        [
            "format-appropriate production unit",
            "smallest practical independently validatable and recoverable units",
            "Coverage before completion",
            "materially more expensive full restart",
            "A project-wide Render / Build / Produce / Bake / Simulate command is an orchestration command",
        ],
        failures,
    )

    require(
        "Native Asset Reconstruction",
        docs["native_assets"],
        [
            "preserve the immutable original",
            "require human approval before marking a reconstruction canonical",
            "runtime and resource cost",
        ],
        failures,
    )

    require(
        "Secure Development",
        docs["security"],
        [
            "never trust client-provided price/credit entitlement as authoritative",
            "keep a durable auditable ledger",
            "separate estimate costings from actual financial evidence",
        ],
        failures,
    )

    require(
        "Latent Defect Assurance",
        docs["latent"],
        [
            "double billing",
            "worker assignment -> disconnect -> requeue -> duplicate completion",
            "GPU out-of-memory",
            "duplicate logical completion cannot create duplicate billable completion",
        ],
        failures,
    )

    require(
        "Growth & Marketing",
        docs["marketing"],
        [
            "Product truth before promotion. Evidence before claims. Creator value before growth metrics.",
            "hiding material limitations, costs, or conditions",
            "claims assurance",
        ],
        failures,
    )

    if failures:
        for failure in failures:
            print(f"PRODUCTION ASSURANCE ALIGNMENT FAIL: {failure}")
        return 1

    print("Production Assurance and format-general production alignment passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
