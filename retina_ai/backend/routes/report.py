"""
Clinical Report API Routes
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import ScreeningRecord, Patient

router = APIRouter(prefix="/api/reports", tags=["Clinical Reports"])


@router.get("/{screening_id}/pdf")
def download_clinical_report(screening_id: int, db: Session = Depends(get_db)):
    """Downloads or previews the official ophthalmology referral PDF."""
    screening = db.query(ScreeningRecord).filter(ScreeningRecord.id == screening_id).first()
    if not screening:
        raise HTTPException(status_code=404, detail="Screening record not found")

    if not screening.report_pdf_path or not os.path.exists(screening.report_pdf_path):
        raise HTTPException(status_code=404, detail="Report PDF has not been generated for this screening")

    filename = os.path.basename(screening.report_pdf_path)
    return FileResponse(
        screening.report_pdf_path,
        media_type="application/pdf",
        filename=filename
    )


@router.get("/{screening_id}/summary")
def get_report_summary(screening_id: int, db: Session = Depends(get_db)):
    """Fetches high-level clinical summary for telemedicine dashboard cards."""
    screening = db.query(ScreeningRecord).filter(ScreeningRecord.id == screening_id).first()
    if not screening:
        raise HTTPException(status_code=404, detail="Screening record not found")

    patient = db.query(Patient).filter(Patient.id == screening.patient_id).first()

    return {
        "screening_id": screening.id,
        "screening_uid": screening.screening_uid,
        "patient_name": patient.full_name if patient else "Unknown",
        "patient_uid": patient.patient_uid if patient else "Unknown",
        "eye": screening.eye,
        "icdr_grade": screening.icdr_grade,
        "grade_name": screening.grade_name,
        "is_referable": screening.is_referable,
        "confidence_percent": f"{screening.confidence * 100:.1f}%",
        "urgency": screening.urgency,
        "pdf_download_url": f"/api/reports/{screening.id}/pdf",
        "created_at": screening.created_at
    }
