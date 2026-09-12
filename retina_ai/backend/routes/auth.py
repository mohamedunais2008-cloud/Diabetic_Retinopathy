"""
Authentication & Authorization API Routes
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import hashlib
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import User, Patient

router = APIRouter(prefix="/api/auth", tags=["Stakeholder Authentication"])


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


class LoginRequest(BaseModel):
    username_or_email: str
    password: Optional[str] = ""
    role: Optional[str] = None  # nurse, doctor, admin, patient


class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    role: str  # nurse, doctor, admin
    full_name: str
    license_or_id: Optional[str] = None
    organization: Optional[str] = None


class PatientRegisterRequest(BaseModel):
    full_name: str
    phone: str
    village: str
    email: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    district: Optional[str] = "Madurai"
    age: Optional[int] = 45
    gender: Optional[str] = "Male"
    diabetes_years: Optional[float] = 2.0
    hba1c: Optional[float] = 7.0


class PatientLoginRequest(BaseModel):
    identifier: str  # patient_uid (e.g. PAT-2026-0001) or phone number (e.g. 9842173829)


@router.post("/login")
def login(req: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticates Nurse, Doctor, Admin strictly with passwords.
    Patients can log in password-free using Patient UID or Phone Number.
    """
    ident = req.username_or_email.strip()
    pwd = (req.password or "").strip()
    hashed = hash_password(pwd) if pwd else ""

    # 1. Search in User table by email or username
    user = (
        db.query(User)
        .filter((User.email.ilike(ident)) | (User.username.ilike(ident)))
        .first()
    )

    # 2. If not found in User, check if ident is a Patient UID or Phone
    patient_record = None
    clean_digits = "".join(filter(str.isdigit, ident))
    if not user:
        pat = db.query(Patient).filter(Patient.patient_uid.ilike(ident)).first()
        if not pat and clean_digits and len(clean_digits) >= 8:
            for p in db.query(Patient).all():
                if p.phone:
                    p_digits = "".join(filter(str.isdigit, p.phone))
                    if p_digits.endswith(clean_digits[-10:]) or clean_digits.endswith(p_digits[-10:] if len(p_digits) >= 10 else p_digits):
                        pat = p
                        break
        if pat:
            patient_record = pat
            # Look for linked User account
            user = db.query(User).filter(
                (User.email.ilike(pat.email or "")) |
                (User.username.ilike(pat.patient_uid))
            ).first()

    # If it's a patient and user doesn't exist yet, we can create/link one
    if not user and patient_record:
        user = User(
            username=patient_record.patient_uid.lower().replace("-", "_"),
            email=patient_record.email or f"{patient_record.patient_uid.lower()}@retina.ai",
            hashed_password=hash_password("rural_patient_access"),
            role="patient",
            full_name=patient_record.full_name,
            license_or_id=patient_record.patient_uid,
            organization=f"{patient_record.village}, {patient_record.district}"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Account not found for '{ident}'. If you are a patient, please enter your registered Phone Number or Patient UID."
        )

    # Password validation: Staff (nurse, doctor, admin) REQUIRE valid password; Patients are password-free
    is_patient = (user.role == "patient") or (req.role == "patient")
    if not is_patient:
        if not pwd or user.hashed_password != hashed:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password. Please verify your credentials and try again."
            )

    # Role validation if specified
    if req.role and req.role.strip().lower() != user.role.lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"This account is registered as '{user.role.title()}', not '{req.role.title()}'. Please select the '{user.role.title()}' tab to sign in."
        )

    token = f"retina_token_{user.id}_{user.role}_{hash_password(user.username)[:10]}"

    res = {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "full_name": user.full_name,
            "license_or_id": user.license_or_id,
            "organization": user.organization
        }
    }

    # If patient, attach Patient demographics
    if user.role == "patient":
        if not patient_record:
            patient_record = db.query(Patient).filter(
                (Patient.email.ilike(user.email)) |
                (Patient.patient_uid.ilike(user.username)) |
                (Patient.full_name.ilike(user.full_name))
            ).first()

        if patient_record:
            res["patient"] = {
                "id": patient_record.id,
                "patient_uid": patient_record.patient_uid,
                "full_name": patient_record.full_name,
                "age": patient_record.age,
                "gender": patient_record.gender,
                "village": patient_record.village,
                "district": patient_record.district,
                "phone": patient_record.phone,
                "email": patient_record.email,
                "diabetes_years": patient_record.diabetes_years,
                "hba1c": patient_record.hba1c
            }

    return res


