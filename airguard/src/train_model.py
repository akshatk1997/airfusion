"""
Model Training & Evaluation Pipeline for AirFusion.
Trains and benchmarks multiple forecasting models:
1. Persistence Baseline
2. Ridge Regression
3. Random Forest Regressor
4. XGBoost Regressor
5. PyTorch LSTM (Optional Deep Learning)

Selects the best performing model based on Validation MAE/R²,
persists model artifacts, scalers, and performance metrics.
"""

from __future__ import annotations

import os
import sys
import json
import logging
from pathlib import Path

# Add project root to sys.path
SRC_DIR = Path(__file__).resolve().parent
ROOT_DIR = SRC_DIR.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from typing import Dict, Any, List, Tuple, Optional
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import xgboost as xgb
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

from src.config import (
    BEST_MODEL_PATH,
    MODEL_METRICS_PATH,
    FEATURE_NAMES_PATH,
    SCALER_PATH,
    LSTM_MODEL_PATH,
    HIGH_POLLUTION_PM25_THRESHOLD,
    DB_PATH
)
from src.database import fetch_historical_records, init_db
from src.preprocessing import clean_air_quality_dataframe
from src.feature_engineering import build_feature_pipeline, time_series_split
from src.evaluation import evaluate_forecast_performance

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("airfusion.train")


# PyTorch LSTM Architecture
class AirQualityLSTM(nn.Module):
    def __init__(self, input_size: int, hidden_size: int = 64, num_layers: int = 2, output_size: int = 1):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers=num_layers, batch_first=True, dropout=0.2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Linear(32, output_size)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        out, _ = self.lstm(x)
        # Take last time step
        out = self.fc(out[:, -1, :])
        return out


def train_lstm_model(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray,
    y_val: np.ndarray,
    epochs: int = 25,
    batch_size: int = 32
) -> Tuple[AirQualityLSTM, np.ndarray]:
    """
    Train PyTorch LSTM on sequential tabular features.
    """
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    input_dim = X_train.shape[1]

    # Reshape for LSTM: (batch, seq_len=1, features)
    X_tr_t = torch.tensor(X_train[:, np.newaxis, :], dtype=torch.float32)
    y_tr_t = torch.tensor(y_train[:, np.newaxis], dtype=torch.float32)
    X_val_t = torch.tensor(X_val[:, np.newaxis, :], dtype=torch.float32).to(device)

    dataset = TensorDataset(X_tr_t, y_tr_t)
    loader = DataLoader(dataset, batch_size=batch_size, shuffle=False)

    model = AirQualityLSTM(input_size=input_dim, hidden_size=48, num_layers=2).to(device)
    criterion = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.005)

    model.train()
    for epoch in range(epochs):
        for batch_x, batch_y in loader:
            batch_x, batch_y = batch_x.to(device), batch_y.to(device)
            optimizer.zero_grad()
            preds = model(batch_x)
            loss = criterion(preds, batch_y)
            loss.backward()
            optimizer.step()

    model.eval()
    with torch.no_grad():
        val_preds = model(X_val_t).cpu().numpy().flatten()

    return model, val_preds


def prepare_training_dataset(
    db_path: Optional[Path | str] = None,
    cities: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, List[str], List[str]]:
    """
    Extracts multi-city time-series from SQLite, cleans the records,
    and runs feature pipeline.
    """
    init_db(db_path)
    if cities is None:
        cities = ["Chandigarh", "Mohali", "Kharar", "Delhi"]

    all_dfs = []
    for city in cities:
        df_city = fetch_historical_records(city=city, db_path=db_path)
        if not df_city.empty and len(df_city) >= 48:
            df_cleaned = clean_air_quality_dataframe(df_city)
            all_dfs.append(df_cleaned)

    if not all_dfs:
        raise ValueError("No historical data found in database. Run data collection first.")

    # Combine multi-city observations
    combined_df = pd.concat(all_dfs, ignore_index=True)
    combined_df.sort_values("timestamp", inplace=True)
    combined_df.reset_index(drop=True, inplace=True)

    featured_df, feature_cols, target_cols = build_feature_pipeline(combined_df, horizons=[24, 72])
    return featured_df, feature_cols, target_cols


