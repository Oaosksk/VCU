"""Tests for file validation utilities"""
import pytest
from app.utils.file_utils import validate_video_file, format_file_size


class TestValidateVideoFile:
    def test_valid_mp4(self):
        result = validate_video_file("test.mp4", 1024)
        assert result["valid"] is True
        assert result["error"] is None

    def test_valid_avi(self):
        result = validate_video_file("test.avi", 1024)
        assert result["valid"] is True

    def test_valid_mov(self):
        result = validate_video_file("test.mov", 1024)
        assert result["valid"] is True

    def test_valid_mkv(self):
        result = validate_video_file("test.mkv", 1024)
        assert result["valid"] is True

    def test_invalid_extension(self):
        result = validate_video_file("test.exe", 1024)
        assert result["valid"] is False
        assert "Invalid file type" in result["error"]

    def test_no_filename(self):
        result = validate_video_file("", 1024)
        assert result["valid"] is False

    def test_none_filename(self):
        result = validate_video_file(None, 1024)
        assert result["valid"] is False

    def test_file_too_large(self):
        huge_size = 600 * 1024 * 1024  # 600MB
        result = validate_video_file("test.mp4", huge_size)
        assert result["valid"] is False
        assert "exceeds" in result["error"]

    def test_file_at_limit(self):
        max_size = 524_288_000  # 500MB
        result = validate_video_file("test.mp4", max_size)
        assert result["valid"] is True

    def test_case_insensitive(self):
        result = validate_video_file("TEST.MP4", 1024)
        assert result["valid"] is True


class TestFormatFileSize:
    def test_zero(self):
        assert format_file_size(0) == "0 Bytes"

    def test_bytes(self):
        result = format_file_size(500)
        assert "Bytes" in result or "KB" in result

    def test_megabytes(self):
        result = format_file_size(5 * 1024 * 1024)
        assert "MB" in result
