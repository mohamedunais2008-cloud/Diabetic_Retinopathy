"""
Patient Management API Routes
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import os

from ..database.connection import get_db
from ..database.models import Patient, ScreeningRecord
from ..database.schemas import PatientCreate, PatientResponse

router = APIRouter(prefix="/api/patients", tags=["Patients"])


class PatientLookupRequest(BaseModel):
    identifier: str  # UID or Phone Number


@router.post("", response_model=PatientResponse)
def create_patient(patient_in: PatientCreate, db: Session = Depends(get_db)):
    """Registers a new patient for rural screening camps with manual village entry."""
    short_uuid = uuid.uuid4().hex[:6].upper()
    patient_uid = patient_in.patient_uid or f"PAT-{datetime.utcnow().year}-{short_uuid}"

    existing = db.query(Patient).filter(Patient.patient_uid == patient_uid).first()
    if existing:
        raise HTTPException(status_code=400, detail="Patient UID already exists")

    patient = Patient(
        patient_uid=patient_uid,
        full_name=patient_in.full_name,
        age=patient_in.age,
        gender=patient_in.gender,
        phone=patient_in.phone,
        email=patient_in.email,
        village=patient_in.village,  # Manually entered by nurse
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
    """Retrieves patient demographics and all past eye screening records with doctor remarks."""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    screenings = db.query(ScreeningRecord).filter(
        ScreeningRecord.patient_id == patient_id
    ).order_by(ScreeningRecord.created_at.desc()).all()

    return format_patient_records(patient, screenings)


@router.post("/lookup")
def lookup_patient_private(req: PatientLookupRequest, db: Session = Depends(get_db)):
    """
    Secure Patient Portal endpoint:
    Patient inputs their own Patient ID or Phone number.
    Returns ONLY this specific patient's record and doctor certifications.
    """
    ident = req.identifier.strip().upper()
    clean_digits = "".join(filter(str.isdigit, req.identifier))

    patient = db.query(Patient).filter(Patient.patient_uid == ident).first()

    if not patient and clean_digits:
        for p in db.query(Patient).all():
            if p.phone and "".join(filter(str.isdigit, p.phone)).endswith(clean_digits[-10:]):
                patient = p
                break

    if not patient:
        raise HTTPException(
            status_code=404,
            detail=f"No patient found matching '{req.identifier}'. Please check your Patient ID or registered phone number."
        )

    screenings = db.query(ScreeningRecord).filter(
        ScreeningRecord.patient_id == patient.id
    ).order_by(ScreeningRecord.created_at.desc()).all()

    return format_patient_records(patient, screenings)


def format_patient_records(patient: Patient, screenings: List[ScreeningRecord]) -> dict:
    return {
        "patient": {
            "id": patient.id,
            "patient_uid": patient.patient_uid,
            "full_name": patient.full_name,
            "age": patient.age,
            "gender": patient.gender,
            "phone": patient.phone,
            "email": patient.email,
            "village": patient.village,
            "district": patient.district,
            "diabetes_years": patient.diabetes_years,
            "hba1c": patient.hba1c
        },
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
                "doctor_review_status": s.doctor_review_status,
                "doctor_signed_by": s.doctor_signed_by,
                "doctor_signed_at": s.doctor_signed_at.strftime("%d %b %Y, %I:%M %p") if s.doctor_signed_at else None,
                "doctor_clinical_action": s.doctor_clinical_action,
                "doctor_prescription": s.doctor_prescription,
                "whatsapp_status": s.whatsapp_status,
                "email_status": s.email_status,
                "nurse_camp_name": s.nurse_camp_name,
                "nurse_gps_lat": s.nurse_gps_lat,
                "nurse_gps_lon": s.nurse_gps_lon,
                "image_quality_status": s.image_quality_status,
                "progression_risk_percent": s.progression_risk_percent,
                "raw_image_url": f"/uploads/{os.path.basename(s.raw_image_path)}",
                "gradcam_image_url": f"/uploads/{os.path.basename(s.gradcam_image_path)}" if s.gradcam_image_path else None,
                "report_pdf_url": f"/api/reports/{s.id}/pdf" if s.report_pdf_path else None,
                "created_at": s.created_at.strftime("%d %b %Y, %I:%M %p") if s.created_at else None
            }
            for s in screenings
        ]
    }


class PatientUpdateRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    village: Optional[str] = None
    district: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    diabetes_years: Optional[float] = None
    hba1c: Optional[float] = None


@router.put("/{patient_id}")
def update_patient(patient_id: int, req: PatientUpdateRequest, db: Session = Depends(get_db)):
    """Updates patient demographics or contact email for report forwarding."""
    pat = db.query(Patient).filter(Patient.id == patient_id).first()
    if not pat:
        raise HTTPException(status_code=404, detail="Patient not found")

    if req.full_name is not None: pat.full_name = req.full_name.strip()
    if req.phone is not None: pat.phone = req.phone.strip()
    if req.email is not None: pat.email = req.email.strip()
    if req.village is not None: pat.village = req.village.strip()
    if req.district is not None: pat.district = req.district.strip()
    if req.age is not None: pat.age = req.age
    if req.gender is not None: pat.gender = req.gender
    if req.diabetes_years is not None: pat.diabetes_years = req.diabetes_years
    if req.hba1c is not None: pat.hba1c = req.hba1c

    db.commit()
    db.refresh(pat)
    return pat
