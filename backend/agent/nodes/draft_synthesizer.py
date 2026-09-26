import json
import re

from agent.state import draft_state
from ai.llm import generate_response
from rag.retriever import retrieve_chunks
from rag.prompt_builder import build_prompt


EVIDENCE_LIMIT_PER_SECTION = 4


def _resolve_case_id(state: draft_state):
    metadata = state.get("metadata") or {}
    case_id = metadata.get("case_id")
    if case_id is not None:
        return case_id
    return state.get("case_id")


def gather_section_evidence(state: draft_state) -> list[dict]:
    case_id = _resolve_case_id(state)
    sections = state.get("document_plan", {}).get("sections", [])
    evidence = []
    seen = set()

    for section in sections:
        query = section.get("evidence_query")
        if not query:
            continue

        payloads = retrieve_chunks(
            query=query,
            case_id=case_id,
            limit=EVIDENCE_LIMIT_PER_SECTION,
        )

        for payload in payloads:
            key = (payload.get("source"), payload.get("text"))
            if key in seen:
                continue
            seen.add(key)
            item = dict(payload)
            item["section"] = section.get("name")
            evidence.append(item)

    return evidence


def _structure_contract(template_structure: dict) -> str:
    return json.dumps(template_structure, indent=2, ensure_ascii=False)


def _build_synthesis_prompt(
    state: draft_state,
    retrieved_knowledge: list[dict],
) -> str:
    template_structure = state.get("template_structure") or {}
    case_facts = state.get("case_facts") or {}
    custom_prompt = state.get("custom_prompt", "")

    # Reuse the project's structure-aware prompt builder. The builder expects
    # a template_markdown argument, so pass the structure-only text.
    structure_text = _structure_contract(template_structure)
    base = build_prompt(
        case_facts=case_facts,
        template_markdown=structure_text,
        retrieved_payloads=retrieved_knowledge,
        custom_prompt=custom_prompt,
    )

    document_type = getattr(state.get("template"), "document_type", None)
    structure = structure_text

    return f"""
YEVRAH DRAFT SYNTHESIZER

Create the final legal document for the PRESENT CASE.

DOCUMENT TYPE:
{document_type or 'Use the template record document type.'}

STRUCTURE-ONLY CONTRACT:
The structure below is the ONLY template information. It contains no source
paragraphs and no source wording.

{structure}

MANDATORY EXECUTION RULES:
1. Follow the structural block order exactly.
2. Generate ALL wording fresh for the present case.
3. Use CASE FACTS as the factual source of truth.
4. Use retrieved RAG only for drafting language, legal principles, statutes,
   precedents, and relevant case law.
5. Never treat GLOBAL RAG material as present-case facts.
6. Do not invent facts, parties, dates, amounts, allegations, contracts,
   evidence, procedural history, or legal propositions.
7. Include the structural elements represented by the template blocks,
   including lists/tables/verification/signature blocks where applicable.
8. Do not create placeholders from the old template system. When a required
   fact is genuinely unavailable, write [INFORMATION REQUIRED].
9. Return ONLY the final Markdown legal document.

{base}
"""


def synthesize_draft(state: draft_state) -> draft_state:
    if not state.get("template_structure"):
        raise ValueError("Draft Synthesizer requires template_structure")
    if not state.get("case_facts"):
        raise ValueError("Draft Synthesizer requires case_facts")
    if not state.get("document_plan", {}).get("sections"):
        raise ValueError("Draft Synthesizer requires document_plan sections")

    retrieved_knowledge = gather_section_evidence(state)
    prompt = _build_synthesis_prompt(state, retrieved_knowledge)
    draft_text = generate_response(prompt)

    if not draft_text:
        raise ValueError("Draft Synthesizer produced no draft")

    return {
        **state,
        "retrieved_knowledge": retrieved_knowledge,
        "draft": draft_text.strip(),
        "status": "draft_synthesized",
    }
