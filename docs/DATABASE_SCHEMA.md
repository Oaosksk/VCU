# 🗄️ Database Schema Documentation

Complete database structure for the Vehicle Crash Detection System.

## 📊 Database Overview

- **Database Name:** `acvi`
- **Type:** MySQL 8.0+ (via XAMPP)
- **ORM:** SQLAlchemy 2.0.25
- **Driver:** PyMySQL 1.1.0

## 📋 Tables

### 1. videos

Stores uploaded video metadata.

```sql
CREATE TABLE videos (
    id VARCHAR(36) PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    size INT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending'
);
```

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(36) | UUID primary key |
| filename | VARCHAR(255) | Original filename |
| filepath | VARCHAR(500) | Server storage path |
| size | INT | File size in bytes |
| uploaded_at | DATETIME | Upload timestamp |
| status | VARCHAR(50) | Processing status (pending/processing/completed/failed) |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `uploaded_at` for sorting

**Example Data:**
```json
{
  "id": "87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "filename": "dashcam_accident.mp4",
  "filepath": "./storage/uploads/87c0282b-95eb-4bf0-937c-ff68975fa0d8.mp4",
  "size": 15728640,
  "uploaded_at": "2024-02-10 14:30:00",
  "status": "completed"
}
```

---

### 2. analysis_results

Stores accident detection analysis results.

```sql
CREATE TABLE analysis_results (
    id VARCHAR(50) PRIMARY KEY,
    video_id VARCHAR(36) NOT NULL,
    status VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    details JSON,
    inference_time FLOAT,
    temporal_stability FLOAT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| id | VARCHAR(50) | Result ID (result-{video_id}) |
| video_id | VARCHAR(36) | Foreign key to videos.id |
| status | VARCHAR(50) | Detection result (accident/no_accident) |
| confidence | FLOAT | Confidence score (0.0-1.0) |
| details | JSON | Analysis details (frames, features, etc.) |
| inference_time | FLOAT | Processing time in seconds |
| temporal_stability | FLOAT | TCA stability score (0.0-1.0) |
| created_at | DATETIME | Analysis timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- INDEX on `video_id` for lookups
- INDEX on `created_at` for sorting

**Example Data:**
```json
{
  "id": "result-87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "video_id": "87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "status": "accident",
  "confidence": 0.847,
  "details": {
    "spatialFeatures": "Detected 245 objects across 150 frames",
    "temporalFeatures": "Temporal stability: 0.82",
    "frameCount": 150,
    "duration": "15.0 seconds",
    "temporalStability": 0.82,
    "spikeFiltered": true,
    "eventFrames": [[45, 78]],
    "maxConfidence": 0.92,
    "meanConfidence": 0.65
  },
  "inference_time": 8.234,
  "temporal_stability": 0.82,
  "created_at": "2024-02-10 14:30:15"
}
```

---

### 3. events

Stores detected accident event timeframes.

```sql
CREATE TABLE events (
    id INT PRIMARY KEY AUTO_INCREMENT,
    video_id VARCHAR(36) NOT NULL,
    result_id VARCHAR(50) NOT NULL,
    start_frame INT NOT NULL,
    end_frame INT NOT NULL,
    start_time FLOAT NOT NULL,
    end_time FLOAT NOT NULL,
    confidence FLOAT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (video_id) REFERENCES videos(id),
    FOREIGN KEY (result_id) REFERENCES analysis_results(id)
);
```

**Columns:**
| Column | Type | Description |
|--------|------|-------------|
| id | INT | Auto-increment primary key |
| video_id | VARCHAR(36) | Foreign key to videos.id |
| result_id | VARCHAR(50) | Foreign key to analysis_results.id |
| start_frame | INT | Event start frame number |
| end_frame | INT | Event end frame number |
| start_time | FLOAT | Event start time in seconds |
| end_time | FLOAT | Event end time in seconds |
| confidence | FLOAT | Event confidence score |
| created_at | DATETIME | Detection timestamp |

**Indexes:**
- PRIMARY KEY on `id`
- FOREIGN KEY on `video_id` → `videos(id)`
- FOREIGN KEY on `result_id` → `analysis_results(id)`
- INDEX on `video_id` for lookups

**Example Data:**
```json
{
  "id": 1,
  "video_id": "87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "result_id": "result-87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "start_frame": 45,
  "end_frame": 78,
  "start_time": 4.5,
  "end_time": 7.8,
  "confidence": 0.92,
  "created_at": "2024-02-10 14:30:15"
}
```

---

## 🔗 Relationships

```
videos (1) ──────────── (0..1) analysis_results
  │                              │
  │                              │
  └──────────────────────────────┴──── (0..*) events
