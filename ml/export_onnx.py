"""
AirFusion ONNX Export & Browser Optimization Pipeline (ml/export_onnx.py)

Exports PyTorch MobileNetV3 model to a compact ONNX graph suitable for
client-side onnxruntime-web execution (budget < 10 MB).
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path
from typing import Optional
import torch

from ml.model import AirFusionVisionModel

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AirFusion-ONNX-Export")


def export_to_onnx(
    checkpoint_path: Optional[Path | str] = None,
    output_path: Path | str = "public/models/airfusion_cnn_v1.onnx",
    opset_version: int = 14
) -> Optional[Path]:
    out_file = Path(output_path)
    out_file.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Instantiating AirFusion Vision Model architecture...")
    model = AirFusionVisionModel(dropout_rate=0.0)
    model.eval()

    if checkpoint_path and Path(checkpoint_path).exists():
        logger.info(f"Loading trained weights from {checkpoint_path}...")
        state_dict = torch.load(checkpoint_path, map_location="cpu")
        model.load_state_dict(state_dict)
    else:
        logger.warning("No checkpoint provided or file not found. Exporting structural baseline weights.")

    dummy_input = torch.randn(1, 3, 224, 224, dtype=torch.float32)

    logger.info(f"Exporting to ONNX at {out_file} (opset {opset_version})...")
    try:
        torch.onnx.export(
            model,
            dummy_input,
            str(out_file),
            export_params=True,
            opset_version=opset_version,
            do_constant_folding=True,
            input_names=["input"],
            output_names=["pm25", "uncertainty", "ood_score"],
            dynamic_axes={
                "input": {0: "batch_size"},
                "pm25": {0: "batch_size"},
                "uncertainty": {0: "batch_size"},
                "ood_score": {0: "batch_size"}
            }
        )
        size_mb = out_file.stat().st_size / (1024 * 1024)
        logger.info(f"Export complete! Model file size: {size_mb:.2f} MB (Budget: 10.00 MB)")
        return out_file
    except (ImportError, ModuleNotFoundError) as e:
        logger.warning(
            f"Local ONNX exporter dependency missing: {e}. "
            "In environments without onnx/onnxscript, export is performed via Google Colab T4 runtime. "
            "See TRAINING.md and ml/notebooks/Train_AirFusion_CNN.ipynb."
        )
        return None


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Export AirFusion Vision model to ONNX")
    parser.add_argument("--checkpoint", type=str, default=None, help="Path to .pt model weights")
    parser.add_argument("--output", type=str, default="public/models/airfusion_cnn_v1.onnx", help="Output .onnx path")
    args = parser.parse_args()

    export_to_onnx(args.checkpoint, args.output)
