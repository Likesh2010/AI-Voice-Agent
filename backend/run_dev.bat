@echo off
REM Simple helper to run the FastAPI backend with an existing .env file
if exist .env (
  echo Using existing .env
) else (
  echo No .env file found. Copy backend\.env.example to backend\.env and update secrets.
)
set FLASK_ENV=development
set PYTHONUNBUFFERED=1
python -m uvicorn app.main:app --reload --port 8000