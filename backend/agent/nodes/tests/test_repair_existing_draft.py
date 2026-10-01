"""
YEVRAH — Repair Agent test using verifier output only.

This test deliberately does NOT pass the draft to the Repair Agent.
The Repair Agent receives only the verifier's already-generated issue list.

Place this file and e2e_verification_test_output.json in the YEVRAH project
root, then run:

    py -m test_repair_existing_draft

The test validates:
    - exactly one repair per verifier issue
    - issue IDs preserved in order
    - block IDs copied exactly
    - current_text copied exactly
    - action is REPLACE or DELETE
    - replacement is valid for that action
    - missing_information copied exactly
"""

import json
import sys
from pathlib import Path

from agent.nodes.repair_agent import repair_draft


BASE_DIR = Path(__file__).resolve().parent
VERIFICATION_PATH = BASE_DIR / "e2e_verification_test_output.json"
OUTPUT_PATH = BASE_DIR / "e2e_repair_test_output.json"


def load_json(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_repair(repair: dict, warning: dict, index: int):
    issue_id = warning.get("issue_id")

    required = {
        "issue_id",
        "block_id",
        "current_text",
        "action",
        "replacement",
        "missing_information",
    }
    missing = required - set(repair)
    if missing:
        raise AssertionError(
            f"Repair #{index} ({issue_id}) missing fields: {sorted(missing)}"
        )

    if repair["issue_id"] != warning.get("issue_id"):
        raise AssertionError(
            f"{issue_id}: issue_id does not match verifier"
        )

    if repair["block_id"] != warning.get("block_id"):
        raise AssertionError(
            f"{issue_id}: block_id does not match verifier"
        )

    if repair["current_text"] != warning.get("current_text"):
        raise AssertionError(
            f"{issue_id}: current_text does not match verifier exactly"
        )

    action = repair["action"]
    if action not in {"REPLACE", "DELETE"}:
        raise AssertionError(f"{issue_id}: invalid action {action!r}")

    replacement = repair["replacement"]
    if action == "REPLACE":
        if not isinstance(replacement, str) or not replacement.strip():
            raise AssertionError(
                f"{issue_id}: REPLACE requires non-empty replacement"
            )
    elif replacement != "":
        raise AssertionError(
            f"{issue_id}: DELETE requires empty replacement"
        )

    if repair["missing_information"] != warning.get("missing_information"):
        raise AssertionError(
            f"{issue_id}: missing_information does not match verifier exactly"
        )

    return repair


def main():
    print("=" * 70)
    print("  YEVRAH — Repair Agent Test (Verifier Output Only)")
    print("=" * 70)

    verification_output = load_json(VERIFICATION_PATH)
    warnings = verification_output.get("warnings", [])

    if not isinstance(warnings, list):
        raise ValueError("Verifier output 'warnings' must be a list")

    print(f"\nVerifier output : {VERIFICATION_PATH.name}")
    print(f"Verifier issues : {len(warnings)}")
    print("Repair input    : verification_warnings ONLY")
    print("Draft supplied  : NO")
    print("Case facts supplied: NO")

    state = {
        "verification_warnings": warnings,
        "repair_patches": [],
    }

    print("\nRunning Repair Agent...\n")
    result_state = repair_draft(state)
    repairs = result_state.get("repair_patches", [])

    print(f"Repair Agent returned {len(repairs)} repair(s).\n")

    expected_ids = [warning.get("issue_id") for warning in warnings]
    returned_ids = [repair.get("issue_id") for repair in repairs]

    if len(repairs) != len(warnings):
        raise AssertionError(
            f"Expected {len(warnings)} repairs, got {len(repairs)}"
        )

    if returned_ids != expected_ids:
        raise AssertionError(
            "Repair issue order mismatch. "
            f"Expected {expected_ids}, got {returned_ids}"
        )

    normalized = []

    for index, (repair, warning) in enumerate(
        zip(repairs, warnings),
        start=1,
    ):
        item = validate_repair(repair, warning, index)
        normalized.append(item)

        print(f"{item['issue_id']} [{item['action']}]")
        print(f"  block_id:            {item['block_id']}")
        print(f"  current_text:        {item['current_text']}")
        print(f"  replacement:         {item['replacement']}")

        missing_info = item.get("missing_information")
        if missing_info:
            print(f"  missing_info.type:   {missing_info['type']}")
            print(f"  missing_info.detail: {missing_info['description']}")
        else:
            print("  missing_info:        None")
        print()

    output = {
        "verification_file": str(VERIFICATION_PATH),
        "verification_issue_count": len(warnings),
        "repair_count": len(repairs),
        "passed": True,
        "repairs": normalized,
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"Saved: {OUTPUT_PATH}")
    print("\nPASS — Repair Agent contract is ready for Python Patch Engine integration.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"\nFAILED: {exc}")
        sys.exit(1)
