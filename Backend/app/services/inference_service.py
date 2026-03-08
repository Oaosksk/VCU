"""Inference service for video analysis"""
from datetime import datetime
from pathlib import Path
import numpy as np
import logging
import time

INFERENCE_TIMEOUT_SECONDS = 1800  # Abort analysis after 30 minutes


from app.services.video_service import get_video_path
from app.ml.models.yolo_detector import YOLODetector
from app.ml.models.lstm_model import LSTMDetector
from app.ml.pipeline.frame_extractor import FrameExtractor
# FramePreprocessor removed — not used in the current pipeline
from app.services.confidence_service import TemporalConfidenceAggregator
from app.services.frame_service import accident_frame_service
from app.core.config import settings

logger = logging.getLogger(__name__)


# ═════════════════════════════════════════════════════════════════════
# CONFIDENCE RESCALING — Enforced ranges: Accident 91-100, Safe 0-49
# ═════════════════════════════════════════════════════════════════════

def rescale_confidence(raw_confidence: float, is_accident: bool) -> int:
    """
    Map internal 0.0-1.0 confidence to enforced output ranges.

    Rules:
        Accident detected  → 91–100
        No accident        → 0–49
        Range 50–90 is NEVER produced.

    Args:
        raw_confidence: Internal model confidence (0.0 to 1.0)
        is_accident: Whether the system classified this as an accident

    Returns:
        int: Rescaled confidence score in the enforced range.
    """
    clamped = max(0.0, min(1.0, raw_confidence))

    if is_accident:
        # Internal accident threshold is ~0.5; map 0.5-1.0 → 91-100
        normalized = (clamped - 0.5) / 0.5  # 0.0 to 1.0
        normalized = max(0.0, min(1.0, normalized))
        return int(91 + normalized * 9)  # 91-100
    else:
        # Map 0.0-0.5 → 0-49 (linear)
        if clamped >= 0.5:
            # Edge case: internal conf is ≥0.5 but is_accident is False
            # (forced off by vehicle penalty). Cap at 49.
            return 49
        return int((clamped / 0.5) * 49)  # 0-49


def classify_severity(
    confidence: int,
    is_accident: bool,
    event_frames: list,
    total_event_duration: float,
) -> str:
    """
    Classify accident severity based on confidence + event characteristics.

    Returns: "critical" | "moderate" | "minor" | "none"
    """
    if not is_accident:
        return "none"

    if confidence >= 97 or total_event_duration > 3.0:
        return "critical"
    if confidence >= 94 or len(event_frames) > 1:
        return "moderate"
    return "minor"


def infer_accident_type(
    detections_per_frame: list,
    event_frames: list,
    total_vehicles: int,
) -> str | None:
    """
    Infer accident type from detection patterns.

    Returns: Accident type string or None if no accident.
    """
    if not event_frames:
        return None

    # Count vehicles specifically in event frames
    event_vehicle_counts = []
    for start, end in event_frames:
        for idx in range(start, min(end + 1, len(detections_per_frame))):
            vehicles_in_frame = [
                d for d in detections_per_frame[idx]
                if d['class_name'] in ['car', 'truck', 'bus', 'motorcycle']
            ]
            event_vehicle_counts.append(len(vehicles_in_frame))

    max_vehicles_in_event = max(event_vehicle_counts) if event_vehicle_counts else 0

    if max_vehicles_in_event >= 3:
        return "Multi-Vehicle Collision"
    elif max_vehicles_in_event == 2:
        return "Vehicle Collision"
    elif max_vehicles_in_event == 1:
        return "Single Vehicle Accident"
    elif total_vehicles > 0:
        return "Vehicle Incident"
    else:
        return "Unclassified Incident"


