"""Inference service for video analysis"""
from datetime import datetime
from pathlib import Path
import numpy as np
import logging

from app.services.video_service import get_video_path
from app.ml.models.yolo_detector import YOLODetector
from app.ml.pipeline.frame_extractor import FrameExtractor
from app.ml.pipeline.preprocessor import FramePreprocessor

logger = logging.getLogger(__name__)


async def analyze_video_file(video_id: str) -> dict:
    """Analyze video file for accident detection"""
    try:
        logger.info(f"Starting analysis for video: {video_id}")
        video_path = get_video_path(video_id)
        logger.info(f"Video path: {video_path}")
        
        # Initialize components
        frame_extractor = FrameExtractor()
        yolo_detector = YOLODetector()
        preprocessor = FramePreprocessor()
        
        # Extract frames
        logger.info("Extracting frames...")
        frames = frame_extractor.extract_frames(video_path)
        video_info = frame_extractor.get_video_info(video_path)
        logger.info(f"Extracted {len(frames)} frames from video")
        
        if not frames:
            raise ValueError("No frames extracted from video")
        
        # Detect objects in frames
        logger.info("Running YOLOv8 detection...")
        detections_per_frame = []
        vehicle_count = 0
        
        for idx, frame in enumerate(frames):
            detections = yolo_detector.detect(frame)
            detections_per_frame.append(detections)
            
            # Count vehicles
            for det in detections:
                if det['class_name'] in ['car', 'truck', 'bus', 'motorcycle']:
                    vehicle_count += 1
        
        logger.info(f"Detection complete. Total vehicles detected: {vehicle_count}")
        
        # Analyze patterns for accident detection
        logger.info("Analyzing patterns...")
        confidence, status, spatial_features, temporal_features = analyze_patterns(
            detections_per_frame, frames, video_info
        )
        
        logger.info(f"Analysis complete. Status: {status}, Confidence: {confidence:.2f}")
        
        result = {
            "id": f"result-{video_id}",
            "status": status,
            "confidence": round(confidence, 2),
            "timestamp": datetime.now().isoformat(),
            "details": {
                "spatialFeatures": spatial_features,
                "temporalFeatures": temporal_features,
                "frameCount": len(frames),
                "duration": f"{video_info['duration']:.1f} seconds"
            }
        }
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Video not found: {video_id}")
        raise
    except Exception as e:
        logger.error(f"Analysis failed for video {video_id}: {str(e)}", exc_info=True)
        raise RuntimeError(f"Analysis failed: {str(e)}")


def analyze_patterns(detections_per_frame, frames, video_info):
    """Analyze detection patterns for accident indicators"""
    try:
        # Calculate metrics
        total_frames = len(frames)
        if total_frames == 0:
            return 0.0, "no_accident", "No frames to analyze", "No temporal data"
        
        vehicle_frames = sum(1 for dets in detections_per_frame if any(
            d['class_name'] in ['car', 'truck', 'bus', 'motorcycle'] for d in dets
        ))
        
        # Check for sudden changes in detections
        detection_counts = [len(dets) for dets in detections_per_frame]
        if len(detection_counts) > 1:
            detection_variance = np.var(detection_counts)
        else:
            detection_variance = 0
        
        # Simple heuristic-based detection (placeholder for LSTM)
        confidence = 0.0
        spatial_features = "No significant spatial anomalies detected"
        temporal_features = "Normal traffic flow patterns observed"
        
        # High variance in detections might indicate accident
        if detection_variance > 5:
            confidence += 0.3
            spatial_features = "Irregular object distribution detected"
            temporal_features = "Sudden changes in scene composition"
        
        # Low vehicle presence might indicate aftermath
        if vehicle_frames < total_frames * 0.3 and vehicle_frames > 0:
            confidence += 0.2
            spatial_features = "Sparse vehicle presence detected"
        
        # Multiple vehicles in frames
        avg_vehicles = sum(len(dets) for dets in detections_per_frame) / max(total_frames, 1)
        if avg_vehicles > 3:
            confidence += 0.2
            spatial_features = "Multiple vehicles detected in scene"
        
        status = "accident" if confidence > 0.5 else "no_accident"
        
        logger.debug(f"Pattern analysis: variance={detection_variance:.2f}, avg_vehicles={avg_vehicles:.2f}")
        
        return confidence, status, spatial_features, temporal_features
        
    except Exception as e:
        logger.error(f"Pattern analysis failed: {str(e)}")
        return 0.0, "no_accident", "Analysis error", "Analysis error"
