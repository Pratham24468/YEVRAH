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

    if not prompt_record:
        raise ValueError("Prompt not found")

    query = (
        case.title +
        " " +
        case.defendant +
        " " +
        case.facts
    )

    payloads = retrieve_chunks(query)

    prompt = build_prompt(
        case,
        template,
        payloads,
        prompt_record.content
    )

    draft_text = generate_response(prompt)

    draft = DraftCreate(
        case_id=case_id,
        document_type=template.name,
        generated_text=draft_text,
    )

    saved_draft = create_draft(draft, db)

    return saved_draft