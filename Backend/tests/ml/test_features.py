"""Tests for shared YOLO-to-LSTM feature engineering."""
from app.ml.features import normalize_vehicle_features


def test_normalize_vehicle_features_matches_expected_z_scores():
    features = normalize_vehicle_features(
        vehicle_count=5,
        average_confidence=0.65,
        bbox_variance=200_000,
    )

    assert features == [
        (5 - 2.5) / 3.0,
        (0.65 - 0.4) / 0.25,
        (200_000 - 50_000.0) / 150_000.0,
    ]
