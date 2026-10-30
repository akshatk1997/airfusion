# AirFusion Atmospheric Vision & CNN Photo AQI Module (`ml/`)

This directory contains the offline machine learning training, evaluation, and ONNX export pipeline for AirFusion's image-based PM2.5 estimation engine.

## Architecture Highlights

1. **Edge-First Deployment**: The model exports to quantized ONNX format (`public/models/airfusion_cnn_v1.onnx`, target budget $<10\text{ MB}$), designed to execute purely client-side in the user's browser via `onnxruntime-web`.
2. **Residual Fusion Formulation**: Rather than relying exclusively on vision (which can mistake morning fog for smog or fail under overcast skies), AirFusion combines vision with meteorological reanalysis:
   $$\hat{y}_{\text{final}} = \hat{y}_{\text{baseline}} + \lambda \times (\hat{y}_{\text{cnn}} - \hat{y}_{\text{baseline}})$$
   where:
   - $\hat{y}_{\text{baseline}}$ is real-time meteorological PM2.5 from Open-Meteo.
   - $\lambda = \frac{1}{1 + \sigma^2} \times \text{OOD\_confidence}$. When optical uncertainty $\sigma^2$ is elevated or out-of-distribution confidence drops, $\lambda \to 0$ and the system gracefully defaults to the meteorological baseline.
3. **Out-of-Distribution (OOD) Gating**: Rejects non-outdoor scenes (indoor ceilings, close-up portraits, night scenes without street illumination) before inference.
4. **Data Leakage Prevention**: Station-aware and time-aware splitting ensures that no photos from the same monitoring station on the same calendar day appear in both training and test sets.

## Module Structure

- `dataset.py`: Multi-source data loader (PM25Vision, India/Nepal dataset, Dhaka smartphone, HVAQ) with perceptual hashing and split management.
- `model.py`: MobileNetV3-Small vision backbone with heteroscedastic uncertainty regression head and OOD gate.
- `train.py`: Offline training loop with validation early stopping and metric logging.
- `export_onnx.py`: Quantization and export to `public/models/airfusion_cnn_v1.onnx`.
- `notebooks/Train_AirFusion_CNN.ipynb`: Interactive Google Colab notebook for GPU-accelerated training.
