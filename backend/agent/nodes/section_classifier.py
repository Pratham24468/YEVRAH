import json

from agent.state import draft_state
from ai.llm import generate_json


def build_classifier_prompt(template_structure: dict, case_facts: dict) -> str:
    structure_text = json.dumps(template_structure, indent=2, ensure_ascii=False)
    case_text = json.dumps(case_facts, indent=2, ensure_ascii=False)

    return f"""
You are YEVRAH's Section Classifier.

The TEMPLATE is STRUCTURE ONLY. It contains no reusable legal wording and no
case-specific content. Do not invent text from a source template.

Your job is to map structural blocks to logical drafting sections for the
PRESENT CASE.

For each section, return:
- id
- name: a short generated section label
- block_orders: the template block orders that belong to this section
- case_fact_categories: choose only from parties, relationships, chronology,
  agreements, financials, defaults, communications, legal_issues, demands,
  relief
- evidence_query: a focused 5-12 word search query for Indian legal drafting
  knowledge or supporting legal authority

Do not invent structural blocks.
Do not add sections that the template does not structurally contain.
Do not reproduce any source-template wording because none is needed.

Return ONLY valid JSON:
{{
  "sections": [
    {{
      "id": "section_1",
      "name": "<generated label>",
      "block_orders": [5],
      "case_fact_categories": ["parties"],
      "evidence_query": "Indian affidavit party identification drafting"
    }}
  ]
}}

TEMPLATE STRUCTURE:
{structure_text}

PRESENT CASE FACTS:
{case_text}
"""


def classify_sections(state: draft_state) -> draft_state:
    template_structure = state.get("template_structure")
    case_facts = state.get("case_facts")

    if not template_structure:
        raise ValueError("Section Classifier requires template_structure")
    if not case_facts:
        raise ValueError("Section Classifier requires case_facts")

    prompt = build_classifier_prompt(template_structure, case_facts)
    plan = generate_json(prompt, heavy=False)

    sections = plan.get("sections", [])
    if not sections:
        raise ValueError("Section Classifier returned no sections")

    return {
        **state,
        "document_plan": {"sections": sections},
        "status": "sections_classified",
    }
