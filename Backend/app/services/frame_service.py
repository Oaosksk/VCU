"""Frame extraction and accident clip generation service"""
import cv2
import logging
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np

from app.core.config import settings

logger = logging.getLogger(__name__)


def _compute_iou(b1, b2):
    """Intersection-over-Union of two [x1,y1,x2,y2] boxes."""
    ix1 = max(b1[0], b2[0]); iy1 = max(b1[1], b2[1])
    ix2 = min(b1[2], b2[2]); iy2 = min(b1[3], b2[3])
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    inter = (ix2 - ix1) * (iy2 - iy1)
    a1 = max((b1[2]-b1[0]) * (b1[3]-b1[1]), 1)
    a2 = max((b2[2]-b2[0]) * (b2[3]-b2[1]), 1)
    return inter / (a1 + a2 - inter)


def _find_collision_peak(
    frames: list,
    detections_per_frame: list,
    per_frame_physics: list,
    event_frames: List[Tuple[int, int]],
) -> int:
    """
    Find the exact frame index of peak collision signal.
    Uses per-frame physics scores (overlap + motion) rather than LSTM confidence.
    Falls back to middle of event_frames if no physics scores available.
    """
    vehicle_classes = {'car', 'truck', 'bus', 'motorcycle'}

    if per_frame_physics and len(per_frame_physics) > 0:
        # Use the physics score peak as the collision moment
        scores = np.array(per_frame_physics)
        peak_idx = int(np.argmax(scores))
        # Clip to valid frame range
        return min(peak_idx, len(frames) - 1)

    # Fallback 1: compute overlap per frame directly
    if detections_per_frame:
        overlap_per_frame = []
        for dets in detections_per_frame:
            vehicles = [d for d in dets if d['class_name'] in vehicle_classes]
            bboxes = [v['bbox'] for v in vehicles]
            frame_max_iou = 0.0
            for i in range(len(bboxes)):
                for j in range(i + 1, len(bboxes)):
                    iou = _compute_iou(bboxes[i], bboxes[j])
                    frame_max_iou = max(frame_max_iou, iou)
            overlap_per_frame.append(frame_max_iou)

        if max(overlap_per_frame) > 0:
            return int(np.argmax(overlap_per_frame))

    # Fallback 2: middle of event_frames span
    if event_frames:
        all_indices = [i for s, e in event_frames for i in range(s, e + 1) if i < len(frames)]
        if all_indices:
            return all_indices[len(all_indices) // 2]

    return len(frames) // 2


def _draw_annotated_frame(
    frame: np.ndarray,
    detections: list,
    is_impact: bool,
    frame_label: str = "",
) -> np.ndarray:
    """
    Draw bounding boxes on a frame with collision-aware colour coding.

    Colour scheme:
      RED   (#FF4444) — colliding vehicles (IoU overlap detected between any pair)
      AMBER (#FFA000) — vehicles involved in high-motion event (impact frame)
      GREEN (#00C853) — other detected vehicles (context)

    Labels show vehicle class + detection confidence.
    """
    vehicle_classes = {'car', 'truck', 'bus', 'motorcycle'}
    out = frame.copy()
    h, w = out.shape[:2]

    vehicles = [d for d in detections if d['class_name'] in vehicle_classes]
    if not vehicles:
        # Still stamp a label overlay
        _stamp_frame_label(out, frame_label, color=(200, 200, 200))
        return out

    bboxes = [v['bbox'] for v in vehicles]

    # ── Determine which vehicles are in collision ──────────────────
    collision_set = set()
    for i in range(len(bboxes)):
        for j in range(i + 1, len(bboxes)):
            if _compute_iou(bboxes[i], bboxes[j]) > 0.05:   # 5% IoU = overlap
                collision_set.add(i)
                collision_set.add(j)

    # ── Draw each vehicle ──────────────────────────────────────────
    for idx, (det, bbox) in enumerate(zip(vehicles, bboxes)):
        x1, y1, x2, y2 = map(int, bbox)
        conf  = det.get('confidence', 0)
        label = det['class_name'].capitalize()

        if idx in collision_set:
            # Colliding — RED with thick border
            color      = (0, 60, 255)     # BGR red
            thickness  = 4
            tag        = f"COLLISION  {conf:.0%}"
        elif is_impact:
            # Impact frame, not directly colliding — AMBER
            color      = (0, 160, 255)    # BGR amber
            thickness  = 3
            tag        = f"{label}  {conf:.0%}"
        else:
            # Context vehicle — GREEN
            color      = (50, 200, 80)    # BGR green
            thickness  = 2
            tag        = f"{label}  {conf:.0%}"

        # Draw box
        cv2.rectangle(out, (x1, y1), (x2, y2), color, thickness)

        # Draw label pill
        font       = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = max(0.55, min(w / 1500, 0.9))
        (tw, th), bl = cv2.getTextSize(tag, font, font_scale, 2)
        pill_y1 = max(y1 - th - 8, 0)
        pill_y2 = max(y1, th + 8)
        cv2.rectangle(out, (x1, pill_y1), (x1 + tw + 8, pill_y2), color, -1)
        cv2.putText(out, tag, (x1 + 4, pill_y2 - 4), font, font_scale, (255, 255, 255), 2, cv2.LINE_AA)

    # ── Stamp frame context label (e.g. "-1s", "IMPACT", "+1s") ───
    if frame_label:
        _stamp_frame_label(out, frame_label, color=(0, 60, 255) if frame_label == "IMPACT" else (255, 255, 255))

    return out


def _stamp_frame_label(frame: np.ndarray, label: str, color=(255, 255, 255)):
    """Stamp a small timestamp / context label in the bottom-left corner."""
    h, w = frame.shape[:2]
    font = cv2.FONT_HERSHEY_SIMPLEX
    scale = max(0.6, min(w / 1200, 1.0))
    (tw, th), bl = cv2.getTextSize(label, font, scale, 2)
    x, y = 12, h - 14
    cv2.rectangle(frame, (x - 4, y - th - 6), (x + tw + 4, y + bl), (0, 0, 0), -1)
    cv2.putText(frame, label, (x, y), font, scale, color, 2, cv2.LINE_AA)


class AccidentFrameService:
    """Service for extracting and saving accident-detected frames"""

    def __init__(self):
        self.frames_dir = Path("./storage/frames")
        self.clips_dir  = Path("./storage/clips")
        self.frames_dir.mkdir(parents=True, exist_ok=True)
        self.clips_dir.mkdir(parents=True, exist_ok=True)

    def save_accident_frames(
        self,
        video_id: str,
        frames: List[np.ndarray],
        event_frames: List[Tuple[int, int]],
        detections_per_frame: List[List] = None,
        per_frame_physics: List[float] = None,
    ) -> dict:
        """
        Save the 5-frame accident sequence centred on the physics peak.

        Frame selection:
          [-2s]  [-1s]  [IMPACT]  [+1s]  [+2s]
          relative to the frame with highest collision signal.

        Bounding boxes:
          RED   — vehicles with detected overlap (collision pair)
          AMBER — other vehicles in the impact frame
          GREEN — vehicles in context frames
        """
        if not event_frames and not per_frame_physics:
            logger.info(f"No accident frames to save for video {video_id}")
            return {'total_count': 0, 'saved_frames': [], 'frame_dir': ''}

        video_frames_dir = self.frames_dir / video_id
        video_frames_dir.mkdir(parents=True, exist_ok=True)

        # ── Find exact collision peak ──────────────────────────────
        peak_idx = _find_collision_peak(
            frames, detections_per_frame or [], per_frame_physics or [], event_frames
        )
        logger.info(f"Collision peak at frame {peak_idx} (of {len(frames)} total)")

        # ── Build 5-frame sequence around peak ─────────────────────
        # Labels: -2s, -1s, IMPACT, +1s, +2s
        offsets = [-2, -1, 0, 1, 2]
        labels  = ["-2s", "-1s", "IMPACT", "+1s", "+2s"]

        selected = []
        for offset, lbl in zip(offsets, labels):
            idx = peak_idx + offset
            if 0 <= idx < len(frames):
                selected.append((idx, lbl))

        saved_frames = []
        for idx, lbl in selected:
            frame = frames[idx].copy()
            is_impact = (lbl == "IMPACT")

            dets = detections_per_frame[idx] if (detections_per_frame and idx < len(detections_per_frame)) else []
            annotated = _draw_annotated_frame(frame, dets, is_impact=is_impact, frame_label=lbl)

            frame_path = video_frames_dir / f"frame_{idx:04d}.jpg"
            try:
                cv2.imwrite(str(frame_path), annotated, [cv2.IMWRITE_JPEG_QUALITY, 95])
                saved_frames.append(idx)
                logger.debug(f"Saved {'IMPACT' if is_impact else 'context'} frame {idx} → {frame_path.name}")
            except Exception as e:
                logger.error(f"Failed to save frame {idx}: {e}")

        logger.info(f"Saved {len(saved_frames)} accident frames for video {video_id} (peak={peak_idx})")
        return {
            'total_count': len(saved_frames),
            'saved_frames': saved_frames,
            'frame_dir': str(video_frames_dir),
            'peak_frame': peak_idx,
        }

    def generate_accident_clip(
        self,
        video_id: str,
        frames: List[np.ndarray],
        event_frames: List[Tuple[int, int]],
        fps: float = 10.0,
        detections_per_frame: List[List] = None,
        per_frame_physics: List[float] = None,
    ) -> str:
        """
        Generate a short clip (±3s around collision peak) with annotated bounding boxes.
        """
        if not frames:
            return ""

        peak_idx = _find_collision_peak(
            frames, detections_per_frame or [], per_frame_physics or [], event_frames
        )

        # ±3 seconds around peak
        window = int(fps * 3)
        start  = max(0, peak_idx - window)
        end    = min(len(frames) - 1, peak_idx + window)
        clip_indices = list(range(start, end + 1))

        if not clip_indices:
            return ""

        h, w = frames[0].shape[:2]
        clip_path = self.clips_dir / f"{video_id}_accident.mp4"

        try:
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out_writer = cv2.VideoWriter(str(clip_path), fourcc, fps, (w, h))

            for idx in clip_indices:
                frame = frames[idx].copy()
                dets  = detections_per_frame[idx] if (detections_per_frame and idx < len(detections_per_frame)) else []
                is_impact = (idx == peak_idx)
                lbl = "IMPACT" if is_impact else (f"-{peak_idx-idx}f" if idx < peak_idx else f"+{idx-peak_idx}f")
                annotated = _draw_annotated_frame(frame, dets, is_impact=is_impact, frame_label=lbl)
                out_writer.write(annotated)

            out_writer.release()
            logger.info(f"Generated accident clip ({len(clip_indices)} frames, peak={peak_idx}): {clip_path}")
            return str(clip_path)

        except Exception as e:
            logger.error(f"Failed to generate accident clip: {e}")
            return ""

    def get_frame_urls(
        self,
        video_id: str,
        saved_frames: List[int],
        limit: int = 5,
    ) -> List[str]:
        """Return relative URL paths for saved frames, in chronological order."""
        return [
            f"/frames/{video_id}/frame_{idx:04d}.jpg"
            for idx in sorted(saved_frames)[:limit]
        ]

    def get_clip_url(self, video_id: str) -> str:
        clip_path = self.clips_dir / f"{video_id}_accident.mp4"
        return f"/clips/{video_id}_accident.mp4" if clip_path.exists() else ""


# Global instance
accident_frame_service = AccidentFrameService()
