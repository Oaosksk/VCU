"""YOLOv8 detector wrapper"""
from pathlib import Path
from typing import List, Dict
import cv2
import numpy as np
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class YOLODetector:
    """YOLOv8 object detector for vehicle detection"""
    
    def __init__(self):
        self.model = None
        self.model_path = Path(settings.YOLO_MODEL_PATH)
    
    def load_model(self):
        """Load YOLOv8 model"""
        try:
            logger.info(f"Loading YOLOv8 model from {self.model_path}")
            from ultralytics import YOLO
            
            if not self.model_path.exists():
                logger.warning(f"Model not found at {self.model_path}, downloading...")
                self.model = YOLO('yolov8s.pt')
            else:
                self.model = YOLO(str(self.model_path))
            
            logger.info("YOLOv8 model loaded successfully")
        except ImportError as e:
            logger.error("ultralytics package not installed")
            raise RuntimeError("ultralytics package required. Install with: pip install ultralytics")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {str(e)}")
            raise RuntimeError(f"Failed to load YOLO model: {e}")
    
    def detect(self, frame: np.ndarray, conf_threshold: float = 0.25) -> List[Dict]:
        """Detect objects in frame"""
        try:
            if self.model is None:
                self.load_model()
            
            if frame is None or frame.size == 0:
                logger.warning("Empty frame provided for detection")
                return []
            
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
            
        except Exception as e:
            logger.error(f"Detection failed: {str(e)}")
            return []
