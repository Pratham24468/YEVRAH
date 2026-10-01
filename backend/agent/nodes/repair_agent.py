import json

from agent.state import draft_state
from ai.llm import generate_json


def build_repair_prompt(verification_warnings: list[dict]) -> str:
    """Build a one-call information-required patch prompt from verifier output only."""

    warnings_text = json.dumps(
        verification_warnings,
        indent=2,
        ensure_ascii=False,
    )

    return f"""
You are YEVRAH's Repair Agent.

Your ONLY job is to convert each Fact Verifier issue into a precise
INFORMATION REQUIRED replacement.

The verifier has already determined:
- what is wrong
- exactly where it occurs
- the exact text that must be replaced
- what information is missing, when applicable

You receive ONLY the verifier issue list.

IMPORTANT:
- Do NOT receive or request the full draft.
- Do NOT receive or request case facts.
- Do NOT receive or request RAG knowledge.
- Do NOT rewrite the document.
- Do NOT invent facts.
- Do NOT resolve the legal/factual issue yourself.
- Do NOT preserve the unsupported assertion.
- Do NOT add new factual claims.
- Do NOT change the verifier's issue, location, or missing-information data.

For every verifier issue, replace the supplied current_text with a concise,
lawyer-visible information-required marker.

The replacement must be:

[INFORMATION REQUIRED: <specific missing information>]

Use the verifier's missing_information.description exactly when it exists.

When missing_information is null, create an information-required marker from
the verifier's issue that tells the lawyer what needs factual review or
confirmation. Do not invent new facts.

The lawyer will receive the verifier output separately, including:
- issue_id
- block_id
- current_text
- issue
- severity
- missing_information

Therefore, the replacement itself does NOT need to explain the entire problem.
It only needs to mark the exact location where information/review is required.

OUTPUT RULES:
1. Return exactly one repair for every verifier issue.
2. Preserve verifier order.
3. Copy issue_id exactly.
4. Copy block_id exactly.
5. Copy current_text exactly.
6. Copy missing_information exactly.
7. Use action = "REPLACE".
8. replacement must contain ONLY the information-required marker.
9. Keep the replacement concise and directly substitutable.
10. Return JSON only.

Return ONLY valid JSON in this exact shape:

{{
  "repairs": [
    {{
      "issue_id": "F-001",
      "block_id": "paragraph_04",
      "current_text": "<exact verifier current_text>",
      "action": "REPLACE",
      "replacement": "[INFORMATION REQUIRED: <specific missing information>]",
      "missing_information": {{
        "type": "<verifier type>",
        "description": "<verifier description>"
      }}
    }}
  ]
}}

If missing_information is null, use:

"missing_information": null

and make the replacement:

[INFORMATION REQUIRED: <concise factual review/confirmation required based only on the verifier issue>]

VERIFIER ISSUES:

{warnings_text}
"""


def repair_draft(state: draft_state) -> draft_state:
    """Generate one repair patch set from verifier output in a single LLM call."""

    verification_warnings = state.get("verification_warnings", [])

    if verification_warnings is None:
        verification_warnings = []

    if not isinstance(verification_warnings, list):
        raise ValueError(
            "Repair Agent requires verification_warnings to be a list"
        )

    if not verification_warnings:
        return {
            **state,
            "repair_patches": [],
            "status": "repairs_generated",
        }

    prompt = build_repair_prompt(verification_warnings)
    result = generate_json(prompt, heavy=True)
    repairs = result.get("repairs", [])

    if not isinstance(repairs, list):
        raise ValueError("Repair Agent returned invalid repairs list")

    expected_ids = [warning.get("issue_id") for warning in verification_warnings]
    returned_ids = [repair.get("issue_id") for repair in repairs]

    if len(repairs) != len(verification_warnings):
        raise ValueError(
            "Repair Agent must return exactly one repair per verifier issue: "
            f"expected {len(verification_warnings)}, got {len(repairs)}"
        )

    if returned_ids != expected_ids:
        raise ValueError(
            "Repair Agent returned repairs out of order or with mismatched "
            f"issue IDs. Expected {expected_ids}, got {returned_ids}"
        )

    for index, repair in enumerate(repairs):
        warning = verification_warnings[index]
        issue_id = repair.get("issue_id")

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
            raise ValueError(
                f"{issue_id}: missing required repair fields: {sorted(missing)}"
            )

        if repair["block_id"] != warning.get("block_id"):
            raise ValueError(
                f"{issue_id}: block_id does not match verifier"
            )

        if repair["current_text"] != warning.get("current_text"):
            raise ValueError(
                f"{issue_id}: current_text does not match verifier exactly"
            )

        action = repair["action"]
        if action != "REPLACE":
            raise ValueError(
                f"{issue_id}: action must be REPLACE"
            )

        replacement = repair["replacement"]
        if not isinstance(replacement, str) or not replacement.strip():
            raise ValueError(
                f"{issue_id}: replacement must be non-empty"
            )

        stripped = replacement.strip()
        if not stripped.startswith("[INFORMATION REQUIRED:") or not stripped.endswith("]"):
            raise ValueError(
                f"{issue_id}: replacement must be an INFORMATION REQUIRED marker"
            )

        verifier_missing = warning.get("missing_information")
        if repair["missing_information"] != verifier_missing:
            raise ValueError(
                f"{issue_id}: missing_information does not match verifier exactly"
            )

    return {
        **state,
        "repair_patches": repairs,
        "status": "repairs_generated",
    }
