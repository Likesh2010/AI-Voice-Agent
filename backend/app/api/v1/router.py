from fastapi import APIRouter
from .auth import router as auth_router
from .campaigns import router as campaigns_router
from .candidates import router as candidates_router
from .webhooks import router as webhooks_router
from .analytics import router as analytics_router
from .reports import router as reports_router
from .notifications import router as notifications_router

api_v1_router = APIRouter()

api_v1_router.include_router(auth_router)
api_v1_router.include_router(campaigns_router)
api_v1_router.include_router(candidates_router)
api_v1_router.include_router(webhooks_router)
api_v1_router.include_router(analytics_router)
api_v1_router.include_router(reports_router)
api_v1_router.include_router(notifications_router)
