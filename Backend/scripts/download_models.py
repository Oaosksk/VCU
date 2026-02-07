"""Download pre-trained models"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

def download_models():
    model_dir = Path(settings.MODEL_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading YOLOv8s model...")
    try:
        from ultralytics import YOLO
        
        # Download YOLOv8s model
        model_path = model_dir / "yolov8s.pt"
        if not model_path.exists():
            print("Downloading YOLOv8s weights...")
            model = YOLO('yolov8s.pt')
            # Move to storage directory
            import shutil
            shutil.move('yolov8s.pt', str(model_path))
            print(f"✅ YOLOv8s model downloaded to {model_path}")
        else:
            print(f"✅ YOLOv8s model already exists at {model_path}")
        
        print(f"\nModels directory: {model_dir}")
        print("Note: LSTM model needs to be trained separately")
        
    except Exception as e:
        print(f"❌ Error downloading models: {e}")
        print("Models will be downloaded automatically on first inference")

if __name__ == "__main__":
    download_models()
