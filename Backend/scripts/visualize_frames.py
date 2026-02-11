"""Visualize frames with YOLO detections"""
import cv2
from pathlib import Path
from ultralytics import YOLO

def visualize_video(video_path, output_dir, max_frames=10):
    """Extract and save frames with detections"""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Loading YOLOv8 model...")
    model = YOLO('yolov8s.pt')
    
    print(f"Processing {video_path}...")
    cap = cv2.VideoCapture(str(video_path))
    
    frame_count = 0
    saved = 0
    
    while saved < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % 30 == 0:  # Every 30th frame
            results = model(frame)
            annotated_frame = results[0].plot()
            
            output_path = output_dir / f"frame_{saved:03d}.jpg"
            cv2.imwrite(str(output_path), annotated_frame)
            print(f"  Saved: {output_path.name}")
            saved += 1
        
        frame_count += 1
    
    cap.release()
    print(f"\n✓ Saved {saved} frames to {output_dir}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--video', required=True, help='Video file path')
    parser.add_argument('--output', default='frames_output', help='Output directory')
    parser.add_argument('--max-frames', type=int, default=10, help='Max frames to save')
    args = parser.parse_args()
    
    visualize_video(args.video, args.output, args.max_frames)
