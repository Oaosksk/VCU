"""Frame extraction from video with error handling and memory efficiency"""
import cv2
from pathlib import Path
from typing import List, Generator
import numpy as np
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class FrameExtractor:
    """Extract frames from video at target FPS with robust error handling"""

    def __init__(self, target_fps: int = None):
        self.target_fps = target_fps or settings.TARGET_FPS

    def extract_frames(self, video_path: Path) -> List[np.ndarray]:
        """
        Extract frames from video with error handling.

        Raises:
            ValueError: If video cannot be opened, has no frames, or exceeds duration limit.
            RuntimeError: If an unexpected error occurs during extraction.
        """
        try:
            cap = cv2.VideoCapture(str(video_path))

            if not cap.isOpened():
                raise ValueError(f"Cannot open video file: {video_path}. File may be corrupted or use an unsupported codec.")

            original_fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            # Validate FPS
            if original_fps <= 0:
                cap.release()
                raise ValueError(f"Invalid video FPS ({original_fps}). File may be corrupted.")

            # Validate duration
            duration = total_frames / original_fps
            if duration <= 0:
                cap.release()
                raise ValueError("Video has zero duration.")

            max_duration = getattr(settings, 'MAX_VIDEO_DURATION', 300)
            if duration > max_duration:
                cap.release()
                raise ValueError(
                    f"Video duration ({duration:.1f}s) exceeds maximum allowed ({max_duration}s)."
                )

            # Validate frame count
            if total_frames <= 0:
                cap.release()
                raise ValueError("Video contains no frames.")

            frame_interval = max(1, int(original_fps / self.target_fps))

            frames = []
            frame_count = 0
            extracted = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_count % frame_interval == 0:
                    if frame is not None and frame.size > 0:
                        frames.append(frame)
                        extracted += 1

                frame_count += 1

            cap.release()

            if not frames:
                raise ValueError(
                    f"No valid frames could be extracted from video (read {frame_count} raw frames)."
                )

            logger.info(f"Extracted {extracted} frames from {frame_count} total (interval={frame_interval})")
            return frames

        except ValueError:
            raise
        except cv2.error as e:
            raise RuntimeError(f"OpenCV error processing video: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Unexpected error extracting frames: {str(e)}")

    def get_video_info(self, video_path: Path) -> dict:
        """Get video metadata with error handling"""
        try:
            cap = cv2.VideoCapture(str(video_path))

            if not cap.isOpened():
                raise ValueError(f"Cannot open video: {video_path}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

            info = {
                "fps": fps,
                "frame_count": frame_count,
                "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                "duration": frame_count / fps if fps > 0 else 0.0
            }

            cap.release()
            return info

        except ValueError:
            raise
        except Exception as e:
            raise RuntimeError(f"Failed to read video info: {str(e)}")
