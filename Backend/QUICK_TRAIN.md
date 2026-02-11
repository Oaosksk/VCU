# 🚀 Quick Start: Train Your Model

## Step 1: Prepare Dataset (5 minutes)

Create this folder structure:

```
Backend/
└── dataset/
    ├── accident/
    │   ├── video1.mp4
    │   ├── video2.mp4
    │   └── ...
    └── no_accident/
        ├── video1.mp4
        ├── video2.mp4
        └── ...
```

**Minimum:** 10 videos in each folder (20 total)

### Where to Get Videos:

1. **YouTube** (easiest):
   - Search: "car accident cctv"
   - Search: "normal traffic cctv"
   - Download using: https://yt1s.com/

2. **Kaggle**:
   - https://www.kaggle.com/datasets/ckay16/accident-detection-from-cctv-footage

3. **Record Your Own**:
   - Use phone to record traffic
   - Or use toy cars

---

## Step 2: Extract Features (10 minutes)

```bash
cd Backend
python scripts/extract_features.py
```

This will:
- Load YOLOv8
- Process all videos
- Extract features
- Save to `features.pkl`

**Output:**
```
Processing accident videos...
  video1.mp4
  video2.mp4
Processing normal videos...
  video1.mp4
  video2.mp4

Dataset Summary:
Total videos: 20
Features shape: (20, 150, 3)
Accident videos: 10
Normal videos: 10

✓ Features saved to features.pkl
```

---

## Step 3: Train Model (30 minutes)

```bash
python scripts/train_lstm.py
```

**Output:**
```
Loading features from features.pkl...
Dataset: (20, 150, 3), Labels: (20,)
Train: (16, 150, 3), Test: (4, 150, 3)
Using device: cpu

Training for 50 epochs...
Epoch   1/50 | Loss: 0.6931 | Acc: 0.5000
Epoch   2/50 | Loss: 0.6845 | Acc: 0.5000
...
Epoch  25/50 | Loss: 0.3421 | Acc: 0.7500 ✓ Best model saved!
...
Epoch  50/50 | Loss: 0.1234 | Acc: 0.8750 ✓ Best model saved!

Training complete!
Best accuracy: 0.8750
Model saved to: storage/models/lstm_crash_detector.pth
```

---

## Step 4: Test (1 minute)

Your model is now ready! The backend will automatically use it.

Start the server:
```bash
uvicorn app.main:app --reload
```

Upload a video and see the results!

---

## 📊 Expected Results

### With 20 videos:
- **Accuracy:** 60-75%
- **Training time:** 30 minutes (CPU)
- **Good for:** College demo

### With 50 videos:
- **Accuracy:** 70-80%
- **Training time:** 1 hour
- **Good for:** Better demo

### With 100+ videos:
- **Accuracy:** 80-90%
- **Training time:** 2-3 hours
- **Good for:** Research paper

---

## 🎯 Tips

1. **Balance your dataset:** Same number of accident/normal videos
2. **Use GPU:** 10x faster (Google Colab free)
3. **Start small:** Train with 10 videos first to test
4. **Check videos:** Make sure they're clear and relevant

---

## ❓ Troubleshooting

**"Dataset directory not found"**
- Create `Backend/dataset/accident/` and `Backend/dataset/no_accident/`
- Add videos to both folders

**"No videos found"**
- Make sure videos are `.mp4` format
- Check folder names are correct

**"Out of memory"**
- Reduce batch size: `--batch-size 8`
- Use fewer frames: Edit `max_frames=150` to `max_frames=100`

**"Low accuracy"**
- Need more videos (at least 20)
- Check video quality
- Train for more epochs: `--epochs 100`

---

## 🚀 Advanced Options

### Custom parameters:
```bash
# More epochs
python scripts/train_lstm.py --epochs 100

# Smaller batch size (for low memory)
python scripts/train_lstm.py --batch-size 8

# Different learning rate
python scripts/train_lstm.py --lr 0.0001

# Custom output location
python scripts/train_lstm.py --output my_model.pth
```

### Use GPU (Google Colab):
1. Upload your dataset to Google Drive
2. Open Colab notebook
3. Mount Drive
4. Run training scripts
5. Download trained model

---

## 📝 For Your Report

**What to write:**

> "We trained an LSTM model on a dataset of X videos (Y accident, Z normal). 
> The model was trained for 50 epochs using Adam optimizer with a learning rate of 0.001.
> We achieved an accuracy of X% on the test set."

**Include:**
- Dataset size
- Training parameters
- Accuracy achieved
- Training time

---

**Ready to train? Let's go!** 🎓
