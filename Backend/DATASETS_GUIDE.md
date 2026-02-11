# 📊 DATASETS FOR ACCIDENT DETECTION

## 🎯 Overview

Based on your project specifications, you need datasets for:
1. **Accident learning** - Videos with vehicle crashes
2. **Normal traffic** - Videos without accidents (for false positive control)
3. **Edge cases** - Challenging scenarios

---

## 📦 RECOMMENDED DATASETS

### 1. ✅ UCF-Crime Dataset (Accident Subset)
**Purpose:** Accident learning, temporal patterns

**Details:**
- **Source:** University of Central Florida
- **Size:** ~1,900 videos (128 hours)
- **Accident videos:** ~100-150 videos
- **Resolution:** Various (mostly 320x240 to 640x480)
- **Format:** MP4
- **License:** Research/Academic use

**Download:**
- **Official:** http://www.crcv.ucf.edu/projects/real-world/
- **Kaggle:** https://www.kaggle.com/datasets/mission-ai/crimeucfdataset

**What to use:**
- Filter videos labeled as "Accident" or "RoadAccidents"
- Contains real CCTV footage of traffic accidents
- Good for learning crash patterns

**Pros:**
- ✅ Real-world CCTV footage
- ✅ Diverse accident scenarios
- ✅ Well-documented
- ✅ Widely used in research

**Cons:**
- ⚠️ Large download (~20GB)
- ⚠️ Need to filter accident videos
- ⚠️ Variable quality

---

### 2. ✅ Car Crash Dataset (Kaggle)
**Purpose:** Accident learning, dashcam perspective

**Details:**
- **Source:** Kaggle community
- **Size:** ~500-1000 videos
- **Type:** Dashcam footage
- **Resolution:** 720p-1080p
- **Format:** MP4, AVI
- **License:** Public domain / CC0

**Download:**
- **Kaggle:** https://www.kaggle.com/datasets/ckay16/accident-detection-from-cctv-footage
- **Alternative:** https://www.kaggle.com/datasets/ckay16/car-crash-dataset

**What to use:**
- Pre-labeled accident videos
- Dashcam perspective (driver view)
- Clear accident moments

**Pros:**
- ✅ Pre-labeled (accident/no_accident)
- ✅ Good quality
- ✅ Easy to download
- ✅ Smaller size (~5-10GB)

**Cons:**
- ⚠️ Mostly dashcam (not CCTV)
- ⚠️ Limited diversity

---

### 3. ✅ AI City Challenge Dataset
**Purpose:** Normal traffic, false positive control

**Details:**
- **Source:** NVIDIA AI City Challenge
- **Size:** ~1000+ videos
- **Type:** Traffic surveillance
- **Resolution:** 1080p
- **Format:** MP4
- **License:** Research use (registration required)

**Download:**
- **Official:** https://www.aicitychallenge.org/
- **Registration required:** Free for academic use

**What to use:**
- Normal traffic videos (no accidents)
- Various traffic conditions
- Different camera angles

**Pros:**
- ✅ High quality
- ✅ Diverse traffic scenarios
- ✅ Multiple camera angles
- ✅ Well-annotated

**Cons:**
- ⚠️ Registration required
- ⚠️ Large download (~50GB)
- ⚠️ Mostly normal traffic (need to filter)

---

### 4. ✅ YouTube Traffic Videos (Self-Collected)
**Purpose:** Edge cases, additional data

**Details:**
- **Source:** YouTube
- **Size:** As needed
- **Type:** Mixed (CCTV, dashcam)
- **Resolution:** Various
- **Format:** MP4
- **License:** Fair use for research

**How to Download:**
```bash
# Install yt-dlp
pip install yt-dlp

# Download accident videos
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" -o "accident_%(id)s.mp4"

# Download normal traffic
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" -o "normal_%(id)s.mp4"
```

**Search Terms:**
- **Accidents:** "car accident cctv", "traffic accident surveillance", "crash caught on camera"
- **Normal:** "traffic camera live", "highway traffic", "normal traffic flow"

**Pros:**
- ✅ Free and accessible
- ✅ Can target specific scenarios
- ✅ Recent footage
- ✅ Flexible

**Cons:**
- ⚠️ Manual collection
- ⚠️ Variable quality
- ⚠️ Copyright considerations

---

