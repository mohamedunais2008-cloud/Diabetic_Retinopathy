"""
Explainable AI (XAI) Service for RetinaAI Backend
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
from PIL import Image
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from xai.gradcam import generate_synthetic_gradcam_heatmap, blend_gradcam_with_image
from xai.explanation import generate_clinical_explanation


class XAIService:
    @staticmethod
    def generate_and_save_gradcam(
        raw_image: Image.Image,
        grade: int,
        output_dir: str,
        file_prefix: str,
        alpha: float = 0.45
    ) -> dict:
        """
        Generates Grad-CAM visual heatmap for the predicted DR grade,
        blends it with the fundus photograph, and saves it to disk.
        """
        os.makedirs(output_dir, exist_ok=True)

        # 1. Generate colormapped heatmap
        heatmap_pil = generate_synthetic_gradcam_heatmap(raw_image, grade, target_size=(512, 512))

        # 2. Blend with original image
        blended_pil = blend_gradcam_with_image(raw_image, heatmap_pil, alpha=alpha)

        # 3. Save to disk
        gradcam_filename = f"{file_prefix}_gradcam.jpg"
        gradcam_filepath = os.path.join(output_dir, gradcam_filename)
        blended_pil.save(gradcam_filepath, quality=92)

        return {
            "gradcam_filepath": gradcam_filepath,
            "gradcam_filename": gradcam_filename,
            "heatmap_pil": heatmap_pil,
            "blended_pil": blended_pil
        }

    @staticmethod
    def get_clinical_explanation(grade: int, confidence: float) -> dict:
        """
        Retrieves standardized clinical findings and ASHA guidance.
        """
        return generate_clinical_explanation(grade, confidence)
