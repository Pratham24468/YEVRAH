from services.case_service import get_case_by_id
from services.template_service import get_template_by_id
from rag.retriever import retrieve_chunks
from rag.prompt_builder import build_prompt
from ai.llm import generate_response
from services.draft_service import create_draft
from sqlalchemy.orm import Session
from schemas.draft_schema import DraftCreate
from services.prompt_service import view_prompt


def generate_draft(case_id, template_id, prompt_id, db: Session):
    case = get_case_by_id(case_id, db)
    template = get_template_by_id(template_id, db)
    prompt_record = view_prompt(prompt_id, db)

    if not case:
        raise ValueError("Case not found")

    if not template:
        raise ValueError("Template not found")

    if not prompt_record:
        raise ValueError("Prompt not found")

    # The case remains the source of truth for facts.
    query = " ".join(
        str(value)
        for value in [
            case.title,
            case.plaintiff,
            case.defendant,
            case.facts,
            template.name,
        ]
        if value
    )

    # Retrieve Indian drafting/legal knowledge using the metadata now
    # attached to uploaded knowledge. Case-specific material is isolated
    # with case_id; general firm knowledge is retrieved by the other filters.
    knowledge_types = [
        "drafting_style",
        "precedent",
        "legal_principle",
        "statute",
        "case_law",
    ]

    payloads = retrieve_chunks(
        query=query,
        case_id=case_id,
        knowledge_types=knowledge_types,
        document_type=template.name,
        jurisdiction="india",
        limit=8,
    )

    prompt = build_prompt(
        case_details=case,
        template=template,
        retrieved_payloads=payloads,
        custom_prompt=prompt_record.content,
    )

    draft_text = generate_response(prompt)

    draft = DraftCreate(
        case_id=case_id,
        document_type=template.name,
        generated_text=draft_text,
    )

    return create_draft(draft, db)
