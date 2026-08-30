from fastapi import APIRouter, Depends, HTTPException, status
from services import case_service
from database import get_db
from sqlalchemy.orm import Session
from schemas.case_schema import CaseCreate


router = APIRouter()

@router.post("/cases")
def create_case(case: CaseCreate, db: Session = Depends(get_db)):
    case_service.create_case(case, db)
    return {
        "message": "Case Created"
    }

@router.get("/cases")
def view_cases(db:Session = Depends(get_db)):
    result = case_service.get_all_cases(db)
    return result

@router.get("/cases/{case_id}")
def get_case(
    case_id: int, 
    db: Session = Depends(get_db)
):
    result = case_service.get_case_by_id(case_id, db)
    if result is True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return result
    
@router.put("/cases/{case_id}")
def update_case(
    case_id: int,
    case_data: CaseCreate,
    db: Session = Depends(get_db)
):
    result = case_service.update_case(case_id, case_data, db)
    if result is True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return {
        "message": "Case Update"
    }

@router.delete("/cases/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db)):
    result = case_service.delete_case(case_id, db)
    if result is True:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    return {
        "message": "Case Deleted"
    }