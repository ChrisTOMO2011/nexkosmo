from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

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


def expect_failure(name: str, mutate) -> None:
    repo = copy_repo()
    try:
        mutate(repo)
        result = run_verifier(repo)
        if result.returncode == 0:
            raise RuntimeError(f"drift injection was not detected: {name}")
        print(f"DRIFT GUARD PASS: {name}")
    finally:
        shutil.rmtree(repo.parent, ignore_errors=True)


def replace(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if old not in text:
        raise RuntimeError(f"injection sentinel missing in {path}: {old}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    baseline = run_verifier(ROOT)
    if baseline.returncode != 0:
        print("DRIFT GUARD FAIL: baseline alignment verification is not green")
        print(baseline.stdout)
        print(baseline.stderr)
        return 1

    expect_failure(
        "canonical creative workflow mutation",
        lambda repo: replace(
            repo / "docs" / "CURRENT_STATE.md",
            "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION",
            "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> RENDER",
        ),
    )
    expect_failure(
        "manifest workflow mutation",
        lambda repo: replace(
            repo / "governance" / "alignment-manifest.yaml",
            "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> PRODUCTION",
            "IDEA -> DISCOVER -> SHAPE -> BUILD -> READY -> RENDER",
        ),
    )
    expect_failure(
        "critical fail-closed policy removal",
        lambda repo: replace(
            repo / "governance" / "alignment-manifest.yaml",
            "critical_unknowns_block: true",
            "critical_unknowns_block: false",
        ),
    )
    expect_failure(
        "Director authority removal",
        lambda repo: replace(
            repo / "docs" / "CURRENT_STATE.md",
            "Alignment steward: ChatGPT",
            "Alignment steward: UNKNOWN",
        ),
    )
    expect_failure(
        "vertical status contract mutation",
        lambda repo: replace(
            repo / "docs" / "ENGINEERING_STATUS.md",
            "**Alignment:** `<🟢 PASS|🟠 WARN|🔴 FAIL|⚪ UNKNOWN>`",
            "**Alignment:** `PASS`",
        ),
    )

    print("Deliberate drift-injection verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
