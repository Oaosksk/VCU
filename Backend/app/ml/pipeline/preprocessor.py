"""Frame preprocessing"""
import cv2
import numpy as np
from typing import Tuple


class FramePreprocessor:
    """Preprocess frames for model input"""
    
    def __init__(self, target_size: Tuple[int, int] = (224, 224)):
        self.target_size = target_size
    
    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Preprocess single frame"""
        # Resize
        resized = cv2.resize(frame, self.target_size)
        
        # Normalize
        normalized = resized.astype(np.float32) / 255.0
        
        return normalized
    
    def preprocess_batch(self, frames: list) -> np.ndarray:
        """Preprocess batch of frames"""
        processed = [self.preprocess(frame) for frame in frames]
        return np.array(processed)
