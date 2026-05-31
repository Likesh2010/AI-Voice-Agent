from sqlalchemy.orm import Session

from . import models, schemas


def create_recruiter(db: Session, recruiter_in: schemas.RecruiterCreate) -> models.Recruiter:
    recruiter = models.Recruiter(**recruiter_in.dict())
    db.add(recruiter)
    db.commit()
    db.refresh(recruiter)
    return recruiter


def get_recruiter(db: Session, recruiter_id: int) -> models.Recruiter | None:
    return db.query(models.Recruiter).filter(models.Recruiter.id == recruiter_id).first()


def create_job(db: Session, job_in: schemas.JobCreate) -> models.Job:
    job = models.Job(**job_in.dict())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job(db: Session, job_id: int) -> models.Job | None:
    return db.query(models.Job).filter(models.Job.id == job_id).first()


def list_jobs(db: Session, recruiter_id: int) -> list[models.Job]:
    return db.query(models.Job).filter(models.Job.recruiter_id == recruiter_id).all()


def create_question(db: Session, question_in: schemas.QuestionCreate) -> models.Question:
    question = models.Question(**question_in.dict())
    db.add(question)
    db.commit()
    db.refresh(question)
    return question


def list_questions(db: Session, job_id: int) -> list[models.Question]:
    return db.query(models.Question).filter(models.Question.job_id == job_id).order_by(models.Question.order).all()


def create_candidate(db: Session, candidate_in: schemas.CandidateCreate) -> models.Candidate:
    extra = candidate_in.additional_fields or {}
    fields = [models.CandidateField(field_key=key, field_value=value) for key, value in extra.items()]
    candidate_data = candidate_in.dict(exclude={"additional_fields"})
    candidate = models.Candidate(**candidate_data)
    candidate.fields = fields
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate


def get_candidate(db: Session, candidate_id: int) -> models.Candidate | None:
    return db.query(models.Candidate).filter(models.Candidate.id == candidate_id).first()


def create_call(db: Session, call_in: schemas.CallCreate) -> models.Call:
    call = models.Call(
        **call_in.dict(),
        status="initiated",
        conversation_state={"question_index": 0, "history": [], "metrics": {}},
        call_metadata={},
    )
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


def get_call(db: Session, call_id: int) -> models.Call | None:
    return db.query(models.Call).filter(models.Call.id == call_id).first()


def get_call_by_twilio_sid(db: Session, twilio_sid: str) -> models.Call | None:
    return db.query(models.Call).filter(models.Call.twilio_call_sid == twilio_sid).first()


def update_call_state(db: Session, call: models.Call, state: dict) -> models.Call:
    call.conversation_state = state
    db.add(call)
    db.commit()
    db.refresh(call)
    return call


def create_transcript(db: Session, transcript_in: schemas.TranscriptCreate) -> models.Transcript:
    transcript = models.Transcript(**transcript_in.dict())
    db.add(transcript)
    db.commit()
    db.refresh(transcript)
    return transcript


def create_report(db: Session, report_data: dict) -> models.Report:
    report = models.Report(**report_data)
    db.add(report)
    db.commit()
    db.refresh(report)
    return report


def create_analytics(db: Session, analytics_data: dict) -> models.Analytics:
    analytics = models.Analytics(**analytics_data)
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics


def update_candidate_fields(db: Session, candidate: models.Candidate, updates: dict[str, str]) -> models.Candidate:
    for key, value in updates.items():
        if hasattr(candidate, key):
            setattr(candidate, key, value)
        else:
            field = next((f for f in candidate.fields if f.field_key == key), None)
            if field:
                field.field_value = value
            else:
                candidate.fields.append(models.CandidateField(field_key=key, field_value=value))
    db.add(candidate)
    db.commit()
    db.refresh(candidate)
    return candidate
