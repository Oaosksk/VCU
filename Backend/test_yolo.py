"""Test if YOLO detection works"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from app.ml.models.yolo_detector import YOLODetector
from app.ml.pipeline.frame_extractor import FrameExtractor

# Find first video in dataset
dataset_dir = Path("dataset")
video_path = None

for folder in ["accident", "no_accident"]:
    folder_path = dataset_dir / folder
    if folder_path.exists():
        videos = list(folder_path.glob("*.mp4")) + list(folder_path.glob("*.avi"))
        if videos:
            video_path = str(videos[0])
            break

if not video_path:
    print("Error: No videos found in dataset/accident/ or dataset/no_accident/")
    sys.exit(1)

print(f"Testing YOLO detection on: {video_path}")
extractor = FrameExtractor()
yolo = YOLODetector()

frames = extractor.extract_frames(video_path)
print(f"Extracted {len(frames)} frames")

if frames:
    detections = yolo.detect(frames[0])
    print(f"\nDetections in first frame: {len(detections)}")
    for d in detections:
        print(f"  - {d['class_name']}: {d['confidence']:.2f}")
    print("\n✓ YOLO works!")
