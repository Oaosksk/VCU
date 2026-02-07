"""Inference service for video analysis"""
from datetime import datetime
from pathlib import Path
import numpy as np
import logging
import time

from app.services.video_service import get_video_path
from app.ml.models.yolo_detector import YOLODetector
from app.ml.models.lstm_model import LSTMDetector
from app.ml.pipeline.frame_extractor import FrameExtractor
from app.ml.pipeline.preprocessor import FramePreprocessor
from app.services.confidence_service import TemporalConfidenceAggregator
from app.core.config import settings

logger = logging.getLogger(__name__)


async def analyze_video_file(video_id: str) -> dict:
    """Analyze video file for accident detection using LSTM + Temporal Confidence Aggregation"""
    start_time = time.time()
    
    try:
        logger.info(f"Starting analysis for video: {video_id}")
        video_path = get_video_path(video_id)
        logger.info(f"Video path: {video_path}")
        
        # Initialize components
        frame_extractor = FrameExtractor()
        yolo_detector = YOLODetector()
        lstm_detector = LSTMDetector(settings.LSTM_MODEL_PATH)
        confidence_aggregator = TemporalConfidenceAggregator(
            window_size=15,
            spike_threshold=0.3,
            consistency_threshold=0.6
        )
        
        # Extract frames
        logger.info("Extracting frames...")
        frames = frame_extractor.extract_frames(video_path)
        video_info = frame_extractor.get_video_info(video_path)
        logger.info(f"Extracted {len(frames)} frames from video")
        
        if not frames:
            raise ValueError("No frames extracted from video")
        
        # Step 1: YOLOv8 Detection (Spatial Features)
        logger.info("Running YOLOv8 detection...")
        detections_per_frame = []
        lstm_features = []
        
        for idx, frame in enumerate(frames):
            detections = yolo_detector.detect(frame)
            detections_per_frame.append(detections)
            
            # Extract features for LSTM
            vehicles = [d for d in detections if d['class_name'] in ['car', 'truck', 'bus', 'motorcycle']]
            
            if vehicles:
                num_vehicles = len(vehicles)
                avg_conf = np.mean([d['confidence'] for d in vehicles])
                bboxes = np.array([d['bbox'] for d in vehicles])
                bbox_variance = float(np.var(bboxes))
            else:
                num_vehicles = 0
                avg_conf = 0.0
                bbox_variance = 0.0
            
            lstm_features.append([num_vehicles, avg_conf, bbox_variance])
        
        logger.info(f"Detection complete. Processing {len(lstm_features)} feature vectors")
        
        # Step 2: Pad features to fixed length (150 frames)
        max_frames = 150
        while len(lstm_features) < max_frames:
            lstm_features.append([0, 0, 0])
        lstm_features = np.array(lstm_features[:max_frames])
        
        # Step 3: LSTM Temporal Analysis
        logger.info("Running LSTM temporal analysis...")
        frame_confidences = lstm_detector.predict_sequence(lstm_features)
        
        # Step 4: Temporal Confidence Aggregation (NOVEL CONTRIBUTION)
        logger.info("Applying temporal confidence aggregation...")
        aggregation_result = confidence_aggregator.aggregate(frame_confidences)
        
        # Step 5: Final Decision
        final_confidence = aggregation_result['final_confidence']
        is_accident = aggregation_result['is_accident']
        status = "accident" if is_accident else "no_accident"
        
        # Calculate inference time
        inference_time = time.time() - start_time
        
        logger.info(f"Analysis complete. Status: {status}, Confidence: {final_confidence:.2f}, Time: {inference_time:.2f}s")
        
        # Prepare result
        result = {
            "id": f"result-{video_id}",
            "status": status,
            "confidence": round(final_confidence, 3),
            "timestamp": datetime.now().isoformat(),
            "inference_time": round(inference_time, 3),
            "details": {
                "spatialFeatures": f"Detected {len([d for f in detections_per_frame for d in f])} objects across {len(frames)} frames",
                "temporalFeatures": f"Temporal stability: {aggregation_result['temporal_stability']:.2f}",
                "frameCount": len(frames),
                "duration": f"{video_info['duration']:.1f} seconds",
                "temporalStability": round(aggregation_result['temporal_stability'], 3),
                "spikeFiltered": aggregation_result['spike_filtered'],
                "eventFrames": aggregation_result['event_frames'],
                "maxConfidence": round(aggregation_result['max_confidence'], 3),
                "meanConfidence": round(aggregation_result['mean_confidence'], 3)
            }
        }
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Video not found: {video_id}")
        raise
    except Exception as e:
        logger.error(f"Analysis failed for video {video_id}: {str(e)}", exc_info=True)
        raise RuntimeError(f"Analysis failed: {str(e)}")
