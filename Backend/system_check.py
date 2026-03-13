"""
COMPREHENSIVE SYSTEM CHECK
Tests all components: frame extraction, YOLO detection, LSTM, physics engine
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import cv2
import numpy as np
import torch
from app.ml.pipeline.frame_extractor import FrameExtractor
from app.ml.models.yolo_detector import YOLODetector
from app.ml.models.lstm_model import LSTMDetector
from app.core.config import settings

print("\n" + "="*70)
print("COMPREHENSIVE SYSTEM CHECK")
print("="*70 + "\n")

# CHECK 1: Frame Extraction
print("1. FRAME EXTRACTION TEST")
print("-" * 70)
test_video = Path("C:\\XboxGames\\GameSave\\ACD\\Backend\\dataset\\Accident Videos") / list(Path("C:\\XboxGames\\GameSave\\ACD\\Backend\\dataset\\Accident Videos").glob("*.mp4"))[0] if Path("C:\\XboxGames\\GameSave\\ACD\\Backend\\dataset\\Accident Videos").exists() else None

if test_video and test_video.exists():
    extractor = FrameExtractor()
    frames = extractor.extract_frames(str(test_video))
    video_info = extractor.get_video_info(str(test_video))
    
    print(f"✓ Video: {test_video.name}")
    print(f"✓ Extracted: {len(frames)} frames")
    print(f"✓ Duration: {video_info['duration']:.1f}s")
    print(f"✓ FPS: {video_info['fps']:.1f}")
    print(f"✓ Frame shape: {frames[0].shape if frames else 'N/A'}")
    
    if len(frames) == 0:
        print("✗ ERROR: No frames extracted!")
    elif len(frames) < 30:
        print(f"⚠ WARNING: Only {len(frames)} frames (expected ~150)")
else:
    print("✗ No test video found in dataset/accident/")
    frames = None

print()

# CHECK 2: YOLO Detection
print("2. YOLO DETECTION TEST")
print("-" * 70)
try:
    yolo = YOLODetector()
    yolo.load_model()
    print(f"✓ YOLO model loaded: {settings.YOLO_MODEL_PATH}")
    print(f"✓ Device: {yolo.get_device()}")
    
    if frames:
        test_frame = frames[len(frames)//2]  # middle frame
        detections = yolo.detect(test_frame)
        vehicles = [d for d in detections if d['class_name'] in ['car', 'truck', 'bus', 'motorcycle']]
        
        print(f"✓ Test frame detections: {len(detections)} objects")
        print(f"✓ Vehicles detected: {len(vehicles)}")
        
        if vehicles:
            classes = [v['class_name'] for v in vehicles[:5]]
            confs = [f"{v['confidence']:.2f}" for v in vehicles[:5]]
            print(f"  Classes: {classes}")
            print(f"  Confidences: {confs}")
        else:
            print("⚠ WARNING: No vehicles detected in test frame!")
            
except Exception as e:
    print(f"✗ YOLO ERROR: {e}")

print()

# CHECK 3: LSTM Model
print("3. LSTM MODEL TEST")
print("-" * 70)
try:
    lstm = LSTMDetector(settings.LSTM_MODEL_PATH)
    print(f"✓ LSTM model loaded: {settings.LSTM_MODEL_PATH}")
    print(f"✓ Device: {lstm.device}")
    
    # Test prediction
    test_features = np.random.randn(150, 3).astype(np.float32)
    confidence = lstm.predict(test_features)
    print(f"✓ Test prediction: {confidence:.4f}")
    
    if confidence < 0 or confidence > 1:
        print(f"✗ ERROR: Invalid confidence range!")
    
except FileNotFoundError:
    print(f"✗ LSTM model not found: {settings.LSTM_MODEL_PATH}")
    print("  Run: python scripts/train_lstm.py")
except Exception as e:
    print(f"✗ LSTM ERROR: {e}")

print()

# CHECK 4: Physics Engine
print("4. PHYSICS ENGINE TEST")
print("-" * 70)
if frames and len(frames) > 10:
    # Simulate physics calculations
    vehicle_classes = {'car', 'truck', 'bus', 'motorcycle'}
    
    per_frame_vehicles = []
    for i in range(min(10, len(frames))):
        dets = yolo.detect(frames[i])
        vehicles = [d for d in dets if d['class_name'] in vehicle_classes]
        per_frame_vehicles.append(vehicles)
    
    # Calculate overlap
    overlap_scores = []
    for vehicles in per_frame_vehicles:
        bboxes = [v['bbox'] for v in vehicles]
        frame_overlap = 0.0
        for i in range(len(bboxes)):
            for j in range(i+1, len(bboxes)):
                b1, b2 = bboxes[i], bboxes[j]
                ix1 = max(b1[0], b2[0]); iy1 = max(b1[1], b2[1])
                ix2 = min(b1[2], b2[2]); iy2 = min(b1[3], b2[3])
                if ix2 > ix1 and iy2 > iy1:
                    inter = (ix2-ix1) * (iy2-iy1)
                    areas_i = (b1[2]-b1[0]) * (b1[3]-b1[1])
                    areas_j = (b2[2]-b2[0]) * (b2[3]-b2[1])
                    union = areas_i + areas_j - inter
                    frame_overlap = max(frame_overlap, inter / max(union, 1))
        overlap_scores.append(frame_overlap)
    
    max_overlap = max(overlap_scores) if overlap_scores else 0
    avg_overlap = np.mean(overlap_scores) if overlap_scores else 0
    
    print(f"✓ Tested {len(per_frame_vehicles)} frames")
    print(f"✓ Max overlap (IoU): {max_overlap:.4f}")
    print(f"✓ Avg overlap (IoU): {avg_overlap:.4f}")
    
    if max_overlap > 0.1:
        print(f"  → Collision detected (overlap > 0.1)")
    else:
        print(f"  → No collision (overlap < 0.1)")
else:
    print("⚠ Skipped (no frames available)")

print()

# CHECK 5: Configuration
print("5. CONFIGURATION CHECK")
print("-" * 70)
print(f"YOLO_MODEL_PATH: {settings.YOLO_MODEL_PATH}")
print(f"LSTM_MODEL_PATH: {settings.LSTM_MODEL_PATH}")
print(f"USE_GPU: {settings.USE_GPU}")
print(f"CONFIDENCE_WINDOW_SIZE: {settings.CONFIDENCE_WINDOW_SIZE}")
print(f"CONFIDENCE_THRESHOLD: {settings.CONFIDENCE_THRESHOLD}")
print(f"TARGET_FPS: {settings.TARGET_FPS}")
print(f"MAX_INFERENCE_FRAMES: {settings.MAX_INFERENCE_FRAMES}")

print()

# CHECK 6: GPU/CPU
print("6. HARDWARE CHECK")
print("-" * 70)
if torch.cuda.is_available():
    print(f"✓ GPU Available: {torch.cuda.get_device_name(0)}")
    print(f"✓ CUDA Version: {torch.version.cuda}")
    print(f"✓ GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.1f} GB")
else:
    print("⚠ No GPU available - using CPU")
    print("  (Inference will be slower)")

print()

# SUMMARY
print("="*70)
print("SUMMARY")
print("="*70)
print("\nIf all checks passed (✓), the system is working correctly.")
print("\nIf you see errors (✗) or warnings (⚠):")
print("  1. Check model files exist")
print("  2. Verify dataset structure")
print("  3. Run training if LSTM model missing")
print("  4. Check GPU drivers if GPU not detected")
print("\nTo test a specific video:")
print("  python diagnostic_test.py <video_id>")
print()