@router.post("/register")
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new healthcare worker (Nurse, Doctor, District Health Officer).
    """
    role = req.role.strip().lower()
    if role not in ["nurse", "doctor", "admin"]:
        raise HTTPException(status_code=400, detail="Invalid role. Must be 'nurse', 'doctor', or 'admin'.")

    # Check for duplicate
    if db.query(User).filter(User.username.ilike(req.username.strip())).first():
        raise HTTPException(status_code=400, detail="Username already exists. Please choose another username.")
    if db.query(User).filter(User.email.ilike(req.email.strip())).first():
        raise HTTPException(status_code=400, detail="Email already registered. Please sign in or use another email.")

    new_user = User(
        username=req.username.strip(),
        email=req.email.strip().lower(),
        hashed_password=hash_password(req.password.strip()),
        role=role,
        full_name=req.full_name.strip(),
        license_or_id=req.license_or_id.strip() if req.license_or_id else None,
        organization=req.organization.strip() if req.organization else None
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = f"retina_token_{new_user.id}_{new_user.role}_{hash_password(new_user.username)[:10]}"

    return {
        "success": True,
        "message": f"User {new_user.full_name} registered successfully as {new_user.role}.",
        "token": token,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "full_name": new_user.full_name,
            "license_or_id": new_user.license_or_id,
            "organization": new_user.organization
        }
    }


@router.post("/patient-register")
def patient_register(req: PatientRegisterRequest, db: Session = Depends(get_db)):
    """
    Registers a new Citizen / Patient with clinical profile.
    No complex password required.
    Creates Patient record and linked User record.
    """
    import uuid
    from datetime import datetime

    short_uuid = uuid.uuid4().hex[:6].upper()
    patient_uid = f"PAT-{datetime.utcnow().year}-{short_uuid}"

    username = (req.username or "").strip() or f"pat_{short_uuid.lower()}"
    email = (req.email or "").strip().lower() or f"patient_{short_uuid.lower()}@retina.ai"
    raw_pwd = (req.password or "").strip() or f"patient_{short_uuid.lower()}"

    # Ensure unique username and email for user table
    existing_user = db.query(User).filter(User.username.ilike(username)).first()
    if existing_user:
        username = f"{username}_{short_uuid.lower()}"

    email_for_user = email
    if db.query(User).filter(User.email.ilike(email_for_user)).first():
        email_for_user = f"{short_uuid.lower()}_{email}"

    # Create User
    new_user = User(
        username=username,
        email=email_for_user,
        hashed_password=hash_password(raw_pwd),
        role="patient",
        full_name=req.full_name.strip(),
        license_or_id=patient_uid,
        organization=f"{req.village.strip()}, {req.district.strip() if req.district else 'Madurai'}"
    )
    db.add(new_user)

    # Create Patient record
    new_patient = Patient(
        patient_uid=patient_uid,
        full_name=req.full_name.strip(),
        age=req.age or 45,
        gender=req.gender or "Other",
        phone=req.phone.strip() if req.phone else None,
        email=email,
        village=req.village.strip(),
        district=req.district.strip() if req.district else "Madurai",
        diabetes_years=req.diabetes_years or 0.0,
        hba1c=req.hba1c or 7.0
    )
    db.add(new_patient)
    db.commit()
    db.refresh(new_user)
    db.refresh(new_patient)

    token = f"retina_token_{new_user.id}_patient_{hash_password(new_user.username)[:10]}"

    return {
        "success": True,
        "message": f"Welcome, {new_patient.full_name}! Your Patient Account has been created with ID: {new_patient.patient_uid}",
        "token": token,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": "patient",
            "full_name": new_user.full_name
        },
        "patient": {
            "id": new_patient.id,
            "patient_uid": new_patient.patient_uid,
            "full_name": new_patient.full_name,
            "age": new_patient.age,
            "gender": new_patient.gender,
            "village": new_patient.village,
            "district": new_patient.district,
            "phone": new_patient.phone,
            "email": new_patient.email,
            "diabetes_years": new_patient.diabetes_years,
            "hba1c": new_patient.hba1c
        }
    }


@router.post("/patient-login")
def patient_login(req: PatientLoginRequest, db: Session = Depends(get_db)):
    """
    Patient Sign In using Phone Number or Patient UID (NO PASSWORD REQUIRED).
    Tailored for rural Indian citizens & elderly patients.
    """
    ident = req.identifier.strip()
    if not ident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide your Patient ID or registered mobile phone number."
        )

    clean_digits = "".join(filter(str.isdigit, ident))

    # 1. Match patient by Patient UID or Email
    patient = db.query(Patient).filter(
        (Patient.patient_uid.ilike(ident)) |
        (Patient.email.ilike(ident))
    ).first()

    # 2. Match patient by phone digits
    if not patient and clean_digits and len(clean_digits) >= 8:
        for p in db.query(Patient).all():
            if p.phone:
                p_digits = "".join(filter(str.isdigit, p.phone))
                if p_digits.endswith(clean_digits[-10:]) or clean_digits.endswith(p_digits[-10:] if len(p_digits) >= 10 else p_digits):
                    patient = p
                    break

    # 3. Match from User table if registered as patient
    user = None
    if not patient:
        user = db.query(User).filter(
            (User.role == "patient") &
            ((User.username.ilike(ident)) | (User.email.ilike(ident)))
        ).first()
        if user:
            patient = db.query(Patient).filter(
                (Patient.patient_uid.ilike(user.username)) |
                (Patient.email.ilike(user.email)) |
                (Patient.full_name.ilike(user.full_name))
            ).first()

    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No patient record found matching '{ident}'. Please verify your Patient ID (e.g. PAT-2026-0001) or registered mobile phone number."
        )

    # 4. Link or create User record for token auth
    if not user:
        user = db.query(User).filter(
            (User.email.ilike(patient.email or "none")) |
            (User.username.ilike(patient.patient_uid))
        ).first()

    if not user:
        user = User(
            username=patient.patient_uid.lower().replace("-", "_"),
            email=patient.email or f"{patient.patient_uid.lower()}@retina.ai",
            hashed_password=hash_password("rural_patient_access"),
            role="patient",
            full_name=patient.full_name,
            license_or_id=patient.patient_uid,
            organization=f"{patient.village}, {patient.district}"
        )
        db.add(user)
        db.commit()
        db.refresh(user)

    token = f"patient_token_{patient.id}_{patient.patient_uid}"

    return {
        "success": True,
        "token": token,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": "patient",
            "full_name": user.full_name
        },
        "patient": {
            "id": patient.id,
            "patient_uid": patient.patient_uid,
            "full_name": patient.full_name,
            "age": patient.age or 45,
            "gender": patient.gender or "Other",
            "village": patient.village or "Village Camp",
            "district": patient.district or "Madurai",
            "phone": patient.phone or "",
            "email": patient.email or user.email,
            "diabetes_years": patient.diabetes_years or 0,
            "hba1c": patient.hba1c or 7.0
        }
    }


@router.get("/demo-accounts")
def get_demo_accounts(db: Session = Depends(get_db)):
    """
    Returns verified demo credentials for evaluators / hackathon judges.
    """
    patient = db.query(Patient).filter(Patient.patient_uid == "PAT-2026-0001").first()
    if not patient:
        patient = db.query(Patient).first()

    return {
        "nurse": {
            "email": "nurse@retina.ai",
            "password": "nurse123",
            "name": "Kavitha Selvam, Staff Nurse (ASHA-TN-MAD-104)",
            "role": "nurse"
        },
        "doctor": {
            "email": "doctor@retina.ai",
            "password": "doctor123",
            "name": "Dr. Meenakshi Sundaram, MS (Ophthalmology)",
            "role": "doctor"
        },
        "admin": {
            "email": "admin@retina.ai",
            "password": "admin123",
            "name": "Dr. K. Rajasekaran, District Health Officer",
            "role": "admin"
        },
        "patient": {
            "patient_uid": patient.patient_uid if patient else "PAT-2026-0001",
            "email": "patient@retina.ai",
            "phone": patient.phone if patient else "+91 98421 11021",
            "name": patient.full_name if patient else "Ramesh Kumar",
            "role": "patient",
            "note": "No password needed! Simply enter your Phone Number or Patient ID."
        }
    }
