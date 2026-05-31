from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import crud, schemas
from ..dependencies import get_db

router = APIRouter(prefix="/candidates", tags=["Candidates"])


@router.post("/", response_model=schemas.CandidateOut)
def create_candidate(candidate_in: schemas.CandidateCreate, db: Session = Depends(get_db)):
    job = crud.get_job(db, candidate_in.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return crud.create_candidate(db, candidate_in)


@router.get("/{candidate_id}", response_model=schemas.CandidateOut)
def read_candidate(candidate_id: int, db: Session = Depends(get_db)):
    candidate = crud.get_candidate(db, candidate_id)
    if not candidate:
        raise HTTPException(status_code=404, detail="Candidate not found")
    return candidate
