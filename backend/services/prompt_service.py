from database import SessionLocal
from model_db.prompt_model import Prompt
from sqlalchemy.orm import Session
from schemas.prompt_schema import PromptCreate

db = SessionLocal()

def get_all_prompts(db: Session):
    return db.query(Prompt).all()

def create_prompt(prompt: PromptCreate, db: Session):
    new_prompt = Prompt(
    name=prompt.name,
    content=prompt.content
    )
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    return new_prompt

def view_prompt(prompt_id: int, db: Session):
    prompt = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt is None:
        return None

    return prompt

def update_prompt(
    prompt_id: int,
    prompt_data: PromptCreate,
    db: Session
):
    prompt_up = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt_up is None:
        return True
    prompt_up.name = prompt_data.name
    prompt_up.content = prompt_data.content
    db.commit()
    db.refresh(prompt_up)
    return prompt_up

def delete_prompt(prompt_id: int, db: Session):
    prompt_del = db.query(Prompt).filter(Prompt.id == prompt_id).first()
    if prompt_del is None:
        return True
    db.delete(prompt_del)
    db.commit()