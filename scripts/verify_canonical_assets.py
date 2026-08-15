from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "assets" / "brand" / "canonical-assets.json"


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


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

        actual = git_blob_sha1(path.read_bytes())
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
