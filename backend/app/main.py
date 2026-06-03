import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .api.api import api_router
from .api.v1.router import api_v1_router
from .db.base import Base
from .db.session import engine
from .core.config import settings

app = FastAPI(title=settings.app_name)

from fastapi import Request
from fastapi.responses import JSONResponse
import traceback

@app.middleware("http")
async def catch_exceptions_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        tb = traceback.format_exc()
        headers = {
            "Access-Control-Allow-Origin": request.headers.get("origin", "*"),
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "*",
        }
        return JSONResponse(
            status_code=500,
            content={"detail": str(e), "traceback": tb},
            headers=headers
        )

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database tables
Base.metadata.create_all(bind=engine)

# Mount Routers
app.include_router(api_router, prefix="/api")
app.include_router(api_v1_router, prefix="/api/v1")

# Serve a minimal dashboard / static files
static_dir = "./static"
if not os.path.isdir(static_dir):
    os.makedirs(static_dir, exist_ok=True)
app.mount("/dashboard", StaticFiles(directory=static_dir, html=True), name="dashboard")


@app.get("/")
def health_check():
    return {"status": "ok", "app": settings.app_name}
