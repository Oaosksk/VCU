"""Tests for YOLOv8 detector wrapper"""
import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from app.ml.models.yolo_detector import YOLODetector


class TestYOLODetectorInit:
    def test_initial_state(self):
        detector = YOLODetector()
        assert detector.model is None

    def test_model_path_from_settings(self):
        detector = YOLODetector()
        assert detector.model_path is not None


class TestDetectEmptyFrame:
    def test_none_frame_returns_empty(self):
        detector = YOLODetector()
        # Inject a dummy model so load_model isn't called
        detector.model = MagicMock()
        result = detector.detect(None)
        assert result == []

    def test_empty_frame_returns_empty(self):
        detector = YOLODetector()
        detector.model = MagicMock()
        empty = np.array([])
        result = detector.detect(empty)
        assert result == []


class TestDetectWithMock:
    @pytest.fixture
    def detector_with_mock(self):
        """Create a detector with a mocked YOLO model"""
        detector = YOLODetector()

        # Build a mock result that mimics Ultralytics output
        mock_box = MagicMock()
        mock_box.xyxy = [MagicMock()]
        mock_box.xyxy[0].cpu.return_value.numpy.return_value.tolist.return_value = [10, 20, 100, 200]
        mock_box.conf = [MagicMock()]
        mock_box.conf[0].__float__ = lambda self: 0.85
        mock_box.cls = [MagicMock()]
        mock_box.cls[0].__int__ = lambda self: 2

        mock_result = MagicMock()
        mock_result.boxes = [mock_box]
        mock_result.names = {2: "car"}

        mock_model = MagicMock()
        mock_model.return_value = [mock_result]
        detector.model = mock_model

        return detector

    def test_detect_returns_list(self, detector_with_mock):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector_with_mock.detect(frame)
        assert isinstance(detections, list)
        assert len(detections) == 1

    def test_detection_has_required_keys(self, detector_with_mock):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector_with_mock.detect(frame)
        detection = detections[0]
        assert "bbox" in detection
        assert "confidence" in detection
        assert "class_id" in detection
        assert "class_name" in detection

    def test_detection_values(self, detector_with_mock):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detections = detector_with_mock.detect(frame)
        detection = detections[0]
        assert detection["class_name"] == "car"
        assert detection["class_id"] == 2
        assert isinstance(detection["confidence"], float)

    def test_detect_calls_model(self, detector_with_mock):
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        detector_with_mock.detect(frame, conf_threshold=0.5)
        detector_with_mock.model.assert_called_once_with(
            frame, conf=0.5, verbose=False
        )


class TestDetectErrorHandling:
    def test_detect_raises_on_critical_error(self):
        detector = YOLODetector()
        mock_model = MagicMock()
        mock_model.side_effect = ValueError("Unexpected model error")
        detector.model = mock_model

        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        with pytest.raises(RuntimeError, match="YOLO detection failed"):
            detector.detect(frame)


class TestCleanup:
    def test_cleanup_runs_without_error(self):
        detector = YOLODetector()
        # Should not raise even if torch is not available or GPU is absent
        detector.cleanup()
