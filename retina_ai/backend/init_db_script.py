"""
Database Initializer and Seeder Script
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
import sys
import sqlite3

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "retina_ai.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "database", "schema.sql")
SEED_PATH = os.path.join(BASE_DIR, "database", "seed.sql")


def setup_database():
    print(f"[Database] Setting up SQLite database at: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print("[Database] Schema created successfully.")

    # Check if patients exist
    cursor.execute("SELECT COUNT(*) FROM patients")
    count = cursor.fetchone()[0]
    if count == 0 and os.path.exists(SEED_PATH):
        with open(SEED_PATH, "r", encoding="utf-8") as f:
            cursor.executescript(f.read())
        print("[Database] Initial seed data inserted.")
    else:
        print(f"[Database] Existing patients count: {count}")

    # Safe column migrations for ScreeningRecord
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
        ("progression_risk_percent", "REAL DEFAULT 15.0"),
        ("hospital_compliance_status", "VARCHAR(50) DEFAULT 'Pending Arrival'")
    ]

    cursor.execute("PRAGMA table_info(screening_records)")
    existing_cols = [row[1] for row in cursor.fetchall()]

    for col_name, col_type in cols_to_add:
        if col_name not in existing_cols:
            try:
                cursor.execute(f"ALTER TABLE screening_records ADD COLUMN {col_name} {col_type}")
                print(f"[Database Migration] Added column: {col_name}")
            except Exception as e:
                print(f"[Database Migration Notice] {col_name}: {e}")

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database()
