"""
Model Evaluation Module for AirFusion.
Calculates time-series regression metrics (MAE, RMSE, R², MAPE) and
classification metrics for high-pollution threshold event detection (Recall, Precision, F1).
"""

from __future__ import annotations

import logging
from typing import Dict, Any, Tuple
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.config import HIGH_POLLUTION_PM25_THRESHOLD

logger = logging.getLogger("airfusion.evaluation")


def calculate_regression_metrics(
    y_true: np.ndarray,
    y_pred: np.ndarray
) -> Dict[str, float]:
    """
    Computes standard regression evaluation metrics:
    - MAE: Mean Absolute Error
    - RMSE: Root Mean Squared Error
    - R²: Coefficient of Determination
    - MAPE: Mean Absolute Percentage Error (epsilon protected)
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    # Filter any NaNs
    valid = (~np.isnan(y_true)) & (~np.isnan(y_pred))
    yt = y_true[valid]
    yp = y_pred[valid]

    if len(yt) == 0:
        return {"mae": 0.0, "rmse": 0.0, "r2": 0.0, "mape": 0.0}

    mae = float(mean_absolute_error(yt, yp))
    rmse = float(np.sqrt(mean_squared_error(yt, yp)))
    r2 = float(r2_score(yt, yp))

    # Protected MAPE to prevent zero division
    epsilon = 1.0
    mape = float(np.mean(np.abs((yt - yp) / np.maximum(yt, epsilon))) * 100.0)

    return {
        "mae": round(mae, 3),
        "rmse": round(rmse, 3),
        "r2": round(r2, 4),
        "mape": round(mape, 2)
    }


def calculate_high_pollution_detection(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    threshold: float = HIGH_POLLUTION_PM25_THRESHOLD
) -> Dict[str, Any]:
    """
    Evaluates how effectively the model detects unsafe high-pollution episodes.
    Converts continuous values into binary classifications (Safe vs Unsafe)
    and computes True Positives, False Positives, Precision, Recall, and F1-score.
    """
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    valid = (~np.isnan(y_true)) & (~np.isnan(y_pred))
    yt = y_true[valid]
    yp = y_pred[valid]

    if len(yt) == 0:
        return {
            "threshold": threshold,
            "total_events": 0,
            "detected_events": 0,
            "precision": 0.0,
            "recall": 0.0,
            "f1_score": 0.0,
            "accuracy": 0.0
        }

    actual_unsafe = yt >= threshold
    predicted_unsafe = yp >= threshold

    tp = int(np.sum(actual_unsafe & predicted_unsafe))
    fp = int(np.sum((~actual_unsafe) & predicted_unsafe))
    fn = int(np.sum(actual_unsafe & (~predicted_unsafe)))
    tn = int(np.sum((~actual_unsafe) & (~predicted_unsafe)))

    precision = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
    recall = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    f1 = float(2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0.0
    accuracy = float((tp + tn) / len(yt)) if len(yt) > 0 else 0.0

    return {
        "threshold": threshold,
        "total_actual_unsafe": int(np.sum(actual_unsafe)),
        "total_predicted_unsafe": int(np.sum(predicted_unsafe)),
        "true_positives": tp,
        "false_positives": fp,
        "false_negatives": fn,
        "true_negatives": tn,
        "precision": round(precision, 3),
        "recall": round(recall, 3),
        "f1_score": round(f1, 3),
        "accuracy": round(accuracy, 3)
    }


def evaluate_forecast_performance(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    threshold: float = HIGH_POLLUTION_PM25_THRESHOLD
) -> Dict[str, Any]:
    """
    Combines regression metrics and high-pollution detection diagnostics.
    """
    reg_metrics = calculate_regression_metrics(y_true, y_pred)
    poll_metrics = calculate_high_pollution_detection(y_true, y_pred, threshold)
    return {
        **reg_metrics,
        "high_pollution_detection": poll_metrics
    }
