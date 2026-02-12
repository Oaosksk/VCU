"""Tests for MetricsCalculator"""
import pytest
import numpy as np
from app.utils.metrics import MetricsCalculator, calculate_metrics_from_predictions


class TestMetricsCalculator:
    @pytest.fixture
    def calc(self):
        return MetricsCalculator()

    def test_initial_state(self, calc):
        assert calc.true_positives == 0
        assert calc.false_negatives == 0
        assert calc.accuracy() == 0.0

    def test_update_tp(self, calc):
        calc.update(1, 1)
        assert calc.true_positives == 1

    def test_update_tn(self, calc):
        calc.update(0, 0)
        assert calc.true_negatives == 1

    def test_update_fp(self, calc):
        calc.update(0, 1)
        assert calc.false_positives == 1

    def test_update_fn(self, calc):
        calc.update(1, 0)
        assert calc.false_negatives == 1

    def test_accuracy_perfect(self, calc):
        for _ in range(5):
            calc.update(1, 1)
            calc.update(0, 0)
        assert calc.accuracy() == 1.0

    def test_precision(self, calc):
        calc.update(1, 1)   # TP
        calc.update(0, 1)   # FP
        assert calc.precision() == 0.5

    def test_recall(self, calc):
        calc.update(1, 1)   # TP
        calc.update(1, 0)   # FN
        assert calc.recall() == 0.5

    def test_f1_score(self, calc):
        calc.update(1, 1)   # TP
        calc.update(0, 1)   # FP
        calc.update(1, 0)   # FN
        # precision = 0.5, recall = 0.5, f1 = 0.5
        assert calc.f1_score() == 0.5

    def test_f1_all_zero(self, calc):
        assert calc.f1_score() == 0.0

    def test_inference_time(self, calc):
        calc.update(1, 1, inference_time=1.0)
        calc.update(1, 1, inference_time=3.0)
        assert calc.avg_inference_time() == 2.0

    def test_no_inference_time(self, calc):
        assert calc.avg_inference_time() == 0.0

    def test_reset(self, calc):
        calc.update(1, 1)
        calc.reset()
        assert calc.true_positives == 0
        assert calc.accuracy() == 0.0

    def test_get_all_metrics_keys(self, calc):
        calc.update(1, 1)
        metrics = calc.get_all_metrics()
        expected_keys = [
            'accuracy', 'precision', 'recall', 'f1_score',
            'avg_inference_time', 'true_positives', 'true_negatives',
            'false_positives', 'false_negatives', 'total_samples'
        ]
        for key in expected_keys:
            assert key in metrics

    def test_confusion_matrix_shape(self, calc):
        calc.update(1, 1)
        cm = calc.confusion_matrix()
        assert cm.shape == (2, 2)

    def test_confusion_matrix_values(self, calc):
        calc.update(1, 1)   # TP
        calc.update(0, 0)   # TN
        calc.update(0, 1)   # FP
        calc.update(1, 0)   # FN
        cm = calc.confusion_matrix()
        # [[TN, FP], [FN, TP]]
        np.testing.assert_array_equal(cm, [[1, 1], [1, 1]])

    def test_print_metrics_uses_logger(self, calc, caplog):
        import logging
        with caplog.at_level(logging.INFO):
            calc.update(1, 1)
            calc.print_metrics()
        assert "EVALUATION METRICS" in caplog.text

    def test_update_batch(self, calc):
        y_true = [1, 0, 1, 0]
        y_pred = [1, 0, 0, 1]
        calc.update_batch(y_true, y_pred)
        assert calc.true_positives == 1
        assert calc.true_negatives == 1
        assert calc.false_positives == 1
        assert calc.false_negatives == 1


class TestConvenienceFunction:
    def test_calculate_metrics_from_predictions(self):
        y_true = [1, 1, 0, 0]
        y_pred = [1, 0, 0, 0]
        metrics = calculate_metrics_from_predictions(y_true, y_pred)
        assert metrics['total_samples'] == 4
        assert metrics['true_positives'] == 1
        assert metrics['true_negatives'] == 2
        assert metrics['false_negatives'] == 1
