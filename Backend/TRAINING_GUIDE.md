# LSTM Model Training Guide

## Problem: Model Trained Only on Accident Videos

Your current model was trained on **52 accident videos and 0 normal videos**, causing it to classify EVERYTHING as an accident.

## Solution: Balanced Dataset Required

### Step 1: Collect Normal Driving Videos

You need **at least 50 normal driving videos** (no accidents) to balance the dataset.

**Sources for normal driving videos:**
- YouTube dashcam channels (search "dashcam normal driving")
- Your own dashcam footage
- Public datasets: BDD100K, Waymo Open Dataset
- Download and place in `dataset/no_accident/` folder

### Step 2: Dataset Structure

```
Backend/dataset/
├── accident/          # 52 videos (already have)
│   ├── RoadAccidents001_x264.mp4
│   ├── RoadAccidents002_x264.mp4
│   └── ...
└── no_accident/       # Need 50+ videos (EMPTY NOW!)
    ├── normal_drive_001.mp4
    ├── normal_drive_002.mp4
    └── ...
```

### Step 3: Extract Features

```bash
cd Backend
python scripts/extract_features.py --dataset dataset --output features.pkl
```

This will:
- Process all videos in `accident/` folder (label = 1)
- Process all videos in `no_accident/` folder (label = 0)
- Extract YOLO features (vehicles, confidence, bbox variance)
- Save to `features.pkl`

### Step 4: Train LSTM Model

```bash
python scripts/train_lstm.py --features features.pkl --output storage/models/lstm_crash_detector.pth --epochs 50
```

Expected output:
```
Dataset: (100, 150, 3), Labels: (100,)
Train: (80, 150, 3), Test: (20, 150, 3)
Accident videos: 50
Normal videos: 50

Training for 50 epochs...
Epoch  1/50 | Loss: 0.6234 | Acc: 0.6500
Epoch  2/50 | Loss: 0.5123 | Acc: 0.7500 ✓ Best model saved!
...
Epoch 50/50 | Loss: 0.1234 | Acc: 0.9500 ✓ Best model saved!

Best accuracy: 95.00%
```

## Current Temporary Fix

I've added validation logic to prevent false positives:
- **No vehicles detected** → Force "no_accident" classification
- **< 5 vehicles detected** → Low confidence, likely "no_accident"
- **> 10 vehicles detected** → Use LSTM prediction

This is a **band-aid solution**. You MUST retrain with balanced data for a real system.

## Why This Matters

**Current behavior:**
- Video with 0 vehicles → 97.6% accident (WRONG!)
- Empty video → Accident detected (WRONG!)

**After retraining with balanced data:**
- Video with 0 vehicles → 0% accident (CORRECT)
- Normal driving → No accident (CORRECT)
- Actual accident → High confidence accident (CORRECT)

## Quick Test After Retraining

1. Upload a normal driving video → Should show "No Accident"
2. Upload an accident video → Should show "Accident Detected"
3. Upload a video with no vehicles → Should show "No Accident"
