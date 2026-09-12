from sqlalchemy.orm import Session

from services.case_service import get_case_by_id
from services.template_service import get_template_by_id
from services.prompt_service import view_prompt
from services.draft_service import create_draft

from schemas.draft_schema import DraftCreate

from agent.graph import graph


def generate_draft(
    case_id: int,
    template_id: int,
    prompt_id: int,
    db: Session,
):
    case = get_case_by_id(case_id, db)
    template = get_template_by_id(template_id, db)
    prompt_record = view_prompt(prompt_id, db)

    # get_case_by_id / get_template_by_id return the literal `True`
    # (not None) when the record doesn't exist -- `if not case` would
    # silently pass a boolean through as case_data, since `not True`
    # is False. Check identity, not truthiness.
    if case is True:
        raise ValueError("Case not found")

    if template is True:
        raise ValueError("Template not found")

    if not prompt_record:
        raise ValueError("Prompt not found")

    # ---------------------------------------------------------
    # Build the initial state for the agentic drafting graph
    # ---------------------------------------------------------

    initial_state = {
        "case_data": case,
        "template": template,
        "custom_prompt": prompt_record.content,
        "metadata": {
            "case_id": case_id,
            "template_id": template_id,
            "prompt_id": prompt_id,
        },

        "case_facts": {},
        "template_blueprint": {},
        "parameterized_template": "",

        "document_plan": {},
        "retrieved_knowledge": [],

        "draft": "",
        "review": {},

        "current_section": 0,
        "revision_count": 0,
        "status": "started",
    }

    # ---------------------------------------------------------
    # Run the agentic drafting system
    # ---------------------------------------------------------

    result = graph.invoke(initial_state)

    draft_text = result.get("draft")

    if not draft_text:
        raise ValueError("Agentic drafting system produced no draft")

    # ---------------------------------------------------------
    # Save final draft
    # ---------------------------------------------------------

    draft = DraftCreate(
        case_id=case_id,
        document_type=template.document_type,
        generated_text=draft_text,
    )

    return create_draft(draft, db)
