import json

from agent.state import draft_state
from ai.llm import generate_json


def build_fact_verifier_prompt(case_facts: dict, draft: str) -> str:
    case_facts_text = json.dumps(case_facts, indent=2, ensure_ascii=False)

    return f"""
You are YEVRAH's Verifier.

You are given the STRUCTURED CASE FACTS (the source of truth) and the
FINAL DRAFT generated from them.

Your job is to identify factual statements in the draft that are
unsupported, contradictory, or require information that is missing
from the case facts.

For EVERY issue, identify the exact place in the draft where the issue
occurs. The later Repair Agent will use your output to repair that exact
text.

Find any factual claim in the draft — a monetary amount, a date, a
percentage or interest rate, a party name, a quantity — that does NOT
match what is stated in the case facts, or that appears in the draft
with no support anywhere in the case facts.

Do NOT flag:
- Placeholder text like [INFORMATION REQUIRED: ...] — these are
  correctly-flagged gaps, not errors
- Standard legal boilerplate, statute names, or procedural references
  that are not case-specific facts
- Reasonable legal characterizations built on the facts (e.g.
  describing a partial payment as "admission of liability" is a legal
  characterization, not a fact to verify)

DO flag:
- Any amount, date, rate, quantity, or party name in the draft that
  contradicts or is absent from the case facts
- Any specific factual claim presented as established fact but not
  supported by the case facts
- Invented mode of service, jurisdictional basis, address, receipt,
  acceptance, contract terms, procedural history, or other case facts

LOCATION RULES:
- "block_id" must identify the smallest logical draft block containing
  the problem.
- Use the draft's visible structure where possible, such as:
  "court_header",
  "case_caption",
  "section_01",
  "section_01.paragraph_02",
  "section_04.paragraph_03",
  "ordered_list_01.item_07",
  "table_01.row_03",
  "signature",
  "verification".
- If the draft uses numbered paragraphs, use the paragraph number in
  the block_id when possible, e.g. "paragraph_07".
- "current_text" MUST be copied EXACTLY from the draft. Do not rewrite,
  shorten, summarize, normalize, or paraphrase it.
- Keep current_text to the smallest contiguous span that fully
  contains the unsupported or contradictory claim and can be replaced
  safely by the Repair Agent.
- "claim" should contain the same exact text as current_text for
  backward compatibility.

MISSING INFORMATION RULES:
- When the problem exists because required case information is absent,
  explicitly state what information is missing.
- "missing_information.type" must be a short machine-readable category.
- "missing_information.description" must precisely describe the
  information a lawyer/user must provide.
- If no additional information is needed and the issue is purely a
  contradiction or wording error, return null for missing_information.
- Never invent the missing information.

SEVERITY RULES:
- Use "high" for a material factual assertion, amount, date, party,
  jurisdictional fact, contractual term, receipt/acceptance assertion,
  or other fact that could materially affect the legal document.
- Use "medium" for a smaller factual mismatch that still needs repair.

Return ONLY valid JSON in this exact structure:

{{
  "verified": true,
  "warnings": [
    {{
      "issue_id": "F-001",
      "block_id": "section_04.paragraph_02",
      "current_text": "<exact contiguous text copied from the draft>",
      "claim": "<same exact text as current_text>",
      "issue": "<why this does not match or is unsupported by the case facts>",
      "severity": "high",
      "missing_information": {{
        "type": "<short machine-readable category>",
        "description": "<exact information that is missing>"
      }}
    }}
  ]
}}

Use sequential issue IDs beginning at F-001.

If nothing is wrong, return "verified": true and an empty warnings list.

STRUCTURED CASE FACTS:

{case_facts_text}

FINAL DRAFT:

{draft}
"""


def verify_facts(state: draft_state) -> draft_state:
    case_facts = state.get("case_facts")
    draft = state.get("draft")

    if not case_facts:
        raise ValueError("Verifier requires case_facts")

    if not draft:
        raise ValueError("Verifier requires a draft")

    prompt = build_fact_verifier_prompt(case_facts, draft)

    result = generate_json(prompt, heavy=True)

    warnings = result.get("warnings", [])

    return {
        **state,
        "verification_warnings": warnings,
        "status": "facts_verified",
    }
