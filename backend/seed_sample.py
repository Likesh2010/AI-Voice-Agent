"""Create sample recruiter, job, questions, candidate and a call for quick testing."""
from app.db.session import SessionLocal, engine
from app.db.base import Base
from app import crud, schemas


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        rec = crud.create_recruiter(db, schemas.RecruiterCreate(name="Test Recruiter", email="recruiter@example.com", company="ACME"))
        job = crud.create_job(db, schemas.JobCreate(recruiter_id=rec.id, title="Software Engineer", description="Test role"))
        crud.create_question(db, schemas.QuestionCreate(job_id=job.id, question_text="Tell me about your recent project.", field_name="project", order=0))
        crud.create_question(db, schemas.QuestionCreate(job_id=job.id, question_text="Why are you interested in this role?", field_name="interest", order=1))
        cand = crud.create_candidate(db, schemas.CandidateCreate(job_id=job.id, name="Alice Candidate", email="alice@example.com", phone="+15551234567"))
        call = crud.create_call(db, schemas.CallCreate(candidate_id=cand.id, recruiter_id=rec.id, job_id=job.id, direction="outbound"))
        print("Seeded: recruiter_id=", rec.id, "job_id=", job.id, "candidate_id=", cand.id, "call_id=", call.id)
    finally:
        db.close()


if __name__ == '__main__':
    seed()
