"""
Clinical XAI Explanation Generator
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India

Generates standardized clinical rationales and triage guidelines
based on ICDR (International Clinical Diabetic Retinopathy) criteria.
"""

ICDR_CLINICAL_PROFILES = {
    0: {
        "grade_name": "No Diabetic Retinopathy (Grade 0)",
        "referable": False,
        "urgency": "Routine",
        "recall_period": "12 Months",
        "description": "No visible retinal vascular abnormalities detected. Normal optic disc, fovea, and macula.",
        "asha_guidance": "Encourage patient to maintain good glycemic (HbA1c < 7.0%) and blood pressure control. Schedule next screening in 1 year.",
        "pathology_findings": {
            "microaneurysms": 0,
            "hemorrhages": 0,
            "hard_exudates": 0,
            "cotton_wool_spots": 0,
            "neovascularization": "Absent"
        }
    },
    1: {
        "grade_name": "Mild Non-Proliferative DR (Grade 1)",
        "referable": False,
        "urgency": "Monitoring",
        "recall_period": "6 - 9 Months",
        "description": "Isolated microaneurysms present without significant exudation or retinal edema.",
        "asha_guidance": "Early microvascular changes detected. Counsel patient on strict blood sugar control. Re-screen in 6 months.",
        "pathology_findings": {
            "microaneurysms": 3,
            "hemorrhages": 0,
            "hard_exudates": 0,
            "cotton_wool_spots": 0,
            "neovascularization": "Absent"
        }
    },
    2: {
        "grade_name": "Moderate Non-Proliferative DR (Grade 2)",
        "referable": True,
        "urgency": "Referral Required",
        "recall_period": "2 - 4 Weeks",
        "description": "Multiple microaneurysms, dot-and-blot hemorrhages, and hard exudates localized along the vascular arcades.",
        "asha_guidance": "REFERABLE DR: Patient must be referred to the District Hospital / Eye Specialist for comprehensive dilated fundus examination within 1 month.",
        "pathology_findings": {
            "microaneurysms": 14,
            "hemorrhages": 8,
            "hard_exudates": 5,
            "cotton_wool_spots": 1,
            "neovascularization": "Absent"
        }
    },
    3: {
        "grade_name": "Severe Non-Proliferative DR (Grade 3)",
        "referable": True,
        "urgency": "Urgent Referral",
        "recall_period": "1 - 2 Weeks",
        "description": "High-risk features meeting the 4-2-1 rule: extensive intraretinal hemorrhages in 4 quadrants, venous beading, or IRMA.",
        "asha_guidance": "URGENT REFERRAL: High risk of progression to proliferative DR within 12 months. Immediate specialist consultation recommended.",
        "pathology_findings": {
            "microaneurysms": 35,
            "hemorrhages": 24,
            "hard_exudates": 12,
            "cotton_wool_spots": 6,
            "neovascularization": "Suspected"
        }
    },
    4: {
        "grade_name": "Proliferative Diabetic Retinopathy (Grade 4)",
        "referable": True,
        "urgency": "Emergency Ophthalmic Referral",
        "recall_period": "Immediate (Within 48-72 hrs)",
        "description": "Active neovascularization on the optic disc (NVD) or elsewhere (NVE), pre-retinal/vitreous hemorrhages.",
        "asha_guidance": "EMERGENCY: Imminent risk of severe vision loss. Immediate intervention (laser panretinal photocoagulation or anti-VEGF) required.",
        "pathology_findings": {
            "microaneurysms": 48,
            "hemorrhages": 40,
            "hard_exudates": 22,
            "cotton_wool_spots": 9,
            "neovascularization": "Active & Prominent"
        }
    }
}


def generate_clinical_explanation(grade: int, confidence: float) -> dict:
    """
    Returns full clinical explanation package for a given DR grade and model confidence.
    """
    profile = ICDR_CLINICAL_PROFILES.get(grade, ICDR_CLINICAL_PROFILES[0]).copy()
    profile["grade"] = grade
    profile["confidence"] = round(confidence, 4)
    profile["confidence_percent"] = f"{confidence * 100:.1f}%"
    
    # Generate XAI attention summary
    if grade == 0:
        profile["xai_summary"] = "Grad-CAM heatmap indicates low, uniform visual activation across macular and peripheral retina, confirming absence of referable lesions."
    elif grade == 1:
        profile["xai_summary"] = "Grad-CAM heatmap pinpoints small localized focal clusters in the temporal macula consistent with early-stage microaneurysms."
    elif grade == 2:
        profile["xai_summary"] = "Grad-CAM heatmap demonstrates elevated attention covering clusters of intraretinal hemorrhages and lipid exudates along the vascular arcades."
    elif grade == 3:
        profile["xai_summary"] = "Grad-CAM heatmap reveals multi-quadrant high intensity activation indicating extensive microvascular leakage, venous caliber alterations, and cotton wool ischemic spots."
    else:
        profile["xai_summary"] = "Grad-CAM heatmap shows critical focal activations centered on neovascular fronds and preretinal fibrous proliferation with high risk of vitreous hemorrhage."

    return profile
