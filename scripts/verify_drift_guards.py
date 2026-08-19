from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[1]


def run_verifier(repo_root: Path) -> subprocess.CompletedProcess[str]:
    script = repo_root / "scripts" / "verify_alignment.py"
    return subprocess.run(
        [sys.executable, str(script)],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )


def copy_repo() -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="nexkosmo-drift-"))
    target = temp_dir / "repo"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", ".pytest_cache", ".mypy_cache"),
    )
    return target


def expect_failure(
    name: str,
    mutate: Callable[[Path], None],
    expected_diagnostic: str,
) -> None:
    repo = copy_repo()
    try:
        mutate(repo)
        result = run_verifier(repo)
        output = f"{result.stdout}\n{result.stderr}"
        if result.returncode == 0:
            raise RuntimeError(f"drift injection was not detected: {name}")
        if expected_diagnostic not in output:
            raise RuntimeError(
                f"drift injection failed for an unexpected reason: {name}\n"
                f"expected diagnostic: {expected_diagnostic}\n"
                f"actual output:\n{output}"
            )
        print(f"DRIFT GUARD PASS: {name}")
    finally:
        shutil.rmtree(repo.parent, ignore_errors=True)


def replace_all(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count == 0:
        raise RuntimeError(f"injection sentinel missing in {path}: {old}")
    updated = text.replace(old, new)
    if old in updated:
        raise RuntimeError(f"injection failed to remove all sentinels in {path}: {old}")
    path.write_text(updated, encoding="utf-8")
    print(f"DRIFT INJECTION: {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path.name} occurrences={count}")


def main() -> int:
    baseline = run_verifier(ROOT)
    if baseline.returncode != 0:
        print("DRIFT GUARD FAIL: baseline alignment verification is not green")
        print(baseline.stdout)
        print(baseline.stderr)
        return 1

    expect_failure(
        "canonical creative workflow mutation",
        lambda repo: replace_all(
            repo / "docs" / "CURRENT_STATE.md",
            "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION",
            "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> RENDER",
        ),
        "docs/CURRENT_STATE.md does not contain canonical creative workflow",
    )
    expect_failure(
        "manifest workflow mutation",
        lambda repo: replace_all(
            repo / "governance" / "alignment-manifest.yaml",
            "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION",
            "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> RENDER",
        ),
        "governance/alignment-manifest.yaml does not contain canonical creative workflow",
    )
    expect_failure(
        "critical fail-closed policy removal",
        lambda repo: replace_all(
            repo / "governance" / "alignment-manifest.yaml",
            "critical_unknowns_block: true",
            "critical_unknowns_block: false",
        ),
        "alignment manifest missing required drift guard: critical_unknowns_block: true",
    )
    expect_failure(
        "alignment steward authority mutation",
        lambda repo: replace_all(
            repo / "docs" / "CURRENT_STATE.md",
            "Alignment steward: ChatGPT",
            "Alignment steward: UNKNOWN",
        ),
        "docs/CURRENT_STATE.md missing required rule: Alignment steward: ChatGPT",
    )
    expect_failure(
        "vertical status contract mutation",
        lambda repo: replace_all(
            repo / "docs" / "ENGINEERING_STATUS.md",
            "**Alignment:** `<🟢 PASS|🟠 WARN|🔴 FAIL|⚪ UNKNOWN>`",
            "**Alignment:** `PASS`",
        ),
        "docs/ENGINEERING_STATUS.md missing required visibility rule",
    )

    print("Deliberate drift-injection verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
