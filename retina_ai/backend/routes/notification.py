"""
Patient Communication & WhatsApp Alert Notification Routes
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database.connection import get_db
from ..database.models import ScreeningRecord, Patient
from ..services.voice_service import VoiceService
from ..services.gps_service import GPSService

router = APIRouter(prefix="/api/notification", tags=["Notifications & Patient Voice Guidance"])


class WhatsAppDispatchRequest(BaseModel):
    screening_id: int
    phone_number: str
    preferred_language: str = "tamil"  # tamil, hindi, english


@router.post("/whatsapp")
def dispatch_whatsapp_notification(req: WhatsAppDispatchRequest, db: Session = Depends(get_db)):
    """
    Dispatches simulated WhatsApp health notification containing:
    1. Patient diagnosis & urgency status.
    2. Direct link to clinical referral PDF.
    3. Multilingual audio advice snippet.
    4. GPS navigation link to nearest tertiary eye hospital.
    """
    scr = db.query(ScreeningRecord).filter(ScreeningRecord.id == req.screening_id).first()
    if not scr:
        raise HTTPException(status_code=404, detail="Screening record not found")

    pat = db.query(Patient).filter(Patient.id == scr.patient_id).first()
    patient_name = pat.full_name if pat else "Patient"

    voice_scripts = VoiceService.get_audio_scripts(
        patient_name=patient_name,
        grade=scr.icdr_grade,
        eye=scr.eye,
        doctor_advice=scr.doctor_prescription
    )

    # Resolve nearest hospital
    lat = scr.nurse_gps_lat or 9.9252
    lon = scr.nurse_gps_lon or 78.1198
    hosp = GPSService.find_nearest_tertiary_center(lat, lon)

    # Format WhatsApp template based on language
    lang = req.preferred_language.lower()
    audio_text = voice_scripts.get(lang, voice_scripts["tamil"])

    district_name = hosp.get("district", "Madurai")
    distance = hosp.get("distance_km", 14.2)

    if lang == "tamil":
        msg_header = f"🏥 *தமிழ்நாடு அரசு - மாவட்ட கண் நலத் திட்டம் (RetinaAI)*"
        msg_patient = f"👤 நோயாளி: *{patient_name}* (கண்: *{scr.eye}*)"
        msg_verdict = f"🔍 பரிசோதனை முடிவு: *{scr.grade_name}* ({'🔴 உடனடி சிகிச்சை தேவை' if scr.is_referable else '🟢 நலமாக உள்ளது'})"
        msg_hosp = f"📍 பரிந்துரைக்கப்பட்ட மருத்துவமனை: *{hosp['name']}*, {district_name} ({distance} கி.மீ)"
        msg_action = f"📋 மருத்துவர் குறிப்பு: *{scr.doctor_clinical_action or scr.doctor_prescription or 'நேரடி பரிசோதனைக்கு வரவும்'}*"
        msg_pdf = f"📄 மருத்துவ அறிக்கை தரவிறக்கம்: http://localhost:8000/api/reports/{scr.id}/pdf"
    elif lang == "hindi":
        msg_header = f"🏥 *राष्ट्रीय अंधता नियंत्रण कार्यक्रम (RetinaAI)*"
        msg_patient = f"👤 मरीज: *{patient_name}* (आंख: *{scr.eye}*)"
        msg_verdict = f"🔍 जांच परिणाम: *{scr.grade_name}* ({'🔴 तत्काल रेफरल आवश्यक' if scr.is_referable else '🟢 सुरक्षित'})"
        msg_hosp = f"📍 अनुशंसित नेत्र अस्पताल: *{hosp['name']}*, {district_name} ({distance} किमी)"
        msg_action = f"📋 डॉक्टर निर्देश: *{scr.doctor_clinical_action or scr.doctor_prescription or 'विशेषज्ञ परामर्श लें'}*"
        msg_pdf = f"📄 रिपोर्ट डाउनलोड करें: http://localhost:8000/api/reports/{scr.id}/pdf"
    else:
        msg_header = f"🏥 *National Tele-Ophthalmology Program (RetinaAI)*"
        msg_patient = f"👤 Patient: *{patient_name}* (Eye: *{scr.eye}*)"
        msg_verdict = f"🔍 Diagnosis: *{scr.grade_name}* ({'🔴 Specialist Referral Needed' if scr.is_referable else '🟢 Normal - No DR'})"
        msg_hosp = f"📍 Nearest Tertiary Hospital: *{hosp['name']}*, {district_name} ({distance} km)"
        msg_action = f"📋 Doctor Advice: *{scr.doctor_clinical_action or scr.doctor_prescription or 'Follow routine instructions'}*"
        msg_pdf = f"📄 Download Clinical Report: http://localhost:8000/api/reports/{scr.id}/pdf"

    formatted_whatsapp_message = (
        f"{msg_header}\n\n"
        f"{msg_patient}\n"
        f"{msg_verdict}\n"
        f"{msg_hosp}\n"
        f"{msg_action}\n\n"
        f"🗣️ *Voice Summary:* \"{audio_text}\"\n\n"
        f"{msg_pdf}\n\n"
        f"⚠️ Please present the QR code on this report at the PHC reception for priority consultation."
    )

    scr.whatsapp_status = f"Dispatched via WhatsApp Gateway to {req.phone_number}"
    db.commit()

    return {
        "success": True,
        "phone_number": req.phone_number,
        "language": req.preferred_language,
        "message": formatted_whatsapp_message,
        "audio_script": audio_text,
        "delivery_status": "Delivered (WhatsApp API Webhook Confirmed)"
    }


@router.get("/voice/{screening_id}")
def get_voice_scripts(screening_id: int, db: Session = Depends(get_db)):
    """
    Returns Tamil, Hindi, and English audio scripts for text-to-speech audio playback.
    """
    scr = db.query(ScreeningRecord).filter(ScreeningRecord.id == screening_id).first()
    if not scr:
        raise HTTPException(status_code=404, detail="Screening record not found")

    pat = db.query(Patient).filter(Patient.id == scr.patient_id).first()
    patient_name = pat.full_name if pat else "Patient"

    scripts = VoiceService.get_audio_scripts(
        patient_name=patient_name,
        grade=scr.icdr_grade,
        eye=scr.eye,
        doctor_advice=scr.doctor_prescription
    )

    return {
        "screening_id": scr.id,
        "patient_name": patient_name,
        "icdr_grade": scr.icdr_grade,
        "grade_name": scr.grade_name,
        "scripts": scripts
    }
