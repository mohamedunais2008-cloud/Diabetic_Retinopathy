"""
Preprocessing Service for RetinaAI Backend
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
from PIL import Image
import sys

# Ensure retina_ai root is in sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from preprocessing.enhancement import preprocess_fundus_pipeline
from preprocessing.noise_reduction import smooth_preserving_edges


class PreprocessingService:
    @staticmethod
    def process_and_save_fundus(input_path: str, output_dir: str, file_prefix: str) -> dict:
        """
        Runs the standard ophthalmology fundus enhancement pipeline on input fundus photo.
        Saves the resulting images to output_dir and returns their file paths.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Run preprocessing pipeline
        pipeline_result = preprocess_fundus_pipeline(input_path, target_size=(512, 512))
        
        # Additional edge-preserving smoothing
        smoothed_enhanced = smooth_preserving_edges(pipeline_result["enhanced"])

        # Save preprocessed image
        preprocessed_filename = f"{file_prefix}_enhanced.jpg"
        preprocessed_filepath = os.path.join(output_dir, preprocessed_filename)
        smoothed_enhanced.save(preprocessed_filepath, quality=92)

        return {
            "preprocessed_filepath": preprocessed_filepath,
            "preprocessed_filename": preprocessed_filename,
            "image_pil": smoothed_enhanced,
            "raw_pil": pipeline_result["raw"]
        }