def generate_reasoning(
    is_accident: bool,
    confidence: int,
    total_frames: int,
    total_vehicles: int,
    temporal_stability: float,
    event_frames: list,
    accident_type: str | None,
    severity: str,
) -> str:
    """
    Generate a concise 2-3 sentence forensic reasoning string.
    """
    if not is_accident:
        return (
            f"Analysis of {total_frames} frames detected {total_vehicles} vehicle(s) "
            f"with a temporal stability of {temporal_stability:.2f}. "
            f"No sustained collision patterns were observed. "
            f"Confidence is {confidence}% that this footage contains normal driving."
        )

    # Build event description
    event_desc = ""
    if event_frames:
        frame_ranges = [f"{s}-{e}" for s, e in event_frames]
        event_desc = f"across frames [{', '.join(frame_ranges)}]"

    return (
        f"Detected {accident_type or 'an accident'} with {confidence}% confidence "
        f"({severity} severity). "
        f"Spatio-temporal analysis of {total_frames} frames identified "
        f"{total_vehicles} vehicle(s) with abnormal motion patterns {event_desc}. "
        f"Temporal consistency score: {temporal_stability:.2f}."
    )


async def analyze_video_file(video_id: str, db=None) -> dict:
    """
    Hybrid physics-based + LSTM accident detector.

    Decision hierarchy (in order of priority):
      1. HARD GATE  — No vehicles detected  → NO ACCIDENT (non-dashcam video)
      2. HARD GATE  — Very few vehicles across entire video  → NO ACCIDENT
      3. PHYSICS    — Bounding box overlap, motion velocity, size change
      4. LSTM       — Temporal pattern confirmation (only if physics signal > 0)
      5. FINAL      — Weighted combination of physics + LSTM scores
    """
    start_time = time.time()

    try:
        logger.info(f"Starting analysis for video: {video_id}")
        video_path = get_video_path(video_id)
        logger.info(f"Video path: {video_path}")

        # Initialize components
        frame_extractor = FrameExtractor()
        yolo_detector   = YOLODetector()
        lstm_detector   = LSTMDetector(settings.LSTM_MODEL_PATH)
        confidence_aggregator = TemporalConfidenceAggregator(
            window_size=settings.CONFIDENCE_WINDOW_SIZE,
            spike_threshold=0.3,
            consistency_threshold=0.35,
        )

        # ── Extract frames ────────────────────────────────────────────
        logger.info("Extracting frames...")
        frames = frame_extractor.extract_frames(video_path)
        video_info = frame_extractor.get_video_info(video_path)
        logger.info(f"Extracted {len(frames)} frames from video")
        if not frames:
            raise ValueError("No frames extracted from video")

        elapsed = time.time() - start_time
        if elapsed > INFERENCE_TIMEOUT_SECONDS:
            raise TimeoutError(f"Inference timed out during frame extraction")

        # ── Step 1: YOLO Detection ────────────────────────────────────
        logger.info("Running YOLOv8 detection...")
        detections_per_frame = []
        lstm_features = []
        vehicle_classes = {'car', 'truck', 'bus', 'motorcycle'}

        for frame in frames:
            dets = yolo_detector.detect(frame)
            detections_per_frame.append(dets)
            vehicles = [d for d in dets if d['class_name'] in vehicle_classes]

            if vehicles:
                num_v     = len(vehicles)
                avg_conf  = float(np.mean([d['confidence'] for d in vehicles]))
                bboxes    = np.array([d['bbox'] for d in vehicles])
                bbox_var  = float(np.var(bboxes))
            else:
                num_v, avg_conf, bbox_var = 0, 0.0, 0.0

            # Z-score normalization — identical constants to extract_features.py
            V_MEAN, V_STD = 2.5, 3.0
            C_MEAN, C_STD = 0.4, 0.25
            B_MEAN, B_STD = 50000.0, 150000.0
            lstm_features.append([
                (num_v    - V_MEAN) / V_STD,
                (avg_conf - C_MEAN) / C_STD,
                (bbox_var - B_MEAN) / B_STD,
            ])

        logger.info(f"YOLO detection complete: {len(lstm_features)} frames")
        elapsed = time.time() - start_time
        if elapsed > INFERENCE_TIMEOUT_SECONDS:
            raise TimeoutError(f"Inference timed out during YOLO detection")

        # ── Step 2: Physics-Based Accident Scoring ────────────────────
        # Derived entirely from YOLO bounding boxes — no ML needed.
        logger.info("Computing physics-based accident score...")

        per_frame_vehicles = [
            [d for d in dets if d['class_name'] in vehicle_classes]
            for dets in detections_per_frame
        ]

        # Gate 1: overall vehicle presence
        total_vehicles    = sum(len(v) for v in per_frame_vehicles)
        frames_with_vehicles = sum(1 for v in per_frame_vehicles if len(v) > 0)
        vehicle_coverage  = frames_with_vehicles / max(len(frames), 1)  # 0–1
        avg_vehicles_per_frame = total_vehicles / max(len(frames), 1)

        logger.info(
            f"Vehicle stats: total={total_vehicles}, coverage={vehicle_coverage:.2f}, "
            f"avg_per_frame={avg_vehicles_per_frame:.2f}"
        )

        # ── HARD GATE 1: Not a driving video ──────────────────────────
        if vehicle_coverage < 0.15 or avg_vehicles_per_frame < 0.2:
            logger.info(
                f"HARD GATE triggered: vehicle_coverage={vehicle_coverage:.2f} < 0.15 "
                f"or avg_vehicles={avg_vehicles_per_frame:.2f} < 0.2 → NO ACCIDENT"
            )
            is_accident    = False
            raw_confidence = max(0.01, avg_vehicles_per_frame * 0.2)  # tiny confidence
            aggregation_result = {
                'final_confidence': raw_confidence,
                'is_accident': False,
                'temporal_stability': 0.0,
                'spike_filtered': False,
                'event_frames': [],
                'max_confidence': raw_confidence,
                'mean_confidence': raw_confidence,
            }

        else:
            # ── Physics Score: measure real accident indicators ────────
            overlap_scores   = []   # vehicle bbox overlap  (collision)
            motion_scores    = []   # sudden velocity change (impact)
            size_change_scores = [] # bbox area change      (crash/flip)

            prev_centers = []
            prev_areas   = []

            for vehicles in per_frame_vehicles:
                bboxes = [v['bbox'] for v in vehicles]  # [x1,y1,x2,y2]
                areas  = [(b[2]-b[0])*(b[3]-b[1]) for b in bboxes]
                centers = [((b[0]+b[2])/2, (b[1]+b[3])/2) for b in bboxes]

                # Overlap: do any two vehicle bboxes intersect?
                frame_overlap = 0.0
                for i in range(len(bboxes)):
                    for j in range(i+1, len(bboxes)):
                        b1, b2 = bboxes[i], bboxes[j]
                        ix1 = max(b1[0], b2[0]); iy1 = max(b1[1], b2[1])
                        ix2 = min(b1[2], b2[2]); iy2 = min(b1[3], b2[3])
                        if ix2 > ix1 and iy2 > iy1:
                            inter   = (ix2-ix1) * (iy2-iy1)
                            union   = areas[i] + areas[j] - inter
                            frame_overlap = max(frame_overlap, inter / max(union, 1))
                overlap_scores.append(frame_overlap)

                # Motion: compare centers with previous frame
                if prev_centers and centers:
                    dists = []
                    for c in centers:
                        nearest = min(prev_centers, key=lambda p: (p[0]-c[0])**2+(p[1]-c[1])**2)
                        d = ((nearest[0]-c[0])**2 + (nearest[1]-c[1])**2) ** 0.5
                        dists.append(d)
                    motion_scores.append(float(np.mean(dists)))

                # Area change: sudden size change = crash indicator
                if prev_areas and areas:
                    min_len = min(len(prev_areas), len(areas))
                    pct_changes = [
                        abs(areas[k] - prev_areas[k]) / max(prev_areas[k], 1)
                        for k in range(min_len)
                    ]
                    size_change_scores.append(float(np.mean(pct_changes)))

                prev_centers = centers
                prev_areas   = areas

            # Combine physics signals
            max_overlap     = float(np.max(overlap_scores))         if overlap_scores     else 0.0
            motion_arr      = np.array(motion_scores)               if motion_scores      else np.array([0.0])
            size_arr        = np.array(size_change_scores)          if size_change_scores else np.array([0.0])

            # Sudden motion spike (top 10% of frames exceeds threshold)
            motion_p90      = float(np.percentile(motion_arr, 90))  if len(motion_arr) > 0 else 0.0
            motion_score    = min(motion_p90 / 80.0, 1.0)           # 80px jump = 1.0 score

            size_p90        = float(np.percentile(size_arr, 90))    if len(size_arr) > 0 else 0.0
            size_score      = min(size_p90 / 0.5, 1.0)              # 50% size change = 1.0

            # Per-frame combined physics score (for frame selection later)
            n = len(per_frame_vehicles)
            motion_padded = [0.0] + motion_scores + [0.0] * (n - len(motion_scores) - 1)
            size_padded   = [0.0] + size_change_scores + [0.0] * (n - len(size_change_scores) - 1)
            per_frame_physics = [
                overlap_scores[i] * 0.55 +
                min(motion_padded[i] / 80.0, 1.0) * 0.30 +
                min(size_padded[i] / 0.5,   1.0) * 0.15
                for i in range(n)
            ]

            # Final physics score: weighted combination
            physics_score = (
                max_overlap  * 0.45 +   # vehicle collision (strongest signal)
                motion_score * 0.35 +   # sudden movement
                size_score   * 0.20     # bbox size change
            )

            logger.info(
                f"Physics score: {physics_score:.3f} "
                f"(overlap={max_overlap:.3f}, motion={motion_score:.3f}, size={size_score:.3f})"
            )

            # ── HARD GATE 2: No physics signal = no accident ──────────
            # Even if LSTM fires, without any physical evidence → reject
            if physics_score < 0.05 and max_overlap < 0.01:
                logger.info(
                    f"HARD GATE 2: physics_score={physics_score:.3f} < 0.05 "
                    f"and no overlap → NO ACCIDENT"
                )
                is_accident    = False
                raw_confidence = physics_score * 0.5
                aggregation_result = {
                    'final_confidence': raw_confidence,
                    'is_accident': False,
                    'temporal_stability': 0.0,
                    'spike_filtered': False,
                    'event_frames': [],
                    'max_confidence': raw_confidence,
                    'mean_confidence': raw_confidence,
                }

            else:
                # ── Step 3: LSTM Temporal Analysis ───────────────────
                logger.info("Running LSTM temporal analysis...")
                max_frames = 150
                padded = np.array(lstm_features[:max_frames] if len(lstm_features) >= max_frames
                                  else lstm_features + [[0,0,0]]*(max_frames - len(lstm_features)))
                frame_confidences = lstm_detector.predict_sequence(padded)

                elapsed = time.time() - start_time
                if elapsed > INFERENCE_TIMEOUT_SECONDS:
                    raise TimeoutError(f"Inference timed out during LSTM analysis")

                # ── Step 4: Temporal Aggregation ─────────────────────
                logger.info("Applying temporal confidence aggregation...")
                aggregation_result = confidence_aggregator.aggregate(frame_confidences)
                lstm_confidence    = aggregation_result['final_confidence']

                # ── Step 5: Hybrid Final Decision ────────────────────
                # Physics score gates the LSTM — LSTM alone cannot fire an accident
                # Physics weight: 60%, LSTM weight: 40%
                raw_confidence = physics_score * 0.60 + lstm_confidence * 0.40

                # Extra gate: if physics says no but LSTM says yes → trust physics
                if physics_score < 0.15:
                    raw_confidence = physics_score * 0.80  # physics dominates
                    logger.info(f"Low physics score — LSTM overridden, conf={raw_confidence:.3f}")

                is_accident = raw_confidence > 0.50 and physics_score >= 0.10

                logger.info(
                    f"Hybrid decision: physics={physics_score:.3f} lstm={lstm_confidence:.3f} "
                    f"combined={raw_confidence:.3f} is_accident={is_accident}"
                )

        status = "accident" if is_accident else "no_accident"

        # Variables may not be set when a hard gate fired — ensure they exist
        try:    frame_confidences
        except NameError: frame_confidences = []
        try:    overlap_scores
        except NameError: overlap_scores = []

        # Step 6: Save Accident Events
        event_frames = aggregation_result.get('event_frames', [])
        frame_data = {'total_count': 0, 'frame_urls': [], 'clip_url': ''}

        # Fallback: If accident detected but no specific event frames,
        # pick top overlap frames (physics-based) or LSTM confidence frames
        if is_accident and not event_frames:
            logger.info("Accident detected but no event frames found. Using top physics frames.")
            if 'frame_confidences' in dir() or 'frame_confidences' in locals():
                scores = np.array(frame_confidences)
            elif overlap_scores:
                scores = np.array(overlap_scores + [0.0] * (len(frames) - len(overlap_scores)))
            else:
                scores = np.zeros(len(frames))
            top_indices = sorted(np.argsort(scores)[-10:].tolist())
            if top_indices:
                current_start = top_indices[0]
                current_end   = top_indices[0]
                for i in range(1, len(top_indices)):
                    if top_indices[i] == current_end + 1:
                        current_end = top_indices[i]
                    else:
                        event_frames.append((current_start, current_end))
                        current_start = top_indices[i]
                        current_end   = top_indices[i]
                event_frames.append((current_start, current_end))

        if is_accident and event_frames:
            logger.info(f"Saving accident frames for video: {video_id}")

            # Get per-frame physics if available (from physics analysis path)
            _per_frame_physics = per_frame_physics if 'per_frame_physics' in dir() else []
            try:    _per_frame_physics = per_frame_physics
            except NameError: _per_frame_physics = []

            # Save frames to disk (uses physics peak for exact frame selection)
            save_result = accident_frame_service.save_accident_frames(
                video_id=video_id,
                frames=frames,
                event_frames=event_frames,
                detections_per_frame=detections_per_frame,
                per_frame_physics=_per_frame_physics,
            )

            # Generate annotated accident clip around collision peak
            clip_path = accident_frame_service.generate_accident_clip(
                video_id=video_id,
                frames=frames,
                event_frames=event_frames,
                fps=video_info.get('fps', 10.0),
                detections_per_frame=detections_per_frame,
                per_frame_physics=_per_frame_physics,
            )

            # Get URLs
            frame_urls = accident_frame_service.get_frame_urls(
                video_id=video_id,
                saved_frames=save_result['saved_frames'],
                limit=5
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

        # ═════════════════════════════════════════════════════════════
        # RESCALE CONFIDENCE — Enforced ranges: 91-100 / 0-49
        # ═════════════════════════════════════════════════════════════
        confidence_score = rescale_confidence(raw_confidence, is_accident)

        # Calculate total event duration
        fps = video_info.get('fps', 10.0)
        total_event_duration = 0.0
        for start, end in event_frames:
            total_event_duration += (end - start) / fps

        # Classify severity
        severity = classify_severity(
            confidence_score, is_accident, event_frames, total_event_duration
        )

        # Infer accident type
        accident_type = infer_accident_type(
            detections_per_frame, event_frames, total_vehicles
        )

        # Build frame evidence string
        frame_evidence = ""
        if event_frames:
            frame_ranges = [f"frames {s}-{e}" for s, e in event_frames]
            frame_evidence = ", ".join(frame_ranges)
        else:
            frame_evidence = f"No specific event frames (analyzed {len(frames)} total)"

        # Generate forensic reasoning
        reasoning = generate_reasoning(
            is_accident=is_accident,
            confidence=confidence_score,
            total_frames=len(frames),
            total_vehicles=total_vehicles,
            temporal_stability=aggregation_result['temporal_stability'],
            event_frames=event_frames,
            accident_type=accident_type,
            severity=severity,
        )

        # Calculate inference time
        inference_time = time.time() - start_time

        logger.info(
            f"Analysis complete. Status: {status}, Confidence: {confidence_score}%, "
            f"Severity: {severity}, Time: {inference_time:.2f}s"
        )

        # Prepare result — includes BOTH legacy fields AND new enforced fields
        result = {
            "id": f"result-{video_id}",
            "status": status,
            "confidence": confidence_score,             # 0-100 int (enforced ranges)
            "timestamp": datetime.now().isoformat(),
            "inference_time": round(float(inference_time), 3),

            # ── NEW: Required detection output fields ──
            "isAccident": is_accident,
            "accidentType": accident_type,
            "severity": severity,
            "frameEvidence": frame_evidence,
            "reasoning": reasoning,

            # ── Details (preserved for frontend compatibility) ──
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
                "totalVehicles": total_vehicles,
                # Accident frame data
                "accidentFrameCount": int(frame_data['total_count']),
                "accidentFrameUrls": frame_data['frame_urls'],
                "accidentClipUrl": frame_data['clip_url'],
                # New detailed fields
                "accidentType": accident_type,
                "severity": severity,
                "frameEvidence": frame_evidence,
                "reasoning": reasoning,
                "rawConfidence": round(float(raw_confidence), 4),
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
