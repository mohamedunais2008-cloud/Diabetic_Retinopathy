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

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_database()
