from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = [
    ROOT / "AGENTS.md",
    ROOT / "docs" / "CURRENT_STATE.md",
    ROOT / "docs" / "ALIGNMENT_PROTOCOL.md",
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


def fail(message: str, failures: list[str]) -> None:
    failures.append(message)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []

    for path in REQUIRED_FILES:
        if not path.exists():
            fail(f"missing required alignment file: {path.relative_to(ROOT)}", failures)

    if failures:
        for message in failures:
            print(f"ALIGNMENT FAIL: {message}")
        return 1

    agents = read(ROOT / "AGENTS.md")
    current = read(ROOT / "docs" / "CURRENT_STATE.md")
    protocol = read(ROOT / "docs" / "ALIGNMENT_PROTOCOL.md")
    entry_decision = read(ROOT / "docs" / "decisions" / "DEC-0004-entry-routing-and-flow-layers.md")

    for name, content in (
        ("AGENTS.md", agents),
        ("docs/CURRENT_STATE.md", current),
    ):
        if CANONICAL_JOURNEY not in content:
            fail(f"{name} does not contain canonical creative workflow: {CANONICAL_JOURNEY}", failures)

    for phrase in (NORMAL_ENTRY, IMPORT_ENTRY):
        if phrase not in current:
            fail(f"docs/CURRENT_STATE.md missing required entry route: {phrase}", failures)
        if phrase not in agents:
            fail(f"AGENTS.md missing required entry route: {phrase}", failures)
        if phrase not in entry_decision:
            fail(f"DEC-0004 missing required entry route: {phrase}", failures)

    if PRODUCTION_LOOP not in current:
        fail("docs/CURRENT_STATE.md missing canonical Production/Studio deep-edit loop", failures)
    if PRODUCTION_LOOP not in entry_decision:
        fail("DEC-0004 missing canonical Production/Studio deep-edit loop", failures)

    required_current_phrases = [
        "Studio is not an additional top-level journey stage.",
        "ALIGNMENT STOP GATE.",
        "Conversation alone does not supersede repository canon.",
        "Alignment steward: ChatGPT",
        "The legacy prototype progression `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded as a product-navigation model.",
    ]
    for phrase in required_current_phrases:
        if phrase not in current:
            fail(f"docs/CURRENT_STATE.md missing required rule: {phrase}", failures)

    required_agent_phrases = [
        "docs/CURRENT_STATE.md",
        "docs/ALIGNMENT_PROTOCOL.md",
        "Alignment is a repository and evidence property, not a memory property.",
        "ChatGPT acts as alignment steward",
        "Codex is an implementation agent",
        "The legacy prototype navigation `PRE-PRODUCTION -> SET -> STUDIO -> REVIEW -> RENDER` is superseded.",
    ]
    for phrase in required_agent_phrases:
        if phrase not in agents:
            fail(f"AGENTS.md missing alignment instruction: {phrase}", failures)

    if "Fresh-context reconstruction test" not in protocol:
        fail("alignment protocol is missing the fresh-context reconstruction test", failures)
    if "three distinct flow layers" not in protocol:
        fail("alignment protocol does not distinguish the three flow layers", failures)

    # Legacy prototype sentinels. These checks intentionally activate only if the
    # old frontend paths are merged into the branch under test. They prevent a
    # stale prototype workflow/default character from silently becoming the
    # production contract. Reconciliation may replace these files or remove the
    # forbidden patterns before merge.
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
            fail(
                f"legacy {LEGACY_FLOW} workflow is still encoded in frontend navigation",
                failures,
            )
        if 'characterId = "christopher"' in nav_text:
            fail("frontend navigation still hard-codes Christopher as the default project character", failures)

    character_page = (
        ROOT
        / "frontend"
        / "src"
        / "features"
        / "studio"
        / "pre-production"
        / "pages"
        / "CharacterIdentityPage.tsx"
    )
    if character_page.exists():
        page_text = read(character_page)
        for pattern in (
            'useState("christopher")',
            "useState(35)",
            "useState(180)",
        ):
            if pattern in page_text:
                fail(
                    f"prototype project-state hard coding detected in CharacterIdentityPage.tsx: {pattern}",
                    failures,
                )

    if failures:
        for message in failures:
            print(f"ALIGNMENT FAIL: {message}")
        return 1

    print("Alignment verification passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
