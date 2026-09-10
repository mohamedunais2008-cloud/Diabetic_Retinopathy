"""
Root Launcher for RetinaAI
Redirects to retina_ai/run.py
"""

import os
import sys

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_DIR = os.path.join(CURRENT_DIR, "retina_ai")
if TARGET_DIR not in sys.path:
    sys.path.insert(0, TARGET_DIR)

os.chdir(TARGET_DIR)

from run import main

if __name__ == "__main__":
    main()
