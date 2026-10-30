# AirFusion Atmospheric Vision Training Guide (TRAINING.md)

This guide documents the exact, reproducible workflow to train the AirFusion MobileNetV3 atmospheric vision model and export it to ONNX for client-side browser inference (`ENABLE_CNN_FUSION`).

---

## 1. Quickstart with Free Google Colab (Recommended)

Because full dataset training requires $\sim 25\text{ GB}$ of multi-source imagery and GPU acceleration (NVIDIA T4 or better), the fastest way to train the model is via the provided Colab notebook:

1. Open [Google Colab](https://colab.research.google.com).
2. Upload `ml/notebooks/Train_AirFusion_CNN.ipynb`.
3. Under **Runtime &rarr; Change runtime type**, select **T4 GPU** (Free tier).
4. Run all cells:
   - Cell 1: Clones dependencies and installs `torch`, `torchvision`, `onnx`, `onnxscript`.
   - Cell 2: Downloads the 4 verified open datasets (PM25Vision, India/Nepal, Dhaka, HVAQ).
   - Cell 3: Runs perceptual hashing (`dHash`) to remove duplicate webcam frames.
   - Cell 4: Executes station-aware and time-aware 70/15/15 chronological partitioning.
   - Cell 5: Fine-tunes `AirFusionVisionModel` (MobileNetV3-Small) with heteroscedastic uncertainty loss.
   - Cell 6: Evaluates test MAE, RMSE, $R^2$, and OOD accuracy.
   - Cell 7: Exports quantized ONNX model to `airfusion_cnn_v1.onnx` ($<10\text{ MB}$).
5. Download `airfusion_cnn_v1.onnx` and place it in `public/models/airfusion_cnn_v1.onnx`.

---

## 2. Local Environment Setup & Training Commands

If running on a dedicated Linux/Windows workstation with an NVIDIA GPU and internet access:

### Step 1: Install Training Dependencies
```bash
pip install torch torchvision numpy pandas pillow onnx onnxscript tqdm
```
*(Note: These dependencies are for offline training in `ml/` only and are excluded from production Vercel deployment via `.vercelignore`)*.

### Step 2: Download Dataset Metadata & Imagery
```bash
# 1. PM25Vision (CC-BY-4.0) via Hugging Face
python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='DeadCardassian/PM25Vision', repo_type='dataset', local_dir='ml/data/pm25vision')"

# 2. Air Pollution Image Dataset from India and Nepal (CC0-1.0) via Kaggle
kaggle datasets download -d sanskar457/air-pollution-image-dataset-from-india-and-nepal -p ml/data/india_nepal --unzip

# 3. Aggregate metadata
python -c "
import pandas as pd
from pathlib import Path
# Prepare merged metadata with columns: [filename, station_id, date, timestamp, pm25, baseline_pm25, is_ood]
"
```

### Step 3: Run Training Loop
```bash
python -m ml.train \
  --metadata ml/data/metadata.csv \
  --image_dir ml/data/images \
  --output_dir ml/checkpoints \
  --epochs 20 \
  --batch_size 32 \
  --lr 0.001 \
  --device cuda
```

### Step 4: Export & Validate Quantized ONNX Model
```bash
python -m ml.export_onnx \
  --checkpoint ml/checkpoints/airfusion_vision_best.pt \
  --output public/models/airfusion_cnn_v1.onnx
```

---

## 3. Web Application Mode C Behavior

Until training is executed and `airfusion_cnn_v1.onnx` is placed in `public/models/`, the web application runs in **Mode C ("Model Not Trained Yet")**:
- The Photo AQI interface displays a transparent status badge: `MODEL CHECKPOINT PENDING TRAINING`.
- The user can still upload outdoor photos or use camera capture; the client performs image quality and OOD checks in JavaScript.
- The UI displays the verified real-time meteorological baseline (from Open-Meteo) and shows educational walkthroughs explaining how residual fusion ($\hat{y}_{\text{final}} = \hat{y}_{\text{baseline}} + \lambda(\hat{y}_{\text{cnn}} - \hat{y}_{\text{baseline}})$) operates.
- Once `public/models/airfusion_cnn_v1.onnx` is placed in the directory, `onnxruntime-web` automatically activates dynamic residual fusion.
