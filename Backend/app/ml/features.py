"""Shared feature engineering utilities for YOLO-to-LSTM sequences."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeatureNormalizationStats:
    """Z-score constants used by both training and inference."""

    vehicle_mean: float = 2.5
    vehicle_std: float = 3.0
    confidence_mean: float = 0.4
    confidence_std: float = 0.25
    bbox_variance_mean: float = 50_000.0
    bbox_variance_std: float = 150_000.0


FEATURE_STATS = FeatureNormalizationStats()


def normalize_vehicle_features(
    vehicle_count: float,
    average_confidence: float,
    bbox_variance: float,
    stats: FeatureNormalizationStats = FEATURE_STATS,
) -> list[float]:
    """Normalize per-frame vehicle features exactly as the LSTM expects."""
    return [
        (vehicle_count - stats.vehicle_mean) / stats.vehicle_std,
        (average_confidence - stats.confidence_mean) / stats.confidence_std,
        (bbox_variance - stats.bbox_variance_mean) / stats.bbox_variance_std,
    ]
