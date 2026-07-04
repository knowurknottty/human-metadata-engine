"""
Anomaly Detection
==================

Detects outliers in the identity dataset — names that deviate
significantly from the norm in any encoder dimension.

Usage:
    from src.anomaly import detect_anomalies
    anomalies = detect_anomalies("output/unified_signatures.json")
"""

import json
import math
from typing import Optional


def detect_anomalies(signatures_path: str, threshold: float = 2.0) -> dict:
    """Detect anomalous identities using z-score analysis.

    Args:
        signatures_path: Path to unified signatures JSON
        threshold: Z-score threshold for anomaly detection (default 2.0 = 95th percentile)
    """
    with open(signatures_path) as f:
        data = json.load(f)

    if isinstance(data, list):
        sigs = {s.get("id", s.get("identity", "")): s for s in data}
    else:
        sigs = data

    # Extract all numeric features
    feature_data = {}
    for name, sig in sigs.items():
        feature_data[name] = _flatten(sig)

    # Compute mean and std for each feature
    all_features = set()
    for vec in feature_data.values():
        all_features.update(vec.keys())

    stats = {}
    for feat in all_features:
        values = [vec.get(feat, 0) for vec in feature_data.values()]
        mean = sum(values) / len(values) if values else 0
        variance = sum((v - mean) ** 2 for v in values) / len(values) if values else 0
        std = math.sqrt(variance) if variance > 0 else 1.0
        stats[feat] = {"mean": mean, "std": std}

    # Compute z-scores for each identity
    anomalies = {}
    for name, vec in feature_data.items():
        z_scores = {}
        for feat, val in vec.items():
            mean = stats[feat]["mean"]
            std = stats[feat]["std"]
            if std > 0:
                z = abs(val - mean) / std
                if z > threshold:
                    z_scores[feat] = {
                        "value": val,
                        "mean": round(mean, 2),
                        "std": round(std, 2),
                        "z_score": round(z, 2),
                    }
        if z_scores:
            anomalies[name] = {
                "anomaly_count": len(z_scores),
                "max_z_score": max(z["z_score"] for z in z_scores.values()),
                "features": z_scores,
            }

    # Sort by severity
    sorted_anomalies = dict(sorted(anomalies.items(), key=lambda x: x[1]["max_z_score"], reverse=True))

    return {
        "threshold": threshold,
        "total_identities": len(feature_data),
        "anomalous_count": len(anomalies),
        "anomalies": sorted_anomalies,
        "method": "z_score",
    }


def _flatten(sig: dict) -> dict:
    vec = {}
    for enc_name, enc_data in sig.get("encoders", {}).items():
        if isinstance(enc_data, dict):
            for k, v in enc_data.items():
                if isinstance(v, (int, float)):
                    vec[f"{enc_name}_{k}"] = float(v)
    return vec
