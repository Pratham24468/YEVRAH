from database import SessionLocal
from model_db.case_model import Case
from sqlalchemy.orm import Session
from schemas.case_schema import CaseCreate

db = SessionLocal()

def get_all_cases(db: Session):
    return db.query(Case).all()

def create_case(case: CaseCreate, db: Session):
    new_case = Case(
        title=case.title,
        plaintiff=case.plaintiff,
        defendant=case.defendant,
        facts=case.facts
    )
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    return new_case

def get_case_by_id(
    case_id: int,
    db: Session
):
    case_view = db.query(Case).filter(Case.id == case_id).first()
    if case_view is None:
        return True
    return case_view

def update_case(
    case_id: int,
    case_data: CaseCreate,
    db: Session
):
    case_up = db.query(Case).filter(Case.id == case_id).first()
    if case_up is None:
        return True
    case_up.title = case_data.title
    case_up.plaintiff = case_data.plaintiff
    case_up.defendant = case_data.defendant
    db.commit()
    db.refresh(case_up)
    return case_up

def delete_case(case_id: int, db: Session):
    case_del = db.query(Case).filter(Case.id == case_id).first()
    if case_del is None:
        return True
    db.delete(case_del)
    db.commit()