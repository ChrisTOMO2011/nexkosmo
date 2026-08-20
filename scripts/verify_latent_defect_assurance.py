from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def copy_repo() -> Path:
    temp_dir = Path(tempfile.mkdtemp(prefix="nexkosmo-latent-"))
    target = temp_dir / "repo"
    shutil.copytree(
        ROOT,
        target,
        ignore=shutil.ignore_patterns(
            ".git",
            ".venv",
            "__pycache__",
            ".pytest_cache",
            ".mypy_cache",
            ".hypothesis",
        ),
    )
    return target


def run_authority_tests(repo_root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "tests/test_domain_invariants.py",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )


def main() -> int:
    baseline = run_authority_tests(ROOT)
    if baseline.returncode != 0:
        print("LATENT DEFECT ASSURANCE FAIL: authority baseline is not green")
        print(baseline.stdout)
        print(baseline.stderr)
        return 1

    repo = copy_repo()
    try:
        rules = repo / "app" / "domain" / "rules.py"
        text = rules.read_text(encoding="utf-8")
        sentinel = "if principal.agent_kind is not AgentKind.HUMAN:"
        mutation = "if principal.agent_kind is AgentKind.HUMAN:"
        if sentinel not in text:
            print("LATENT DEFECT ASSURANCE FAIL: authority mutation sentinel missing")
            return 1

        rules.write_text(text.replace(sentinel, mutation, 1), encoding="utf-8")
        mutated = run_authority_tests(repo)
        if mutated.returncode == 0:
            print(
                "LATENT DEFECT ASSURANCE FAIL: authority mutation survived; "
                "tests did not detect removal of human-only authority"
            )
            return 1

        output = f"{mutated.stdout}\n{mutated.stderr}"
        if "failed" not in output.lower():
            print("LATENT DEFECT ASSURANCE FAIL: mutation failed for an unclear reason")
            print(output)
            return 1

        print("LATENT DEFECT ASSURANCE PASS: authority mutation was detected")
        print("LATENT DEFECT ASSURANCE PASS: property-based authority tests are green")
        return 0
    finally:
        shutil.rmtree(repo.parent, ignore_errors=True)


if __name__ == "__main__":
    sys.exit(main())
