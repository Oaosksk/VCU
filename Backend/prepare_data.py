"""Prepare training data from video datasets"""
import os
import numpy as np
from pathlib import Path
import cv2
from app.ml.models.yolo_detector import YOLODetector
from app.ml.pipeline.frame_extractor import FrameExtractor

def prepare_data(accident_dir, no_accident_dir, output_dir='data'):
    """Extract features from videos for LSTM training"""
    
    os.makedirs(output_dir, exist_ok=True)
    
    yolo = YOLODetector()
    extractor = FrameExtractor()
    
    all_features = []
    all_labels = []
    
    # Process accident videos
    print("Processing accident videos...")
    accident_videos = list(Path(accident_dir).glob('*.mp4')) + list(Path(accident_dir).glob('*.avi'))
    for video_path in accident_videos:
        print(f"  {video_path.name}")
        features = extract_features(str(video_path), yolo, extractor)
        if features is not None:
            all_features.append(features)
            all_labels.append(1)
    
    # Process no-accident videos
    print("Processing no-accident videos...")
    no_accident_videos = list(Path(no_accident_dir).glob('*.mp4')) + list(Path(no_accident_dir).glob('*.avi'))
    for video_path in no_accident_videos:
        print(f"  {video_path.name}")
        features = extract_features(str(video_path), yolo, extractor)
        if features is not None:
            all_features.append(features)
            all_labels.append(0)
    
    # Save data
    features_array = np.array(all_features)
    labels_array = np.array(all_labels)
    
    np.save(f'{output_dir}/features.npy', features_array)
    np.save(f'{output_dir}/labels.npy', labels_array)
    
    print(f"\nData saved:")
    print(f"  Features: {features_array.shape}")
    print(f"  Labels: {labels_array.shape}")
    print(f"  Accidents: {np.sum(labels_array)}")
    print(f"  No accidents: {len(labels_array) - np.sum(labels_array)}")

def extract_features(video_path, yolo, extractor):
    """Extract features from single video"""
    try:
        frames = extractor.extract_frames(video_path)
        if not frames:
            return None
        
        features = []
        for frame in frames:
            detections = yolo.detect(frame)
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
            
            norm_num_vehicles = min(num_vehicles / 10.0, 2.0)
            norm_bbox_variance = min(bbox_variance / 100000.0, 5.0)
            
            features.append([norm_num_vehicles, avg_conf, norm_bbox_variance])
        
        # Pad to 150 frames
        while len(features) < 150:
            features.append([0, 0, 0])
        
        return np.array(features[:150])
    
    except Exception as e:
        print(f"    Error: {e}")
        return None

if __name__ == "__main__":
    # Update these paths to your dataset folders
    ACCIDENT_DIR = "./datasets/accident"
    NO_ACCIDENT_DIR = "./datasets/no_accident"
    
    prepare_data(ACCIDENT_DIR, NO_ACCIDENT_DIR)
