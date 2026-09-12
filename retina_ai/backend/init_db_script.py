"""
Database Initializer and Seeder Script with User Authentication & Stakeholders
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
import sys
import sqlite3
import hashlib

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BASE_DIR)
DB_PATH = os.path.join(PROJECT_DIR, "retina_ai.db")
SCHEMA_PATH = os.path.join(PROJECT_DIR, "database", "schema.sql")
SEED_PATH = os.path.join(PROJECT_DIR, "database", "seed.sql")


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def setup_database():
    print(f"[Database] Setting up SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 1. Create users table if not exists
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(120) UNIQUE NOT NULL,
        hashed_password VARCHAR(255) NOT NULL,
        role VARCHAR(30) NOT NULL,
        full_name VARCHAR(150) NOT NULL,
        license_or_id VARCHAR(80),
        organization VARCHAR(150),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Add columns to patients
    cursor.execute("PRAGMA table_info(patients)")
    existing_patient_cols = [row[1] for row in cursor.fetchall()]
    if "email" not in existing_patient_cols:
        try:
            cursor.execute("ALTER TABLE patients ADD COLUMN email VARCHAR(120)")
            print("[Migration] Added 'email' to patients.")
        except Exception as e:
            print(f"[Migration Notice] {e}")

    # 3. Add columns to screening_records
    cursor.execute("PRAGMA table_info(screening_records)")
    existing_cols = [row[1] for row in cursor.fetchall()]
    
    cols_to_add = [
        ("nurse_gps_lat", "REAL"),
        ("nurse_gps_lon", "REAL"),
        ("nurse_camp_name", "VARCHAR(150) DEFAULT 'Mobile Screening Camp'"),
        ("image_quality_status", "VARCHAR(50) DEFAULT 'Good'"),
        ("image_quality_score", "REAL DEFAULT 95.0"),
        ("doctor_clinical_action", "VARCHAR(100)"),
        ("doctor_prescription", "TEXT"),
        ("doctor_signed_by", "VARCHAR(120)"),
        ("doctor_signed_at", "TIMESTAMP"),
        ("is_dispatched_to_doctor", "BOOLEAN DEFAULT 1"),
        ("whatsapp_status", "VARCHAR(100)"),
        ("email_status", "VARCHAR(100)"),
        ("notification_dispatched_at", "TIMESTAMP"),
        ("progression_risk_percent", "REAL DEFAULT 15.0"),
        ("hospital_compliance_status", "VARCHAR(50) DEFAULT 'Pending Arrival'")
    ]

    for col_name, col_type in cols_to_add:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE screening_records ADD COLUMN {col_name} {col_type}")
                print(f"[Migration] Added '{col_name}' to screening_records.")
            except Exception as e:
                print(f"[Migration Notice] {col_name}: {e}")

    # 4. Seed default accounts for Nurse, Doctor, and District Admin
    default_users = [
        (
            "nurse_kavitha",
            "nurse@retina.ai",
            hash_password("nurse123"),
            "nurse",
            "Kavitha Selvam, Staff Nurse",
            "ASHA-TN-MAD-104",
            "Kallandiri PHC Mobile Unit"
        ),
        (
            "dr_meenakshi",
            "doctor@retina.ai",
            hash_password("doctor123"),
            "doctor",
            "Dr. Meenakshi Sundaram, MS (Ophthalmology)",
            "TN-MC-49210",
            "District Tertiary Eye Hospital"
        ),
        (
            "admin_dho",
            "admin@retina.ai",
            hash_password("admin123"),
            "admin",
            "Dr. K. Rajasekaran, District Health Officer",
            "DHO-MAD-01",
            "District Health Directorate"
        )
    ]

    for u in default_users:
        cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (u[1], u[0]))
        if not cursor.fetchone():
            cursor.execute("""
            INSERT INTO users (username, email, hashed_password, role, full_name, license_or_id, organization)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """, u)
            print(f"[Seeder] Created default user: {u[1]} ({u[3]})")

    # Update patient Ramesh Kumar with email if missing
    cursor.execute("UPDATE patients SET email = 'ramesh.kumar1971@gmail.com' WHERE patient_uid = 'PAT-2026-0001' AND (email IS NULL OR email = '')")

    conn.commit()
    conn.close()
    print("[Database] Initialization and migration complete.")


if __name__ == "__main__":
    setup_database()
