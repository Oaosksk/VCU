"""
Auto-generate normal driving clips from accident videos.
Takes the first N seconds of each accident video (pre-accident = normal driving).
"""
import cv2
import sys
from pathlib import Path

def extract_pre_accident_clip(src_path: Path, dst_path: Path, seconds: float = 4.0):
    """Extract first N seconds from an accident video as a normal driving clip."""
    cap = cv2.VideoCapture(str(src_path))
    if not cap.isOpened():
        print(f"  SKIP (cannot open): {src_path.name}")
        return False

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    w   = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h   = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    target_frames = int(fps * seconds)

    if total_frames < target_frames + 10:
        seconds = max(1.5, total_frames / fps - 1.0)
        target_frames = int(fps * seconds)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(dst_path), fourcc, fps, (w, h))

    count = 0
    while count < target_frames:
        ret, frame = cap.read()
        if not ret:
            break
        out.write(frame)
        count += 1

    cap.release()
    out.release()
    return count > 0


def main():
    base = Path(__file__).parent.parent
    accident_dir = base / "dataset" / "accident"
    normal_dir   = base / "dataset" / "no_accident"
    normal_dir.mkdir(parents=True, exist_ok=True)

    videos = list(accident_dir.glob("*.mp4")) + list(accident_dir.glob("*.avi")) + list(accident_dir.glob("*.mov"))

    if not videos:
        print(f"ERROR: No videos found in {accident_dir}")
        sys.exit(1)

    print(f"Found {len(videos)} accident videos")
    print(f"Generating pre-accident normal clips → {normal_dir}")
    print("-" * 60)

    success = 0
    for i, src in enumerate(videos, 1):
        dst = normal_dir / f"normal_{src.stem}.mp4"
        if dst.exists():
            print(f"  [{i:3d}/{len(videos)}] SKIP (exists): {dst.name}")
            success += 1
            continue
        ok = extract_pre_accident_clip(src, dst, seconds=4.0)
        if ok:
            size_kb = dst.stat().st_size // 1024
            print(f"  [{i:3d}/{len(videos)}] OK  {dst.name}  ({size_kb} KB)")
            success += 1
        else:
            print(f"  [{i:3d}/{len(videos)}] FAILED: {src.name}")

    existing_normal = [f for f in normal_dir.glob("*.mp4") if not f.name.startswith("normal_")]
    print()
    print("=" * 60)
    print(f"Generated : {success} normal clips from accident videos")
    print(f"Pre-existing normal videos: {len(existing_normal)}")
    print(f"Total normal videos: {len(list(normal_dir.glob('*.mp4')))}")
    print(f"Total accident videos: {len(videos)}")
    print()
    print("Next: run extract_features.py")


if __name__ == "__main__":
    main()
