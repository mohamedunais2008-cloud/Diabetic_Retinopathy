"""
Doctor Specialist Tele-Ophthalmology Routes
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import ScreeningRecord, Patient, Clinic
from ..services.notification_service import NotificationService
from ..services.report_service import ReportService

router = APIRouter(prefix="/api/doctor", tags=["Doctor Tele-Ophthalmology Review"])


class DoctorReviewRequest(BaseModel):
    doctor_signed_by: str  # e.g. "Dr. Meenakshi Sundaram, MS (Ophthalmology)"
    doctor_clinical_action: str  # e.g. "Urgent Panretinal Laser Photocoagulation (PRP) + Anti-VEGF"
    doctor_prescription: Optional[str] = None
    hospital_compliance_status: Optional[str] = "Referral Scheduled"


@router.get("/queue")
def get_doctor_triage_queue(db: Session = Depends(get_db)):
    """
    Fetches all referable or flagged screenings pending doctor tele-review from PHC camps.
    Sorted by urgency: Severe / PDR first, then Moderate.
    """
    records = (
        db.query(ScreeningRecord, Patient)
        .join(Patient, ScreeningRecord.patient_id == Patient.id)
        .order_by(ScreeningRecord.icdr_grade.desc(), ScreeningRecord.created_at.desc())
        .all()
    )

    queue = []
    for scr, pat in records:
        raw_fn = scr.raw_image_path.replace("\\", "/").split("/")[-1]
        prep_fn = scr.preprocessed_image_path.replace("\\", "/").split("/")[-1] if scr.preprocessed_image_path else None
        grad_fn = scr.gradcam_image_path.replace("\\", "/").split("/")[-1] if scr.gradcam_image_path else None

        queue.append({
            "id": scr.id,
            "screening_uid": scr.screening_uid,
            "patient_id": pat.id,
            "patient_uid": pat.patient_uid,
            "patient_name": pat.full_name,
            "age": pat.age,
            "gender": pat.gender,
            "village": pat.village,
            "district": pat.district,
            "diabetes_years": pat.diabetes_years,
            "hba1c": pat.hba1c,
            "phone": pat.phone,
            "email": pat.email,
            "eye": scr.eye,
            "icdr_grade": scr.icdr_grade,
            "grade_name": scr.grade_name,
            "is_referable": scr.is_referable,
            "confidence": scr.confidence,
            "urgency": scr.urgency,
            "recall_period": scr.recall_period,
            "image_quality_status": scr.image_quality_status,
            "image_quality_score": scr.image_quality_score,
            "nurse_camp_name": scr.nurse_camp_name,
            "nurse_gps_lat": scr.nurse_gps_lat,
            "nurse_gps_lon": scr.nurse_gps_lon,
            "doctor_review_status": scr.doctor_review_status,
            "doctor_signed_by": scr.doctor_signed_by,
            "doctor_signed_at": scr.doctor_signed_at.strftime("%d %b %Y %H:%M") if scr.doctor_signed_at else None,
            "doctor_clinical_action": scr.doctor_clinical_action,
            "doctor_prescription": scr.doctor_prescription,
            "hospital_compliance_status": scr.hospital_compliance_status,
            "whatsapp_status": scr.whatsapp_status,
            "email_status": scr.email_status,
            "raw_image_url": f"/uploads/{raw_fn}",
            "preprocessed_url": f"/uploads/{prep_fn}" if prep_fn else None,
            "gradcam_url": f"/uploads/{grad_fn}" if grad_fn else None,
            "report_pdf_url": f"/api/reports/{scr.id}/pdf",
            "created_at": scr.created_at.strftime("%d %b %Y %H:%M") if scr.created_at else None
        })

    return {"queue": queue, "total_pending": len([q for q in queue if "Pending" in (q["doctor_review_status"] or "")])}


@router.get("/camp-screenings")
def get_all_camp_screenings(db: Session = Depends(get_db)):
    """
    Returns screening history for Nurse Portal to track specialist doctor feedback.
    """
    return get_doctor_triage_queue(db=db)


@router.get("/review/{screening_id}")
def get_screening_detail_for_review(screening_id: int, db: Session = Depends(get_db)):
    """
    Detailed diagnostic data for the ophthalmologist's digital loupe, caliper, and Grad-CAM inspection.
    """
    scr = db.query(ScreeningRecord).filter(ScreeningRecord.id == screening_id).first()
    if not scr:
        raise HTTPException(status_code=404, detail="Screening record not found")

    pat = db.query(Patient).filter(Patient.id == scr.patient_id).first()

    raw_fn = scr.raw_image_path.replace("\\", "/").split("/")[-1]
    prep_fn = scr.preprocessed_image_path.replace("\\", "/").split("/")[-1] if scr.preprocessed_image_path else None
    grad_fn = scr.gradcam_image_path.replace("\\", "/").split("/")[-1] if scr.gradcam_image_path else None

    return {
        "screening": {
            "id": scr.id,
            "screening_uid": scr.screening_uid,
            "eye": scr.eye,
            "icdr_grade": scr.icdr_grade,
            "grade_name": scr.grade_name,
            "is_referable": scr.is_referable,
            "confidence": scr.confidence,
            "urgency": scr.urgency,
            "recall_period": scr.recall_period,
            "pathology_findings": {
                "microaneurysms": scr.microaneurysms_count,
                "hemorrhages": scr.hemorrhages_count,
                "hard_exudates": scr.hard_exudates_count,
                "cotton_wool_spots": scr.cotton_wool_spots_count,
                "neovascularization": scr.neovascularization
            },
            "xai_summary": scr.xai_summary,
            "asha_worker_notes": scr.asha_worker_notes,
            "image_quality_status": scr.image_quality_status,
            "image_quality_score": scr.image_quality_score,
            "nurse_camp_name": scr.nurse_camp_name,
            "nurse_gps_lat": scr.nurse_gps_lat,
            "nurse_gps_lon": scr.nurse_gps_lon,
            "doctor_review_status": scr.doctor_review_status,
            "doctor_signed_by": scr.doctor_signed_by,
            "doctor_signed_at": scr.doctor_signed_at.strftime("%d %b %Y %H:%M") if scr.doctor_signed_at else None,
            "doctor_clinical_action": scr.doctor_clinical_action,
            "doctor_prescription": scr.doctor_prescription,
            "hospital_compliance_status": scr.hospital_compliance_status,
            "whatsapp_status": scr.whatsapp_status,
            "email_status": scr.email_status,
            "raw_image_url": f"/uploads/{raw_fn}",
            "preprocessed_url": f"/uploads/{prep_fn}" if prep_fn else None,
            "gradcam_url": f"/uploads/{grad_fn}" if grad_fn else None,
            "report_pdf_url": f"/api/reports/{scr.id}/pdf"
        },
        "patient": {
            "id": pat.id,
            "patient_uid": pat.patient_uid,
            "full_name": pat.full_name,
            "age": pat.age,
            "gender": pat.gender,
            "village": pat.village,
            "district": pat.district,
            "phone": pat.phone,
            "email": pat.email,
            "diabetes_years": pat.diabetes_years,
            "hba1c": pat.hba1c
        } if pat else None
    }


@router.post("/review/{screening_id}")
def submit_doctor_review(screening_id: int, req: DoctorReviewRequest, db: Session = Depends(get_db)):
    """
    Ophthalmologist signs off on the AI diagnosis:
    1. Updates screening with clinical action, prescription, digital signature.
    2. Regenerates certified referral PDF stamped with doctor signature and QR code.
    3. Automatically dispatches WhatsApp & Email notifications to the patient.
    """
    scr = db.query(ScreeningRecord).filter(ScreeningRecord.id == screening_id).first()
    if not scr:
        raise HTTPException(status_code=404, detail="Screening record not found")

    pat = db.query(Patient).filter(Patient.id == scr.patient_id).first()

    scr.doctor_review_status = "Reviewed & Certified"
    scr.doctor_signed_by = req.doctor_signed_by.strip()
    scr.doctor_clinical_action = req.doctor_clinical_action.strip()
    scr.doctor_prescription = req.doctor_prescription.strip() if req.doctor_prescription else None
    scr.doctor_signed_at = datetime.utcnow()
    if req.hospital_compliance_status:
        scr.hospital_compliance_status = req.hospital_compliance_status

    # Regenerate certified PDF with doctor signature and QR code
    if scr.report_pdf_path and pat:
        try:
            ReportService.generate_pdf_report(
                patient_data={
                    "full_name": pat.full_name,
                    "patient_uid": pat.patient_uid,
                    "age": pat.age,
                    "gender": pat.gender,
                    "village": pat.village,
                    "district": pat.district,
                    "diabetes_years": pat.diabetes_years,
                    "hba1c": pat.hba1c
                },
                screening_data={
                    "screening_uid": scr.screening_uid,
                    "eye": scr.eye,
                    "grade_name": scr.grade_name,
                    "is_referable": scr.is_referable,
                    "confidence_percent": f"{scr.confidence * 100:.1f}%",
                    "recall_period": scr.recall_period,
                    "urgency": scr.urgency,
                    "pathology_findings": {
                        "microaneurysms": scr.microaneurysms_count,
                        "hemorrhages": scr.hemorrhages_count,
                        "hard_exudates": scr.hard_exudates_count,
                        "cotton_wool_spots": scr.cotton_wool_spots_count,
                        "neovascularization": scr.neovascularization
                    },
                    "xai_summary": scr.xai_summary,
                    "asha_guidance": scr.asha_worker_notes
                },
                camp_data={
                    "camp_name": scr.nurse_camp_name,
                    "lat": scr.nurse_gps_lat,
                    "lon": scr.nurse_gps_lon,
                    "image_quality_status": scr.image_quality_status
                },
                doctor_data={
                    "doctor_signed_by": scr.doctor_signed_by,
                    "doctor_clinical_action": scr.doctor_clinical_action,
                    "doctor_prescription": scr.doctor_prescription,
                    "doctor_signed_at": scr.doctor_signed_at
                },
                image_paths={
                    "raw": scr.raw_image_path,
                    "preprocessed": scr.preprocessed_image_path,
                    "gradcam": scr.gradcam_image_path
                },
                output_filepath=scr.report_pdf_path
            )
        except Exception as e:
            print(f"[Warning] PDF regeneration error: {e}")

    # Automated WhatsApp & Email notification dispatch to patient
    notification_result = None
    if pat:
        notification_result = NotificationService.send_screening_ready_alerts(
            screening=scr,
            patient=pat,
            doctor_signed_by=scr.doctor_signed_by,
            doctor_clinical_action=scr.doctor_clinical_action,
            doctor_prescription=scr.doctor_prescription
        )

    db.commit()
    db.refresh(scr)

    return {
        "success": True,
        "message": f"Screening {scr.screening_uid} successfully certified by {scr.doctor_signed_by}",
        "screening_id": scr.id,
        "status": scr.doctor_review_status,
        "doctor_signed_by": scr.doctor_signed_by,
        "doctor_signed_at": scr.doctor_signed_at.strftime("%d %b %Y %H:%M"),
        "doctor_clinical_action": scr.doctor_clinical_action,
        "doctor_prescription": scr.doctor_prescription,
        "notifications": notification_result
    }
