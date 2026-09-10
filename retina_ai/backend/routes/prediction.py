"""
Prediction & Explainable AI Screening API Routes
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
import uuid
import shutil
from datetime import datetime
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
    eye: str = Form("OD"), # OD = Right Eye, OS = Left Eye
    asha_notes: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    Core AI screening pipeline for retinal fundus images:
    1. Saves uploaded fundus photograph.
    2. Runs standard ophthalmic CLAHE / FOV preprocessing.
    3. Executes pluggable deep learning inference.
    4. Produces Grad-CAM explainable saliency heatmap.
    5. Computes sub-pixel lesion metrics and triage classification.
    6. Automatically compiles official clinical referral PDF.
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

    # 4. Pluggable ML Inference Engine
    inference_res = InferenceService.run_inference(prep_result["image_pil"])
    grade = inference_res["grade"]
    confidence = inference_res["confidence"]

    # 5. Explainable AI: Grad-CAM Saliency Overlay
    xai_res = XAIService.generate_and_save_gradcam(
        raw_image=prep_result["raw_pil"],
        grade=grade,
        output_dir=UPLOADS_DIR,
        file_prefix=f"{run_id}",
        alpha=0.45
    )

    # 6. Clinical Findings & Standardized Explanations
    explanation = XAIService.get_clinical_explanation(grade, confidence)

    # 7. Generate Clinical PDF Report
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
            "eye": eye,
            "grade_name": explanation["grade_name"],
            "is_referable": explanation["referable"],
            "confidence_percent": explanation["confidence_percent"],
            "recall_period": explanation["recall_period"],
            "pathology_findings": explanation["pathology_findings"],
            "xai_summary": explanation["xai_summary"],
            "asha_guidance": explanation["asha_guidance"]
        },
        image_paths={
            "raw": raw_path,
            "preprocessed": prep_result["preprocessed_filepath"],
            "gradcam": xai_res["gradcam_filepath"]
        },
        output_filepath=pdf_path
    )

    # 8. Commit to Database
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
        doctor_review_status="Pending Specialist Review" if explanation["referable"] else "Verified (Non-Referable)"
    )
    db.add(screening)
    db.commit()
    db.refresh(screening)

    # Nearest hospital routing
    referral_center = GPSService.find_nearest_tertiary_center(9.9252, 78.1198)

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
        "referral_hospital": referral_center if explanation["referable"] else None,
        "images": {
            "raw_url": f"/uploads/{raw_filename}",
            "preprocessed_url": f"/uploads/{prep_result['preprocessed_filename']}",
            "gradcam_url": f"/uploads/{xai_res['gradcam_filename']}"
        },
        "report_pdf_url": f"/api/reports/{screening.id}/pdf"
    }
