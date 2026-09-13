# 🧠 RetinaAI - Machine Learning Teammate Integration Guide
**Problem Statement 26038: Explainable AI for Diabetic Retinopathy Screening in Rural India**  
**Smart India Hackathon (SIH 2026)**

Welcome! This application has a complete, working frontend and backend for all 4 healthcare stakeholders:
1. **Nurse / ASHA Worker**: Patient ingestion, camera fundus image capture, automated IQA (Image Quality Assessment), live GPS camp tagging.
2. **Ophthalmologist (Doctor)**: 4x digital loupe, micrometer caliper, certified clinical diagnosis, voice dictation, and automated patient email report dispatch.
3. **Patient / Citizen**: Password-free direct access using Mobile Phone or Patient ID, bilingual clinical report, digital prescription, and referral hospital directions.
4. **District Health Officer (Admin)**: Epidemiological heatmap, compliance tracking, and disease progression simulation.

---

## ⚡ Quick Start (Run the App in 2 Steps)

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   *(Optional for your ML model: `pip install torch torchvision` or `pip install onnxruntime`)*

2. **Launch the Application:**
   ```bash
   python run.py
   ```
   Open your browser at: **http://localhost:8000**

---

## 🔌 Where to Plug In Your Machine Learning Model

The backend is built with a **Pluggable Adapter Pattern** in:  
📁 `retina_ai/backend/services/inference.py`

### Option 1: Drop-in ONNX or PyTorch Model (Zero Code Required!)
Simply place your exported model in:  
📁 `retina_ai/models/exported/`
- Name your model file: **`dr_model.onnx`** (or **`dr_model.pt`**)

The backend **automatically detects** the file on startup and routes all real fundus screenings through your neural network!

#### Input Specifications:
- **Input Shape**: `[batch_size, 3, 512, 512]` (RGB fundus image)
- **Normalization**: Standard ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`
- **Preprocessing**: The backend already automatically enhances images using green-channel CLAHE + FOV circular mask (`retina_ai/preprocessing/enhancement.py`).

#### Output Specifications:
- **Logits / Probabilities**: Array/Tensor of size `[batch_size, 5]` corresponding to the 5 ICDR classes:
  - `0`: **No DR** (Normal / Non-referable)
  - `1`: **Mild NPDR** (Microaneurysms only)
  - `2`: **Moderate NPDR** (Microaneurysms, hemorrhages - Referable)
  - `3`: **Severe NPDR** (4-2-1 rule met - Urgent Referral)
  - `4`: **Proliferative DR** (Neovascularization, vitreous hemorrhage - Emergency)

---

### Option 2: Custom Python PyTorch / TensorFlow / Scikit-learn Code
If you want to use custom inference logic or specific weight loading:
1. Open: `retina_ai/backend/services/inference.py`
2. Locate the class `InferenceService` (around line 130).
3. Update `run_inference(cls, image: Image.Image)` to call your custom model:
   ```python
   # Example in backend/services/inference.py:
   import torch
   from PIL import Image

   # Load your model once
   my_model = torch.load("models/exported/my_weights.pth")
   my_model.eval()

   def predict(self, image: Image.Image) -> dict:
       tensor = my_transform(image).unsqueeze(0)
       with torch.no_grad():
           outputs = my_model(tensor)
           probs = torch.softmax(outputs, dim=1)[0].tolist()
           grade = int(torch.argmax(outputs, dim=1).item())
       return {
           "grade": grade,
           "confidence": float(probs[grade]),
           "probabilities": probs,
           "model_source": "Custom PyTorch Model",
           "is_neural_network": True
       }
   ```

---

## 🔑 Demo Login Accounts for Testing

| Role | Username / Email | Password |
| :--- | :--- | :--- |
| **Nurse / ASHA Worker** | `nurse@retina.ai` | `nurse123` |
| **Doctor Specialist** | `doctor@retina.ai` | `doctor123` |
| **District Admin (DHO)** | `admin@retina.ai` | `admin123` |
| **Patient / Citizen** | `PAT-2026-0001` or Phone `9842111021` | **No Password Needed** |

---

## 📧 Email Notification Setup
Clinical reports are automatically sent to patient email addresses when the Doctor signs the certified report.  
The system is configured in:  
📁 `retina_ai/backend/email_config.json`

All the best! Let's win Smart India Hackathon 2026! 🚀
