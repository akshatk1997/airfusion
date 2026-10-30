"""
AirFusion Atmospheric Vision CNN Model (ml/model.py)

MobileNetV3-Small vision backbone with:
1. Heteroscedastic uncertainty regression head (PM2.5 prediction + log-variance sigma^2)
2. Out-of-Distribution (OOD) verification head (indoor / nighttime rejection gate)
3. Dynamic residual fusion formulation with meteorological baseline
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision.models as models


class AirFusionVisionModel(nn.Module):
    """
    Lightweight MobileNetV3-Small based continuous PM2.5 regressor
    with heteroscedastic uncertainty output and OOD gating.
    """
    def __init__(self, pretrained: bool = False, dropout_rate: float = 0.2):
        super().__init__()
        # Load MobileNetV3-Small backbone
        mobilenet = models.mobilenet_v3_small(weights=None)
        self.features = mobilenet.features
        self.avgpool = mobilenet.avgpool

        # In MobileNetV3-Small, feature output before classifier is 576
        in_features = 576

        # Shared representation projection
        self.fc_shared = nn.Sequential(
            nn.Linear(in_features, 128),
            nn.Hardswish(),
            nn.Dropout(p=dropout_rate)
        )

        # Head 1: PM2.5 Prediction (Mean) + Log-Variance (Uncertainty)
        self.fc_pm25 = nn.Linear(128, 1)
        self.fc_logvar = nn.Linear(128, 1)

        # Head 2: Out-Of-Distribution (OOD) Gate (0: Valid Outdoor, 1: Invalid/Indoor/Corrupt)
        self.fc_ood = nn.Linear(128, 1)

    def forward(self, x: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """
        Forward pass.
        Args:
            x: Input tensor [B, 3, 224, 224] normalized with ImageNet stats.
        Returns:
            Tuple: (pm25_pred, uncertainty_sigma, ood_probability)
        """
        feats = self.features(x)
        pooled = self.avgpool(feats)
        flattened = torch.flatten(pooled, 1)
        shared = self.fc_shared(flattened)

        # Regression: continuous PM2.5 (positive via softplus or clamped ReLU)
        pm25_raw = self.fc_pm25(shared)
        pm25_pred = F.softplus(pm25_raw)  # Guarantees strictly non-negative PM2.5

        # Uncertainty: standard deviation sigma = exp(0.5 * logvar)
        logvar = torch.clamp(self.fc_logvar(shared), min=-4.0, max=4.0)
        uncertainty = torch.exp(0.5 * logvar)

        # OOD Gate: Sigmoid probability of out-of-distribution
        ood_prob = torch.sigmoid(self.fc_ood(shared))

        return pm25_pred.squeeze(-1), uncertainty.squeeze(-1), ood_prob.squeeze(-1)


def heteroscedastic_loss(
    y_pred: torch.Tensor,
    log_var: torch.Tensor,
    y_true: torch.Tensor
) -> torch.Tensor:
    """
    Gaussian negative log-likelihood (heteroscedastic loss):
    Loss = 0.5 * exp(-log_var) * (y_true - y_pred)^2 + 0.5 * log_var
    """
    precision = torch.exp(-log_var)
    mse = (y_true - y_pred) ** 2
    loss = 0.5 * precision * mse + 0.5 * log_var
    return torch.mean(loss)


def compute_residual_fusion(
    baseline_pm25: float | np.ndarray,
    cnn_pm25: float | np.ndarray,
    uncertainty_sigma: float | np.ndarray,
    ood_score: float | np.ndarray,
    lambda_scale: float = 1.0
) -> Dict[str, Any]:
    """
    Mathematical residual fusion formula:
    final = baseline + lambda * (cnn - baseline)
    where lambda = (1 / (1 + sigma^2)) * (1 - ood_score) * lambda_scale
    """
    sigma_sq = uncertainty_sigma ** 2
    confidence = 1.0 / (1.0 + sigma_sq)
    validity = max(0.0, 1.0 - ood_score)
    lam = min(1.0, max(0.0, confidence * validity * lambda_scale))
    
    residual = cnn_pm25 - baseline_pm25
    fused = baseline_pm25 + lam * residual
    
    return {
        "fused_pm25": float(fused),
        "meteorological_baseline": float(baseline_pm25),
        "cnn_raw_prediction": float(cnn_pm25),
        "uncertainty_sigma": float(uncertainty_sigma),
        "ood_score": float(ood_score),
        "fusion_weight_lambda": float(lam),
        "is_ood_rejected": bool(ood_score > 0.65)
    }
