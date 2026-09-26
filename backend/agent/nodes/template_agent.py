import json

from agent.state import draft_state
from ai.llm import generate_json


ALLOWED_BLOCK_TYPES = {
    "court_header",
    "case_caption",
    "party_block",
    "versus",
    "document_title",
    "section",
    "table",
    "ordered_list",
    "unordered_list",
    "verification",
    "signature",
    "date_place",
    "other",
}


def build_template_prompt(markdown_content: str) -> str:
    return f"""
You are YEVRAH's Template Structure Agent.

YOUR ONLY JOB:
Extract the STRUCTURE of the supplied legal document.

DO NOT extract or reproduce:
- sentences
- paragraphs
- legal wording
- facts
- names
- dates
- amounts
- places
- institutions
- commodities
- clauses
- case citations
- statutory text
- explanations
- section purposes
- placeholders

The source document is only a layout/organization reference.
The downstream system will write ALL wording from the present case and RAG.

Return ONLY valid JSON.

For each structural block, record only:
- order: integer starting at 1
- type: one of the allowed block types below
- level: heading level (1-6) when relevant, otherwise null
- paragraph_count: number of paragraphs in the block when relevant, otherwise 0
- index: sequential index for repeated blocks such as sections/tables/lists, otherwise null
- rows: table row count when type=table, otherwise 0
- columns: table column count when type=table, otherwise 0
- item_count: list item count when type is a list, otherwise 0

Allowed block types:
{sorted(ALLOWED_BLOCK_TYPES)}

IMPORTANT:
- Do not include any source wording in any JSON value.
- Do not include headings from the source.
- Do not create placeholders.
- Do not summarize what a section says.
- A section is represented only as {{"type": "section", ...}}.
- A table is represented only by its structural dimensions.
- If several consecutive paragraphs form one logical section, represent them as
  one section block and record its paragraph_count.
- Preserve the exact order of structural blocks.
- Preserve repeated sections/tables/lists as separate blocks.

Required JSON shape:
{{
  "blocks": [
    {{
      "order": 1,
      "type": "court_header",
      "level": null,
      "paragraph_count": 1,
      "index": null,
      "rows": 0,
      "columns": 0,
      "item_count": 0
    }}
  ]
}}

REFERENCE DOCUMENT MARKDOWN:
{markdown_content}
"""


def _validate_structure(structure: dict) -> dict:
    if not isinstance(structure, dict):
        raise ValueError("Template Agent returned non-object JSON")

    blocks = structure.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise ValueError("Template Agent returned no structural blocks")

    normalized = []
    orders = []
    required_keys = {"order", "type", "level", "paragraph_count", "index", "rows", "columns", "item_count"}

    for block in blocks:
        if not isinstance(block, dict):
            raise ValueError("Template Agent returned an invalid block")

        if set(block.keys()) != required_keys:
            raise ValueError("Template Agent returned extra or missing block fields")

        block_type = block.get("type")
        if block_type not in ALLOWED_BLOCK_TYPES:
            raise ValueError(f"Template Agent returned invalid block type: {block_type!r}")

        order = block.get("order")
        if not isinstance(order, int) or order < 1:
            raise ValueError("Every template block must have a positive integer order")

        orders.append(order)

        normalized.append({
            "order": order,
            "type": block_type,
            "level": block.get("level") if isinstance(block.get("level"), int) else None,
            "paragraph_count": block.get("paragraph_count") if isinstance(block.get("paragraph_count"), int) else 0,
            "index": block.get("index") if isinstance(block.get("index"), int) else None,
            "rows": block.get("rows") if isinstance(block.get("rows"), int) else 0,
            "columns": block.get("columns") if isinstance(block.get("columns"), int) else 0,
            "item_count": block.get("item_count") if isinstance(block.get("item_count"), int) else 0,
        })

    if sorted(orders) != list(range(1, len(orders) + 1)):
        raise ValueError("Template block orders must be contiguous starting at 1")

    normalized.sort(key=lambda item: item["order"])
    return {"blocks": normalized}


def compile_template(markdown_content: str, document_type: str | None = None) -> tuple[dict, str]:
    if not markdown_content:
        raise ValueError("Template has no markdown_content")

    prompt = build_template_prompt(markdown_content)
    result = generate_json(prompt, heavy=False)
    structure = _validate_structure(result)

    lines = ["TEMPLATE_STRUCTURE", f"DOCUMENT_TYPE: {document_type or '[DOCUMENT_TYPE]'}", "BLOCKS:"]
    for block in structure["blocks"]:
        line = f"{block['order']:02d}. {block['type']}"
        if block["level"] is not None:
            line += f" level={block['level']}"
        if block["paragraph_count"]:
            line += f" paragraphs={block['paragraph_count']}"
        if block["index"] is not None:
            line += f" index={block['index']}"
        if block["type"] == "table":
            line += f" rows={block['rows']} columns={block['columns']}"
        if block["type"] in {"ordered_list", "unordered_list"}:
            line += f" items={block['item_count']}"
        lines.append(line)

    return structure, "\n".join(lines)


def analyze_template(state: draft_state) -> draft_state:
    template = state["template"]
    markdown_content = getattr(template, "markdown_content", None)

    if not markdown_content:
        raise ValueError("Template has no markdown_content")

    document_type = getattr(template, "document_type", None)
    structure, structure_text = compile_template(markdown_content, document_type=document_type)

    return {
        **state,
        "template_structure": structure,
        # Kept for downstream compatibility. It now contains ONLY structure.
        "parameterized_template": structure_text,
        "status_log": [*(state.get("status_log") or []), "template_structure_extracted"],
        "status": "template_structure_extracted",
    }
