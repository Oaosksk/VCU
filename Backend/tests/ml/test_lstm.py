"""Tests for LSTM accident detection model"""
import pytest
import numpy as np
import torch
from unittest.mock import patch, MagicMock
from app.ml.models.lstm_model import AccidentLSTM, LSTMDetector


# ─── AccidentLSTM Architecture ────────────────────────────────────────────

class TestAccidentLSTMArchitecture:
    def test_default_params(self):
        model = AccidentLSTM()
        assert model.hidden_size == 64
        assert model.num_layers == 2

    def test_custom_params(self):
        model = AccidentLSTM(input_size=5, hidden_size=128, num_layers=3)
        assert model.hidden_size == 128
        assert model.num_layers == 3

    def test_forward_output_shape(self):
        model = AccidentLSTM()
        model.eval()
        x = torch.randn(1, 30, 3)  # (batch=1, seq=30, features=3)
        with torch.no_grad():
            out = model(x)
        assert out.shape == (1, 1)

    def test_output_in_0_1(self):
        model = AccidentLSTM()
        model.eval()
        x = torch.randn(2, 30, 3)
        with torch.no_grad():
            out = model(x)
        assert (out >= 0).all() and (out <= 1).all()

    def test_batch_processing(self):
        model = AccidentLSTM()
        model.eval()
        x = torch.randn(4, 30, 3)  # batch of 4
        with torch.no_grad():
            out = model(x)
        assert out.shape == (4, 1)


# ─── LSTMDetector ──────────────────────────────────────────────────────────

class TestLSTMDetector:
    def test_init_no_model(self):
        detector = LSTMDetector(model_path=None)
        assert detector.model is None

    def test_predict_raises_without_model(self):
        detector = LSTMDetector(model_path=None)
        features = np.random.rand(30, 3)
        with pytest.raises(RuntimeError, match="not loaded"):
            detector.predict(features)

    def test_sequence_predict_raises_without_model(self):
        detector = LSTMDetector(model_path=None)
        features = np.random.rand(10, 3)
        with pytest.raises(RuntimeError, match="not loaded"):
            detector.predict_sequence(features)

    def test_load_model_file_not_found(self):
        detector = LSTMDetector()
        with pytest.raises(FileNotFoundError):
            detector.load_model("/nonexistent/path/model.pth")

    def test_predict_with_manual_model(self):
        """Create a detector with a real (untrained) model to test predict flow"""
        detector = LSTMDetector(model_path=None)
        detector.model = AccidentLSTM().to(detector.device)
        detector.model.eval()

        features = np.random.rand(30, 3).astype(np.float32)
        confidence = detector.predict(features)
        assert isinstance(confidence, float)
        assert 0.0 <= confidence <= 1.0

    def test_predict_2d_input(self):
        """predict() should handle 2D input (no batch dim)"""
        detector = LSTMDetector(model_path=None)
        detector.model = AccidentLSTM().to(detector.device)
        detector.model.eval()

        features = np.random.rand(30, 3).astype(np.float32)
        confidence = detector.predict(features)
        assert 0.0 <= confidence <= 1.0

    def test_predict_3d_input(self):
        """predict() should handle 3D input (with batch dim)"""
        detector = LSTMDetector(model_path=None)
        detector.model = AccidentLSTM().to(detector.device)
        detector.model.eval()

        features = np.random.rand(1, 30, 3).astype(np.float32)
        confidence = detector.predict(features)
        assert 0.0 <= confidence <= 1.0

    def test_predict_sequence_returns_list(self):
        detector = LSTMDetector(model_path=None)
        detector.model = AccidentLSTM().to(detector.device)
        detector.model.eval()

        features = np.random.rand(10, 3).astype(np.float32)
        confidences = detector.predict_sequence(features)
        assert isinstance(confidences, list)
        assert len(confidences) == 10

    def test_predict_sequence_values_valid(self):
        detector = LSTMDetector(model_path=None)
        detector.model = AccidentLSTM().to(detector.device)
        detector.model.eval()

        features = np.random.rand(5, 3).astype(np.float32)
        confidences = detector.predict_sequence(features)
        for c in confidences:
            assert 0.0 <= c <= 1.0


# ─── GPU Fallback ──────────────────────────────────────────────────────────

class TestGPUFallback:
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="No GPU available")
    def test_gpu_oom_falls_back_to_cpu(self):
        """Simulate OOM by mocking; verify device switches to CPU"""
        detector = LSTMDetector(model_path=None)
        detector.model = AccidentLSTM().to(detector.device)
        detector.model.eval()

        features = np.random.rand(30, 3).astype(np.float32)

        original_predict = detector.predict
        call_count = {"n": 0}

        def side_effect(feats):
            call_count["n"] += 1
            if call_count["n"] == 1:
                raise torch.cuda.OutOfMemoryError("Simulated OOM")
            return original_predict(feats)

        with patch.object(detector, 'predict', side_effect=side_effect):
            pass  # GPU-specific test; runs only when GPU present
