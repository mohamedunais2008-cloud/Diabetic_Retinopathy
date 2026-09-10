-- Database Schema for RetinaAI
-- Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India

CREATE TABLE IF NOT EXISTS clinics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(150) NOT NULL,
    center_type VARCHAR(50) DEFAULT 'Primary Health Centre (PHC)',
    village VARCHAR(100) NOT NULL,
    block VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    state VARCHAR(100) DEFAULT 'Tamil Nadu',
    latitude REAL,
    longitude REAL,
    bandwidth_type VARCHAR(50) DEFAULT '3G Cellular (2 Mbps)',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS patients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_uid VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(120) NOT NULL,
    age INTEGER NOT NULL,
    gender VARCHAR(20) NOT NULL,
    phone VARCHAR(20),
    village VARCHAR(100) NOT NULL,
    district VARCHAR(100) NOT NULL,
    diabetes_years REAL DEFAULT 0.0,
    hba1c REAL,
    hypertension BOOLEAN DEFAULT 0,
    smoker BOOLEAN DEFAULT 0,
    clinic_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(clinic_id) REFERENCES clinics(id)
);

CREATE TABLE IF NOT EXISTS screening_records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    screening_uid VARCHAR(50) UNIQUE NOT NULL,
    eye VARCHAR(10) DEFAULT 'OD',
    raw_image_path VARCHAR(255) NOT NULL,
    preprocessed_image_path VARCHAR(255),
    gradcam_image_path VARCHAR(255),
    report_pdf_path VARCHAR(255),
    icdr_grade INTEGER NOT NULL,
    grade_name VARCHAR(100) NOT NULL,
    is_referable BOOLEAN NOT NULL,
    confidence REAL NOT NULL,
    urgency VARCHAR(50) NOT NULL,
    recall_period VARCHAR(50) NOT NULL,
    microaneurysms_count INTEGER DEFAULT 0,
    hemorrhages_count INTEGER DEFAULT 0,
    hard_exudates_count INTEGER DEFAULT 0,
    cotton_wool_spots_count INTEGER DEFAULT 0,
    neovascularization VARCHAR(50) DEFAULT 'Absent',
    xai_summary TEXT,
    asha_worker_notes TEXT,
    doctor_review_status VARCHAR(50) DEFAULT 'Pending Specialist Review',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES patients(id)
);

CREATE TABLE IF NOT EXISTS telemedicine_simulations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    annual_population INTEGER DEFAULT 100000,
    num_phcs INTEGER DEFAULT 50,
    bandwidth_mbps REAL DEFAULT 2.0,
    doctor_count INTEGER DEFAULT 5,
    daily_screening_capacity REAL NOT NULL,
    daily_referrals REAL NOT NULL,
    doctors_needed INTEGER NOT NULL,
    transfer_latency_sec REAL NOT NULL,
    workload_reduction_percent REAL NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
