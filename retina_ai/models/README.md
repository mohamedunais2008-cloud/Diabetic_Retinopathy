# Machine Learning Models Directory (Problem Statement 26038)

This directory houses the deep learning architectures and trained weights for Diabetic Retinopathy screening and lesion detection.

## Directory Structure
- `qnet/`: **QNet** (Quantized / Quick Network) for ultra-low latency screening at rural Primary Health Centres (PHCs).
- `lnet/`: **LNet** (Lesion Localization Network) for sub-pixel detection of microaneurysms, hemorrhages, and exudates.
- `gnet/`: **GNet** (Grading Network) for 5-class ICDR Diabetic Retinopathy classification (Grades 0 to 4).
- `exported/`: Target folder for the ML teammate to place production weights (`.onnx` or `.pt`).

## Integration Instructions for ML Teammate
To plug your trained model into the Backend:
1. Export your trained model to ONNX format (preferred) or PyTorch Script format:
   - File path: `retina_ai/models/exported/dr_model.onnx` (or `dr_model.pt`)
2. Model Input Specifications:
   - **Input Shape**: `[batch_size, 3, 512, 512]` (RGB fundus image)
   - **Normalization**: Standard ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`
   - **Preprocessing**: Preprocessed using the green-channel CLAHE + FOV crop pipeline in `retina_ai/preprocessing/enhancement.py`.
3. Model Output Specifications:
   - **Output Shape**: `[batch_size, 5]` logits corresponding to:
     - `0`: No DR (Normal)
     - `1`: Mild Non-Proliferative DR (Microaneurysms only)
     - `2`: Moderate Non-Proliferative DR (Hemorrhages / Microaneurysms)
     - `3`: Severe Non-Proliferative DR (4-2-1 rule met)
     - `4`: Proliferative DR (Neovascularization, Vitreous hemorrhage)
   - **Referable DR Threshold**:
     - Any case with **Grade >= 2** is classified as **Referable DR** requiring clinical ophthalmologist triage.

## Export snippet (PyTorch -> ONNX)
```python
import torch

# Assuming `model` is your trained model
model.eval()
dummy_input = torch.randn(1, 3, 512, 512)
torch.onnx.export(
    model,
    dummy_input,
    "retina_ai/models/exported/dr_model.onnx",
    input_names=["input_image"],
    output_names=["dr_logits"],
    dynamic_axes={"input_image": {0: "batch_size"}, "dr_logits": {0: "batch_size"}},
    opset_version=14
)
print("Model successfully exported to models/exported/dr_model.onnx")
```

## MATLAB Deep Learning Toolbox Export
```matlab
% In MATLAB:
exportONNXNetwork(net, 'models/exported/dr_model.onnx');
```
