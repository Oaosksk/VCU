"""Frame extraction and accident clip generation service"""
import cv2
import logging
from pathlib import Path
from typing import List, Tuple
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


class AccidentFrameService:
    """Service for extracting and saving accident-detected frames"""
    
    def __init__(self):
        self.frames_dir = Path("./storage/frames")
        self.clips_dir = Path("./storage/clips")
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.clips_dir.mkdir(parents=True, exist_ok=True)
    
    def save_accident_frames(
        self, 
        video_id: str, 
        frames: List[np.ndarray], 
        event_frames: List[Tuple[int, int]],
        detections_per_frame: List[List] = None
    ) -> dict:
        """
        Save accident-detected frames to disk
        
        Args:
            video_id: Unique video identifier
            frames: All extracted frames from video
            event_frames: List of (start_frame, end_frame) tuples for accidents
            
        Returns:
            dict: {
                'total_count': int,
                'saved_frames': List[int],  # Frame indices that were saved
                'frame_dir': str
            }
        """
        if not event_frames:
            logger.info(f"No accident frames to save for video {video_id}")
            return {
                'total_count': 0,
                'saved_frames': [],
                'frame_dir': ''
            }
        
        # Create video-specific directory
        video_frames_dir = self.frames_dir / video_id
        video_frames_dir.mkdir(parents=True, exist_ok=True)
        
        # Collect all accident frame indices
        accident_indices = set()
        for start, end in event_frames:
            for idx in range(start, end + 1):
                if idx < len(frames):
                    accident_indices.add(idx)
        
        # Find the middle frame (peak accident moment)
        if accident_indices:
            sorted_accident = sorted(accident_indices)
            middle_idx = sorted_accident[len(sorted_accident) // 2]
            
            # Select 4 frames: 2 before, accident frame, 2 after
            selected_frames = [
                middle_idx - 2,  # 2 before
                middle_idx - 1,  # 1 before
                middle_idx,      # accident moment
                middle_idx + 1,  # 1 after
                middle_idx + 2   # 2 after
            ]
            
            # Filter valid frame indices
            selected_frames = [idx for idx in selected_frames if 0 <= idx < len(frames)]
        else:
            selected_frames = []
        
        saved_frames = []
        
        # Save frames to disk
        for idx in selected_frames:
            frame = frames[idx].copy()
            
            # Only draw bounding boxes on the middle frame (accident moment)
            if idx == middle_idx and detections_per_frame and idx < len(detections_per_frame):
                detections = detections_per_frame[idx]
                for det in detections:
                    if det['class_name'] in ['car', 'truck', 'bus', 'motorcycle']:
                        bbox = det['bbox']
                        x1, y1, x2, y2 = map(int, bbox)
                        
                        # Draw red bounding box
                        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 3)
                        
                        # Add "Accident Detection" label
                        label = "Accident Detection"
                        font = cv2.FONT_HERSHEY_SIMPLEX
                        font_scale = 0.8
                        thickness = 2
                        
                        # Get text size for background
                        (text_width, text_height), baseline = cv2.getTextSize(label, font, font_scale, thickness)
                        
                        # Draw red background for text
                        cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width + 10, y1), (0, 0, 255), -1)
                        
                        # Draw white text
                        cv2.putText(frame, label, (x1 + 5, y1 - 5), font, font_scale, (255, 255, 255), thickness)
            
            frame_path = video_frames_dir / f"frame_{idx:04d}.jpg"
            
            try:
                # Save with high quality
                cv2.imwrite(str(frame_path), frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
                saved_frames.append(idx)
                logger.debug(f"Saved accident frame {idx} to {frame_path}")
            except Exception as e:
                logger.error(f"Failed to save frame {idx}: {e}")
        
        logger.info(f"Saved {len(saved_frames)} accident frames for video {video_id}")
        
        return {
            'total_count': len(saved_frames),
            'saved_frames': saved_frames,
            'frame_dir': str(video_frames_dir)
        }
    
    def generate_accident_clip(
        self, 
        video_id: str, 
        frames: List[np.ndarray], 
        event_frames: List[Tuple[int, int]],
        fps: float = 10.0
    ) -> str:
        """
        Generate video clip containing only accident frames
        
        Args:
            video_id: Unique video identifier
            frames: All extracted frames
            event_frames: List of (start_frame, end_frame) tuples
            fps: Frames per second for output video
            
        Returns:
            str: Path to generated clip, or empty string if no frames
        """
        if not event_frames or not frames:
            logger.info(f"No accident frames to generate clip for video {video_id}")
            return ""
        
        # Collect accident frames
        accident_indices = set()
        for start, end in event_frames:
            for idx in range(start, end + 1):
                if idx < len(frames):
                    accident_indices.add(idx)
        
        if not accident_indices:
            return ""
        
        # Sort indices
        sorted_indices = sorted(accident_indices)
        
        # Get frame dimensions
        height, width = frames[0].shape[:2]
        
        # Output path
        clip_path = self.clips_dir / f"{video_id}_accident.mp4"
        
        try:
            # Initialize video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(str(clip_path), fourcc, fps, (width, height))
            
            # Write accident frames
            for idx in sorted_indices:
                out.write(frames[idx])
            
            out.release()
            
            logger.info(f"Generated accident clip with {len(sorted_indices)} frames: {clip_path}")
            return str(clip_path)
            
        except Exception as e:
            logger.error(f"Failed to generate accident clip: {e}")
            return ""
    
    def get_frame_urls(
        self, 
        video_id: str, 
        saved_frames: List[int], 
        limit: int = 5
    ) -> List[str]:
        """
        Get URLs for first N accident frames
        
        Args:
            video_id: Video identifier
            saved_frames: List of saved frame indices
            limit: Maximum number of URLs to return
            
        Returns:
            List[str]: Frame URLs (relative paths)
        """
        urls = []
        for idx in sorted(saved_frames)[:limit]:
            # Return relative URL path
            urls.append(f"/frames/{video_id}/frame_{idx:04d}.jpg")
        
        return urls
    
    def get_clip_url(self, video_id: str) -> str:
        """
        Get URL for accident clip
        
        Args:
            video_id: Video identifier
            
        Returns:
            str: Clip URL or empty string
        """
        clip_path = self.clips_dir / f"{video_id}_accident.mp4"
        if clip_path.exists():
            return f"/clips/{video_id}_accident.mp4"
        return ""


# Global instance
accident_frame_service = AccidentFrameService()
