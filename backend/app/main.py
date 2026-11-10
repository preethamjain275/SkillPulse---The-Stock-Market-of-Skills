"""SkillPulse FastAPI Main Application.
High-performance REST API & Static Application Host for distributed job market analytics,
classification, prediction, and career guidance.
"""
from __future__ import annotations
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.app.core.config import settings
from backend.app.api.endpoints import router as api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="SkillPulse: Enterprise Job Market Analytics & ML Career Guidance Platform powered by Apache Spark RDDs.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for seamless communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers under /api
app.include_router(api_router, prefix="/api")

# Mount frontend directory for static assets (style.css, app.js, data/insights.js)
frontend_dir = os.path.join(settings.BASE_DIR, "frontend")
if os.path.exists(frontend_dir):
    app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
def serve_index():
    index_path = os.path.join(settings.BASE_DIR, "frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "SkillPulse API is running. Go to /docs for API documentation."}

# Mount entire frontend at root for direct asset resolution (style.css, app.js, data/*)
if os.path.exists(frontend_dir):
    app.mount("/", StaticFiles(directory=frontend_dir, html=True), name="frontend_root")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="localhost", port=8000, reload=True)
