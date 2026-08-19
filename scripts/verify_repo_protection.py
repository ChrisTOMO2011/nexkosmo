from __future__ import annotations

import json
import os
import sys
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def fail(message: str) -> int:
    print(f"REPOSITORY PROTECTION FAIL: {message}")
    return 1


def main() -> int:
    repository = os.environ.get("GITHUB_REPOSITORY")
    if not repository:
        return fail("GITHUB_REPOSITORY is not available")

    token = os.environ.get("GITHUB_TOKEN")
    url = f"https://api.github.com/repos/{repository}/branches/main"
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "nexkosmo-repository-protection-check",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        with urlopen(Request(url, headers=headers), timeout=15) as response:
            data = json.load(response)
    except (HTTPError, URLError, TimeoutError) as exc:
        return fail(f"could not verify main branch protection: {exc}")

    if not data.get("protected", False):
        return fail(
            "main is not protected. Configure the GitHub main-branch ruleset/branch protection before merge. "
            "See docs/REPOSITORY_PROTECTION.md"
        )

    print("Repository protection verification passed: main is protected.")
    print("Detailed policy requirements remain defined in docs/REPOSITORY_PROTECTION.md and require human verification when settings change.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
