from model_db.draft_model import Draft
from sqlalchemy.orm import Session
from schemas.draft_schema import DraftCreate

def get_all_drafts(db: Session):
    return db.query(Draft).all()

def create_draft(draft: DraftCreate, db: Session):
    new_draft = Draft(
    case_id=draft.case_id,
    document_type=draft.document_type,
    generated_text=draft.generated_text
    )
    db.add(new_draft)
    db.commit()
    db.refresh(new_draft)
    return new_draft

def view_draft(draft_id: int, db: Session):
    draft = db.query(Draft).filter(Draft.id == draft_id).first()
    if draft is None:
        return None

    return draft

def delete_draft(draft_id: int, db: Session):
    draft_del = db.query(Draft).filter(Draft.id == draft_id).first()
    if draft_del is None:
        return True
    db.delete(draft_del)
    db.commit()