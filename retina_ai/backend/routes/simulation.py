"""
Telemedicine Workflow & Resource Allocation Simulation Routes
Problem Statement 26038: MathWorks Telemedicine Screening Pipeline Simulation
Serving 100,000+ patients annually across rural Primary Health Centres (PHCs).
"""

import math
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import TelemedicineSimulation
from ..database.schemas import TelemedicineSimulationRequest, TelemedicineSimulationResponse

router = APIRouter(prefix="/api/simulation", tags=["Telemedicine Resource Allocation Simulation"])


@router.post("/run", response_model=TelemedicineSimulationResponse)
def run_telemedicine_simulation(
    req: TelemedicineSimulationRequest,
    db: Session = Depends(get_db)
):
    """
    Simulates the district-level telemedicine screening pipeline for 100,000+ rural patients:
    - Models image acquisition rates across rural PHCs.
    - Factors cellular bandwidth constraints (2G/3G/4G) and image compression.
    - Calculates AI screening throughput vs manual ophthalmologist review capacity.
    - Estimates optimal doctor staffing and specialist workload reduction.
    """
    work_days = 250
    daily_screening_target = req.annual_population / work_days # 400 patients/day
    patients_per_phc_daily = daily_screening_target / req.num_phcs # 8 patients/day/PHC

    # Image payload: 2 eyes per patient, compressed size ~0.6 MB each
    compressed_image_size_mb = 0.6
    patient_payload_mb = 2 * compressed_image_size_mb # 1.2 MB total

    # Bandwidth transmission latency per patient
    transfer_latency_sec = round((patient_payload_mb * 8) / req.bandwidth_mbps, 2)

    # Clinical epidemiology:
    # Approx 15% of diabetic population presents with Referable DR (Grade 2, 3, or 4)
    referral_rate = 0.15
    daily_referrals = round(daily_screening_target * referral_rate, 1)

    # Specialist doctor review capacity:
    # 5 minutes per referable case with AI Grad-CAM assistance (vs 18 minutes unassisted)
    minutes_per_review = 5
    doctor_work_hours_per_day = 6
    cases_per_doctor_per_day = (doctor_work_hours_per_day * 60) / minutes_per_review # 72 cases/doctor/day

    doctors_needed = max(1, math.ceil(daily_referrals / cases_per_doctor_per_day))
    doctor_delta = req.doctor_count - doctors_needed

    # AI triage workload reduction:
    # Without AI, doctors would have to screen all 400 patients/day (requiring 6+ ophthalmologists full-time).
    # With AI, only 60 referable patients reach the doctor's queue.
    workload_reduction = round((1.0 - referral_rate) * 100, 1) # ~85% reduction!

    # Queue saturation status
    if req.doctor_count >= doctors_needed:
        queue_status = "OPTIMAL: Telemedicine queue cleared daily with zero diagnostic backlog."
    elif req.doctor_count == doctors_needed - 1:
        queue_status = "WARNING: Moderate backlog accumulation. 1 additional ophthalmologist recommended."
    else:
        queue_status = "CRITICAL BOTTLENECK: Doctor capacity deficit. Triage delays exceed 48 hours."

    # Save simulation log
    sim_log = TelemedicineSimulation(
        annual_population=req.annual_population,
        num_phcs=req.num_phcs,
        bandwidth_mbps=req.bandwidth_mbps,
        doctor_count=req.doctor_count,
        daily_screening_capacity=daily_screening_target,
        daily_referrals=daily_referrals,
        doctors_needed=doctors_needed,
        transfer_latency_sec=transfer_latency_sec,
        workload_reduction_percent=workload_reduction
    )
    db.add(sim_log)
    db.commit()

    return TelemedicineSimulationResponse(
        annual_population=req.annual_population,
        num_phcs=req.num_phcs,
        bandwidth_mbps=req.bandwidth_mbps,
        doctor_count=req.doctor_count,
        daily_screening_capacity=round(daily_screening_target, 1),
        patients_per_phc_daily=round(patients_per_phc_daily, 1),
        transfer_latency_sec=transfer_latency_sec,
        estimated_referral_rate_percent=round(referral_rate * 100, 1),
        daily_referrals=daily_referrals,
        doctors_needed=doctors_needed,
        doctor_deficit_or_surplus=doctor_delta,
        workload_reduction_percent=workload_reduction,
        simulink_queue_status=queue_status
    )
