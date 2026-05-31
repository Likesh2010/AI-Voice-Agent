from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ... import crud, schemas
from ..dependencies import get_db

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.post("/", response_model=schemas.JobOut)
def create_job(job_in: schemas.JobCreate, db: Session = Depends(get_db)):
    recruiter = crud.get_recruiter(db, job_in.recruiter_id)
    if not recruiter:
        raise HTTPException(status_code=404, detail="Recruiter not found")
    return crud.create_job(db, job_in)


@router.get("/{job_id}", response_model=schemas.JobOut)
def read_job(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job


@router.get("/", response_model=list[schemas.JobOut])
def list_jobs(recruiter_id: int, db: Session = Depends(get_db)):
    return crud.list_jobs(db, recruiter_id)


@router.post("/{job_id}/questions", response_model=schemas.QuestionOut)
def create_question(job_id: int, question_in: schemas.QuestionBase, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    question = schemas.QuestionCreate(**question_in.dict(), job_id=job_id)
    return crud.create_question(db, question)


@router.get("/{job_id}/questions", response_model=list[schemas.QuestionOut])
def list_questions(job_id: int, db: Session = Depends(get_db)):
    job = crud.get_job(db, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return crud.list_questions(db, job_id)
