"""
Extract YOLO features from videos — supports processing one batch at a time.

Usage:
  # Step 1 — accident videos only
  python scripts/extract_features.py --mode accident

  # (GPU break — then run Step 2)
  # Step 2 — non-accident videos only
  python scripts/extract_features.py --mode normal

  # Step 3 — merge both into features.pkl (ready for training)
  python scripts/extract_features.py --mode merge
"""
import cv2
import numpy as np
from pathlib import Path
import pickle
import sys
import time
import torch

sys.path.insert(0, str(Path(__file__).parent.parent))

# ── Paths ─────────────────────────────────────────────────────────
ACCIDENT_DIR  = Path("dataset/Accident Videos")
NORMAL_DIR    = Path("dataset/Non - Accident videos")
ACCIDENT_PKL  = Path("features_accident.pkl")
NORMAL_PKL    = Path("features_normal.pkl")
FINAL_PKL     = Path("features.pkl")

# ── Z-score constants — MUST match inference_service.py ──────────
VEHICLE_MEAN, VEHICLE_STD = 2.5,     3.0
CONF_MEAN,    CONF_STD    = 0.4,     0.25
VAR_MEAN,     VAR_STD     = 50000.0, 150000.0


def _load_yolo(model_path='yolo11m.pt'):
    """Load YOLO with PyTorch 2.6+ compatibility patch."""
    print(f"Loading YOLO model: {model_path}")
    _orig = torch.load
    torch.load = lambda *a, **kw: _orig(*a, **{**kw, 'weights_only': False})
    try:
        from ultralytics import YOLO
        model = YOLO(model_path)
    finally:
        torch.load = _orig
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    model.to(device)
    print(f"  → Model loaded on {device.upper()}")
    return model


def extract_features_from_video(video_path, model, target_fps=10, max_frames=150):
    """Extract per-frame YOLO features from a single video."""
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"    ⚠ Could not open {video_path.name}")
        return None

    original_fps = cap.get(cv2.CAP_PROP_FPS) or 25
    frame_interval = max(1, int(original_fps / target_fps))

    features   = []
    frame_count = 0
    extracted   = 0
    vehicle_classes = {2, 3, 5, 7}  # car, motorcycle, bus, truck (COCO ids)

    while extracted < max_frames:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            results  = model(frame, verbose=False)
            boxes    = results[0].boxes
            vehicles = [b for b in boxes if int(b.cls[0]) in vehicle_classes]

            if vehicles:
                num_v    = len(vehicles)
                avg_conf = float(np.mean([float(b.conf[0]) for b in vehicles]))
                bboxes   = np.array([b.xyxy[0].cpu().numpy() for b in vehicles])
                bbox_var = float(np.var(bboxes))
            else:
                num_v, avg_conf, bbox_var = 0, 0.0, 0.0

            norm_v   = (num_v    - VEHICLE_MEAN) / VEHICLE_STD
            norm_c   = (avg_conf - CONF_MEAN)    / CONF_STD
            norm_b   = (bbox_var - VAR_MEAN)     / VAR_STD

            features.append([norm_v, norm_c, norm_b])
            extracted += 1

        frame_count += 1

    cap.release()

    # Pad to fixed length
    while len(features) < max_frames:
        features.append([0.0, 0.0, 0.0])

    return np.array(features[:max_frames])


def process_class(video_dir: Path, label: int, out_pkl: Path, model):
    """Extract features from all videos in a folder and save to pkl."""
    video_exts = {'.mp4', '.avi', '.mov', '.mkv', '.MP4', '.MOV', '.AVI'}
    videos = [v for v in video_dir.iterdir() if v.suffix in video_exts]

    if not videos:
        print(f"  ⚠ No videos found in {video_dir}")
        return

    label_name = "ACCIDENT" if label == 1 else "NORMAL"
    print(f"\n{'='*60}")
    print(f"  Processing {len(videos)} {label_name} videos")
    print(f"  Source : {video_dir}")
    print(f"  Output : {out_pkl}")
    print(f"{'='*60}\n")

    X, y = [], []
    failed = []

    for i, vpath in enumerate(sorted(videos), 1):
        t0 = time.time()
        print(f"  [{i:03d}/{len(videos)}] {vpath.name} ... ", end='', flush=True)
        feat = extract_features_from_video(vpath, model)
        if feat is None:
            failed.append(vpath.name)
            print("FAILED")
            continue
        X.append(feat)
        y.append(label)
        print(f"done ({time.time()-t0:.1f}s)")

    X = np.array(X)
    y = np.array(y)

    with open(out_pkl, 'wb') as f:
        pickle.dump({'X': X, 'y': y, 'label': label_name}, f)

    print(f"\n  ✅ Saved {len(X)} sequences → {out_pkl}")
    if failed:
        print(f"  ⚠  Failed ({len(failed)}): {', '.join(failed)}")

    # Free GPU memory
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        print("  GPU memory cleared.")


def merge():
    """Merge accident + normal pkl files into final features.pkl."""
    print("\n" + "="*60)
    print("  Merging partial feature files → features.pkl")
    print("="*60)

    parts = []
    for pkl_path in [ACCIDENT_PKL, NORMAL_PKL]:
        if not pkl_path.exists():
            print(f"  ⚠ Missing: {pkl_path} — run --mode accident/normal first")
            return
        with open(pkl_path, 'rb') as f:
            data = pickle.load(f)
        print(f"  Loaded {len(data['X'])} {data['label']} sequences from {pkl_path}")
        parts.append(data)

    X = np.concatenate([p['X'] for p in parts], axis=0)
    y = np.concatenate([p['y'] for p in parts], axis=0)

    # Shuffle
    idx = np.random.permutation(len(X))
    X, y = X[idx], y[idx]

    with open(FINAL_PKL, 'wb') as f:
        pickle.dump({'X': X, 'y': y}, f)

    print(f"\n  ✅ Merged dataset:")
    print(f"     Total   : {len(X)} sequences")
    print(f"     Accident: {int(np.sum(y==1))}")
    print(f"     Normal  : {int(np.sum(y==0))}")
    print(f"     Shape   : {X.shape}")
    print(f"\n  Saved → {FINAL_PKL}")
    print(f"\n  Next step: python scripts/train_lstm.py --features features.pkl --output storage/models/lstm_crash_detector.pth --epochs 100")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Extract YOLO features from videos")
    parser.add_argument('--mode', choices=['accident', 'normal', 'merge'], required=True,
                        help='accident = process accident videos | normal = process normal videos | merge = combine both')
    parser.add_argument('--model', default='yolo11m.pt', help='YOLO model file')
    args = parser.parse_args()

    if args.mode == 'merge':
        merge()
    else:
        model = _load_yolo(args.model)
        if args.mode == 'accident':
            process_class(ACCIDENT_DIR, label=1, out_pkl=ACCIDENT_PKL, model=model)
        else:
            process_class(NORMAL_DIR, label=0, out_pkl=NORMAL_PKL, model=model)
