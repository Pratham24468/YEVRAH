import json

from agent.state import draft_state
from ai.llm import generate_json


# These are the only case-fact categories the Section Classifier
# is allowed to reference.
ALLOWED_CASE_FACT_CATEGORIES = [
    "parties",
    "relationships",
    "chronology",
    "agreements",
    "financials",
    "defaults",
    "communications",
    "legal_issues",
    "demands",
    "relief",
]


def build_case_fact_availability(case_facts: dict) -> dict:
    """
    Build a compact representation of the available case-fact
    categories.

    The Section Classifier does NOT need the full case facts.
    It only needs to know which categories exist so it can
    associate template sections with relevant information.

    The complete case_facts remain available in state for
    downstream nodes such as the Draft Synthesizer.
    """

    return {
        category: bool(case_facts.get(category))
        for category in ALLOWED_CASE_FACT_CATEGORIES
    }


def build_classifier_prompt(
    parameterized_template: str,
    case_facts: dict,
) -> str:
    """
    Build a compact Section Classifier prompt.

    Important:
    We intentionally do NOT send the complete case-facts JSON
    to the LLM. This prevents large prompts and avoids wasting
    tokens on information the classifier does not need.
    """

    case_fact_availability = build_case_fact_availability(case_facts)

    case_facts_text = json.dumps(
        case_fact_availability,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    return f"""
You are YEVRAH's Section Classifier.

Your task is to create a section-level drafting plan for a legal
document.

You are given:

1. A PARAMETERIZED LEGAL TEMPLATE.
2. A compact map showing which CASE-FACT CATEGORIES are available.

Your job is NOT to draft the document.
Your job is ONLY to analyze the template and create a structured
plan that tells the Draft Synthesizer how the document is organized.

==================================================
SECTION IDENTIFICATION
==================================================

Identify the distinct legal or logical sections represented by
the parameterized template.

Examples include:

- cause title
- court/case information
- party identification
- deponent/affiant identification
- relationship between parties
- agreement or contract formation
- transaction details
- payment obligations
- payment history
- default/non-payment
- notices and communications
- legal issues
- demands
- relief sought
- verification
- signature/exhibit sections

These are examples only.

Use the actual structure of the supplied template.

Do NOT fabricate sections that are not supported by the template.

Use the template's headings, numbering, paragraph structure,
tables, and wording patterns as the primary guide.

Group closely related paragraphs into one logical section when
appropriate.

==================================================
PLACEHOLDERS
==================================================

For every section, identify the placeholders belonging to that
section.

Copy placeholders EXACTLY as they appear in the template.

For example:

[CLAIMANT_NAME]
[RESPONDENT_NAME]
[PRINCIPAL_AMOUNT]
[INTEREST_AMOUNT]
[NOTICE_DATE]

Do NOT:

- rename placeholders
- modify placeholders
- create new placeholders
- remove brackets
- invent placeholders based on case facts

A placeholder belongs to a section only when it actually appears
in that section of the supplied template.

==================================================
CASE FACT CATEGORIES
==================================================

For every section, identify which available case-fact categories
feed that section.

You may ONLY use:

parties
relationships
chronology
agreements
financials
defaults
communications
legal_issues
demands
relief

Only select categories that are relevant to the section.

Do not invent categories.

If a section does not require case facts, return:

"case_fact_categories": []

==================================================
EVIDENCE QUERY
==================================================

For each section that would benefit from supporting evidence,
create a short, specific retrieval query.

The query should:

- be 5-12 words
- be specific to that section
- focus on the information needed for that section
- be useful for retrieving relevant evidence or legal drafting
  knowledge
- NOT be a query for the entire document

For example:

"contract formation agreement terms date"
"outstanding principal amount payment default"
"legal notice demand non-payment"
"interest rate recovery amount"

For purely structural sections such as:

- exhibit references
- signature blocks
- verification formatting
- headings/captions that contain no substantive facts

use:

"evidence_query": null

Do NOT create unnecessary RAG queries.

==================================================
IMPORTANT FACTUAL RULE
==================================================

The classifier must NEVER invent facts.

The availability map only tells you whether a category exists.

Do not infer specific:

- names
- dates
- amounts
- contract numbers
- case numbers
- addresses
- payment periods
- interest rates

Those values will be supplied later by the Draft Synthesizer.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
  "sections": [
    {{
      "id": "section_1",
      "name": "Short Section Name",
      "placeholders": [
        "[PLACEHOLDER_A]",
        "[PLACEHOLDER_B]"
      ],
      "case_fact_categories": [
        "financials",
        "defaults"
      ],
      "evidence_query": "specific evidence query"
    }}
  ]
}}

Every section must contain:

- id
- name
- placeholders
- case_fact_categories
- evidence_query

==================================================
PARAMETERIZED LEGAL TEMPLATE
==================================================

{parameterized_template}

==================================================
AVAILABLE CASE-FACT CATEGORIES
==================================================

{case_facts_text}

Remember:

Analyze the supplied template.
Do not draft.
Do not invent.
Do not add unsupported sections.
Do not create placeholders that do not exist.
Copy placeholders exactly.
Use null for evidence_query when RAG is unnecessary.

Return ONLY valid JSON.
"""


def validate_section_plan(
    plan: dict,
    parameterized_template: str,
) -> list[dict]:
    """
    Validate and normalize the classifier output before allowing
    it into the YEVRAH state.

    This protects downstream nodes from malformed LLM output.
    """

    if not isinstance(plan, dict):
        raise ValueError(
            "Section Classifier returned an invalid response"
        )

    sections = plan.get("sections")

    if not isinstance(sections, list) or not sections:
        raise ValueError(
            "Section Classifier returned no sections"
        )

    validated_sections = []

    for index, section in enumerate(sections, start=1):

        if not isinstance(section, dict):
            raise ValueError(
                f"Section Classifier returned invalid section at index {index}"
            )

        section_id = section.get("id")
        name = section.get("name")
        placeholders = section.get("placeholders", [])
        categories = section.get("case_fact_categories", [])
        evidence_query = section.get("evidence_query")

        if not section_id:
            raise ValueError(
                f"Section {index} is missing 'id'"
            )

        if not name:
            raise ValueError(
                f"Section {index} is missing 'name'"
            )

        if not isinstance(placeholders, list):
            raise ValueError(
                f"Section {index} has invalid 'placeholders'"
            )

        if not isinstance(categories, list):
            raise ValueError(
                f"Section {index} has invalid 'case_fact_categories'"
            )

        # Validate categories.
        invalid_categories = [
            category
            for category in categories
            if category not in ALLOWED_CASE_FACT_CATEGORIES
        ]

        if invalid_categories:
            raise ValueError(
                f"Section '{name}' contains invalid case-fact "
                f"categories: {invalid_categories}"
            )

        # Validate that every placeholder actually exists
        # somewhere in the parameterized template.
        invalid_placeholders = [
            placeholder
            for placeholder in placeholders
            if placeholder not in parameterized_template
        ]

        if invalid_placeholders:
            raise ValueError(
                f"Section '{name}' contains placeholders that "
                f"do not exist in the parameterized template: "
                f"{invalid_placeholders}"
            )

        # evidence_query may intentionally be null.
        if evidence_query is not None:
            if not isinstance(evidence_query, str):
                raise ValueError(
                    f"Section '{name}' has an invalid evidence_query"
                )

            evidence_query = evidence_query.strip()

            if not evidence_query:
                evidence_query = None

        validated_sections.append(
            {
                "id": str(section_id),
                "name": str(name).strip(),
                "placeholders": placeholders,
                "case_fact_categories": categories,
                "evidence_query": evidence_query,
            }
        )

    return validated_sections


def classify_sections(state: draft_state) -> draft_state:
    """
    YEVRAH Section Classifier node.

    Inputs:
        state["parameterized_template"]
        state["case_facts"]

    Outputs:
        state["document_plan"]["sections"]

    The full case facts remain untouched in state.
    Only a compact category-availability map is sent to the LLM.
    """

    parameterized_template = state.get(
        "parameterized_template"
    )

    case_facts = state.get("case_facts")

    if not parameterized_template:
        raise ValueError(
            "Section Classifier requires a parameterized_template"
        )

    if not case_facts:
        raise ValueError(
            "Section Classifier requires case_facts"
        )

    if not isinstance(case_facts, dict):
        raise ValueError(
            "Section Classifier requires case_facts to be a dictionary"
        )

    # Build prompt using only the information this node actually needs.
    prompt = build_classifier_prompt(
        parameterized_template=parameterized_template,
        case_facts=case_facts,
    )

    # Section planning requires structured JSON.
    # Use the heavy model because this is a reasoning/classification task.
    plan = generate_json(
        prompt,
        heavy=False,
    )

    sections = validate_section_plan(
        plan=plan,
        parameterized_template=parameterized_template,
    )

    return {
        **state,
        "document_plan": {
            "sections": sections,
        },
        "status": "sections_classified",
    }

