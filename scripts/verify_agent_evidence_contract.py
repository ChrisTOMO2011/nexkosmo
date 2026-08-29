from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AGENTS = ROOT / "AGENTS.md"
CI_WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
SECTION_HEADING = "## Agent finding and evidence levels"
LEVELS = (
    "OBSERVED",
    "SUSPECTED",
    "SUPPORTED",
    "STRONGLY_SUPPORTED",
    "VERIFIED",
    "CONTRADICTED",
)
REQUIRED_RULES = (
    "MUST report material findings according to the strength of the evidence",
    "Agent statements are not evidence merely because another agent repeats or agrees with them.",
    "An agent MUST NOT upgrade a finding merely because another AI says it is correct",
    "the decisive requirements within the claimed scope MUST be `VERIFIED`",
    "Uncertainty is acceptable and MUST be stated truthfully.",
    "Agents must never fabricate certainty",
)
CI_COMMAND = "python scripts/verify_agent_evidence_contract.py"


def extract_section(text: str) -> str | None:
    start = text.find(SECTION_HEADING)
    if start < 0:
        return None

    next_heading = text.find("\n## ", start + len(SECTION_HEADING))
    if next_heading < 0:
        return text[start:]
    return text[start:next_heading]


def validate_agent_contract(text: str) -> list[str]:
    failures: list[str] = []
    section = extract_section(text)
    if section is None:
        return [f"MISSING section: {SECTION_HEADING}"]

    positions: list[int] = []
    for level in LEVELS:
        marker = f"`{level}`"
        position = section.find(marker)
        if position < 0:
            failures.append(f"MISSING finding level: {level}")
        positions.append(position)

    present_positions = [position for position in positions if position >= 0]
    if len(present_positions) == len(LEVELS) and present_positions != sorted(present_positions):
        failures.append("Finding levels are not in the required evidence-strength order")

    for rule in REQUIRED_RULES:
        if rule not in section:
            failures.append(f"MISSING or weakened agent evidence rule: {rule}")

    return failures


def validate_ci_wiring(text: str) -> list[str]:
    if CI_COMMAND not in text:
        return [f"CI does not invoke required verifier: {CI_COMMAND}"]
    return []


def main() -> int:
    failures: list[str] = []

    if not AGENTS.exists():
        failures.append("MISSING AGENTS.md")
    else:
        failures.extend(validate_agent_contract(AGENTS.read_text(encoding="utf-8")))

    if not CI_WORKFLOW.exists():
        failures.append("MISSING .github/workflows/ci.yml")
    else:
        failures.extend(validate_ci_wiring(CI_WORKFLOW.read_text(encoding="utf-8")))

    if failures:
        print("Agent evidence contract verification FAILED")
        for failure in failures:
            print(f"- {failure}")
        return 1

    print("Agent evidence contract verification PASSED")
    print("- finding levels present and ordered")
    print("- independent-evidence rule present")
    print("- consequential VERIFIED gate present")
    print("- truthful uncertainty rule present")
    print("- CI wiring present")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
