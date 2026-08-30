from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from database import get_db
from services.template_service import create_template_from_file, get_all_templates, delete_template


router = APIRouter()


@router.post("/templates")
def create_template(
    file: UploadFile = File(...),
    name: str = Form(...),
    document_type: str = Form(...),
    db: Session = Depends(get_db),
):
    return create_template_from_file(
        file=file,
        name=name,
        document_type=document_type,
        db=db,
    )

@router.get("/templates")
def get_templates(db: Session = Depends(get_db)):
    return get_all_templates(db)

@router.delete("/templates/{template_id}")
def delete_templates(template_id: int, db: Session = Depends(get_db)):
    return delete_template(template_id, db)
    