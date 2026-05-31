# Voice Recruitment Agent

This repository contains a backend FastAPI implementation for an AI-powered voice recruitment agent.

## Features
- Recruiter and job management APIs
- Question-driven candidate screening
- Candidate and call data capture
- OpenAI-based speech-to-text, text-to-speech, and candidate analysis
- Twilio webhook integration for voice calls
- Interest scoring and recruiter report generation

## Local setup
1. Create a `.env` file from `.env.example`.
2. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
3. Start the backend server:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```
4. Open `http://localhost:8000/docs` for the interactive API docs.

## Key endpoints
- `POST /api/recruiters/`
- `POST /api/jobs/`
- `POST /api/jobs/{job_id}/questions`
- `POST /api/candidates/`
- `POST /api/calls/`
- `POST /api/calls/{call_id}/transcribe`
- `GET /api/calls/{call_id}/tts?text=...`
- `POST /api/calls/{call_id}/analysis`
- `POST /api/twilio/voice`
- `POST /api/twilio/record`

## Notes
- `OPENAI_API_KEY` is required for AI synthesis and transcription.
- `TWILIO_*` values are required for actual outbound call orchestration.
- The code is designed for PostgreSQL, but defaults to SQLite for local testing.
