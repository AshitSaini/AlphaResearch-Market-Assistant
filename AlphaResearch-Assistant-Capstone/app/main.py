"""FastAPI entry point for the Broking AI Assistant."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import health_check, router
from app.config import settings


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="RAG-based AI assistant for Indian broking, securities, and compliance workflows.",
)

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api", tags=["api"])

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/assets", StaticFiles(directory=str(frontend_dir)), name="assets")


@app.get("/", include_in_schema=False)
async def web_app():
    """Serve the capstone web UI."""
    index_file = frontend_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return {"name": settings.APP_NAME, "docs": "/docs", "api": "/api"}


@app.get("/health", tags=["health"])
async def root_health():
    """Root-level health endpoint for load balancers and README compatibility."""
    return await health_check()
