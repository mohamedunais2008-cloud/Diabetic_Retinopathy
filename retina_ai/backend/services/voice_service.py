"""
Multilingual Patient Audio Guidance Service
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India

Provides reassuring, non-jargon spoken health explanations in:
- Tamil (தமிழ்)
- Hindi (हिंदी)
- English
"""

class VoiceService:
    @staticmethod
    def get_audio_scripts(patient_name: str, grade: int, eye: str, doctor_advice: str = None) -> dict:
        eye_name_en = "Right Eye" if eye == "OD" else "Left Eye"
        eye_name_ta = "வலது கண்" if eye == "OD" else "இடது கண்"
        eye_name_hi = "दाहिनी आंख" if eye == "OD" else "बाईं आंख"

        if grade == 0:
            en_text = f"Hello {patient_name}. Great news! Your {eye_name_en} retinal examination is normal. No diabetic eye damage was found. Please maintain healthy diet and repeat your screening in 12 months."
            ta_text = f"வணக்கம் {patient_name}. உங்கள் {eye_name_ta} பரிசோதனை நலமாக உள்ளது. சர்க்கரை நோயினால் கண் பாதிப்பு எதுவும் இல்லை. ஆரோக்கியமான உணவு முறையைப் பின்பற்றி, 1 வருடம் கழித்து மீண்டும் பரிசோதிக்கவும்."
            hi_text = f"नमस्ते {patient_name}. आपकी {eye_name_hi} की जांच सामान्य है। मधुमेह से रेटिना में कोई क्षति नहीं है। कृपया स्वस्थ आहार लें और 1 वर्ष बाद पुनः जांच कराएं।"
        elif grade == 1:
            en_text = f"Hello {patient_name}. Mild early diabetic changes were noticed in your {eye_name_en}. Your vision is safe now, but strict blood sugar and blood pressure control is needed. Re-screen in 6 months."
            ta_text = f"வணக்கம் {patient_name}. உங்கள் {eye_name_ta} பகுதியில் ஆரம்ப கட்ட சர்க்கரை நோய் மாற்றங்கள் உள்ளன. கவலைப்பட வேண்டாம், உங்கள் சர்க்கரை அளவைக் கட்டுப்பாட்டில் வைத்து 6 மாதங்களில் மீண்டும் பரிசோதிக்கவும்."
            hi_text = f"नमस्ते {patient_name}. आपकी {eye_name_hi} में शुरुआती मधुमेह के हल्के लक्षण दिखे हैं। अपनी शुगर और बीपी नियंत्रित रखें और 6 महीने में दोबारा जांच कराएं।"
        elif grade == 2:
            en_text = f"Attention {patient_name}. Moderate diabetic retinopathy detected in your {eye_name_en}. Dr. Meenakshi recommends a comprehensive specialist check-up at the District Eye Hospital within 2 to 4 weeks to prevent vision loss."
            ta_text = f"கவனம் {patient_name}. உங்கள் {eye_name_ta} பகுதியில் மிதமான சர்க்கரை நோய் பாதிப்பு உள்ளது. கண் பார்வை குறையாமல் பாதுகாக்க, 2 முதல் 4 வாரங்களுக்குள் மாவட்ட கண் மருத்துவமனைக்கு சென்று சிறப்பு மருத்துவரை அணுகவும்."
            hi_text = f"ध्यान दें {patient_name}. आपकी {eye_name_hi} में मध्यम डायबिटिक रेटिनोपैथी पाई गई है। दृष्टि सुरक्षा के लिए 2 से 4 सप्ताह में जिला नेत्र अस्पताल में विशेषज्ञ डॉक्टर से परामर्श लें।"
        elif grade == 3:
            en_text = f"Urgent notice for {patient_name}. Severe diabetic changes detected in your {eye_name_en}. Immediate consultation at the District Eye Hospital is required within 1 to 2 weeks for laser protection."
            ta_text = f"அவசர அறிவிப்பு {patient_name}. உங்கள் {eye_name_ta} பகுதியில் தீவிர சர்க்கரை நோய் பாதிப்பு உள்ளது. லேசர் சிகிச்சை மூலம் பார்வையைப் பாதுகாக்க 1 முதல் 2 வாரங்களுக்குள் அரசு அல்லது மாவட்ட கண் மருத்துவமனைக்கு செல்லவும்."
            hi_text = f"अति आवश्यक {patient_name}. आपकी {eye_name_hi} में गंभीर रेटिनोपैथी के लक्षण हैं। लेजर सुरक्षा के लिए 1 से 2 सप्ताह में तुरंत नेत्र विशेषज्ञ से मिलें।"
        else:
            en_text = f"Emergency medical alert for {patient_name}. Advanced proliferative retinopathy detected. High risk of severe vision impairment. Please reach the tertiary eye hospital immediately within 48 to 72 hours."
            ta_text = f"முக்கிய அவசர எச்சரிக்கை {patient_name}. உங்கள் {eye_name_ta} பகுதியில் முற்றிய சர்க்கரை நோய் பாதிப்பு உள்ளது. உடனடி சிகிச்சை தேவை. தயவுசெய்து 48 மணி நேரத்திற்குள் பெரிய கண் மருத்துவமனைக்கு செல்லவும்."
            hi_text = f"आपातकालीन सूचना {patient_name}. आपकी {eye_name_hi} में उन्नत रेटिनोपैथी पाई गई है। कृपया तुरंत 48 से 72 घंटों के भीतर बड़े अस्पताल में जाएं।"

        return {
            "tamil": ta_text,
            "hindi": hi_text,
            "english": en_text,
            "doctor_custom_prescription": doctor_advice
        }
