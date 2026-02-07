"""Frame extraction from video"""
import cv2
from pathlib import Path
from typing import List
import numpy as np

from app.core.config import settings


class FrameExtractor:
    """Extract frames from video at target FPS"""
    
    def __init__(self, target_fps: int = None):
        self.target_fps = target_fps or settings.TARGET_FPS
    
    def extract_frames(self, video_path: Path) -> List[np.ndarray]:
        """Extract frames from video"""
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise ValueError(f"Cannot open video: {video_path}")
        
        original_fps = cap.get(cv2.CAP_PROP_FPS)
        frame_interval = int(original_fps / self.target_fps)
        
        frames = []
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                frames.append(frame)
            
            frame_count += 1
        
        cap.release()
        return frames
    
    def get_video_info(self, video_path: Path) -> dict:
        """Get video metadata"""
        cap = cv2.VideoCapture(str(video_path))
        
        info = {
            "fps": cap.get(cv2.CAP_PROP_FPS),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "duration": cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
        }
        
        cap.release()
        return info
