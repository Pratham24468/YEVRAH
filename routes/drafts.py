from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas.draft_schema import DraftCreate
from services import draft_service
from services.export_service import markdown_to_docx
from fastapi.responses import FileResponse


router = APIRouter()

@router.post("/drafts")
def create_draft(draft: DraftCreate, db: Session = Depends(get_db)):
    result = draft_service.create_draft(draft, db)
    return result

@router.get("/drafts")
def view_drafts(db: Session = Depends(get_db)):
    result = draft_service.get_all_drafts(db)
    return result

@router.get("/drafts/{draft_id}")
def view_draft(draft_id: int, db: Session = Depends(get_db)):
    result = draft_service.view_draft(draft_id, db)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    return result

@router.delete("/drafts/{draft_id}")
def delete_draft(draft_id: int, db: Session = Depends(get_db)):
    result = draft_service.delete_draft(draft_id, db)
    if result is True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Draft not found"
        )
    return result

@router.get("/draft/{draft_id}/export")
def export(draft_id: int, db: Session = Depends(get_db)):

    draft = draft_service.view_draft(draft_id, db)
    if draft is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Draft not found"
            )
    draft.generated_text

    with open("temp.md", "w", encoding="utf-8") as f:
        f.write(draft.generated_text)

    markdown_to_docx(
        "temp.md",
        f"generated/draft_{draft_id}.docx"
    )

    return FileResponse(
        f"generated/draft_{draft_id}.docx",
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        filename=f"draft_{draft_id}.docx"
    )