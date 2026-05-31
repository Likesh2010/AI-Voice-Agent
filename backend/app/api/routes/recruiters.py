from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import crud, schemas
from ..dependencies import get_db

router = APIRouter(prefix="/recruiters", tags=["Recruiters"])


@router.post("/", response_model=schemas.RecruiterOut)
def create_recruiter(recruiter_in: schemas.RecruiterCreate, db: Session = Depends(get_db)):
    existing = db.query(crud.models.Recruiter).filter(crud.models.Recruiter.email == recruiter_in.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Recruiter already exists")
    return crud.create_recruiter(db, recruiter_in)


@router.get("/{recruiter_id}", response_model=schemas.RecruiterOut)
def read_recruiter(recruiter_id: int, db: Session = Depends(get_db)):
    recruiter = crud.get_recruiter(db, recruiter_id)
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    return recruiter
