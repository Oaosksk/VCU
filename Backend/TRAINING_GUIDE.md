# 🎓 Training Guide: Accident Detection Model

## 📋 Overview

This guide explains how to train your accident detection model using video data.

---

## 🎯 Current Implementation Status

**Your Current System:**
- ✅ YOLOv8 for object detection (pre-trained, no training needed)
- ❌ LSTM model (NOT implemented - using heuristics)
- ⚠️ Pattern analysis (simple rule-based)

**What Needs Training:**
- LSTM/RNN model for temporal sequence analysis
- Or: Train a custom accident classifier

---

## 📊 Option 1: Train LSTM Model (Recommended for College Project)

### Step 1: Prepare Dataset

#### Dataset Structure:
```
dataset/
├── accident/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
└── no_accident/
    ├── video1.mp4
    ├── video2.mp4
    └── ...
```

#### Where to Get Data:
1. **Kaggle Datasets:**
   - [Car Crash Dataset](https://www.kaggle.com/datasets/ckay16/accident-detection-from-cctv-footage)
   - [Traffic Accident Dataset](https://www.kaggle.com/datasets/ckay16/accident-detection-from-cctv-footage)

2. **YouTube:**
   - Search "car accident CCTV"
   - Search "normal traffic CCTV"
   - Use `yt-dlp` to download

3. **Create Your Own:**
   - Record traffic videos
   - Simulate accidents (toy cars)

#### Minimum Dataset Size:
- **Accident videos:** 50-100 videos
- **Normal videos:** 50-100 videos
- **Total:** 100-200 videos minimum

---

### Step 2: Extract Features Using YOLOv8

Create `Backend/scripts/extract_features.py`:

```python
"""Extract spatial features from videos using YOLOv8"""
import cv2
import numpy as np
from pathlib import Path
from ultralytics import YOLO
import pickle

# Load YOLOv8
model = YOLO('yolov8s.pt')

def extract_features_from_video(video_path, target_fps=10, max_frames=150):
    """Extract YOLOv8 features from video"""
    cap = cv2.VideoCapture(str(video_path))
    original_fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(original_fps / target_fps)
    
    features = []
    frame_count = 0
    extracted = 0
    
    while extracted < max_frames:
        ret, frame = cap.read()
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            # Run YOLOv8 detection
            results = model(frame, verbose=False)
            
            # Extract features: [num_vehicles, avg_confidence, bbox_variance]
            detections = results[0].boxes
            
            vehicle_classes = [2, 3, 5, 7]  # car, motorcycle, bus, truck
            vehicles = [d for d in detections if int(d.cls[0]) in vehicle_classes]
            
            if len(vehicles) > 0:
                num_vehicles = len(vehicles)
                avg_conf = np.mean([float(d.conf[0]) for d in vehicles])
                bboxes = np.array([d.xyxy[0].cpu().numpy() for d in vehicles])
                bbox_variance = np.var(bboxes)
            else:
                num_vehicles = 0
                avg_conf = 0
                bbox_variance = 0
            
            features.append([num_vehicles, avg_conf, bbox_variance])
            extracted += 1
        
        frame_count += 1
    
    cap.release()
    
    # Pad if needed
    while len(features) < max_frames:
        features.append([0, 0, 0])
    
    return np.array(features[:max_frames])


def process_dataset(dataset_dir, output_file):
    """Process entire dataset"""
    dataset_dir = Path(dataset_dir)
    
    X = []  # Features
    y = []  # Labels
    
    # Process accident videos
    print("Processing accident videos...")
    accident_dir = dataset_dir / "accident"
    for video_path in accident_dir.glob("*.mp4"):
        print(f"  {video_path.name}")
        features = extract_features_from_video(video_path)
        X.append(features)
        y.append(1)  # 1 = accident
    
    # Process normal videos
    print("Processing normal videos...")
    normal_dir = dataset_dir / "no_accident"
    for video_path in normal_dir.glob("*.mp4"):
        print(f"  {video_path.name}")
        features = extract_features_from_video(video_path)
        X.append(features)
        y.append(0)  # 0 = no accident
    
    X = np.array(X)
    y = np.array(y)
    
    print(f"\nDataset shape: {X.shape}")
    print(f"Labels shape: {y.shape}")
    print(f"Accident videos: {np.sum(y == 1)}")
    print(f"Normal videos: {np.sum(y == 0)}")
    
    # Save
    with open(output_file, 'wb') as f:
        pickle.dump({'X': X, 'y': y}, f)
    
    print(f"\nSaved to {output_file}")


if __name__ == "__main__":
    process_dataset("dataset", "features.pkl")
```

**Run:**
```bash
cd Backend
python scripts/extract_features.py
```

---

### Step 3: Train LSTM Model

Create `Backend/scripts/train_lstm.py`:

```python
"""Train LSTM model for accident detection"""
import numpy as np
import pickle
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split

# Load features
with open('features.pkl', 'rb') as f:
    data = pickle.load(f)
    X = data['X']
    y = data['y']

# Split dataset
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

print(f"Train: {X_train.shape}, Test: {X_test.shape}")


# Dataset class
class VideoDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.FloatTensor(X)
        self.y = torch.FloatTensor(y)
    
    def __len__(self):
        return len(self.X)
    
    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]


# LSTM Model
class AccidentLSTM(nn.Module):
    def __init__(self, input_size=3, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.3)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.fc2 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        x = self.relu(self.fc1(last_output))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        return x


# Training
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"Using device: {device}")

model = AccidentLSTM().to(device)
criterion = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

train_dataset = VideoDataset(X_train, y_train)
test_dataset = VideoDataset(X_test, y_test)

train_loader = DataLoader(train_dataset, batch_size=16, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=16)

# Train
epochs = 50
best_acc = 0

for epoch in range(epochs):
    model.train()
    train_loss = 0
    
    for X_batch, y_batch in train_loader:
        X_batch = X_batch.to(device)
        y_batch = y_batch.to(device).unsqueeze(1)
        
        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()
        
        train_loss += loss.item()
    
    # Evaluate
    model.eval()
    correct = 0
    total = 0
    
    with torch.no_grad():
        for X_batch, y_batch in test_loader:
            X_batch = X_batch.to(device)
            y_batch = y_batch.to(device)
            
            outputs = model(X_batch).squeeze()
            predicted = (outputs > 0.5).float()
            
            total += y_batch.size(0)
            correct += (predicted == y_batch).sum().item()
    
    accuracy = correct / total
    
    print(f"Epoch {epoch+1}/{epochs} - Loss: {train_loss/len(train_loader):.4f} - Acc: {accuracy:.4f}")
    
    # Save best model
    if accuracy > best_acc:
        best_acc = accuracy
        torch.save(model.state_dict(), 'storage/models/lstm_crash_detector.pth')
        print(f"  ✓ Saved best model (acc: {accuracy:.4f})")

print(f"\nTraining complete! Best accuracy: {best_acc:.4f}")
```

**Run:**
```bash
python scripts/train_lstm.py
```

---

### Step 4: Integrate Trained Model

Update `Backend/app/ml/models/lstm_model.py`:

```python
"""LSTM model for temporal analysis"""
import torch
import torch.nn as nn
import numpy as np
from pathlib import Path
from app.core.config import settings

class AccidentLSTM(nn.Module):
    def __init__(self, input_size=3, hidden_size=64, num_layers=2):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, num_layers, 
                           batch_first=True, dropout=0.3)
        self.fc1 = nn.Linear(hidden_size, 32)
        self.fc2 = nn.Linear(32, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.3)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        lstm_out, _ = self.lstm(x)
        last_output = lstm_out[:, -1, :]
        x = self.relu(self.fc1(last_output))
        x = self.dropout(x)
        x = self.sigmoid(self.fc2(x))
        return x


class LSTMDetector:
    def __init__(self):
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.load_model()
    
    def load_model(self):
        model_path = Path(settings.LSTM_MODEL_PATH)
        if model_path.exists():
            self.model = AccidentLSTM().to(self.device)
            self.model.load_state_dict(torch.load(model_path, map_location=self.device))
            self.model.eval()
            print(f"LSTM model loaded from {model_path}")
        else:
            print(f"LSTM model not found at {model_path}")
    
    def predict(self, features):
        """Predict accident probability from features"""
        if self.model is None:
            return 0.5  # Default
        
        with torch.no_grad():
            features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
            output = self.model(features_tensor)
            return float(output.squeeze())
```

Update `Backend/app/services/inference_service.py`:

```python
from app.ml.models.lstm_model import LSTMDetector

# In analyze_video_file function:
lstm_detector = LSTMDetector()

# Extract features for LSTM
lstm_features = []
for detections in detections_per_frame:
    vehicles = [d for d in detections if d['class_name'] in ['car', 'truck', 'bus', 'motorcycle']]
    
    if vehicles:
        num_vehicles = len(vehicles)
        avg_conf = np.mean([d['confidence'] for d in vehicles])
        bboxes = np.array([d['bbox'] for d in vehicles])
        bbox_variance = np.var(bboxes)
    else:
        num_vehicles = 0
        avg_conf = 0
        bbox_variance = 0
    
    lstm_features.append([num_vehicles, avg_conf, bbox_variance])

# Pad to 150 frames
while len(lstm_features) < 150:
    lstm_features.append([0, 0, 0])
lstm_features = np.array(lstm_features[:150])

# Predict
confidence = lstm_detector.predict(lstm_features)
status = "accident" if confidence > 0.5 else "no_accident"
```

---

## 📊 Option 2: Use Pre-trained Model (Quick Start)

If you don't have time to train, use a pre-trained action recognition model:

### Using I3D or SlowFast:

```python
# Install
pip install pytorchvideo

# Use pre-trained model
from pytorchvideo.models import create_slowfast

model = create_slowfast(
    model_num_class=2,  # accident / no_accident
    slowfast_channel_reduction_ratio=8,
)

# Fine-tune on your small dataset
```

---

## 📊 Option 3: Simple Approach (For Demo)

If you just need something working for your college project:

### Rule-Based System (Already Implemented):

Your current system uses heuristics:
- Sudden changes in object count
- High variance in detections
- Multiple vehicles present

**This is acceptable for a college project!**

Just document it as:
> "Due to limited training data and computational resources, we implemented a heuristic-based temporal analysis system that detects anomalies in traffic patterns."

---

## 🎯 Quick Start for College Project

### Minimal Training (1-2 hours):

1. **Download 20 videos:**
   - 10 accident videos from YouTube
   - 10 normal traffic videos

2. **Extract features:**
   ```bash
   python scripts/extract_features.py
   ```

3. **Train simple model:**
   ```bash
   python scripts/train_lstm.py
   ```

4. **Test:**
   ```bash
   python scripts/test_model.py
   ```

---

## 📈 Expected Results

### With Minimal Training (20 videos):
- **Accuracy:** 60-70%
- **Good enough for:** College demo

### With Proper Training (100+ videos):
- **Accuracy:** 75-85%
- **Good enough for:** Research paper

### With Large Dataset (1000+ videos):
- **Accuracy:** 85-95%
- **Good enough for:** Production

---

## 🎓 For Your College Report

### What to Write:

**Dataset:**
- "We collected X videos from [source]"
- "Dataset split: 80% training, 20% testing"

**Model Architecture:**
- "YOLOv8 for spatial feature extraction"
- "LSTM with 2 layers for temporal analysis"
- "Binary classification (accident/no_accident)"

**Training:**
- "Trained for 50 epochs using Adam optimizer"
- "Learning rate: 0.001"
- "Batch size: 16"

**Results:**
- "Achieved X% accuracy on test set"
- "Precision: X%, Recall: X%"

---

## 🚀 Next Steps

1. **Collect Data** (1-2 days)
2. **Extract Features** (1 hour)
3. **Train Model** (2-3 hours)
4. **Integrate** (1 hour)
5. **Test** (1 hour)

**Total Time:** 3-4 days

---

## 💡 Tips

1. **Start Small:** Train with 20 videos first
2. **Use GPU:** Training is 10x faster
3. **Data Augmentation:** Flip, rotate videos
4. **Balance Dataset:** Equal accident/normal videos
5. **Document Everything:** For your report

---

## 📚 Resources

- [YOLOv8 Docs](https://docs.ultralytics.com/)
- [PyTorch LSTM Tutorial](https://pytorch.org/tutorials/beginner/nlp/sequence_models_tutorial.html)
- [Kaggle Datasets](https://www.kaggle.com/datasets)

---

## ❓ FAQ

**Q: Do I need a GPU?**
A: No, but it's 10x faster. Use Google Colab (free GPU).

**Q: How many videos do I need?**
A: Minimum 20 (10 each class), ideal 100+.

**Q: Can I use the current system without training?**
A: Yes! The heuristic-based system works for demo.

**Q: Where to get accident videos?**
A: YouTube, Kaggle, or simulate with toy cars.

---

**Good luck with your training!** 🎓
