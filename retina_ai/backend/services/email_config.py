"""
SMTP & Email Configuration Manager
Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India
"""

import os
import json

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "email_config.json")


def get_smtp_config() -> dict:
    default_config = {
        "smtp_host": os.getenv("SMTP_HOST", "smtp.gmail.com"),
        "smtp_port": int(os.getenv("SMTP_PORT", 587)),
        "smtp_user": os.getenv("SMTP_USER", ""),
        "smtp_password": os.getenv("SMTP_PASSWORD", ""),
        "sender_name": os.getenv("SMTP_SENDER_NAME", "RetinaAI National Eye Care Program"),
        "is_configured": False
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                default_config.update(data)
        except Exception as e:
            print(f"[EmailConfig] Error reading config file: {e}")

    default_config["is_configured"] = bool(default_config.get("smtp_user") and default_config.get("smtp_password"))
    return default_config


def save_smtp_config(host: str, port: int, user: str, password: str, sender_name: str = None) -> dict:
    config = {
        "smtp_host": host.strip() or "smtp.gmail.com",
        "smtp_port": int(port) if port else 587,
        "smtp_user": user.strip(),
        "smtp_password": password.strip(),
        "sender_name": sender_name.strip() if sender_name else "RetinaAI National Eye Care Program"
    }

    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)

    config["is_configured"] = bool(config.get("smtp_user") and config.get("smtp_password"))
    return config
