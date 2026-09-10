-- Sample Seed Data for RetinaAI
-- Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India

-- 1. Insert Rural Primary Health Centres (PHCs)
INSERT INTO clinics (code, name, center_type, village, block, district, state, latitude, longitude, bandwidth_type)
VALUES 
('PHC-TN-MAD-01', 'Alanganallur Primary Health Centre', 'Primary Health Centre (PHC)', 'Alanganallur', 'Vadipatti', 'Madurai', 'Tamil Nadu', 10.0435, 78.0831, '3G Cellular (2 Mbps)'),
('PHC-TN-MAD-02', 'Usilampatti Community Health Centre', 'Community Health Centre (CHC)', 'Usilampatti', 'Usilampatti', 'Madurai', 'Tamil Nadu', 9.9702, 77.7944, '4G Cellular (8 Mbps)'),
('PHC-MH-PUN-01', 'Shirur Rural Sub-Centre', 'Sub-Centre', 'Shirur', 'Shirur', 'Pune', 'Maharashtra', 18.8256, 74.3789, '2G/Edge (0.5 Mbps)'),
('PHC-UP-SIT-01', 'Maholi Block Primary Health Centre', 'Primary Health Centre (PHC)', 'Maholi', 'Maholi', 'Sitapur', 'Uttar Pradesh', 27.6653, 80.4746, '3G Cellular (2 Mbps)');

-- 2. Insert Sample Rural Diabetic Patients
INSERT INTO patients (patient_uid, full_name, age, gender, phone, village, district, diabetes_years, hba1c, hypertension, smoker, clinic_id)
VALUES
('PAT-2026-0001', 'Ramesh Kumar', 56, 'Male', '+91 98421 11021', 'Alanganallur', 'Madurai', 8.5, 8.4, 1, 0, 1),
('PAT-2026-0002', 'Meenakshi Sundaram', 62, 'Female', '+91 98421 22032', 'Kalligudi', 'Madurai', 12.0, 9.1, 1, 0, 1),
('PAT-2026-0003', 'Anand Patil', 48, 'Male', '+91 97654 33043', 'Shirur', 'Pune', 4.0, 6.8, 0, 1, 3),
('PAT-2026-0004', 'Sita Devi', 58, 'Female', '+91 94567 44054', 'Maholi', 'Sitapur', 15.0, 10.2, 1, 0, 4);
