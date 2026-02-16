"""Temporal Confidence Aggregation - Novel Contribution"""
import numpy as np
from collections import deque
import logging

logger = logging.getLogger(__name__)


class TemporalConfidenceAggregator:
    """
    Temporal Confidence Aggregation for stable accident detection
    
    Novel Contribution:
    - Sliding window confidence aggregation
    - Spike filtering to reduce false positives
    - Temporal consistency validation
    - Multi-frame reasoning for robust detection
    """
    
    def __init__(self, window_size=15, spike_threshold=0.3, consistency_threshold=0.6):
        """
        Args:
            window_size: Number of frames for sliding window
            spike_threshold: Threshold to detect confidence spikes
            consistency_threshold: Minimum consistency ratio for accident detection
        """
        self.window_size = window_size
        self.spike_threshold = spike_threshold
        self.consistency_threshold = consistency_threshold
    
    def aggregate(self, frame_confidences):
        """
        Aggregate frame-wise confidences using temporal reasoning
        
        Args:
            frame_confidences: List of confidence scores per frame
        
        Returns:
            dict: {
                'final_confidence': float,
                'is_accident': bool,
                'temporal_stability': float,
                'spike_filtered': bool,
                'event_frames': list
            }
        """
        if not frame_confidences or len(frame_confidences) == 0:
            return self._default_result()
        
        # Convert to numpy array
        confidences = np.array(frame_confidences)
        
        # Step 1: Spike filtering
        filtered_confidences, spike_detected = self._filter_spikes(confidences)
        
        # Step 2: Sliding window aggregation
        window_scores = self._sliding_window_aggregate(filtered_confidences)
        
        # Step 3: Temporal consistency check
        consistency_score = self._check_temporal_consistency(filtered_confidences)
        
        # Step 4: Event detection
        event_frames = self._detect_event_frames(filtered_confidences)
        
        # Step 5: Final decision
        final_confidence = self._compute_final_confidence(
            window_scores, 
            consistency_score,
            filtered_confidences
        )
        
        is_accident = (
            final_confidence > 0.5 and 
            consistency_score > self.consistency_threshold
        )
        
        result = {
            'final_confidence': float(final_confidence),
            'is_accident': is_accident,
            'temporal_stability': float(consistency_score),
            'spike_filtered': spike_detected,
            'event_frames': event_frames,
            'max_confidence': float(np.max(confidences)),
            'mean_confidence': float(np.mean(confidences)),
            'confidence_variance': float(np.var(confidences))
        }
        
        logger.info(f"Temporal aggregation: confidence={final_confidence:.3f}, "
                   f"stability={consistency_score:.3f}, accident={is_accident}")
        
        return result
    
    def _filter_spikes(self, confidences):
        """
        Filter out single-frame confidence spikes (false positives)
        
        Returns:
            tuple: (filtered_confidences, spike_detected)
        """
        if len(confidences) < 3:
            return confidences, False
        
        filtered = confidences.copy()
        spike_detected = False
        
        for i in range(1, len(confidences) - 1):
            prev_conf = confidences[i-1]
            curr_conf = confidences[i]
            next_conf = confidences[i+1]
            
            # Detect spike: high confidence surrounded by low confidences
            if (curr_conf > 0.7 and 
                prev_conf < 0.4 and 
                next_conf < 0.4 and
                abs(curr_conf - prev_conf) > self.spike_threshold):
                
                # Replace spike with average of neighbors
                filtered[i] = (prev_conf + next_conf) / 2
                spike_detected = True
                logger.debug(f"Spike filtered at frame {i}: {curr_conf:.3f} -> {filtered[i]:.3f}")
        
        return filtered, spike_detected
    
    def _sliding_window_aggregate(self, confidences):
        """
        Apply sliding window to compute local confidence scores
        
        Returns:
            numpy array: Window-aggregated scores
        """
        if len(confidences) < self.window_size:
            return np.array([np.mean(confidences)])
        
        window_scores = []
        
        for i in range(len(confidences) - self.window_size + 1):
            window = confidences[i:i + self.window_size]
            
            # Weighted average: recent frames have more weight
            weights = np.linspace(0.5, 1.0, self.window_size)
            weighted_score = np.average(window, weights=weights)
            
            window_scores.append(weighted_score)
        
        return np.array(window_scores)
    
    def _check_temporal_consistency(self, confidences):
        """
        Check if high confidence is sustained over multiple frames
        
        Returns:
            float: Consistency score (0-1)
        """
        if len(confidences) == 0:
            return 0.0
        
        # Count frames with confidence > 0.5
        high_conf_frames = np.sum(confidences > 0.5)
        consistency_ratio = high_conf_frames / len(confidences)
        
        # Check for sustained high confidence (at least 3 consecutive frames)
        max_consecutive = 0
        current_consecutive = 0
        
        for conf in confidences:
            if conf > 0.5:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 0
        
        # Combine ratio and consecutive frames
        consistency_score = (consistency_ratio * 0.6) + (min(max_consecutive / 10, 1.0) * 0.4)
        
        return consistency_score
    
    def _detect_event_frames(self, confidences, threshold=0.7):
        """
        Detect frames where accident event likely occurred
        
        Returns:
            list: Frame indices with high confidence
        """
        event_frames = []
        
        for i, conf in enumerate(confidences):
            if conf > threshold:
                event_frames.append(i)
        
        # Group consecutive frames into events
        if event_frames:
            events = []
            start = event_frames[0]
            end = event_frames[0]
            
            for i in range(1, len(event_frames)):
                if event_frames[i] == end + 1:
                    end = event_frames[i]
                else:
                    events.append((start, end))
                    start = event_frames[i]
                    end = event_frames[i]
            
            events.append((start, end))
            return events
        
        return []
    
    def _compute_final_confidence(self, window_scores, consistency_score, confidences):
        """
        Compute final aggregated confidence score
        
        Combines:
        - Maximum window score
        - Temporal consistency
        - Overall mean confidence
        """
        if len(window_scores) == 0:
            return np.mean(confidences)
        
        max_window_score = np.max(window_scores)
        mean_confidence = np.mean(confidences)
        
        # Weighted combination
        final_confidence = (
            max_window_score * 0.5 +
            consistency_score * 0.3 +
            mean_confidence * 0.2
        )
        
        return np.clip(final_confidence, 0.0, 1.0)
    
    def _default_result(self):
        """Return default result when no confidences available"""
        return {
            'final_confidence': 0.0,
            'is_accident': False,
            'temporal_stability': 0.0,
            'spike_filtered': False,
            'event_frames': [],
            'max_confidence': 0.0,
            'mean_confidence': 0.0,
            'confidence_variance': 0.0
        }
