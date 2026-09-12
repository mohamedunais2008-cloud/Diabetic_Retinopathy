"""
Pydantic Schemas for Request & Response Validation
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


# ---------------- Patient Schemas ----------------
class PatientBase(BaseModel):
    full_name: str = Field(..., example="Ramesh Kumar")
    age: Optional[int] = Field(50, ge=1, le=120, example=54)
    gender: Optional[str] = Field("Male", example="Male")
    phone: Optional[str] = Field(None, example="+91 98765 43210")
    email: Optional[str] = Field(None, example="patient@gmail.com")
    village: Optional[str] = Field("Rural Village", example="Alanganallur")
    district: Optional[str] = Field("Madurai", example="Madurai")
    diabetes_years: Optional[float] = Field(0.0, ge=0.0, example=8.5)
    hba1c: Optional[float] = Field(None, ge=0.0, le=30.0, example=8.4)
    hypertension: Optional[bool] = Field(False, example=True)
    smoker: Optional[bool] = Field(False, example=False)
    clinic_id: Optional[int] = None


class PatientCreate(PatientBase):
    patient_uid: Optional[str] = None


class PatientResponse(PatientBase):
    id: int
    patient_uid: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Screening Record Schemas ----------------
class LesionBreakdown(BaseModel):
    microaneurysms: int = 0
    hemorrhages: int = 0
    hard_exudates: int = 0
    cotton_wool_spots: int = 0
    neovascularization: str = "Absent"


class ScreeningResponse(BaseModel):
    id: int
    screening_uid: str
    patient_id: int
    eye: str
    raw_image_url: str
    preprocessed_image_url: Optional[str] = None
    gradcam_image_url: Optional[str] = None
    report_pdf_url: Optional[str] = None
    
    icdr_grade: int
    grade_name: str
    is_referable: bool
    confidence: float
    confidence_percent: str
    urgency: str
    recall_period: str

    pathology_findings: LesionBreakdown
    xai_summary: Optional[str] = None
    asha_worker_notes: Optional[str] = None
    doctor_review_status: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------- Simulation Schemas ----------------
class TelemedicineSimulationRequest(BaseModel):
    annual_population: int = Field(100000, ge=1000, le=1000000)
    num_phcs: int = Field(50, ge=1, le=500)
    bandwidth_mbps: float = Field(2.0, ge=0.1, le=100.0)
    doctor_count: int = Field(5, ge=1, le=50)


class TelemedicineSimulationResponse(BaseModel):
    annual_population: int
    num_phcs: int
    bandwidth_mbps: float
    doctor_count: int
    daily_screening_capacity: float
    patients_per_phc_daily: float
    transfer_latency_sec: float
    estimated_referral_rate_percent: float
    daily_referrals: float
    doctors_needed: int
    doctor_deficit_or_surplus: int
    workload_reduction_percent: float
    simulink_queue_status: str
