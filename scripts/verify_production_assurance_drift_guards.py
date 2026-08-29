from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]


def run_verifier(repo_root: Path) -> subprocess.CompletedProcess[str]:
    script = repo_root / "scripts" / "verify_production_assurance_alignment.py"
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )


def copy_repo() -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="nexkosmo-production-assurance-drift-"))
    target = temp_dir / "repo"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(
            ".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache", ".hypothesis"
        ),
    )
    return target


def replace_all(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        raise RuntimeError(f"drift sentinel missing in {path}: {old}")
    updated = text.replace(old, new)
    if old in updated:
        raise RuntimeError(f"failed to remove drift sentinel in {path}: {old}")
    path.write_text(updated, encoding="utf-8")


def expect_failure(name: str, mutate: Callable[[Path], None], expected: str) -> None:
    repo = copy_repo()
    try:
        mutate(repo)
        result = run_verifier(repo)
        output = f"{result.stdout}\n{result.stderr}"
        if result.returncode == 0:
            raise RuntimeError(f"Production Assurance drift was not detected: {name}")
        if expected not in output:
            raise RuntimeError(
                f"Production Assurance drift failed for an unexpected reason: {name}\n"
                f"expected diagnostic: {expected}\nactual output:\n{output}"
            )
        print(f"PRODUCTION ASSURANCE DRIFT GUARD PASS: {name}")
    finally:
        shutil.rmtree(repo.parent, ignore_errors=True)


def main() -> int:
    baseline = run_verifier(ROOT)
    if baseline.returncode != 0:
        print("PRODUCTION ASSURANCE DRIFT GUARD FAIL: baseline verifier is not green")
        print(baseline.stdout)
        print(baseline.stderr)
        return 1

    cases: list[tuple[str, Callable[[Path], None], str]] = [
        (
            "format-general production disabled",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "format_general_production_required: true",
                "format_general_production_required: false",
            ),
            "format_general_production_required: true",
        ),
        (
            "movie-only semantics allowed universally",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "movie_only_semantics_prohibited_as_universal_contract: true",
                "movie_only_semantics_prohibited_as_universal_contract: false",
            ),
            "movie_only_semantics_prohibited_as_universal_contract: true",
        ),
        (
            "general Production Studio loop collapsed to film-only",
            lambda repo: replace_all(
                repo / "docs" / "CURRENT_STATE.md",
                "PRODUCTION -> select production unit -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair",
                "PRODUCTION -> select scene/shot -> Open in Studio -> edit -> return to PRODUCTION -> Brain revalidate -> approve or repair",
            ),
            "PRODUCTION -> select production unit",
        ),
        (
            "shared user-visible progress disabled",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "shared_progress_bar_required_for_user_visible_execution: true",
                "shared_progress_bar_required_for_user_visible_execution: false",
            ),
            "shared_progress_bar_required_for_user_visible_execution: true",
        ),
        (
            "fake percentage precision allowed",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "false_percentage_precision_prohibited: true",
                "false_percentage_precision_prohibited: false",
            ),
            "false_percentage_precision_prohibited: true",
        ),
        (
            "raw attempt count allowed as progress",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "raw_attempt_count_progress_prohibited: true",
                "raw_attempt_count_progress_prohibited: false",
            ),
            "raw_attempt_count_progress_prohibited: true",
        ),
        (
            "Nexkosmo failure made automatically customer billable",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "nexkosmo_caused_failure_not_automatically_customer_billable: true",
                "nexkosmo_caused_failure_not_automatically_customer_billable: false",
            ),
            "nexkosmo_caused_failure_not_automatically_customer_billable: true",
        ),
        (
            "fault attribution removed before billing",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "fault_attribution_before_recovery_billing: true",
                "fault_attribution_before_recovery_billing: false",
            ),
            "fault_attribution_before_recovery_billing: true",
        ),
        (
            "assurance cost collapsed into billable cost",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "nexkosmo_assurance_cost_separate: true",
                "nexkosmo_assurance_cost_separate: false",
            ),
            "nexkosmo_assurance_cost_separate: true",
        ),
        (
            "economic containment disabled",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "repeated_failure_requires_economic_containment: true",
                "repeated_failure_requires_economic_containment: false",
            ),
            "repeated_failure_requires_economic_containment: true",
        ),
        (
            "coverage before completion disabled",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "coverage_before_completion_supported: true",
                "coverage_before_completion_supported: false",
            ),
            "coverage_before_completion_supported: true",
        ),
        (
            "expensive restart reassessment disabled",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "materially_more_expensive_restart_requires_reassessment: true",
                "materially_more_expensive_restart_requires_reassessment: false",
            ),
            "materially_more_expensive_restart_requires_reassessment: true",
        ),
        (
            "Brain allowed to raise own production budget",
            lambda repo: replace_all(
                repo / "governance" / "alignment-manifest.yaml",
                "brain_cannot_raise_own_budget_compute_or_material_spend_authority: true",
                "brain_cannot_raise_own_budget_compute_or_material_spend_authority: false",
            ),
            "brain_cannot_raise_own_budget_compute_or_material_spend_authority: true",
        ),
    ]

    for name, mutate, expected in cases:
        expect_failure(name, mutate, expected)

    print("Production Assurance deliberate drift-injection verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