def run_model_training_pipeline(
    db_path: Optional[Path | str] = None,
    primary_target: str = "target_lead_24h"
) -> Dict[str, Any]:
    """
    Executes end-to-end model training, validation, comparison, and serialization.
    """
    logger.info("Starting AirFusion ML Training Pipeline...")
    featured_df, feature_cols, target_cols = prepare_training_dataset(db_path=db_path)

    # Drop NaNs generated by lags and future target shifts
    valid_df = featured_df.dropna(subset=feature_cols + [primary_target]).copy()
    logger.info(f"Usable dataset size after feature lagging: {len(valid_df)} samples, {len(feature_cols)} features.")

    # Time-series split (70% train, 15% validation, 15% test)
    train_df, val_df, test_df = time_series_split(valid_df, train_ratio=0.70, val_ratio=0.15, test_ratio=0.15)

    X_train = train_df[feature_cols].values
    y_train = train_df[primary_target].values

    X_val = val_df[feature_cols].values
    y_val = val_df[primary_target].values

    X_test = test_df[feature_cols].values
    y_test = test_df[primary_target].values

    # Feature Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_val_scaled = scaler.transform(X_val)
    X_test_scaled = scaler.transform(X_test)

    # Current PM2.5 persistence column for baseline
    current_pm25_idx = feature_cols.index("pm2_5") if "pm2_5" in feature_cols else 0
    val_persistence_preds = X_val[:, current_pm25_idx]
    test_persistence_preds = X_test[:, current_pm25_idx]

    models_dict = {}
    metrics_summary = {}

    # 1. Baseline: Persistence
    logger.info("Evaluating Persistence Baseline...")
    metrics_summary["Persistence Baseline"] = {
        "val": evaluate_forecast_performance(y_val, val_persistence_preds, HIGH_POLLUTION_PM25_THRESHOLD),
        "test": evaluate_forecast_performance(y_test, test_persistence_preds, HIGH_POLLUTION_PM25_THRESHOLD)
    }

    # 2. Ridge Regression
    logger.info("Training Ridge Regression...")
    ridge = Ridge(alpha=10.0)
    ridge.fit(X_train_scaled, y_train)
    val_ridge_pred = ridge.predict(X_val_scaled)
    test_ridge_pred = ridge.predict(X_test_scaled)
    models_dict["Ridge Regression"] = ridge
    metrics_summary["Ridge Regression"] = {
        "val": evaluate_forecast_performance(y_val, val_ridge_pred, HIGH_POLLUTION_PM25_THRESHOLD),
        "test": evaluate_forecast_performance(y_test, test_ridge_pred, HIGH_POLLUTION_PM25_THRESHOLD)
    }

    # 3. Random Forest Regressor
    logger.info("Training Random Forest Regressor...")
    rf = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    rf.fit(X_train, y_train)
    val_rf_pred = rf.predict(X_val)
    test_rf_pred = rf.predict(X_test)
    models_dict["Random Forest"] = rf
    metrics_summary["Random Forest"] = {
        "val": evaluate_forecast_performance(y_val, val_rf_pred, HIGH_POLLUTION_PM25_THRESHOLD),
        "test": evaluate_forecast_performance(y_test, test_rf_pred, HIGH_POLLUTION_PM25_THRESHOLD)
    }

    # 4. XGBoost Regressor
    logger.info("Training XGBoost Regressor...")
    xgb_model = xgb.XGBRegressor(
        n_estimators=150,
        max_depth=6,
        learning_rate=0.05,
        subsample=0.85,
        colsample_bytree=0.85,
        random_state=42,
        n_jobs=-1
    )
    xgb_model.fit(
        X_train, y_train,
        eval_set=[(X_val, y_val)],
        verbose=False
    )
    val_xgb_pred = xgb_model.predict(X_val)
    test_xgb_pred = xgb_model.predict(X_test)
    models_dict["XGBoost"] = xgb_model
    metrics_summary["XGBoost"] = {
        "val": evaluate_forecast_performance(y_val, val_xgb_pred, HIGH_POLLUTION_PM25_THRESHOLD),
        "test": evaluate_forecast_performance(y_test, test_xgb_pred, HIGH_POLLUTION_PM25_THRESHOLD)
    }

    # 5. Optional PyTorch LSTM
    try:
        logger.info("Training PyTorch LSTM Regressor...")
        lstm_model, val_lstm_pred = train_lstm_model(X_train_scaled, y_train, X_val_scaled, y_val, epochs=20)
        with torch.no_grad():
            test_lstm_t = torch.tensor(X_test_scaled[:, np.newaxis, :], dtype=torch.float32)
            test_lstm_pred = lstm_model(test_lstm_t).cpu().numpy().flatten()
        torch.save(lstm_model.state_dict(), LSTM_MODEL_PATH)
        metrics_summary["PyTorch LSTM"] = {
            "val": evaluate_forecast_performance(y_val, val_lstm_pred, HIGH_POLLUTION_PM25_THRESHOLD),
            "test": evaluate_forecast_performance(y_test, test_lstm_pred, HIGH_POLLUTION_PM25_THRESHOLD)
        }
    except Exception as e:
        logger.warning(f"LSTM training skipped or encountered exception: {e}")

    # Determine Best Model based on Validation MAE
    best_model_name = "XGBoost"
    lowest_mae = float("inf")
    for name, m in metrics_summary.items():
        if name in models_dict:
            val_mae = m["val"]["mae"]
            if val_mae < lowest_mae:
                lowest_mae = val_mae
                best_model_name = name

    logger.info(f"Champion Model Selected: '{best_model_name}' (Val MAE: {lowest_mae:.3f})")
    best_model = models_dict[best_model_name]

    # Also train a 72-hour lead model using the champion architecture
    logger.info("Training 72-hour forecast lead model...")
    valid_72_df = featured_df.dropna(subset=feature_cols + ["target_lead_72h"]).copy()
    train_72, val_72, test_72 = time_series_split(valid_72_df)
    if best_model_name == "XGBoost":
        model_72h = xgb.XGBRegressor(n_estimators=150, max_depth=6, learning_rate=0.05, random_state=42, n_jobs=-1)
    else:
        model_72h = RandomForestRegressor(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1)
    model_72h.fit(train_72[feature_cols].values, train_72["target_lead_72h"].values)

    # Also train 1-hour step model for iterative hourly trajectories
    logger.info("Training 1-hour step trajectory model...")
    valid_1h_df = featured_df.dropna(subset=feature_cols + ["target_lead_1h"]).copy()
    train_1h, _, _ = time_series_split(valid_1h_df)
    if best_model_name == "XGBoost":
        model_1h = xgb.XGBRegressor(n_estimators=100, max_depth=5, learning_rate=0.08, random_state=42, n_jobs=-1)
    else:
        model_1h = RandomForestRegressor(n_estimators=80, max_depth=10, random_state=42, n_jobs=-1)
    model_1h.fit(train_1h[feature_cols].values, train_1h["target_lead_1h"].values)

    # Save artifacts
    artifacts_bundle = {
        "best_model_name": best_model_name,
        "model_24h": best_model,
        "model_72h": model_72h,
        "model_1h": model_1h,
        "feature_names": feature_cols,
        "target": primary_target
    }
    joblib.dump(artifacts_bundle, BEST_MODEL_PATH)
    joblib.dump(scaler, SCALER_PATH)

    with open(FEATURE_NAMES_PATH, "w") as f:
        json.dump(feature_cols, f, indent=2)

    with open(MODEL_METRICS_PATH, "w") as f:
        json.dump({
            "champion_model": best_model_name,
            "metrics_comparison": metrics_summary,
            "num_features": len(feature_cols),
            "training_samples": len(train_df),
            "test_samples": len(test_df)
        }, f, indent=2)

    logger.info(f"Artifacts saved successfully to {BEST_MODEL_PATH}")
    return metrics_summary


if __name__ == "__main__":
    run_model_training_pipeline()