### 5. ⚠️ DETRAC Dataset (Optional)
**Purpose:** Vehicle detection, tracking

**Details:**
- **Source:** UA-DETRAC
- **Size:** 100 videos (10 hours)
- **Type:** Traffic surveillance
- **Resolution:** Various
- **Format:** MP4
- **License:** Research use

**Download:**
- **Official:** http://detrac-db.rit.albany.edu/

**Note:** Primarily for vehicle detection/tracking, not accidents

---

## 🎯 RECOMMENDED DATASET COMBINATION

### For Your Project (Minimum):

| Dataset | Videos | Purpose | Priority |
|---------|--------|---------|----------|
| **Car Crash Dataset (Kaggle)** | 50-100 | Accident learning | ⭐⭐⭐ HIGH |
| **YouTube (Self-collected)** | 50-100 | Normal traffic | ⭐⭐⭐ HIGH |
| **UCF-Crime (Accident subset)** | 20-50 | Additional accidents | ⭐⭐ MEDIUM |
| **AI City Challenge** | 50-100 | Normal traffic (quality) | ⭐ LOW |

**Total Minimum:** 100-200 videos (50 accident + 50 normal)

---

## 📥 QUICK START GUIDE

### Option 1: Kaggle Dataset (EASIEST) ⭐ RECOMMENDED

**Step 1: Download from Kaggle**
```bash
# Install Kaggle CLI
pip install kaggle

# Setup Kaggle API (get token from kaggle.com/account)
# Place kaggle.json in ~/.kaggle/

# Download dataset
kaggle datasets download -d ckay16/accident-detection-from-cctv-footage
unzip accident-detection-from-cctv-footage.zip -d dataset/
```

**Step 2: Organize**
```
Backend/dataset/
├── accident/
│   ├── video1.mp4
│   ├── video2.mp4
│   └── ...
└── no_accident/
    ├── video1.mp4
    ├── video2.mp4
    └── ...
```

---

### Option 2: YouTube Collection (FLEXIBLE)

**Step 1: Install downloader**
```bash
pip install yt-dlp
```

**Step 2: Create download script**
```python
# download_videos.py
import subprocess

accident_urls = [
    "https://www.youtube.com/watch?v=XXXXX",
    "https://www.youtube.com/watch?v=YYYYY",
    # Add more URLs
]

normal_urls = [
    "https://www.youtube.com/watch?v=AAAAA",
    "https://www.youtube.com/watch?v=BBBBB",
    # Add more URLs
]

# Download accidents
for i, url in enumerate(accident_urls):
    subprocess.run([
        "yt-dlp", url, 
        "-o", f"dataset/accident/video_{i}.mp4",
        "--format", "mp4"
    ])

# Download normal
for i, url in enumerate(normal_urls):
    subprocess.run([
        "yt-dlp", url,
        "-o", f"dataset/no_accident/video_{i}.mp4",
        "--format", "mp4"
    ])
```

**Step 3: Run**
```bash
python download_videos.py
```

---

### Option 3: UCF-Crime Dataset (COMPREHENSIVE)

**Step 1: Download**
```bash
# Download from official site or Kaggle
wget http://www.crcv.ucf.edu/projects/real-world/UCF_Crimes.zip
unzip UCF_Crimes.zip
```

**Step 2: Filter accident videos**
```python
# filter_accidents.py
import os
import shutil

source_dir = "UCF_Crimes"
target_dir = "dataset/accident"

# Look for accident-related videos
accident_keywords = ["Accident", "RoadAccidents", "Crash"]

for root, dirs, files in os.walk(source_dir):
    for file in files:
        if any(keyword in root for keyword in accident_keywords):
            if file.endswith(('.mp4', '.avi')):
                src = os.path.join(root, file)
                dst = os.path.join(target_dir, file)
                shutil.copy(src, dst)
                print(f"Copied: {file}")
```

---

## 📊 DATASET STATISTICS (RECOMMENDED)

### Minimum for College Project:
- **Accident videos:** 50
- **Normal videos:** 50
- **Total:** 100 videos
- **Training:** 80 videos (40 each)
- **Testing:** 20 videos (10 each)

### Ideal for Good Results:
- **Accident videos:** 100-150
- **Normal videos:** 100-150
- **Total:** 200-300 videos
- **Training:** 80% (160-240 videos)
- **Testing:** 20% (40-60 videos)

