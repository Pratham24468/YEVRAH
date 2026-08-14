from fastapi import APIRouter, Depends
from services.generate_service import generate_draft
from sqlalchemy.orm import Session
from database import get_db

router = APIRouter()


@router.post("/generate")
def generate(
    case_id: int,
    template_id: int,
    prompt_id: int,
    db: Session = Depends(get_db)
):
    draft = generate_draft(
        case_id,
        template_id,
        prompt_id,
        db
    )

    return {
        "draft": draft
    }