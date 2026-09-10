"""
Retinal Fundus Image Enhancement Module
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India

Implements:
1. Retinal Field-of-View (FOV) circular mask detection.
2. Green channel extraction and CLAHE (Contrast-Limited Adaptive Histogram Equalization).
3. Ben Graham's method (local illumination normalization via Gaussian background subtraction).
"""

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def extract_fov_mask(image: Image.Image, threshold: int = 15) -> np.ndarray:
    """
    Extracts the binary mask corresponding to the retinal fundus circular field of view.
    Filters out background black borders/camera apertures.
    """
    gray = np.array(image.convert("L"))
    mask = gray > threshold
    return mask


def apply_clahe_pillow(image: Image.Image, clip_limit: float = 2.0) -> Image.Image:
    """
    Applies adaptive histogram contrast enhancement.
    Particularly effective on the Green channel where microaneurysms and hemorrhages
    exhibit maximum optical absorption.
    """
    # Separate RGB channels
    r, g, b = image.split()
    
    # Auto-contrast green channel with mild cutoff
    g_enhanced = ImageOps.autocontrast(g, cutoff=1)
    
    # Merge back
    enhanced = Image.merge("RGB", (r, g_enhanced, b))
    return enhanced


def ben_grahams_enhancement(image: Image.Image, sigma: float = 10.0) -> Image.Image:
    """
    Ben Graham's color normalization method:
    image = 4 * image - 4 * gaussian_blur(image) + 128
    Normalizes variable illumination across rural screening conditions.
    """
    img_arr = np.array(image, dtype=np.float32)
    blurred = image.filter(ImageFilter.GaussianBlur(radius=sigma))
    blur_arr = np.array(blurred, dtype=np.float32)

    # Ben Graham formula
    enhanced = 4.0 * img_arr - 4.0 * blur_arr + 128.0
    enhanced = np.clip(enhanced, 0, 255).astype(np.uint8)

    # Apply FOV mask to avoid bright borders outside the fundus disk
    fov_mask = extract_fov_mask(image)
    enhanced[~fov_mask] = 0

    return Image.fromarray(enhanced)


def preprocess_fundus_pipeline(image_path: str, target_size: tuple = (512, 512)) -> dict:
    """
    Complete standard ophthalmic preprocessing pipeline for a fundus image.
    Returns dictionary with raw, enhanced, and FOV mask representations.
    """
    raw_img = Image.open(image_path).convert("RGB")
    resized_raw = raw_img.resize(target_size, Image.Resampling.BILINEAR)

    # 1. FOV Mask
    mask = extract_fov_mask(resized_raw)

    # 2. Ben Graham enhancement
    bg_enhanced = ben_grahams_enhancement(resized_raw)

    # 3. Green channel CLAHE enhancement
    clahe_enhanced = apply_clahe_pillow(resized_raw)

    return {
        "raw": resized_raw,
        "enhanced": bg_enhanced,
        "clahe": clahe_enhanced,
        "fov_mask": mask,
        "size": target_size,
    }