```

- One video can have zero or one analysis result
- One video can have zero or many events
- One analysis result can have zero or many events

---

## 🛠️ Setup Instructions

### 1. Create Database (XAMPP)

```sql
-- Open phpMyAdmin: http://localhost/phpmyadmin
-- Create database
CREATE DATABASE acvi CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Configure Connection

Edit `Backend/.env`:
```env
DATABASE_URL=mysql+pymysql://root:@localhost:3306/acvi
```

### 3. Initialize Tables

```bash
cd Backend
python scripts/init_db.py
```

This creates all tables automatically using SQLAlchemy.

---

## 📝 SQLAlchemy Models

### Video Model
```python
class Video(Base):
    __tablename__ = "videos"
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")
```

### AnalysisResult Model
```python
class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(String(50), primary_key=True)
    video_id = Column(String(36), nullable=False)
    status = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    details = Column(JSON)
    inference_time = Column(Float, nullable=True)
    temporal_stability = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Event Model
```python
class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False)
    result_id = Column(String(50), ForeignKey('analysis_results.id'), nullable=False)
    start_frame = Column(Integer, nullable=False)
    end_frame = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## 🔍 Common Queries

### Get All Videos
```sql
SELECT * FROM videos ORDER BY uploaded_at DESC;
```

### Get Analysis Result for Video
```sql
SELECT ar.* 
FROM analysis_results ar
WHERE ar.video_id = '87c0282b-95eb-4bf0-937c-ff68975fa0d8';
```

### Get Events for Video
```sql
SELECT e.* 
FROM events e
WHERE e.video_id = '87c0282b-95eb-4bf0-937c-ff68975fa0d8'
ORDER BY e.start_frame;
```

### Get Accident Videos
```sql
SELECT v.*, ar.confidence, ar.temporal_stability
FROM videos v
JOIN analysis_results ar ON v.id = ar.video_id
WHERE ar.status = 'accident'
ORDER BY ar.confidence DESC;
```

### Get Statistics
```sql
SELECT 
    COUNT(*) as total_videos,
    SUM(CASE WHEN ar.status = 'accident' THEN 1 ELSE 0 END) as accidents,
    AVG(ar.confidence) as avg_confidence,
    AVG(ar.inference_time) as avg_inference_time
FROM videos v
LEFT JOIN analysis_results ar ON v.id = ar.video_id;
```

---

## 🔧 Maintenance

### Backup Database
```bash
mysqldump -u root -p acvi > backup_acvi.sql
```

### Restore Database
```bash
mysql -u root -p acvi < backup_acvi.sql
```

### Clear Old Data
```sql
-- Delete videos older than 30 days
DELETE FROM videos WHERE uploaded_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Cascade deletes will remove related analysis_results and events
```

### Optimize Tables
```sql
OPTIMIZE TABLE videos;
OPTIMIZE TABLE analysis_results;
OPTIMIZE TABLE events;
```

---

## 📊 Database Size Estimates

| Table | Rows | Size per Row | Total Size |
|-------|------|--------------|------------|
| videos | 1000 | ~500 bytes | ~500 KB |
| analysis_results | 1000 | ~2 KB | ~2 MB |
| events | 2000 | ~200 bytes | ~400 KB |

**Total:** ~3 MB for 1000 analyzed videos

---

## 🐛 Troubleshooting

### Connection Error
```
sqlalchemy.exc.OperationalError: (2003, "Can't connect to MySQL server")
```
**Solution:** Start MySQL in XAMPP Control Panel

### Table Already Exists
```
sqlalchemy.exc.ProgrammingError: (1050, "Table 'videos' already exists")
```
**Solution:** Tables already created, skip init_db.py

### Foreign Key Constraint
```
sqlalchemy.exc.IntegrityError: FOREIGN KEY constraint failed
```
**Solution:** Ensure parent record exists before inserting child

---

## 📚 Related Files

- `app/db/models.py` - SQLAlchemy model definitions
- `app/db/database.py` - Database connection and session
- `scripts/init_db.py` - Database initialization script

---

**Database Status:** ✅ Configured  
**Tables:** 3  
**Relationships:** 2 Foreign Keys
