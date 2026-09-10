# Exported Models Directory

Place the final production weights here:
- `dr_model.onnx` (Recommended format for platform-independent high-performance inference)
- or `dr_model.pt` (TorchScript / PyTorch model)

The backend (`retina_ai/backend/services/inference.py`) automatically checks this directory at startup:
- If a model file is detected, it immediately activates neural network inference.
- If no model is found yet, it runs in simulated clinical mode with deterministic ophthalmic feature extraction so the full frontend, API, and PDF reports can be demonstrated seamlessly.
