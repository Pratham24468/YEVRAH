import re

from agent.state import draft_state


class TemplateMismatchError(ValueError):
    """Raised when the structure-only template contract is invalid."""
    pass


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


def _extract_placeholders(template_markdown: str) -> list[str]:
    """Legacy compatibility helper used by structure_verifier.py."""
    return sorted(set(re.findall(r"\[([A-Z0-9_]+)\]", template_markdown or "")))


def check_template_match(state: draft_state) -> draft_state:
    """Validate the STRUCTURE-only template contract."""

    structure = state.get("template_structure")
    if not isinstance(structure, dict):
        raise TemplateMismatchError(
            "Template Structure Guard requires template_structure"
        )

    blocks = structure.get("blocks")
    if not isinstance(blocks, list) or not blocks:
        raise TemplateMismatchError(
            "Template Structure Guard found no structural blocks"
        )

    expected_orders = list(range(1, len(blocks) + 1))
    actual_orders = [block.get("order") for block in blocks]

    if actual_orders != expected_orders:
        raise TemplateMismatchError(
            f"Template structure order is invalid: {actual_orders}"
        )

    for block in blocks:
        if block.get("type") not in ALLOWED_BLOCK_TYPES:
            raise TemplateMismatchError(
                f"Invalid template block type: {block.get('type')!r}"
            )

    template = state.get("template")
    document_type = getattr(template, "document_type", None) if template else None
    if not document_type:
        raise TemplateMismatchError(
            "Template Structure Guard requires template.document_type"
        )

    return {
        **state,
        "review": {
            **(state.get("review") or {}),
            "template_document_type": document_type,
            "template_block_count": len(blocks),
        },
        "status": "template_structure_confirmed",
    }
