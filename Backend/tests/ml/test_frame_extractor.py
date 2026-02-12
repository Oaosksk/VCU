"""Tests for frame extraction from video"""
import pytest
import numpy as np
from pathlib import Path
from unittest.mock import patch, MagicMock, PropertyMock
from app.ml.pipeline.frame_extractor import FrameExtractor


class TestFrameExtractorInit:
    def test_default_fps(self):
        extractor = FrameExtractor()
        assert extractor.target_fps > 0

    def test_custom_fps(self):
        extractor = FrameExtractor(target_fps=5)
        assert extractor.target_fps == 5


class TestExtractFramesErrors:
    def test_missing_file_raises(self):
        extractor = FrameExtractor()
        with pytest.raises((ValueError, RuntimeError)):
            extractor.extract_frames(Path("/nonexistent/video.mp4"))

    @patch("app.ml.pipeline.frame_extractor.cv2.VideoCapture")
    def test_corrupted_video_raises(self, mock_cap_cls):
        """VideoCapture.isOpened() returns False for corrupted files"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cap_cls.return_value = mock_cap

        extractor = FrameExtractor()
        with pytest.raises(ValueError, match="Cannot open"):
            extractor.extract_frames(Path("corrupted.mp4"))

    @patch("app.ml.pipeline.frame_extractor.cv2.VideoCapture")
    def test_zero_fps_raises(self, mock_cap_cls):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            0: 0,    # CAP_PROP_POS_MSEC
            1: 0,    # CAP_PROP_POS_FRAMES
            3: 640,  # WIDTH
            4: 480,  # HEIGHT
            5: 0,    # FPS = 0 → invalid
            7: 100,  # FRAME_COUNT
        }.get(prop, 0)
        mock_cap_cls.return_value = mock_cap

        extractor = FrameExtractor()
        with pytest.raises(ValueError, match="Invalid video FPS"):
            extractor.extract_frames(Path("bad_fps.mp4"))

    @patch("app.ml.pipeline.frame_extractor.cv2.VideoCapture")
    def test_zero_frame_count_raises(self, mock_cap_cls):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            5: 30.0,  # FPS
            7: 0,     # FRAME_COUNT = 0
        }.get(prop, 0)
        mock_cap_cls.return_value = mock_cap

        extractor = FrameExtractor()
        with pytest.raises(ValueError):
            extractor.extract_frames(Path("empty.mp4"))

    @patch("app.ml.pipeline.frame_extractor.cv2.VideoCapture")
    def test_exceeds_max_duration_raises(self, mock_cap_cls):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        # 30 fps × 10000 frames = 333s, which exceeds default 300s max
        mock_cap.get.side_effect = lambda prop: {
            5: 30.0,    # FPS
            7: 10000,   # FRAME_COUNT → 333s
        }.get(prop, 0)
        mock_cap_cls.return_value = mock_cap

        extractor = FrameExtractor()
        with pytest.raises(ValueError, match="exceeds maximum"):
            extractor.extract_frames(Path("long_video.mp4"))


class TestExtractFramesSuccess:
    @patch("app.ml.pipeline.frame_extractor.cv2.VideoCapture")
    def test_extracts_frames(self, mock_cap_cls):
        """Simulate a 10-frame video at 30fps, target 10fps → every 3rd frame"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            5: 30.0,  # FPS
            7: 10,     # FRAME_COUNT
        }.get(prop, 0)

        fake_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        # read() returns 10 frames then stops
        side_effects = [(True, fake_frame)] * 10 + [(False, None)]
        mock_cap.read.side_effect = side_effects
        mock_cap_cls.return_value = mock_cap

        extractor = FrameExtractor(target_fps=10)
        frames = extractor.extract_frames(Path("test.mp4"))

        assert len(frames) > 0
        assert all(isinstance(f, np.ndarray) for f in frames)

    @patch("app.ml.pipeline.frame_extractor.cv2.VideoCapture")
    def test_no_valid_frames_raises(self, mock_cap_cls):
        """All read() calls return empty frames"""
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            5: 30.0,
            7: 5,
        }.get(prop, 0)

        empty_frame = np.array([])
        mock_cap.read.side_effect = [
            (True, empty_frame),
            (True, empty_frame),
            (True, empty_frame),
            (True, empty_frame),
            (True, empty_frame),
            (False, None),
        ]
        mock_cap_cls.return_value = mock_cap

        extractor = FrameExtractor()
        with pytest.raises(ValueError, match="No valid frames"):
            extractor.extract_frames(Path("empty_frames.mp4"))


class TestGetVideoInfo:
    @patch("app.ml.pipeline.frame_extractor.cv2.VideoCapture")
    def test_returns_info_dict(self, mock_cap_cls):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = True
        mock_cap.get.side_effect = lambda prop: {
            3: 1920,   # WIDTH
            4: 1080,   # HEIGHT
            5: 30.0,   # FPS
            7: 300,    # FRAME_COUNT
        }.get(prop, 0)
        mock_cap_cls.return_value = mock_cap

        extractor = FrameExtractor()
        info = extractor.get_video_info(Path("test.mp4"))

        assert info["fps"] == 30.0
        assert info["frame_count"] == 300
        assert info["width"] == 1920
        assert info["height"] == 1080
        assert info["duration"] == 10.0

    @patch("app.ml.pipeline.frame_extractor.cv2.VideoCapture")
    def test_unopenable_raises(self, mock_cap_cls):
        mock_cap = MagicMock()
        mock_cap.isOpened.return_value = False
        mock_cap_cls.return_value = mock_cap

        extractor = FrameExtractor()
        with pytest.raises(ValueError, match="Cannot open"):
            extractor.get_video_info(Path("bad.mp4"))
