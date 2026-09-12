"""
RetinaAI Backend Main Application
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
MathWorks / Smart India Hackathon (SHS 2026)
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .database.connection import init_db
from .routes.patient import router as patient_router
from .routes.prediction import router as prediction_router
from .routes.doctor import router as doctor_router
from .routes.admin import router as admin_router
from .routes.notification import router as notification_router
from .routes.report import router as report_router
from .routes.simulation import router as simulation_router

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
FRONTEND_STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(FRONTEND_STATIC_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    print("[RetinaAI] Database initialized successfully.")
    yield


app = FastAPI(
    title="RetinaAI - Explainable AI for Diabetic Retinopathy Screening",
    description="Telemedicine screening & triage system for rural Primary Health Centres (PHCs). Problem Statement 26038 (MathWorks).",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for local Vite dev server and external clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Directories for Images and PDFs
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")
app.mount("/reports", StaticFiles(directory=REPORTS_DIR), name="reports")
if os.path.exists(FRONTEND_STATIC_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_STATIC_DIR), name="static")

# Register API Routers for 4 Stakeholders
app.include_router(patient_router)
app.include_router(prediction_router)
app.include_router(doctor_router)
app.include_router(admin_router)
app.include_router(notification_router)
app.include_router(report_router)
app.include_router(simulation_router)


@app.get("/api/health")
def health_check():
    return {
        "status": "online",
        "service": "RetinaAI Rural DR Screening Backend",
        "problem_statement": "26038",
        "supported_grades": ["0: No DR", "1: Mild", "2: Moderate", "3: Severe", "4: Proliferative DR"],
        "xai_engine": "Grad-CAM Saliency Maps",
        "roles": ["nurse", "doctor", "patient", "admin"]
    }


@app.get("/")
def serve_index():
    index_file = os.path.join(FRONTEND_STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {
        "message": "RetinaAI Backend is running! Access Swagger API docs at /docs or mount frontend in frontend/static/index.html."
    }
