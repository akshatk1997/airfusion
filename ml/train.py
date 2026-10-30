"""
AirFusion Atmospheric Vision Training Pipeline (ml/train.py)

Trains MobileNetV3-Small on multi-station datasets with heteroscedastic
uncertainty loss, station-aware validation, and early stopping.
"""

from __future__ import annotations

import argparse
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import DataLoader

from ml.dataset import (
    AirQualityPhotoDataset,
    get_default_transforms,
    station_and_time_aware_split
)
from ml.model import AirFusionVisionModel, heteroscedastic_loss

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("AirFusion-Vision-Train")


def train_epoch(
    model: nn.Module,
    loader: DataLoader,
    optimizer: torch.optim.Optimizer,
    device: torch.device
) -> Dict[str, float]:
    model.train()
    total_loss = 0.0
    total_mae = 0.0
    count = 0

    for batch in loader:
        images = batch["image"].to(device)
        targets = batch["target_pm25"].to(device)
        is_ood = batch["is_ood"].to(device)

        optimizer.zero_grad()
        pm25_pred, uncertainty, ood_prob = model(images)

        # Regression loss on in-distribution samples
        in_dist_mask = (is_ood < 0.5)
        if in_dist_mask.sum() > 0:
            logvar = 2.0 * torch.log(uncertainty[in_dist_mask] + 1e-6)
            reg_loss = heteroscedastic_loss(pm25_pred[in_dist_mask], logvar, targets[in_dist_mask])
            mae = torch.abs(pm25_pred[in_dist_mask] - targets[in_dist_mask]).mean().item()
        else:
            reg_loss = torch.tensor(0.0, device=device)
            mae = 0.0

        # OOD binary classification loss
        bce_loss = nn.functional.binary_cross_entropy(ood_prob, is_ood)
        loss = reg_loss + 0.5 * bce_loss

        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=2.0)
        optimizer.step()

        batch_size = images.size(0)
        total_loss += loss.item() * batch_size
        total_mae += mae * batch_size
        count += batch_size

    return {"loss": total_loss / max(1, count), "mae": total_mae / max(1, count)}


def evaluate(
    model: nn.Module,
    loader: DataLoader,
    device: torch.device
) -> Dict[str, float]:
    model.eval()
    y_preds, y_trues = [], []

    with torch.no_grad():
        for batch in loader:
            images = batch["image"].to(device)
            targets = batch["target_pm25"].to(device)
            is_ood = batch["is_ood"].to(device)

            pm25_pred, _, _ = model(images)
            in_dist_mask = (is_ood < 0.5)

            if in_dist_mask.sum() > 0:
                y_preds.extend(pm25_pred[in_dist_mask].cpu().numpy().tolist())
                y_trues.extend(targets[in_dist_mask].cpu().numpy().tolist())

    if not y_trues:
        return {"mae": 0.0, "rmse": 0.0, "r2": 0.0}

    y_p = np.array(y_preds)
    y_t = np.array(y_trues)
    mae = float(np.mean(np.abs(y_p - y_t)))
    rmse = float(np.sqrt(np.mean((y_p - y_t) ** 2)))
    ss_tot = float(np.sum((y_t - np.mean(y_t)) ** 2))
    ss_res = float(np.sum((y_t - y_p) ** 2))
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0

    return {"mae": round(mae, 3), "rmse": round(rmse, 3), "r2": round(r2, 4)}


def run_training_pipeline(
    metadata_csv: Path | str,
    image_dir: Path | str,
    output_dir: Path | str,
    epochs: int = 15,
    batch_size: int = 32,
    lr: float = 1e-3,
    device_str: str = "cpu"
) -> Dict[str, Any]:
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    device = torch.device(device_str)

    logger.info("Loading metadata...")
    df = pd.read_csv(metadata_csv)
    train_df, val_df, test_df = station_and_time_aware_split(df)
    logger.info(f"Splits created: Train={len(train_df)}, Val={len(val_df)}, Test={len(test_df)}")

    train_ds = AirQualityPhotoDataset(train_df, image_dir, transform=get_default_transforms(is_train=True))
    val_ds = AirQualityPhotoDataset(val_df, image_dir, transform=get_default_transforms(is_train=False))
    test_ds = AirQualityPhotoDataset(test_df, image_dir, transform=get_default_transforms(is_train=False))

    train_loader = DataLoader(train_ds, batch_size=batch_size, shuffle=True, drop_last=True)
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    model = AirFusionVisionModel(dropout_rate=0.2).to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs, eta_min=1e-5)

    best_val_mae = float("inf")
    best_weights_path = output_path / "airfusion_vision_best.pt"
    history = []

    for epoch in range(1, epochs + 1):
        t0 = time.time()
        train_metrics = train_epoch(model, train_loader, optimizer, device)
        val_metrics = evaluate(model, val_loader, device)
        scheduler.step()

        elapsed = time.time() - t0
        logger.info(f"Epoch {epoch}/{epochs} ({elapsed:.1f}s) - Train Loss: {train_metrics['loss']:.4f}, Val MAE: {val_metrics['mae']:.2f}")

        history.append({
            "epoch": epoch,
            "train_loss": train_metrics["loss"],
            "val_mae": val_metrics["mae"],
            "val_rmse": val_metrics["rmse"],
            "val_r2": val_metrics["r2"]
        })

        if val_metrics["mae"] < best_val_mae:
            best_val_mae = val_metrics["mae"]
            torch.save(model.state_dict(), best_weights_path)
            logger.info(f"Saved new champion model with Val MAE: {best_val_mae:.2f}")

    # Evaluate test split on best model
    if best_weights_path.exists():
        model.load_state_dict(torch.load(best_weights_path, map_location=device))
    test_metrics = evaluate(model, test_loader, device)
    logger.info(f"Final Test Evaluation: MAE={test_metrics['mae']}, RMSE={test_metrics['rmse']}, R2={test_metrics['r2']}")

    results = {
        "best_val_mae": best_val_mae,
        "test_metrics": test_metrics,
        "training_history": history,
        "saved_checkpoint": str(best_weights_path)
    }

    metrics_log = output_path / "training_summary.json"
    metrics_log.write_text(json.dumps(results, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train AirFusion Vision PM2.5 CNN")
    parser.add_argument("--metadata", type=str, default="ml/data/metadata.csv")
    parser.add_argument("--image_dir", type=str, default="ml/data/images")
    parser.add_argument("--output_dir", type=str, default="ml/checkpoints")
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--batch_size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--device", type=str, default="cuda" if torch.cuda.is_available() else "cpu")
    args = parser.parse_args()

    run_training_pipeline(
        metadata_csv=args.metadata,
        image_dir=args.image_dir,
        output_dir=args.output_dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        device_str=args.device
    )
