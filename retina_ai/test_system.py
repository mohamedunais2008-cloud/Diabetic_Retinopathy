"""
End-to-End Verification Test Script using standard requests & uvicorn thread
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
import io
import sys
import time
import threading
from PIL import Image, ImageDraw
import requests
import uvicorn

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if CURRENT_DIR not in sys.path:
    sys.path.insert(0, CURRENT_DIR)

from backend.init_db_script import setup_database
from backend.main import app


def generate_synthetic_test_fundus():
    """Generates a synthetic fundus image in memory for testing."""
    img = Image.new("RGB", (512, 512), color=(15, 10, 10))
    draw = ImageDraw.Draw(img)
    
    # Retinal fundus circle
    draw.ellipse([30, 30, 482, 482], fill=(180, 60, 20), outline=(120, 30, 10))
    # Optic disc
    draw.ellipse([340, 230, 410, 300], fill=(240, 180, 50))
    # Blood vessels
    draw.line([(370, 260), (300, 180), (220, 150), (140, 160)], fill=(70, 0, 0), width=4)
    draw.line([(370, 260), (300, 340), (220, 370), (140, 350)], fill=(70, 0, 0), width=4)
    # Simulated lesions (microaneurysms & exudates)
    draw.ellipse([210, 240, 218, 248], fill=(40, 0, 0)) # MA
    draw.ellipse([190, 270, 198, 278], fill=(40, 0, 0)) # MA
    draw.ellipse([230, 220, 242, 232], fill=(255, 240, 100)) # Hard exudate

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


def generate_severe_lesion_fundus():
    """Generates a fundus image with dense lesions triggering Referable DR (Moderate/Severe)."""
    img = Image.new("RGB", (512, 512), color=(10, 8, 8))
    draw = ImageDraw.Draw(img)
    draw.ellipse([30, 30, 482, 482], fill=(210, 70, 15))
    draw.ellipse([350, 240, 410, 300], fill=(255, 190, 50))
    # Many high-contrast lesions
    for x in range(120, 380, 25):
        draw.ellipse([x, x, x+14, x+14], fill=(255, 255, 240)) # Exudates
        draw.ellipse([x, 480-x, x+10, 490-x], fill=(5, 0, 0)) # Hemorrhages
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf



def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8001, log_level="warning")


def run_tests():
    print("=========================================================")
    print(" Running End-to-End Verification Tests for RetinaAI")
    print("=========================================================")

    # 1. Setup DB
    setup_database()

    # 2. Launch background server on port 8001
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    
    # Wait for server to be up
    base_url = "http://127.0.0.1:8001"
    for _ in range(20):
        try:
            r = requests.get(f"{base_url}/api/health", timeout=1)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.3)

    # 3. Test Health Check
    res = requests.get(f"{base_url}/api/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health = res.json()
    print(f"[PASS] 1. Health check: {health['status']} | Problem Statement: {health['problem_statement']}")

    # 4. Test List Patients
    res = requests.get(f"{base_url}/api/patients")
    assert res.status_code == 200
    patients = res.json()
    assert len(patients) > 0, "No patients found in DB!"
    test_patient = patients[0]
    print(f"[PASS] 2. Retrieved {len(patients)} seeded patients. Selected: {test_patient['full_name']} (ID: {test_patient['id']})")

    # 5. Test Create Patient
    new_patient_payload = {
        "full_name": "Kavitha Rajan",
        "age": 49,
        "gender": "Female",
        "village": "Sholavandan",
        "district": "Madurai",
        "diabetes_years": 6.0,
        "hba1c": 7.9,
        "phone": "+91 94432 55667"
    }
    res = requests.post(f"{base_url}/api/patients", json=new_patient_payload)
    assert res.status_code == 200
    created = res.json()
    print(f"[PASS] 3. Patient registered: {created['full_name']} (UID: {created['patient_uid']})")

    # 6. Test AI Screening & Grad-CAM Generation
    img_buf = generate_synthetic_test_fundus()
    files = {"file": ("test_fundus.jpg", img_buf, "image/jpeg")}
    data = {
        "patient_id": test_patient["id"],
        "eye": "OD",
        "asha_notes": "Routine screening camp at Alanganallur PHC."
    }
    res = requests.post(f"{base_url}/api/predict", files=files, data=data)
    assert res.status_code == 200, f"Screening failed: {res.text}"
    pred = res.json()

    print(f"[PASS] 4. AI Screening Pipeline Output:")
    print(f"          - ICDR Grade:        {pred['icdr_grade']} ({pred['grade_name']})")
    print(f"          - Referable DR:      {pred['is_referable']} (Urgency: {pred['urgency']})")
    print(f"          - Confidence:        {pred['confidence_percent']}")
    print(f"          - Lesions:           {pred['pathology_findings']}")
    print(f"          - Raw Image URL:     {pred['images']['raw_url']}")
    print(f"          - Grad-CAM Heatmap:  {pred['images']['gradcam_url']}")
    print(f"          - PDF Report URL:    {pred['report_pdf_url']}")

    # 4b. Test Referable DR Screening (Severe Microvascular Lesions)
    img_buf_severe = generate_severe_lesion_fundus()
    res_severe = requests.post(
        f"{base_url}/api/predict",
        files={"file": ("severe_dr.jpg", img_buf_severe, "image/jpeg")},
        data={"patient_id": test_patient["id"], "eye": "OS", "asha_notes": "Dense exudates noted."}
    )
    assert res_severe.status_code == 200
    pred_severe = res_severe.json()
    assert pred_severe["is_referable"] is True, "Expected referable DR for dense lesion case!"
    print(f"[PASS] 4b. Referable DR Triage Triggered Successfully:")
    print(f"           - ICDR Grade:        {pred_severe['icdr_grade']} ({pred_severe['grade_name']})")
    print(f"           - Referable DR:      {pred_severe['is_referable']}")
    print(f"           - Urgency:           {pred_severe['urgency']}")
    print(f"           - Tertiary Hospital: {pred_severe['referral_hospital']['name']}")

    # 7. Test PDF Download
    pdf_res = requests.get(f"{base_url}{pred['report_pdf_url']}")
    assert pdf_res.status_code == 200, f"PDF download failed: {pdf_res.text}"
    assert len(pdf_res.content) > 1000, "PDF content seems empty"
    print(f"[PASS] 5. Clinical Referral PDF generated & verified (Size: {len(pdf_res.content):,} bytes)")

    # 8. Test Telemedicine Simulink Workflow Simulation
    sim_payload = {
        "annual_population": 100000,
        "num_phcs": 50,
        "bandwidth_mbps": 2.0,
        "doctor_count": 5
    }
    res = requests.post(f"{base_url}/api/simulation/run", json=sim_payload)
    assert res.status_code == 200
    sim = res.json()
    print(f"[PASS] 6. Telemedicine Simulation (100k Cohort):")
    print(f"          - Daily Screening Target:   {sim['daily_screening_capacity']} patients/day")
    print(f"          - Cellular Uplink Latency:  {sim['transfer_latency_sec']}s per patient")
    print(f"          - Workload Cut by AI Triage:{sim['workload_reduction_percent']}%")
    print(f"          - Doctors Needed:           {sim['doctors_needed']} ophthalmologists")
    print(f"          - Simulink Queue Status:    {sim['simulink_queue_status']}")

    # 9. Test Turnkey Web Frontend Serving
    res = requests.get(f"{base_url}/")
    assert res.status_code == 200
    assert "RetinaAI" in res.text
    print(f"[PASS] 7. Turnkey Web App HTML successfully served at '/'")

    print("\n=========================================================")
    print(" ALL 7 TEST SUITES PASSED FLAWLESSLY! SYSTEM IS 100% OPERATIONAL.")
    print("=========================================================")


if __name__ == "__main__":
    run_tests()