### For Research Paper:
- **Accident videos:** 200+
- **Normal videos:** 200+
- **Total:** 400+ videos

---

## 🎯 DATASET PREPARATION CHECKLIST

### Step 1: Download
- [ ] Choose dataset source (Kaggle recommended)
- [ ] Download videos
- [ ] Verify file formats (MP4, AVI, MOV)

### Step 2: Organize
- [ ] Create `Backend/dataset/` folder
- [ ] Create `accident/` subfolder
- [ ] Create `no_accident/` subfolder
- [ ] Move videos to correct folders

### Step 3: Validate
- [ ] Check video count (minimum 50 each)
- [ ] Verify videos play correctly
- [ ] Check file sizes (not corrupted)
- [ ] Balance dataset (equal accident/normal)

### Step 4: Extract Features
```bash
cd Backend
python scripts/extract_features.py
```

### Step 5: Train Model
```bash
python scripts/train_lstm.py
```

---

## 📝 FOR YOUR REPORT

### Dataset Section:

> **Datasets Used:**
> 
> We compiled a dataset of X videos from multiple sources:
> 
> 1. **Car Crash Dataset (Kaggle):** Y accident videos showing various crash scenarios including rear-end collisions, side impacts, and multi-vehicle accidents.
> 
> 2. **YouTube Traffic Videos:** Z normal traffic videos captured from surveillance cameras, representing typical traffic flow without incidents.
> 
> 3. **UCF-Crime Dataset (Accident Subset):** Additional W accident videos for training diversity.
> 
> **Dataset Statistics:**
> - Total videos: X
> - Accident videos: Y (Z%)
> - Normal videos: W (V%)
> - Training set: 80% (A videos)
> - Test set: 20% (B videos)
> - Average duration: C seconds
> - Resolution: 480p-1080p
> 
> The dataset was balanced to prevent class imbalance and includes diverse scenarios such as different weather conditions, lighting, camera angles, and traffic densities.

---

## 🔗 QUICK LINKS

### Direct Download Links:

1. **Kaggle Car Crash Dataset:**
   https://www.kaggle.com/datasets/ckay16/accident-detection-from-cctv-footage

2. **UCF-Crime Dataset:**
   http://www.crcv.ucf.edu/projects/real-world/

3. **AI City Challenge:**
   https://www.aicitychallenge.org/

4. **YouTube Downloader:**
   https://github.com/yt-dlp/yt-dlp

---

## ⚠️ IMPORTANT NOTES

### Legal Considerations:
- ✅ Use datasets with academic/research licenses
- ✅ Cite dataset sources in your report
- ✅ YouTube videos: Fair use for research
- ❌ Don't redistribute datasets
- ❌ Don't use for commercial purposes

### Quality Considerations:
- ✅ Prefer 480p or higher resolution
- ✅ Videos should be 5-60 seconds long
- ✅ Clear visibility of vehicles
- ❌ Avoid very dark/blurry videos
- ❌ Skip videos with heavy occlusion

---

## 🚀 RECOMMENDED APPROACH

**For Quick Start (1-2 days):**
1. Download Kaggle Car Crash Dataset (50 accident videos)
2. Collect 50 normal traffic videos from YouTube
3. Organize in dataset folder
4. Extract features and train

**For Better Results (1 week):**
1. Kaggle dataset (100 accident videos)
2. YouTube collection (100 normal videos)
3. UCF-Crime subset (50 additional accidents)
4. AI City Challenge (50 high-quality normal)
5. Total: 300 videos

**For Research Quality (2-3 weeks):**
1. All above sources
2. Self-recorded videos
3. Edge cases collection
4. Total: 500+ videos

---

## 📞 SUPPORT

**If you need help:**
1. Check dataset documentation
2. Verify file formats
3. Test with small subset first
4. Use provided scripts

**Common Issues:**
- **Download fails:** Use VPN or alternative source
- **Format issues:** Convert with ffmpeg
- **Size too large:** Start with subset
- **Imbalanced:** Collect more of minority class

---

**Recommendation:** Start with Kaggle dataset (easiest) + YouTube videos (flexible)

**Total Time:** 1-2 days to collect 100 videos

**Ready to download?** Follow Option 1 (Kaggle) above! 🚀
