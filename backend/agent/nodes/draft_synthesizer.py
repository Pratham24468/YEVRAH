from agent.state import draft_state
from ai.llm import generate_response
from rag.retriever import retrieve_chunks
from rag.prompt_builder import build_prompt


EVIDENCE_LIMIT_PER_SECTION = 4


def gather_section_evidence(state: draft_state) -> list[dict]:
    """
    Runs one RAG query per section identified by the Section Classifier,
    scoped to the current case (case-specific documents + global
    knowledge), and tags each retrieved chunk with the section it was
    retrieved for.
    """

    case_id = state.get("metadata", {}).get("case_id")
    sections = state.get("document_plan", {}).get("sections", [])

    evidence = []
    seen_ids = set()

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
            # de-dupe: the same global-knowledge chunk can legitimately
            # satisfy more than one section's query
            dedupe_key = (payload.get("source"), payload.get("text"))
            if dedupe_key in seen_ids:
                continue
            seen_ids.add(dedupe_key)

            tagged = dict(payload)
            tagged["section"] = section.get("name")
            evidence.append(tagged)

    return evidence


def synthesize_draft(state: draft_state) -> draft_state:
    parameterized_template = state.get("parameterized_template")
    case_facts = state.get("case_facts")
    custom_prompt = state.get("custom_prompt", "")

    if not parameterized_template:
        raise ValueError(
            "Draft Synthesizer requires a parameterized_template"
        )

    if not case_facts:
        raise ValueError("Draft Synthesizer requires case_facts")

    retrieved_knowledge = gather_section_evidence(state)

    prompt = build_prompt(
        case_facts=case_facts,
        template_markdown=parameterized_template,
        retrieved_payloads=retrieved_knowledge,
        custom_prompt=custom_prompt,
    )

    draft_text = generate_response(prompt)

    if not draft_text:
        raise ValueError("Draft Synthesizer produced no draft")

    return {
        **state,
        "retrieved_knowledge": retrieved_knowledge,
        "draft": draft_text,
        "status": "draft_synthesized",
    }
