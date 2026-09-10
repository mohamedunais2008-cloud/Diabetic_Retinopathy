"""
Database Connection & Session Configuration
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Path to database file inside retina_ai/
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "retina_ai.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

# Thread-safe SQLite engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides an isolated database session per request.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Creates all tables if they do not already exist.
    """
    Base.metadata.create_all(bind=engine)
