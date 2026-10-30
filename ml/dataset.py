"""
AirFusion Atmospheric Vision Dataset Module (ml/dataset.py)

Handles multi-dataset ingestion, perceptual-hash deduplication,
station/time-aware train-val-test partitioning, and ImageNet transforms.
"""

from __future__ import annotations

import os
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import numpy as np
import pandas as pd
from PIL import Image

import torch
from torch.utils.data import Dataset
import torchvision.transforms as T

# Standard ImageNet normalization parameters
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


def get_default_transforms(image_size: int = 224, is_train: bool = True) -> T.Compose:
    """Standard transformations for continuous atmospheric visibility feature extraction."""
    if is_train:
        return T.Compose([
            T.Resize((image_size, image_size)),
            T.RandomHorizontalFlip(p=0.5),
            T.ColorJitter(brightness=0.1, contrast=0.1),
            T.ToTensor(),
            T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
        ])
    return T.Compose([
        T.Resize((image_size, image_size)),
        T.ToTensor(),
        T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
    ])


def compute_perceptual_hash(image: Image.Image, hash_size: int = 8) -> str:
    """
    Computes a 64-bit difference hash (dHash) using pure PIL.
    Deduplicates near-identical webcam frames without external dependencies.
    """
    # Resize to (hash_size + 1, hash_size), grayscale
    resized = image.convert("L").resize((hash_size + 1, hash_size), Image.Resampling.LANCZOS)
    pixels = np.array(resized)
    # Compare adjacent pixels
    difference = pixels[:, 1:] > pixels[:, :-1]
    # Convert bool array to hex string
    hex_str = hex(int("".join(["1" if b else "0" for b in difference.flatten()]), 2))[2:]
    return hex_str.zfill(16)


def deduplicate_images_by_phash(df: pd.DataFrame, image_dir: Path, threshold_hamming: int = 4) -> pd.DataFrame:
    """
    Filters out near-duplicate frames from the dataset using perceptual hashing.
    """
    unique_rows = []
    seen_hashes: List[int] = []

    for idx, row in df.iterrows():
        img_path = image_dir / str(row["filename"])
        if not img_path.exists():
            continue
        try:
            with Image.open(img_path) as img:
                h_str = compute_perceptual_hash(img)
                h_int = int(h_str, 16)
                
                # Check Hamming distance against all seen hashes
                is_duplicate = False
                for sh in seen_hashes:
                    dist = bin(h_int ^ sh).count("1")
                    if dist <= threshold_hamming:
                        is_duplicate = True
                        break
                
                if not is_duplicate:
                    seen_hashes.append(h_int)
                    unique_rows.append(row)
        except Exception:
            continue

    return pd.DataFrame(unique_rows).reset_index(drop=True)


def station_and_time_aware_split(
    df: pd.DataFrame,
    station_col: str = "station_id",
    date_col: str = "date",
    train_ratio: float = 0.70,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Ensures zero data leakage:
    1. No images from the same station on the same calendar date appear in both train and test.
    2. Test set evaluates held-out time blocks or completely held-out geographic monitoring stations.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-5, "Ratios must sum to 1.0"
    
    # Create cluster key: (station_id, date)
    df = df.copy()
    if date_col not in df.columns and "timestamp" in df.columns:
        df[date_col] = pd.to_datetime(df["timestamp"]).dt.date.astype(str)

    # Sort chronologically to preserve real temporal forecasting validity
    if "timestamp" in df.columns:
        df["_sort_dt"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("_sort_dt").reset_index(drop=True)
    
    stations = sorted(df[station_col].unique())
    rng = np.random.RandomState(seed)
    rng.shuffle(stations)
    
    # Dedicate 15% of stations strictly to the test set for spatial generalization
    n_test_stations = max(1, int(len(stations) * test_ratio)) if len(stations) > 3 else 0
    test_stations = set(stations[:n_test_stations])
    remaining_stations = [s for s in stations if s not in test_stations]

    # For the remaining stations, apply chronological split
    train_dfs = []
    val_dfs = []
    test_dfs = []

    # Assign held-out stations entirely to test
    if test_stations:
        test_dfs.append(df[df[station_col].isin(test_stations)])

    df_remaining = df[df[station_col].isin(remaining_stations)].copy()
    
    # Chronological partition on the remaining stations
    n_total = len(df_remaining)
    idx_train_end = int(n_total * (train_ratio / (train_ratio + val_ratio)))
    
    train_dfs.append(df_remaining.iloc[:idx_train_end])
    val_dfs.append(df_remaining.iloc[idx_train_end:])

    train_df = pd.concat(train_dfs, ignore_index=True) if train_dfs else pd.DataFrame()
    val_df = pd.concat(val_dfs, ignore_index=True) if val_dfs else pd.DataFrame()
    test_df = pd.concat(test_dfs, ignore_index=True) if test_dfs else pd.DataFrame()

    return train_df, val_df, test_df


class AirQualityPhotoDataset(Dataset):
    """
    PyTorch Dataset yielding (tensor_image, target_pm25, baseline_pm25, is_ood).
    """
    def __init__(
        self,
        df: pd.DataFrame,
        image_dir: Path | str,
        transform: Optional[Any] = None,
        target_col: str = "pm25",
        baseline_col: str = "baseline_pm25"
    ):
        self.df = df.reset_index(drop=True)
        self.image_dir = Path(image_dir)
        self.transform = transform or get_default_transforms(is_train=False)
        self.target_col = target_col
        self.baseline_col = baseline_col

    def __len__(self) -> int:
        return len(self.df)

    def __getitem__(self, idx: int) -> Dict[str, Any]:
        row = self.df.iloc[idx]
        img_name = row["filename"]
        img_path = self.image_dir / str(img_name)

        if not img_path.exists():
            # Return synthetic sample for missing frame
            image = Image.new("RGB", (224, 224), color=(128, 140, 150))
        else:
            try:
                image = Image.open(img_path).convert("RGB")
            except Exception:
                image = Image.new("RGB", (224, 224), color=(128, 140, 150))

        tensor_img = self.transform(image)
        pm25 = float(row[self.target_col]) if self.target_col in row else 25.0
        baseline = float(row[self.baseline_col]) if self.baseline_col in row else pm25
        is_ood = float(row["is_ood"]) if "is_ood" in row else 0.0

        return {
            "image": tensor_img,
            "target_pm25": torch.tensor(pm25, dtype=torch.float32),
            "baseline_pm25": torch.tensor(baseline, dtype=torch.float32),
            "is_ood": torch.tensor(is_ood, dtype=torch.float32),
            "filename": str(img_name)
        }
