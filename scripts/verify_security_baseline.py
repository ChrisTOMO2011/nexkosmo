from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

TEXT_SUFFIXES = {
    ".py",
    ".md",
    ".yaml",
    ".yml",
    ".json",
    ".toml",
    ".ini",
    ".cfg",
    ".env",
    ".example",
    ".txt",
    ".sh",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
}

SECRET_PATTERNS = [
    ("private key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----")),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}")),
    ("Stripe live secret", re.compile(r"sk_live_[A-Za-z0-9]{16,}")),
    ("OpenAI-style secret", re.compile(r"sk-[A-Za-z0-9_-]{20,}")),
]

DANGEROUS_SOURCE_PATTERNS = [
    ("shell=True", re.compile(r"shell\s*=\s*True")),
    ("eval()", re.compile(r"\beval\s*\(")),
    ("exec()", re.compile(r"\bexec\s*\(")),
    ("pickle.loads", re.compile(r"\bpickle\.loads\s*\(")),
    ("yaml.load without SafeLoader", re.compile(r"\byaml\.load\s*\(")),
    ("TLS verification disabled", re.compile(r"verify\s*=\s*False")),
]

EXCLUDED_DIRS = {
    ".git",
    ".venv",
    "node_modules",
    "dist",
    "build",
    ".pytest_cache",
    ".mypy_cache",
    ".hypothesis",
}


def iter_text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        if any(part in EXCLUDED_DIRS for part in path.parts):
            continue
        if path.suffix.lower() in TEXT_SUFFIXES or path.name in {"Dockerfile", ".gitignore"}:
            yield path


def check_required_files(failures: list[str]) -> None:
    required = [
        ROOT / "docs" / "SECURE_DEVELOPMENT_PROTOCOL.md",
        ROOT / "docs" / "THREAT_MODEL_TEMPLATE.md",
        ROOT / "governance" / "security-assurance-matrix.yaml",
    ]
    for path in required:
        if not path.exists():
            failures.append(f"missing required security file: {path.relative_to(ROOT)}")


def check_gitignore(failures: list[str]) -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    for required in (".env", ".venv/", "__pycache__/"):
        if required not in gitignore:
            failures.append(f".gitignore missing security hygiene rule: {required}")


def scan_secrets(failures: list[str]) -> None:
    for path in iter_text_files():
        if path.name == ".env.example":
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for name, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                failures.append(f"possible committed secret ({name}) in {path.relative_to(ROOT)}")


def scan_dangerous_patterns(failures: list[str]) -> None:
    for path in (ROOT / "app").rglob("*.py"):
        text = path.read_text(encoding="utf-8")
        for name, pattern in DANGEROUS_SOURCE_PATTERNS:
            if pattern.search(text):
                failures.append(
                    f"security-sensitive pattern ({name}) requires explicit review: "
                    f"{path.relative_to(ROOT)}"
                )


def run_dependency_audit(failures: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "pip_audit", "-r", "requirements.txt", "--progress-spinner", "off"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        failures.append("dependency vulnerability audit failed")
        print(result.stdout)
        print(result.stderr)


def run_bandit(failures: list[str]) -> None:
    result = subprocess.run(
        [sys.executable, "-m", "bandit", "-q", "-r", "app"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        failures.append("Bandit security scan failed")
        print(result.stdout)
        print(result.stderr)


def main() -> int:
    failures: list[str] = []
    check_required_files(failures)
    check_gitignore(failures)
    scan_secrets(failures)
    scan_dangerous_patterns(failures)
    run_dependency_audit(failures)
    run_bandit(failures)

    if failures:
        for failure in failures:
            print(f"SECURITY BASELINE FAIL: {failure}")
        return 1

    print(
        "SECURITY BASELINE PASS: required security docs, current-tree secret patterns, "
        "source patterns, dependency audit, and Bandit checks passed"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
