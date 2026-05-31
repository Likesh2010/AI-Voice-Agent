from fastapi import APIRouter

from .routes import recruiters, jobs, candidates, calls, twilio

api_router = APIRouter()
api_router.include_router(recruiters.router)
api_router.include_router(jobs.router)
api_router.include_router(candidates.router)
api_router.include_router(calls.router)
api_router.include_router(twilio.router)
