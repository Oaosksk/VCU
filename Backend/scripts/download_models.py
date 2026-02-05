"""Download pre-trained models"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.config import settings

def download_models():
    model_dir = Path(settings.MODEL_DIR)
    model_dir.mkdir(parents=True, exist_ok=True)
    
    print("Downloading YOLOv8s model...")
    # YOLOv8 will auto-download on first use
    
    print(f"Models will be stored in: {model_dir}")
    print("Models will be downloaded automatically on first inference")

if __name__ == "__main__":
    download_models()
