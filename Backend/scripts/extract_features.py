"""Extract spatial features from videos using YOLOv8"""
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import pickle
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

def extract_features_from_video(video_path, model, target_fps=10, max_frames=150):
    """Extract YOLOv8 features from video"""
    cap = cv2.VideoCapture(str(video_path))
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = max(1, int(original_fps / target_fps))
    
    features = []
    frame_count = 0
    extracted = 0
    
    while extracted < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            results = model(frame, verbose=False)
            detections = results[0].boxes
            
            vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
            vehicles = [d for d in detections if int(d.cls[0]) in vehicle_classes]
            
            if len(vehicles) > 0:
                num_vehicles = len(vehicles)
                avg_conf = np.mean([float(d.conf[0]) for d in vehicles])
                bboxes = np.array([d.xyxy[0].cpu().numpy() for d in vehicles])
                bbox_variance = float(np.var(bboxes))
            else:
                num_vehicles = 0
                avg_conf = 0.0
                bbox_variance = 0.0
            
            features.append([num_vehicles, avg_conf, bbox_variance])
            extracted += 1
        
        frame_count += 1
    
    cap.release()
    
    # Pad if needed
    while len(features) < max_frames:
        features.append([0, 0, 0])
    
    return np.array(features[:max_frames])


def process_dataset(dataset_dir, output_file, skip_processed=True):
    """Process entire dataset"""
    dataset_dir = Path(dataset_dir)
    cache_file = Path('processed_videos.pkl')
    
    if not dataset_dir.exists():
        print(f"Error: Dataset directory '{dataset_dir}' not found!")
        print("\nCreate dataset structure:")
        print("  dataset/")
        print("    ├── accident/")
        print("    │   └── video1.mp4")
        print("    └── no_accident/")
        print("        └── video1.mp4")
        return
    
    # Load existing features and processed videos list
    X = []
    y = []
    processed_videos = set()
    
    if skip_processed and cache_file.exists():
        print(f"Loading cached features from {cache_file}...")
        with open(cache_file, 'rb') as f:
            cache = pickle.load(f)
            X = cache.get('X', []).tolist() if len(cache.get('X', [])) > 0 else []
            y = cache.get('y', []).tolist() if len(cache.get('y', [])) > 0 else []
            processed_videos = cache.get('processed', set())
        print(f"Loaded {len(X)} previously processed videos")
    
    print("Loading YOLOv8 model...")
    model = YOLO('yolov8s.pt')
    
    # Process accident videos - NO LIMIT
    accident_dir = dataset_dir / "accident"
    if accident_dir.exists():
        print(f"\nProcessing accident videos from {accident_dir}...")
        video_files = list(accident_dir.glob("*.mp4"))
        new_count = 0
        for video_path in video_files:
            video_id = f"accident/{video_path.name}"
            if video_id in processed_videos:
                print(f"  {video_path.name} (skipped - already processed)")
                continue
            print(f"  {video_path.name} (processing...)")
            features = extract_features_from_video(video_path, model)
            X.append(features)
            y.append(1)
            processed_videos.add(video_id)
            new_count += 1
        print(f"Processed {new_count} new accident videos")
    else:
        print(f"Warning: {accident_dir} not found")
    
    # Process normal videos - NO LIMIT
    normal_dir = dataset_dir / "no_accident"
    if normal_dir.exists():
        print(f"\nProcessing normal videos from {normal_dir}...")
        video_files = list(normal_dir.glob("*.mp4"))
        new_count = 0
        for video_path in video_files:
            video_id = f"no_accident/{video_path.name}"
            if video_id in processed_videos:
                print(f"  {video_path.name} (skipped - already processed)")
                continue
            print(f"  {video_path.name} (processing...)")
            features = extract_features_from_video(video_path, model)
            X.append(features)
            y.append(0)
            processed_videos.add(video_id)
            new_count += 1
        print(f"Processed {new_count} new normal videos")
    else:
        print(f"Warning: {normal_dir} not found")
    
    if len(X) == 0:
        print("\nError: No videos found!")
        return
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"\n{'='*50}")
    print(f"Dataset Summary:")
    print(f"{'='*50}")
    print(f"Total videos: {len(X)}")
    print(f"Features shape: {X.shape}")
    print(f"Accident videos: {np.sum(y == 1)}")
    print(f"Normal videos: {np.sum(y == 0)}")
    
    # Save features
    with open(output_file, 'wb') as f:
        pickle.dump({'X': X, 'y': y}, f)
    
    # Save cache
    with open(cache_file, 'wb') as f:
        pickle.dump({'X': X, 'y': y, 'processed': processed_videos}, f)
    
    print(f"\n✓ Features saved to {output_file}")
    print(f"✓ Cache saved to {cache_file}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', default='dataset', help='Dataset directory')
    parser.add_argument('--output', default='features.pkl', help='Output file')
    parser.add_argument('--reprocess', action='store_true', help='Reprocess all videos (ignore cache)')
    args = parser.parse_args()
    
    process_dataset(args.dataset, args.output, skip_processed=not args.reprocess)
