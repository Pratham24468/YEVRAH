import json

from agent.state import draft_state
from ai.llm import generate_json
from ai.schemas.template_blueprint import TEMPLATE_BLUEPRINT_SCHEMA


def build_merger_prompt(blueprint_chunks: list[dict]) -> str:
    return f"""
You are merging multiple independent analyses of the same legal
document template.

Produce one canonical template blueprint.

Rules:

1. Combine sections representing the same substantive content.
2. Preserve important information from all analyses.
3. Remove duplicate or redundant sections.
4. Resolve conflicts using the representation best supported by
   the source analyses.
5. Establish a coherent document order.
6. Update dependencies to match the final section ordering.
7. Preserve important numbering, heading, paragraph, closing,
   and formatting conventions.
8. Do not invent legal requirements or factual information.
9. The template may contain example or instance-specific names,
dates, amounts, locations, case numbers, contract numbers,
invoice numbers, GSTINs, legal citations, quantities, or other
factual values. These are examples from the source template and
MUST NOT be preserved as factual requirements in the canonical
blueprint.

10. Extract the structural role of instance-specific information,
not the information itself.

11. Convert concrete values into abstract semantic fields.
For example:
- "15% p.a." → "Applicable interest rate"
- "500 bales" → "Quantity of goods"
- "Rs.1,02,68,072" → "Principal amount"
- "Mumbai, Aurangabad" → "Delivery locations"
- "2022" → "Year of proceeding"
- a person's name → "Deponent's full name"

12. Do not treat facts appearing in the template as facts that
must appear in every future document.

13. The canonical blueprint must describe HOW the document is
structured and written, not WHAT the particular source case
contained.

Blueprint analyses:

{json.dumps(blueprint_chunks, ensure_ascii=False, indent=2)}
"""


def compact_blueprint_chunks(blueprint_chunks: list[dict]) -> list[dict]:
    compacted = []

    for chunk in blueprint_chunks:
        compact_sections = []

        for section in chunk.get("sections", []):
            compact_sections.append({
                "order": section.get("order"),
                "title": section.get("title"),
                "purpose": section.get("purpose"),
                "section_type": section.get("section_type"),
                "required_information": section.get(
                    "required_information", []
                ),
                "optional_information": section.get(
                    "optional_information", []
                ),
                "depends_on": section.get("depends_on", [])
            })

        compacted.append({
            "sections": compact_sections,
            "numbering_style": chunk.get(
                "numbering_style", ""
            ),
            "heading_style": chunk.get(
                "heading_style", ""
            ),
            "paragraph_style": chunk.get(
                "paragraph_style", ""
            ),
            "closing_style": chunk.get(
                "closing_style", ""
            ),
            "formatting_rules": chunk.get(
                "formatting_rules", []
            )
        })

    return compacted


def merge_blueprints(blueprint_chunks: list[dict]) -> dict:
    if not blueprint_chunks:
        raise ValueError("No blueprint chunks provided")

    # Extract the actual blueprint from each analyzed chunk.
    raw_blueprints = [
        chunk["blueprint"]
        for chunk in blueprint_chunks
    ]

    # Remove unnecessary wrapper data before sending
    # the analyses to the merger.
    compacted_blueprints = compact_blueprint_chunks(
        raw_blueprints
    )

    prompt = build_merger_prompt(
        compacted_blueprints
    )

    return generate_json(
        prompt,
        TEMPLATE_BLUEPRINT_SCHEMA
    )


def analyze_template(state: draft_state) -> draft_state:
    blueprint_chunks = state.get(
        "template_blueprint", {}
    ).get("chunks", [])

    if not blueprint_chunks:
        raise ValueError(
            "No template blueprint chunks found"
        )

    canonical_blueprint = merge_blueprints(
        blueprint_chunks
    )

    return {
        **state,
        "template_blueprint": canonical_blueprint,
        "status": "template_blueprint_merged",
    }