"""
YEVRAH — Fact Verifier test against an already-generated draft.

Runs ONLY the fact verifier. It does not execute the Case Agent,
Template Agent, Section Classifier, Draft Synthesizer, or Structure
Verifier.

Place this file, e2e_case_facts(3).json, and e2e_draft(3).md in the
YEVRAH project root, then run:

    python test_verifier_existing_draft.py

The verifier is imported from:
    agent.nodes.verifier_node

The test checks that every verifier issue is patch-ready by validating:
    - issue_id
    - block_id
    - exact current_text
    - claim is reported when present (mismatch is a warning, not a test failure)
    - issue explanation
    - severity
    - missing-information details when applicable
    - exact current_text exists in the draft
    - character range can be resolved deterministically by Python
"""

import json
import sys
from pathlib import Path

from agent.nodes.verifier_node import verify_facts


BASE_DIR = Path(__file__).resolve().parent
CASE_FACTS_PATH = BASE_DIR / "e2e_case_facts.json"
DRAFT_PATH = BASE_DIR / "e2e_draft.md"
OUTPUT_PATH = BASE_DIR / "e2e_verification_test_output.json"


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Case facts file not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def load_text(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"Draft file not found: {path}")
    return path.read_text(encoding="utf-8")


def validate_warning(warning: dict, draft: str, index: int):
    required = {
        "issue_id",
        "block_id",
        "current_text",
        "claim",
        "issue",
        "severity",
        "missing_information",
    }

    missing = required - set(warning)
    if missing:
        raise AssertionError(
            f"Warning #{index} missing fields: {sorted(missing)}"
        )

    issue_id = warning["issue_id"]
    block_id = warning["block_id"]
    current_text = warning["current_text"]

    if not isinstance(issue_id, str) or not issue_id.startswith("F-"):
        raise AssertionError(f"{issue_id!r}: invalid issue_id")

    if not isinstance(block_id, str) or not block_id.strip():
        raise AssertionError(f"{issue_id}: block_id is empty")

    if warning.get("claim") != current_text:
        print(
            f"  [WARN] {issue_id}: claim differs from current_text; "
            "continuing because current_text is the patch source."
        )

    if not isinstance(current_text, str) or not current_text.strip():
        raise AssertionError(f"{issue_id}: current_text is empty")

    occurrences = draft.count(current_text)
    if occurrences == 0:
        raise AssertionError(
            f"{issue_id}: current_text was not found exactly in the draft"
        )

    if not warning["issue"].strip():
        raise AssertionError(f"{issue_id}: issue explanation is empty")

    if warning["severity"] not in {"high", "medium"}:
        raise AssertionError(
            f"{issue_id}: invalid severity {warning['severity']!r}"
        )

    missing_info = warning["missing_information"]
    if missing_info is not None:
        if not isinstance(missing_info, dict):
            raise AssertionError(
                f"{issue_id}: missing_information must be an object or null"
            )
        if not missing_info.get("type"):
            raise AssertionError(f"{issue_id}: missing_information.type is empty")
        if not missing_info.get("description"):
            raise AssertionError(
                f"{issue_id}: missing_information.description is empty"
            )

    start = draft.find(current_text)
    end = start + len(current_text)

    return {
        **warning,
        "char_start": start,
        "char_end": end,
        "text_occurrences": occurrences,
    }


def main():
    print("=" * 70)
    print("  YEVRAH — Existing Draft Fact Verifier Test")
    print("=" * 70)

    case_facts = load_json(CASE_FACTS_PATH)
    draft = load_text(DRAFT_PATH)

    state = {
        "case_facts": case_facts,
        "draft": draft,
        "verification_warnings": [],
    }

    print(f"\nCase facts : {CASE_FACTS_PATH.name}")
    print(f"Draft      : {DRAFT_PATH.name}")
    print(f"Draft size : {len(draft)} characters")
    print("\nRunning fact verifier...\n")

    result_state = verify_facts(state)
    warnings = result_state.get("verification_warnings", [])

    print(f"Verifier returned {len(warnings)} issue(s).\n")

    normalized = []
    seen_issue_ids = set()

    for index, warning in enumerate(warnings, start=1):
        item = validate_warning(warning, draft, index)

        if item["issue_id"] in seen_issue_ids:
            raise AssertionError(
                f"Duplicate issue_id returned: {item['issue_id']}"
            )
        seen_issue_ids.add(item["issue_id"])

        normalized.append(item)

        print(f"{item['issue_id']} [{item['severity'].upper()}]")
        print(f"  block_id:            {item['block_id']}")
        print(f"  char_range:          {item['char_start']} -> {item['char_end']}")
        print(f"  occurrences:         {item['text_occurrences']}")
        print(f"  current_text:        {item['current_text']}")
        print(f"  issue:                {item['issue']}")

        missing_info = item.get("missing_information")
        if missing_info:
            print(f"  missing_info.type:   {missing_info['type']}")
            print(
                "  missing_info.detail: "
                f"{missing_info['description']}"
            )
        else:
            print("  missing_info:        None")

        print()

    output = {
        "draft_file": str(DRAFT_PATH),
        "case_facts_file": str(CASE_FACTS_PATH),
        "draft_length": len(draft),
        "verified": len(warnings) == 0,
        "warnings": normalized,
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved: {OUTPUT_PATH}")
    print("\nPASS — verifier output is ready for Repair Agent integration.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nFAILED: {exc}")
        sys.exit(1)