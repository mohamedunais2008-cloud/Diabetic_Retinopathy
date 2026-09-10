"""
Live Verification & Demonstration Script
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import requests
import json
import io
from PIL import Image, ImageDraw

base_url = 'http://127.0.0.1:8000'

print('=' * 65)
print('  RETINAAI LIVE DEMONSTRATION & OUTPUT REPORT')
print('  Problem Statement ID: 26038 (MathWorks / SHS 2026)')
print('=' * 65)

# 1. Health Check
print('\n[1] SYSTEM HEALTH CHECK')
r = requests.get(f'{base_url}/api/health')
print('HTTP Status:', r.status_code)
print(json.dumps(r.json(), indent=2))

# 2. Patients Registry
print('\n[2] RURAL PATIENTS REGISTRY')
r = requests.get(f'{base_url}/api/patients')
patients = r.json()
print(f'Total Registered Patients: {len(patients)}')
for p in patients[:4]:
    print(f"  • {p['full_name']} ({p['patient_uid']}) | Age: {p['age']} | Village: {p['village']}, {p['district']} | HbA1c: {p.get('hba1c')}%")

# 3. Live AI Screening
print('\n[3] AI SCREENING & GRAD-CAM GENERATION')
img = Image.new('RGB', (512, 512), color=(12, 8, 8))
draw = ImageDraw.Draw(img)
draw.ellipse([30, 30, 482, 482], fill=(210, 70, 15))
draw.ellipse([350, 240, 410, 300], fill=(255, 190, 50))
for x in range(140, 360, 28):
    draw.ellipse([x, x, x+12, x+12], fill=(255, 255, 230))
    draw.ellipse([x, 480-x, x+8, 488-x], fill=(5, 0, 0))

buf = io.BytesIO()
img.save(buf, format='JPEG')
buf.seek(0)

predict_res = requests.post(
    f'{base_url}/api/predict',
    files={'file': ('rural_screening_fundus.jpg', buf, 'image/jpeg')},
    data={'patient_id': patients[0]['id'], 'eye': 'OD', 'asha_notes': 'Screened at Alanganallur PHC Camp'}
)
pred = predict_res.json()
print(f"Screening UID:        {pred['screening_uid']}")
print(f"Patient Name:         {pred['patient_name']} ({pred['patient_uid']})")
print(f"Eye Examined:         {pred['eye']} (Right Eye)")
print(f"ICDR Classification:  {pred['grade_name']} (Grade {pred['icdr_grade']})")
print(f"Referable DR Triage:  {'YES - URGENT SPECIALIST REVIEW' if pred['is_referable'] else 'NO - ROUTINE'}")
print(f"Model Confidence:     {pred['confidence_percent']}")
print(f"Urgency Window:       {pred['urgency']} ({pred['recall_period']})")
print(f"Sub-pixel Lesions:    Microaneurysms: {pred['pathology_findings']['microaneurysms']}, Hemorrhages: {pred['pathology_findings']['hemorrhages']}, Exudates: {pred['pathology_findings']['hard_exudates']}")
print(f"Grad-CAM Heatmap URL: {base_url}{pred['images']['gradcam_url']}")
print(f"Clinical PDF Report:  {base_url}{pred['report_pdf_url']}")
if pred.get('referral_hospital'):
    print(f"Assigned Hospital:    {pred['referral_hospital']['name']} ({pred['referral_hospital']['distance_km']} km away)")
    print(f"Emergency Hotline:    {pred['referral_hospital']['phone']}")

# 4. MathWorks Telemedicine Simulation
print('\n[4] MATHWORKS TELEMEDICINE PIPELINE SIMULATION (100,000+ POPULATION)')
sim_res = requests.post(f'{base_url}/api/simulation/run', json={
    'annual_population': 100000,
    'num_phcs': 50,
    'bandwidth_mbps': 2.0,
    'doctor_count': 5
})
sim = sim_res.json()
print(f"Annual Cohort Size:   {sim['annual_population']:,} patients")
print(f"PHC Centers Network:  {sim['num_phcs']} Primary Health Centres")
print(f"Daily Screening Goal: {sim['daily_screening_capacity']} patients/day across district")
print(f"Bandwidth Latency:    {sim['transfer_latency_sec']} seconds per fundus pair over 3G (2 Mbps)")
print(f"AI Triage Filter:     {sim['workload_reduction_percent']}% of non-referable cases automatically cleared")
print(f"Doctor Review Queue:  {sim['daily_referrals']} referable patients/day (instead of 400)")
print(f"Doctors Needed:       {sim['doctors_needed']} ophthalmologist (Staffed: {sim['doctor_count']})")
print(f"Simulink Status:      {sim['simulink_queue_status']}")

# 5. Web Client Serving
print('\n[5] FRONTEND WEB APPLICATION')
web_res = requests.get(base_url)
print(f"Web Server Status:    {web_res.status_code} OK")
print(f"Frontend URL:         {base_url}/")
print(f"Swagger API Docs:     {base_url}/docs")
print('=' * 65)
