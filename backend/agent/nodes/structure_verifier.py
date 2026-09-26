import re

from agent.state import draft_state


def _count_markdown_tables(text: str) -> int:
    return sum(
        1
        for line in (text or "").splitlines()
        if re.search(r"\|\s*:?-{3,}:?\s*(\||$)", line)
    )


def _count_numbered_items(text: str) -> int:
    return sum(1 for line in (text or "").splitlines() if re.match(r"^\s*\d+[.)]\s+", line))


def _contains_any(text: str, phrases: tuple[str, ...]) -> bool:
    low = (text or "").lower()
    return any(p in low for p in phrases)


def verify_structure(state: draft_state) -> draft_state:
    structure = state.get("template_structure") or {}
    blocks = structure.get("blocks") or []
    draft = state.get("draft") or ""
    warnings: list[str] = []

    expected_tables = sum(1 for b in blocks if b.get("type") == "table")
    actual_tables = _count_markdown_tables(draft)
    if actual_tables < expected_tables:
        warnings.append(
            f"Template structure contains {expected_tables} table(s), draft contains {actual_tables}."
        )

    ordered_lists = [b for b in blocks if b.get("type") == "ordered_list"]
    if ordered_lists and _count_numbered_items(draft) == 0:
        warnings.append("Template structure contains an ordered list, but draft contains no numbered list.")

    if any(b.get("type") == "verification" for b in blocks):
        if not _contains_any(draft, ("verification", "verified")):
            warnings.append("Template structure contains a verification block, but no verification language was detected.")

    if any(b.get("type") == "signature" for b in blocks):
        if not _contains_any(draft, ("deponent", "signature", "advocate", "authorized signatory")):
            warnings.append("Template structure contains a signature block, but no signature/deponent language was detected.")

    document_type = getattr(state.get("template"), "document_type", None)
    if document_type:
        title_hint = document_type.lower()
        key_terms = [w for w in re.findall(r"[a-z]+", title_hint) if len(w) >= 5]
        if key_terms and not any(term in draft.lower() for term in key_terms[:2]):
            warnings.append(
                f"Draft may not clearly reflect the template document type: {document_type}."
            )

    return {
        **state,
        "structural_warnings": warnings,
        "status": "structure_verified" if not warnings else "structure_review",
    }
