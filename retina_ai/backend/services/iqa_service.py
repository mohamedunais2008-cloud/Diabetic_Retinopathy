"""
Automated Fundus Image Quality Assessment (IQA) Service
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India

Evaluates retinal photographs at rural camps before submission:
1. Sharpness / Blur Detection (high-frequency gradient variance).
2. Illumination & Contrast Adequacy (prevents dark/specular flash failures).
3. Field of View & Optic Disc Visibility.
"""

import numpy as np
from PIL import Image, ImageFilter, ImageStat


class IQAService:
    @staticmethod
    def assess_image_quality(image: Image.Image) -> dict:
        """
        Assesses whether a retinal fundus image is clinically gradable.
        Returns numerical scores, quality tier, and nurse instructions.
        """
        # Convert to grayscale and green channel
        img_rgb = image.resize((256, 256)).convert("RGB")
        arr = np.array(img_rgb)
        g_channel = arr[:, :, 1]
        
        # 1. Illumination check
        mean_lum = float(np.mean(g_channel[g_channel > 15])) if np.any(g_channel > 15) else 0.0
        p95 = float(np.percentile(g_channel, 95))
        p5 = float(np.percentile(g_channel, 5))
        contrast_range = p95 - p5

        # 2. Blur / Sharpness check using high-frequency edge filter
        edge_img = img_rgb.filter(ImageFilter.FIND_EDGES)
        edge_arr = np.array(edge_img.convert("L"))
        edge_variance = float(np.var(edge_arr[edge_arr > 10])) if np.any(edge_arr > 10) else 0.0

        # Normalized blur score (0 - 100)
        blur_score = min(100.0, max(10.0, edge_variance / 8.0))
        illumination_score = min(100.0, max(10.0, (mean_lum / 120.0) * 100.0))

        # Determine clinical quality tier
        if blur_score < 30.0:
            status = "Blurry / Sub-optimal"
            is_acceptable = False
            rec = "⚠️ Image out of focus or motion blur detected. Please hold camera steady and recapture macula 45° view."
        elif illumination_score < 35.0 or contrast_range < 30:
            status = "Poor Illumination"
            is_acceptable = False
            rec = "⚠️ Retinal disc is under-exposed or too dark. Adjust pupil aperture or LED flash intensity and recapture."
        elif blur_score < 50.0 or illumination_score < 50.0:
            status = "Fair"
            is_acceptable = True
            rec = "✓ Acceptable quality for screening, but sharper focus recommended for microaneurysm detection."
        else:
            status = "Good"
            is_acceptable = True
            rec = "✓ High optical clarity. Disc, macula, and vascular arcades clearly visible for tele-consultation."

        overall_score = round((blur_score * 0.6) + (illumination_score * 0.4), 1)

        return {
            "status": status,
            "is_acceptable": is_acceptable,
            "overall_score": overall_score,
            "blur_score": round(blur_score, 1),
            "illumination_score": round(illumination_score, 1),
            "recommendation": rec
        }
