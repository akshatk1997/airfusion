"""
Unit tests for AirFusion Atmospheric Vision CNN Pipeline (ml/tests/test_cnn_pipeline.py)
"""

import sys
from pathlib import Path
import numpy as np
import pandas as pd
from PIL import Image

import torch
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml.dataset import (
    get_default_transforms,
    compute_perceptual_hash,
    station_and_time_aware_split,
    AirQualityPhotoDataset
)
from ml.model import AirFusionVisionModel, compute_residual_fusion


def test_default_transforms_shape_and_normalization():
    """Verify transforms resize to 224x224 and output standard 3-channel PyTorch tensor."""
    img = Image.new("RGB", (640, 480), color=(100, 150, 200))
    transform = get_default_transforms(image_size=224, is_train=False)
    tensor = transform(img)

    assert tensor.shape == (3, 224, 224)
    assert isinstance(tensor, torch.Tensor)
    assert tensor.dtype == torch.float32


def test_perceptual_hash_dhash():
    """Verify difference hash produces consistent 16-hex characters for near-identical frames."""
    img1 = Image.new("RGB", (200, 200), color=(120, 140, 160))
    img2 = Image.new("RGB", (200, 200), color=(120, 140, 160))
    # Slight pixel difference
    img2.putpixel((10, 10), (121, 141, 161))

    h1 = compute_perceptual_hash(img1)
    h2 = compute_perceptual_hash(img2)

    assert len(h1) == 16
    assert len(h2) == 16
    assert h1 == h2  # Small noise should yield identical hash


def test_station_and_time_aware_split_no_leakage():
    """Verify zero station-day leakage between train and test splits."""
    data = []
    stations = [f"station_{i}" for i in range(10)]
    dates = [f"2026-10-{d:02d}" for d in range(1, 21)]

    for s in stations:
        for d in dates:
            data.append({
                "filename": f"{s}_{d}.jpg",
                "station_id": s,
                "date": d,
                "timestamp": f"{d} 12:00:00",
                "pm25": float(np.random.uniform(10, 150))
            })

    df = pd.DataFrame(data)
    train_df, val_df, test_df = station_and_time_aware_split(df, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)

    assert len(train_df) > 0
    assert len(val_df) > 0
    assert len(test_df) > 0

    # Test for station-day overlap
    train_pairs = set(zip(train_df["station_id"], train_df["date"]))
    test_pairs = set(zip(test_df["station_id"], test_df["date"]))
    leakage = train_pairs.intersection(test_pairs)

    assert len(leakage) == 0, f"Data leakage detected across train and test: {len(leakage)} station-days overlap!"


def test_airfusion_vision_model_forward():
    """Verify model forward pass outputs non-negative PM2.5, positive uncertainty, and valid OOD score."""
    model = AirFusionVisionModel(dropout_rate=0.0)
    model.eval()

    dummy_input = torch.randn(2, 3, 224, 224, dtype=torch.float32)
    with torch.no_grad():
        pm25_pred, uncertainty, ood_prob = model(dummy_input)

    assert pm25_pred.shape == (2,)
    assert uncertainty.shape == (2,)
    assert ood_prob.shape == (2,)

    # PM2.5 strictly non-negative
    assert torch.all(pm25_pred >= 0.0)
    # Uncertainty standard deviation strictly positive
    assert torch.all(uncertainty > 0.0)
    # OOD probability strictly between 0 and 1
    assert torch.all((ood_prob >= 0.0) & (ood_prob <= 1.0))


def test_residual_fusion_bounds():
    """Verify that OOD scenes or extreme uncertainty gracefully default to meteorological baseline."""
    # Scenario A: High OOD score (indoor photo, ood_score=0.95)
    res_ood = compute_residual_fusion(
        baseline_pm25=45.0,
        cnn_pm25=180.0,
        uncertainty_sigma=5.0,
        ood_score=0.95
    )
    # Should reject and keep baseline
    assert res_ood["is_ood_rejected"] is True
    assert abs(res_ood["fused_pm25"] - 45.0) < 3.0

    # Scenario B: High uncertainty (sigma=50)
    res_uncertain = compute_residual_fusion(
        baseline_pm25=50.0,
        cnn_pm25=120.0,
        uncertainty_sigma=50.0,
        ood_score=0.05
    )
    # Fusion weight should be nearly zero (<0.001)
    assert res_uncertain["fusion_weight_lambda"] < 0.001
    assert abs(res_uncertain["fused_pm25"] - 50.0) < 0.2

    # Scenario C: Confident in-distribution outdoor image (sigma=0.5, ood=0.0)
    res_confident = compute_residual_fusion(
        baseline_pm25=30.0,
        cnn_pm25=60.0,
        uncertainty_sigma=0.5,
        ood_score=0.0
    )
    # Lambda = 1 / (1 + 0.25) = 0.8
    assert res_confident["fusion_weight_lambda"] > 0.7
    assert 50.0 < res_confident["fused_pm25"] < 60.0
