"""
SQLAlchemy Database ORM Models
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from .connection import Base


class Clinic(Base):
    __tablename__ = "clinics"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True) # e.g. PHC-TN-MAD-01
    name = Column(String(150), nullable=False)
    center_type = Column(String(50), default="Primary Health Centre (PHC)") # PHC, CHC, Sub-Centre, Mobile Van
    village = Column(String(100), nullable=False)
    block = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), default="Tamil Nadu")
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    bandwidth_type = Column(String(50), default="3G Cellular (2 Mbps)") # 2G, 3G, 4G, Broadband, Offline Store-and-Forward
    created_at = Column(DateTime, default=datetime.utcnow)

    patients = relationship("Patient", back_populates="clinic")


class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    patient_uid = Column(String(50), unique=True, index=True) # e.g. PAT-2026-0042
    full_name = Column(String(120), nullable=False)
    age = Column(Integer, nullable=False)
    gender = Column(String(20), nullable=False) # Male, Female, Other
    phone = Column(String(20), nullable=True)
    village = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    
    # Clinical history
    diabetes_years = Column(Float, default=0.0)
    hba1c = Column(Float, nullable=True) # % HbA1c
    hypertension = Column(Boolean, default=False)
    smoker = Column(Boolean, default=False)
    
    clinic_id = Column(Integer, ForeignKey("clinics.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    clinic = relationship("Clinic", back_populates="patients")
    screenings = relationship("ScreeningRecord", back_populates="patient", cascade="all, delete-orphan")


class ScreeningRecord(Base):
    __tablename__ = "screening_records"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    screening_uid = Column(String(50), unique=True, index=True) # SCR-2026-0012
    
    # Eye examined
    eye = Column(String(10), default="OD") # OD (Right), OS (Left)
    
    # Image file paths
    raw_image_path = Column(String(255), nullable=False)
    preprocessed_image_path = Column(String(255), nullable=True)
    gradcam_image_path = Column(String(255), nullable=True)
    report_pdf_path = Column(String(255), nullable=True)

    # Diagnostic output
    icdr_grade = Column(Integer, nullable=False) # 0 to 4
    grade_name = Column(String(100), nullable=False)
    is_referable = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    urgency = Column(String(50), nullable=False)
    recall_period = Column(String(50), nullable=False)

    # Sub-pixel lesion counts
    microaneurysms_count = Column(Integer, default=0)
    hemorrhages_count = Column(Integer, default=0)
    hard_exudates_count = Column(Integer, default=0)
    cotton_wool_spots_count = Column(Integer, default=0)
    neovascularization = Column(String(50), default="Absent")

    # XAI explanation and clinical notes
    xai_summary = Column(Text, nullable=True)
    asha_worker_notes = Column(Text, nullable=True)
    doctor_review_status = Column(String(50), default="Pending Specialist Review") # Pending Specialist Review, Reviewed & Certified

    # 4-Stakeholder Telemedicine Extensions
    nurse_gps_lat = Column(Float, nullable=True)
    nurse_gps_lon = Column(Float, nullable=True)
    nurse_camp_name = Column(String(150), default="Mobile Screening Camp")
    image_quality_status = Column(String(50), default="Good") # Good, Fair, Blurry / Sub-optimal
    image_quality_score = Column(Float, default=95.0)
    
    # Doctor Consultation & Digital Prescription
    doctor_clinical_action = Column(String(100), nullable=True) # e.g. Laser Photocoagulation Required
    doctor_prescription = Column(Text, nullable=True)
    doctor_signed_by = Column(String(120), nullable=True)
    doctor_signed_at = Column(DateTime, nullable=True)
    is_dispatched_to_doctor = Column(Boolean, default=True)
    
    # Patient & Follow-up Compliance
    whatsapp_status = Column(String(100), nullable=True)
    progression_risk_percent = Column(Float, default=15.0)
    hospital_compliance_status = Column(String(50), default="Pending Arrival") # Pending Arrival, Checked In, Laser Completed
    
    created_at = Column(DateTime, default=datetime.utcnow)

    patient = relationship("Patient", back_populates="screenings")


class TelemedicineSimulation(Base):
    __tablename__ = "telemedicine_simulations"

    id = Column(Integer, primary_key=True, index=True)
    annual_population = Column(Integer, default=100000)
    num_phcs = Column(Integer, default=50)
    bandwidth_mbps = Column(Float, default=2.0)
    doctor_count = Column(Integer, default=5)
    
    daily_screening_capacity = Column(Float, nullable=False)
    daily_referrals = Column(Float, nullable=False)
    doctors_needed = Column(Integer, nullable=False)
    transfer_latency_sec = Column(Float, nullable=False)
    workload_reduction_percent = Column(Float, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
