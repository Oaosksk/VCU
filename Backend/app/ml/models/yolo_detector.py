"""YOLOv8 detector wrapper"""
from pathlib import Path
from typing import List, Dict
import cv2
import numpy as np

from app.core.config import settings


class YOLODetector:
    """YOLOv8 object detector for vehicle detection"""
    
    def __init__(self):
        self.model = None
        self.model_path = Path(settings.YOLO_MODEL_PATH)
    
    def load_model(self):
        """Load YOLOv8 model"""
        try:
            from ultralytics import YOLO
            self.model = YOLO(str(self.model_path))
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")
    
    def detect(self, frame: np.ndarray, conf_threshold: float = 0.25) -> List[Dict]:
        """Detect objects in frame"""
        if self.model is None:
            self.load_model()
        
        results = self.model(frame, conf=conf_threshold, verbose=False)
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                detection = {
                    "bbox": box.xyxy[0].cpu().numpy().tolist(),
                    "confidence": float(box.conf[0]),
                    "class_id": int(box.cls[0]),
                    "class_name": result.names[int(box.cls[0])]
                }
                detections.append(detection)
        
        return detections
