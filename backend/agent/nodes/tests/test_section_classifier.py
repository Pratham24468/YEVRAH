from agent.state import draft_state
from ai.llm import generate_json


def build_classifier_prompt(
    parameterized_template: str,
    available_categories: list,
) -> str:
    categories_text = ", ".join(available_categories)

    return f"""
You are YEVRAH's Section Classifier.

You are given a PARAMETERIZED LEGAL TEMPLATE.

Your job is NOT to draft anything. Your job is to plan the draft.

Identify the distinct legal/logical sections the template is built from
(for example: cause title, deponent identification, purchase/contract
formation, payment history, default, notices/communications, legal issue,
relief sought, verification). Use the template's own numbering as a guide,
but group related paragraphs into one logical section where that makes
sense. Do not fabricate sections the template does not support.

For EACH section, determine:

- a short section name
- which of the template's placeholders (e.g. [PRINCIPAL_AMOUNT]) belong to it
  — copy these EXACTLY as they appear in the template, including brackets
- which categories of case facts feed it. Choose ONLY from this list:
  {categories_text}
- a short, specific search query (5-12 words) that would retrieve the most
  useful supporting evidence or Indian drafting knowledge for THIS section
  specifically — not the whole document

Do not invent placeholders that are not in the template.
Do not invent categories outside the list above.

Return ONLY valid JSON in this exact structure:

{{
  "sections": [
    {{
      "id": "section_1",
      "name": "<short section name>",
      "placeholders": ["[PLACEHOLDER_A]", "[PLACEHOLDER_B]"],
      "case_fact_categories": ["financials", "defaults"],
      "evidence_query": "<short search query for this section>"
    }}
  ]
}}

PARAMETERIZED TEMPLATE:

{parameterized_template}
"""


def classify_sections(state: draft_state) -> draft_state:
    parameterized_template = state.get("parameterized_template")
    case_facts = state.get("case_facts")

    if not parameterized_template:
        raise ValueError(
            "Section Classifier requires a parameterized_template"
        )

    if not case_facts:
        raise ValueError("Section Classifier requires case_facts")

    # Pass only the category KEYS that have values, not the full JSON.
    # The Classifier is a planner — it maps template sections to
    # fact categories. It doesn't need the actual amounts, names, or
    # dates — those belong to the Synthesizer. This also keeps the
    # prompt well within Groq's 8000 TPM limit.
    available_categories = [k for k, v in case_facts.items() if v]

    prompt = build_classifier_prompt(
        parameterized_template,
        available_categories,
    )

    # fast=True is now correct — prompt is small (template + category
    # list only). The heavy Groq model was only needed when passing
    # full case_facts JSON, which caused the 413 error.
    plan = generate_json(prompt, heavy=False)

    sections = plan.get("sections", [])

    if not sections:
        raise ValueError("Section Classifier returned no sections")

    return {
        **state,
        "document_plan": {"sections": sections},
        "status": "sections_classified",
    }