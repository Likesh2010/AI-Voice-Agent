from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session
import requests
import os
import json
from typing import Optional

from ... import crud, schemas, models
from ...services.openai_service import OpenAIService
from ...services.twilio_service import TwilioService
from ..dependencies import get_db
from ...core.config import settings

router = APIRouter(prefix="/twilio", tags=["Twilio"])
openai_service = OpenAIService()
twilio_service = TwilioService()


@router.post("/voice")
def incoming_voice(call_sid: str = Form(...), From: str = Form(...), To: str = Form(...), db: Session = Depends(get_db)):
    # Determine first question (fallback to a simple prompt)
    question_text = "Tell me why you're interested in this role and what makes you a good fit."
    # Try to find the first question in the DB (best-effort)
    try:
        q = db.query(models.Question).order_by(models.Question.order).first()
        if q and q.question_text:
            question_text = q.question_text
    except Exception:
        pass

    action_url = f"{settings.public_base_url.rstrip('/')}/api/twilio/record"
    twiml = twilio_service.build_twiml_record(question_text, action_url)
    return Response(content=twiml, media_type="application/xml")


@router.post("/record")
def recording_webhook(RecordingUrl: str = Form(...), RecordingSid: str = Form(...), CallSid: str = Form(...), db: Session = Depends(get_db)):
    if not RecordingUrl:
        raise HTTPException(status_code=400, detail="Recording URL missing")

    # Twilio provides a wav/ogg; request mp3 by appending .mp3 if available
    audio_url = f"{RecordingUrl}.mp3"
    resp = requests.get(audio_url)
    if resp.status_code != 200:
        # try original URL
        resp = requests.get(RecordingUrl)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Unable to download recording")

    os.makedirs("./tmp", exist_ok=True)
    temp_path = f"./tmp/twilio_{RecordingSid}.mp3"
    with open(temp_path, "wb") as f:
        f.write(resp.content)

    # Transcribe audio
    transcription = openai_service.transcribe_audio(temp_path)

    # Find call record (if any)
    call = crud.get_call_by_twilio_sid(db, CallSid)
    call_id: Optional[int] = None
    job_title = ""
    previous_answers: dict[str, str] = {}
    question_text = ""

    if call:
        call_id = call.id
        # get job title if available
        try:
            job = crud.get_job(db, call.job_id)
            job_title = job.title if job else ""
        except Exception:
            job_title = ""
        # load last question from call state
        state = call.conversation_state or {}
        history = state.get("history", [])
        if history:
            previous_answers = {str(i): h.get("text") for i, h in enumerate(history)}
        # attempt to get last asked question
        if history and len(history) > 0:
            question_text = history[-1].get("question", "")

    # persist transcript
    if call_id:
        transcript_in = schemas.TranscriptCreate(call_id=call_id, speaker="candidate", text=transcription, segment_index=0)
        crud.create_transcript(db, transcript_in)

    # analyze the candidate response
    analysis = openai_service.analyze_candidate_response(transcription, question_text or "", job_title or "", previous_answers)

    # Update candidate profile if possible
    try:
        if call and call.candidate_id:
            candidate = crud.get_candidate(db, call.candidate_id)
            updates = analysis.get("candidate_updates", {}) or {}
            if updates:
                crud.update_candidate_fields(db, candidate, updates)
    except Exception:
        pass

    # update call state history
    if call:
        state = call.conversation_state or {"question_index": 0, "history": [], "metrics": {}}
        state.setdefault("history", []).append({"question": question_text, "text": transcription, "analysis": analysis})
        crud.update_call_state(db, call, state)

    # Determine next question
    next_twiml = twilio_service.build_twiml_prompt(text="Thank you. That response was recorded.")

    # Attempt to progress to next question from job questions
    try:
        if call and call.job_id:
            questions = crud.list_questions(db, call.job_id)
            state = call.conversation_state or {"question_index": 0}
            idx = state.get("question_index", 0) + 1
            if idx < len(questions):
                next_q = questions[idx]
                action_url = f"{settings.public_base_url.rstrip('/')}/api/twilio/record"
                next_twiml = twilio_service.build_twiml_record(next_q.question_text, action_url)
                # update question_index
                state["question_index"] = idx
                crud.update_call_state(db, call, state)
            else:
                # no more questions: summarize and finish
                report = openai_service.summarize_report({"history": state.get("history", [])})
                # store report
                try:
                    if call_id:
                        report_data = {"call_id": call_id, "interest_score": int(report.get("interest_score", 0) or 0), "interest_category": report.get("interest_category", "unknown"), "recommendation": report.get("recommendation", "review"), "summary": report.get("summary", ""), "key_observations": json.dumps(report.get("key_observations", {})), "risk_factors": json.dumps(report.get("risk_factors", {}))}
                        crud.create_report(db, report_data)
                except Exception:
                    pass
                next_twiml = twilio_service.build_twiml_prompt(text="Thank you for your time. Goodbye.")
    except Exception:
        pass

    return Response(content=next_twiml, media_type="application/xml")
