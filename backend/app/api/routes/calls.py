import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ... import crud, schemas
from ...services.analytics_service import AnalyticsService
from ...services.openai_service import OpenAIService
from ...services.twilio_service import TwilioService
from ..dependencies import get_db
from ... import models
from typing import List

router = APIRouter(prefix="/calls", tags=["Calls"])
openai_service = OpenAIService()
analytics_service = AnalyticsService()


@router.post("/", response_model=schemas.CallOut)
def start_call(call_in: schemas.CallCreate, db: Session = Depends(get_db)):
    candidate = crud.get_candidate(db, call_in.candidate_id)
    job = crud.get_job(db, call_in.job_id)
    recruiter = crud.get_recruiter(db, call_in.recruiter_id)
    if not candidate or not job or not recruiter:
        raise HTTPException(status_code=404, detail="Invalid candidate, job, or recruiter")
    call = crud.create_call(db, call_in)
    return call


@router.post("/{call_id}/transcribe")
def transcribe_response(call_id: int, upload_file: UploadFile = File(...), db: Session = Depends(get_db)):
    call = crud.get_call(db, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    temp_path = f"./tmp/{call_id}_{upload_file.filename}"
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(upload_file.file.read())

    transcription = openai_service.transcribe_audio(temp_path)
    transcript = schemas.TranscriptCreate(call_id=call_id, speaker="candidate", text=transcription)
    crud.create_transcript(db, transcript)
    return {"transcript": transcription}


@router.post("/{call_id}/analysis", response_model=schemas.ReportOut)
def analyze_call(call_id: int, db: Session = Depends(get_db)):
    call = crud.get_call(db, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    candidate = crud.get_candidate(db, call.candidate_id)
    job = crud.get_job(db, call.job_id)
    transcripts = db.query(crud.models.Transcript).filter(crud.models.Transcript.call_id == call_id).all()
    if not transcripts:
        raise HTTPException(status_code=400, detail="No transcript available for this call")

    combined_text = "\n".join([t.text for t in transcripts])
    analysis = openai_service.analyze_candidate_response(
        candidate_text=combined_text,
        question_text="Complete recruitment conversation",
        job_title=job.title,
        previous_answers={},
    )

    metrics = {
        "response_time_seconds": 10,
        "engagement_points": 5,
        "cooperation_points": 5,
        "enthusiasm_points": analysis.get("enthusiasm", 3),
        "curiosity_points": 2,
        "sentiment_score": 1 if analysis.get("sentiment", "neutral") == "positive" else 0,
        "availability_score": 4,
        "job_change_intent_score": 3,
        "risk_score": 0 if analysis.get("clarity") == "clear" else 4,
    }
    interest_score = analytics_service.compute_interest_score(metrics)
    category = analytics_service.category(interest_score)
    report_data = analytics_service.build_report(
        candidate=candidate.__dict__, analysis=analysis, score=interest_score, category=category
    )
    report = crud.create_report(db, {**report_data, "call_id": call_id})
    return report


@router.get("/", response_model=List[schemas.CallOut])
def list_calls(db: Session = Depends(get_db)):
    calls = db.query(models.Call).order_by(models.Call.started_at.desc()).all()
    return calls


@router.get("/reports", response_model=List[schemas.ReportOut])
def list_reports(db: Session = Depends(get_db)):
    reports = db.query(models.Report).order_by(models.Report.created_at.desc()).all()
    return reports


@router.get("/{call_id}/tts")
def serve_tts(call_id: int, text: str, db: Session = Depends(get_db)):
    call = crud.get_call(db, call_id)
    if not call:
        raise HTTPException(status_code=404, detail="Call not found")
    audio_bytes = openai_service.generate_tts(text)
    temp_path = f"./tmp/tts_{call_id}.mp3"
    os.makedirs(os.path.dirname(temp_path), exist_ok=True)
    with open(temp_path, "wb") as f:
        f.write(audio_bytes)
    return FileResponse(temp_path, media_type="audio/mpeg")
