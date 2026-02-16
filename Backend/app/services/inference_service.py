"""Inference service for video analysis"""
from datetime import datetime
from pathlib import Path
import numpy as np
import logging
import time

INFERENCE_TIMEOUT_SECONDS = 120  # Abort analysis after 2 minutes


from app.services.video_service import get_video_path
from app.ml.models.yolo_detector import YOLODetector
from app.ml.models.lstm_model import LSTMDetector
from app.ml.pipeline.frame_extractor import FrameExtractor
from app.ml.pipeline.preprocessor import FramePreprocessor
from app.services.confidence_service import TemporalConfidenceAggregator
from app.services.frame_service import accident_frame_service
from app.core.config import settings

logger = logging.getLogger(__name__)


async def analyze_video_file(video_id: str, db = None) -> dict:
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

        # Timeout guard after frame extraction
        elapsed = time.time() - start_time
        if elapsed > INFERENCE_TIMEOUT_SECONDS:
            raise TimeoutError(f"Inference timed out after {elapsed:.0f}s during frame extraction")
        
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
            
            # Normalize features to prevent LSTM saturation
            # num_vehicles: 0-20 -> 0-2
            # bbox_variance: 0-1,000,000+ -> 0-10+ (Log scaling might be better but linear is safer for now)
            norm_num_vehicles = min(num_vehicles / 10.0, 2.0)
            norm_bbox_variance = min(bbox_variance / 100000.0, 5.0)
            
            lstm_features.append([norm_num_vehicles, avg_conf, norm_bbox_variance])
        
        logger.info(f"Detection complete. Processing {len(lstm_features)} feature vectors")

        # Timeout guard after YOLO detection
        elapsed = time.time() - start_time
        if elapsed > INFERENCE_TIMEOUT_SECONDS:
            raise TimeoutError(f"Inference timed out after {elapsed:.0f}s during YOLO detection")
        
        # Step 2: Pad features to fixed length (150 frames)
        max_frames = 150
        while len(lstm_features) < max_frames:
            lstm_features.append([0, 0, 0])
        lstm_features = np.array(lstm_features[:max_frames])
        
        # Step 3: LSTM Temporal Analysis
        logger.info("Running LSTM temporal analysis...")
        frame_confidences = lstm_detector.predict_sequence(lstm_features)

        # Timeout guard after LSTM prediction
        elapsed = time.time() - start_time
        if elapsed > INFERENCE_TIMEOUT_SECONDS:
            raise TimeoutError(f"Inference timed out after {elapsed:.0f}s during LSTM analysis")
        
        # Step 4: Temporal Confidence Aggregation (NOVEL CONTRIBUTION)
        logger.info("Applying temporal confidence aggregation...")
        aggregation_result = confidence_aggregator.aggregate(frame_confidences)
        
        # Step 5: Final Decision - REQUIRE vehicle detections for accident classification
        final_confidence = aggregation_result['final_confidence']
        
        # Count total vehicle detections
        total_vehicles = len([d for f in detections_per_frame for d in f if d['class_name'] in ['car', 'truck', 'bus', 'motorcycle']])
        
        # CRITICAL: Accident requires both high confidence AND vehicle detections
        if total_vehicles == 0:
            # No vehicles detected = cannot be accident
            is_accident = False
            final_confidence = 0.0
            logger.warning(f"No vehicles detected in video - forcing no_accident classification")
        elif total_vehicles < 5:
            # Very few vehicles = likely not accident
            is_accident = False
            final_confidence = min(final_confidence, 0.3)
            logger.warning(f"Only {total_vehicles} vehicles detected - low confidence")
        else:
            # Sufficient vehicles detected - use aggregation result
            is_accident = aggregation_result['is_accident']
            # Only boost confidence if we have strong evidence (vehicles + temporal pattern)
            if is_accident and total_vehicles > 10:
                final_confidence = min(final_confidence * 1.1, 0.99)
        
        status = "accident" if is_accident else "no_accident"
        
        # Step 6: Save Accident Frames and Generate Clip (NEW)
        frame_data = {'total_count': 0, 'frame_urls': [], 'clip_url': ''}
        
        # Ensure we have event frames if it's an accident
        event_frames = aggregation_result.get('event_frames', [])
        
        # Fallback: If accident detected but no specific event frames (e.g. strict threshold),
        # pick the top 10 frames with highest confidence
        if is_accident and not event_frames:
            logger.info("Accident detected but no event frames found. Using top confidence frames.")
            # Get indices of top 10 frames
            scores = np.array(frame_confidences)
            # Get indices of frames > 0.5, sorted by confidence
            top_indices = np.argsort(scores)[-10:]
            # Group into synthetic events (consecutive frames)
            top_indices = sorted(top_indices)
            if len(top_indices) > 0:
                # Simple grouping: start a new event if gap > 1
                current_start = top_indices[0]
                current_end = top_indices[0]
                
                for i in range(1, len(top_indices)):
                    if top_indices[i] == current_end + 1:
                        current_end = top_indices[i]
                    else:
                        event_frames.append((current_start, current_end))
                        current_start = top_indices[i]
                        current_end = top_indices[i]
                event_frames.append((current_start, current_end))
        
        if is_accident and event_frames:
            logger.info(f"Saving accident frames for video: {video_id}")
            
            # Save frames to disk
            save_result = accident_frame_service.save_accident_frames(
                video_id=video_id,
                frames=frames,
                event_frames=event_frames,
                detections_per_frame=detections_per_frame
            )
            
            # Generate accident-only video clip
            clip_path = accident_frame_service.generate_accident_clip(
                video_id=video_id,
                frames=frames,
                event_frames=event_frames,
                fps=video_info.get('fps', 10.0)
            )
            
            # Get URLs (show 4 frames: 2 before, accident, 2 after)
            frame_urls = accident_frame_service.get_frame_urls(
                video_id=video_id,
                saved_frames=save_result['saved_frames'],
                limit=5  # 2 before + accident + 2 after
            )
            
            clip_url = accident_frame_service.get_clip_url(video_id)
            
            frame_data = {
                'total_count': save_result['total_count'],
                'frame_urls': frame_urls,
                'clip_url': clip_url
            }
            
            logger.info(
                f"Accident frames saved: {frame_data['total_count']}, "
                f"URLs returned: {len(frame_urls)}, Clip: {bool(clip_url)}"
            )
        
        # Calculate inference time
        inference_time = time.time() - start_time
        
        logger.info(f"Analysis complete. Status: {status}, Confidence: {final_confidence:.2f}, Time: {inference_time:.2f}s")
        
        # Prepare result
        result = {
            "id": f"result-{video_id}",
            "status": status,
            "confidence": round(float(final_confidence), 3),
            "timestamp": datetime.now().isoformat(),
            "inference_time": round(float(inference_time), 3),
            "details": {
                "spatialFeatures": f"Detected {len([d for f in detections_per_frame for d in f])} objects across {len(frames)} frames",
                "temporalFeatures": f"Temporal stability: {aggregation_result['temporal_stability']:.2f}",
                "frameCount": int(len(frames)),
                "duration": f"{video_info['duration']:.1f} seconds",
                "temporalStability": round(float(aggregation_result['temporal_stability']), 3),
                "spikeFiltered": bool(aggregation_result['spike_filtered']),
                "eventFrames": [[int(start), int(end)] for start, end in aggregation_result['event_frames']],
                "maxConfidence": round(float(aggregation_result['max_confidence']), 3),
                "meanConfidence": round(float(aggregation_result['mean_confidence']), 3),
                # NEW: Accident frame data
                "accidentFrameCount": int(frame_data['total_count']),
                "accidentFrameUrls": frame_data['frame_urls'],
                "accidentClipUrl": frame_data['clip_url']
            }
        }
        
        return result
        
    except FileNotFoundError as e:
        logger.error(f"Video not found: {video_id}")
        raise
    except TimeoutError as e:
        logger.error(f"Inference timeout for video {video_id}: {e}")
        raise
    except Exception as e:
        logger.error(f"Analysis failed for video {video_id}: {str(e)}", exc_info=True)
        raise RuntimeError(f"Analysis failed: {str(e)}")
    finally:
        # Cleanup GPU memory
        try:
            import torch
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                logger.debug("GPU memory cleared after inference")
        except ImportError:
            pass
