from fastapi import APIRouter, Depends, HTTPException, status
from services import prompt_service
from database import get_db
from sqlalchemy.orm import Session
from schemas.prompt_schema import PromptCreate

router = APIRouter()

@router.post("/prompts")
def create_prompt(prompt: PromptCreate, db: Session = Depends(get_db)):
    prompt_service.create_prompt(prompt, db)
    return {
        "message": "Prompt Created"
    }

@router.get("/prompts")
def view_prompts(db:Session = Depends(get_db)):
    result = prompt_service.get_all_prompts(db)
    return result

@router.get("/prompts/{prompt_id}")
def get_prompt(
    prompt_id: int, 
    db: Session = Depends(get_db)
):
    result = prompt_service.view_prompt(prompt_id, db)
    if result is True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    return result
    
@router.put("/prompts/{prompt_id}")
def update_prompt(
    prompt_id: int,
    prompt_data: PromptCreate,
    db: Session = Depends(get_db)
):
    result = prompt_service.update_prompt(prompt_id, prompt_data, db)
    if result is True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    return {
        "message": "Prompt Update"
    }

@router.delete("/prompts/{prompt_id}")
def delete_prompt(prompt_id: int, db: Session = Depends(get_db)):
    result = prompt_service.delete_prompt(prompt_id, db)
    if result is True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt not found"
        )
    return {
        "message": "Prompt Deleted"
    }