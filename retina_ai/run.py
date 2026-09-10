"""
RetinaAI Master Application Launcher
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
MathWorks / Smart India Hackathon (SHS 2026)
"""

import os
import sys
import uvicorn

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.init_db_script import setup_database


def main():
    print("=" * 65)
    print("  RetinaAI - Rural Diabetic Retinopathy Screening System")
    print("  Problem Statement ID: 26038 (MathWorks / SHS 2026)")
    print("=" * 65)

    # 1. Ensure SQLite database is set up and seeded
    setup_database()

    print("\n[RetinaAI] Starting FastAPI Application Server...")
    print("[RetinaAI] Web Dashboard available at:   http://127.0.0.1:8000")
    print("[RetinaAI] Interactive API Docs at:     http://127.0.0.1:8000/docs\n")

    # 2. Launch Uvicorn server
    uvicorn.run(
        "backend.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
        log_level="info"
    )


if __name__ == "__main__":
    main()
