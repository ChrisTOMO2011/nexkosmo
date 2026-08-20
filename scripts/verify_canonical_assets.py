from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets" / "brand" / "canonical-assets.json"


def canonical_git_blob_sha1(path: Path, registered_path: str) -> str:
    result = subprocess.run(
        ["git", "hash-object", f"--path={registered_path}", str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "git hash-object failed"
        raise RuntimeError(detail)

    digest = result.stdout.strip()
    if re.fullmatch(r"[0-9a-f]{40}", digest) is None:
        raise RuntimeError(f"git hash-object returned an invalid digest: {digest!r}")
    return digest


def main() -> int:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    failures: list[str] = []

    for asset in registry.get("assets", []):
        path = ROOT / asset["path"]
        expected = asset.get("git_blob_sha1")
        status = asset.get("status")

        if not path.exists():
            failures.append(f"MISSING canonical asset: {asset['id']} -> {asset['path']}")
            continue

        try:
            actual = canonical_git_blob_sha1(path, asset["path"])
        except (OSError, RuntimeError) as exc:
            failures.append(
                f"UNVERIFIABLE canonical asset: {asset['id']} -> {exc}"
            )
            continue

        if expected and actual != expected:
            failures.append(
                f"DRIFT detected for {asset['id']}: expected {expected}, got {actual}"
            )

        if status not in {"FROZEN", "APPROVED"}:
            failures.append(
                f"INVALID canonical status for {asset['id']}: {status!r}"
            )

    if failures:
        print("Canonical asset verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Canonical asset verification PASSED")
    for asset in registry.get("assets", []):
        print(f"- {asset['id']} [{asset['status']}] -> {asset['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
