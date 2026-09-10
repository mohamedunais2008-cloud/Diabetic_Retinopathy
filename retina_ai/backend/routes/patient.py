"""
Patient Management API Routes
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import os

from ..database.connection import get_db
from ..database.models import Patient, ScreeningRecord
from ..database.schemas import PatientCreate, PatientResponse

router = APIRouter(prefix="/api/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse)
def create_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    """Registers a new patient for rural screening camps."""
    # Generate unique patient UID if not provided
    short_uuid = uuid.uuid4().hex[:6].upper()
    patient_uid = patient_in.patient_uid or f"PAT-{datetime.utcnow().year}-{short_uuid}"

    # Check for duplicate UID
    existing = db.query(Patient).filter(Patient.patient_uid == patient_uid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient UID already exists")

    patient = Patient(
        patient_uid=patient_uid,
        full_name=patient_in.full_name,
        age=patient_in.age,
        gender=patient_in.gender,
        phone=patient_in.phone,
        village=patient_in.village,
        district=patient_in.district,
        diabetes_years=patient_in.diabetes_years,
        hba1c=patient_in.hba1c,
        hypertension=patient_in.hypertension,
        smoker=patient_in.smoker,
        clinic_id=patient_in.clinic_id
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("", response_model=List[PatientResponse])
def list_patients(
    search: Optional[str] = Query(None, description="Search by Name, Village, Phone, or UID"),
    district: Optional[str] = Query(None, description="Filter by District"),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Lists registered patients with optional filtering for camp coordinators."""
    query = db.query(Patient)

    if district:
        query = query.filter(Patient.district.ilike(f"%{district}%"))

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (Patient.full_name.ilike(search_pattern)) |
            (Patient.village.ilike(search_pattern)) |
            (Patient.patient_uid.ilike(search_pattern)) |
            (Patient.phone.ilike(search_pattern))
        )

    return query.order_by(Patient.created_at.desc()).offset(skip).limit(limit).all()


@router.get("/{patient_id}")
def get_patient_detail(patient_id: int, db: Session = Depends(get_db)):
    """Retrieves patient demographics and all past eye screening records."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    screenings = db.query(ScreeningRecord).filter(
        ScreeningRecord.patient_id == patient_id
    ).order_by(ScreeningRecord.created_at.desc()).all()

    return {
        "patient": PatientResponse.model_validate(patient),
        "screenings_count": len(screenings),
        "screenings": [
            {
                "id": s.id,
                "screening_uid": s.screening_uid,
                "eye": s.eye,
                "icdr_grade": s.icdr_grade,
                "grade_name": s.grade_name,
                "is_referable": s.is_referable,
                "confidence_percent": f"{s.confidence * 100:.1f}%",
                "urgency": s.urgency,
                "recall_period": s.recall_period,
                "raw_image_url": f"/uploads/{os.path.basename(s.raw_image_path)}",
                "gradcam_image_url": f"/uploads/{os.path.basename(s.gradcam_image_path)}" if s.gradcam_image_path else None,
                "report_pdf_url": f"/api/reports/{s.id}/pdf" if s.report_pdf_path else None,
                "created_at": s.created_at
            }
            for s in screenings
        ]
    }
