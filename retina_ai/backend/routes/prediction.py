"""
Prediction & Explainable AI Screening API Routes
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
import uuid
import shutil
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from PIL import Image

from ..database.connection import get_db
from ..database.models import Patient, ScreeningRecord
from ..services.preprocessing_service import PreprocessingService
from ..services.inference import InferenceService
from ..services.xai_service import XAIService
from ..services.report_service import ReportService
from ..services.gps_service import GPSService
from ..services.iqa_service import IQAService

router = APIRouter(prefix="/api/predict", tags=["Screening & XAI Prediction"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


@router.post("")
async def screen_retinal_fundus(
    file: UploadFile = File(...),
    patient_id: int = Form(...),
    eye: str = Form("OD"),  # OD = Right Eye, OS = Left Eye
    asha_notes: Optional[str] = Form(None),
    nurse_gps_lat: Optional[float] = Form(None),
    nurse_gps_lon: Optional[float] = Form(None),
    nurse_camp_name: Optional[str] = Form("PHC Outreach Screening Camp"),
    db: Session = Depends(get_db)
):
    """
    Core AI screening pipeline for retinal fundus images:
    1. Saves uploaded fundus photograph.
    2. Runs Automated Fundus Image Quality Assessment (IQA: blur & illumination).
    3. Runs standard ophthalmic CLAHE / FOV preprocessing.
    4. Executes pluggable deep learning inference.
    5. Produces Grad-CAM explainable saliency heatmap.
    6. Computes sub-pixel lesion metrics and 5-year progression risk.
    7. Automatically compiles official clinical referral PDF with GPS stamp & QR code.
    """
    # 1. Verify Patient exists
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail=f"Patient ID {patient_id} not found")

    # Validate eye label
    eye = eye.upper()
    if eye not in ["OD", "OS", "OU"]:
        eye = "OD"

    # Unique identifiers
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    run_id = f"SCR_{ts}_{uuid.uuid4().hex[:6].upper()}"

    # 2. Save raw fundus image
    raw_ext = os.path.splitext(file.filename)[1] or ".jpg"
    raw_filename = f"{run_id}_raw{raw_ext}"
    raw_path = os.path.join(UPLOADS_DIR, raw_filename)
    
    with open(raw_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 3. Ophthalmic Preprocessing Pipeline
    prep_result = PreprocessingService.process_and_save_fundus(
        input_path=raw_path,
        output_dir=UPLOADS_DIR,
        file_prefix=f"{run_id}"
    )

    # 4. Automated Image Quality Assessment (IQA)
    iqa_result = IQAService.assess_image_quality(prep_result["raw_pil"])

    # 5. Pluggable ML Inference Engine
    inference_res = InferenceService.run_inference(prep_result["image_pil"])
    grade = inference_res["grade"]
    confidence = inference_res["confidence"]

    # 6. Explainable AI: Grad-CAM Saliency Overlay
    xai_res = XAIService.generate_and_save_gradcam(
        raw_image=prep_result["raw_pil"],
        grade=grade,
        output_dir=UPLOADS_DIR,
        file_prefix=f"{run_id}",
        alpha=0.45
    )

    # 7. Clinical Findings & Standardized Explanations
    explanation = XAIService.get_clinical_explanation(grade, confidence)

    # 8. Multi-Factor Progression Risk Calculation (HbA1c + Diabetes Duration + Grade)
    base_risk = {0: 8.0, 1: 24.0, 2: 52.0, 3: 78.0, 4: 94.0}.get(grade, 10.0)
    dur_extra = min(20.0, (patient.diabetes_years or 0) * 1.5)
    hba1c_val = patient.hba1c or 7.0
    hba1c_extra = max(0.0, (hba1c_val - 6.5) * 5.0)
    progression_risk = min(99.0, max(5.0, round(base_risk + dur_extra + hba1c_extra, 1)))

    # Fallback default GPS if not supplied (e.g. Madurai PHC)
    camp_lat = nurse_gps_lat if nurse_gps_lat is not None else 9.9252
    camp_lon = nurse_gps_lon if nurse_gps_lon is not None else 78.1198

    # 9. Generate Clinical PDF Report
    pdf_filename = f"{run_id}_referral_report.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    
    ReportService.generate_pdf_report(
        patient_data={
            "full_name": patient.full_name,
            "patient_uid": patient.patient_uid,
            "age": patient.age,
            "gender": patient.gender,
            "village": patient.village,
            "district": patient.district,
            "diabetes_years": patient.diabetes_years,
            "hba1c": patient.hba1c
        },
        screening_data={
            "screening_uid": run_id,
            "eye": eye,
            "grade_name": explanation["grade_name"],
            "is_referable": explanation["referable"],
            "confidence_percent": explanation["confidence_percent"],
            "recall_period": explanation["recall_period"],
            "urgency": explanation["urgency"],
            "pathology_findings": explanation["pathology_findings"],
            "xai_summary": explanation["xai_summary"],
            "asha_guidance": explanation["asha_guidance"]
        },
        camp_data={
            "camp_name": nurse_camp_name,
            "lat": camp_lat,
            "lon": camp_lon,
            "image_quality_status": iqa_result["status"]
        },
        image_paths={
            "raw": raw_path,
            "preprocessed": prep_result["preprocessed_filepath"],
            "gradcam": xai_res["gradcam_filepath"]
        },
        output_filepath=pdf_path
    )

    # 10. Commit to Database
    screening = ScreeningRecord(
        patient_id=patient.id,
        screening_uid=run_id,
        eye=eye,
        raw_image_path=raw_path,
        preprocessed_image_path=prep_result["preprocessed_filepath"],
        gradcam_image_path=xai_res["gradcam_filepath"],
        report_pdf_path=pdf_path,
        icdr_grade=grade,
        grade_name=explanation["grade_name"],
        is_referable=explanation["referable"],
        confidence=confidence,
        urgency=explanation["urgency"],
        recall_period=explanation["recall_period"],
        microaneurysms_count=explanation["pathology_findings"]["microaneurysms"],
        hemorrhages_count=explanation["pathology_findings"]["hemorrhages"],
        hard_exudates_count=explanation["pathology_findings"]["hard_exudates"],
        cotton_wool_spots_count=explanation["pathology_findings"]["cotton_wool_spots"],
        neovascularization=explanation["pathology_findings"]["neovascularization"],
        xai_summary=explanation["xai_summary"],
        asha_worker_notes=asha_notes,
        nurse_gps_lat=camp_lat,
        nurse_gps_lon=camp_lon,
        nurse_camp_name=nurse_camp_name,
        image_quality_status=iqa_result["status"],
        image_quality_score=iqa_result["overall_score"],
        progression_risk_percent=progression_risk,
        doctor_review_status="Pending Specialist Review" if explanation["referable"] else "Verified (Non-Referable)",
        is_dispatched_to_doctor=explanation["referable"],
        hospital_compliance_status="Pending Referral Check-In" if explanation["referable"] else "Completed"
    )
    db.add(screening)
    db.commit()
    db.refresh(screening)

    # Nearest tertiary eye hospital routing
    referral_center = GPSService.find_nearest_tertiary_center(camp_lat, camp_lon)

    return {
        "screening_id": screening.id,
        "screening_uid": screening.screening_uid,
        "patient_uid": patient.patient_uid,
        "patient_name": patient.full_name,
        "eye": eye,
        "icdr_grade": grade,
        "grade_name": explanation["grade_name"],
        "is_referable": explanation["referable"],
        "confidence": confidence,
        "confidence_percent": explanation["confidence_percent"],
        "urgency": explanation["urgency"],
        "recall_period": explanation["recall_period"],
        "model_source": inference_res["model_source"],
        "pathology_findings": explanation["pathology_findings"],
        "xai_summary": explanation["xai_summary"],
        "asha_guidance": explanation["asha_guidance"],
        "iqa": iqa_result,
        "progression_risk_percent": progression_risk,
        "camp": {
            "camp_name": nurse_camp_name,
            "latitude": camp_lat,
            "longitude": camp_lon
        },
        "referral_hospital": referral_center if explanation["referable"] else None,
        "images": {
            "raw_url": f"/uploads/{raw_filename}",
            "preprocessed_url": f"/uploads/{prep_result['preprocessed_filename']}",
            "gradcam_url": f"/uploads/{xai_res['gradcam_filename']}"
        },
        "report_pdf_url": f"/api/reports/{screening.id}/pdf"
    }
