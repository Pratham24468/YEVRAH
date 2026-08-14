from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas.template_schema import TemplateCreate
from services import template_service

router = APIRouter()

@router.post("/templates")
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    template_service.create_template(template, db)
    return {
        "message": "Template Created"
    }

@router.get("/templates")
def view_templates(db: Session = Depends(get_db)):
    result = template_service.get_all_templates(db)
    return result

@router.get("/templates/{template_id}")
def get_template(template_id: int, db: Session = Depends(get_db)):
    result = template_service.get_template_by_id(template_id, db)
    if result is True:
        raise HTTPException(
            status_code=404, 
            detail="Template Not Found"
        )
    return result

@router.put("/templates/{template_id}")
def update_template(
    template_id: int,
    template_data: TemplateCreate,
    db: Session = Depends(get_db)
):
    result = template_service.update_template(template_id, template_data, db)
    if result is True:
        raise HTTPException(
            status_code=404, 
            detail="Template Not Found"
        )
    return result

@router.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    result = template_service.delete_template(template_id, db)
    if result is True:
        raise HTTPException(
            status_code=404, 
            detail="Template Not Found"
        )
    return {
        "message": "Template Deleted Successfully"
    }
    
