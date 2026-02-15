# 📡 API Reference

Complete REST API documentation for the Vehicle Crash Detection System.

## 🌐 Base URL

```
http://localhost:8000
```

## 📋 Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint |
| GET | `/health` | Health check |
| POST | `/api/upload` | Upload video |
| POST | `/api/analyze` | Analyze video |
| GET | `/api/explanation/{result_id}` | Get AI explanation |

---

## 🏠 Root Endpoint

### `GET /`

Returns API information.

**Response:**
```json
{
  "message": "Accident Detection API",
  "version": "1.0.0"
}
```

---

## ❤️ Health Check

### `GET /health`

Check API health status.

**Response:**
```json
{
  "status": "healthy"
}
```

---

## 📤 Upload Video

### `POST /api/upload`

Upload a video file for analysis.

**Request:**
- **Content-Type:** `multipart/form-data`
- **Body:**
  - `video` (file): Video file

**Constraints:**
- Max size: 500 MB
- Formats: `.mp4`, `.avi`, `.mov`, `.mkv`
- Max duration: 300 seconds

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "video=@accident_video.mp4"
```

**Example (JavaScript):**
```javascript
const formData = new FormData();
formData.append('video', file);

const response = await fetch('http://localhost:8000/api/upload', {
  method: 'POST',
  body: formData
});

const data = await response.json();
```

**Success Response (200):**
```json
{
  "video_id": "87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "message": "Video uploaded successfully",
  "filename": "accident_video.mp4",
  "size": 15728640
}
```

**Error Responses:**

**400 Bad Request** - Invalid file
```json
{
  "detail": "Invalid file format. Allowed: .mp4, .avi, .mov, .mkv"
}
```

**413 Payload Too Large** - File too large
```json
{
  "detail": "File size exceeds maximum allowed size of 500 MB"
}
```

**500 Internal Server Error** - Upload failed
```json
{
  "detail": "Upload failed: [error message]"
}
```

---

## 🔍 Analyze Video

### `POST /api/analyze`

Analyze an uploaded video for accident detection.

**Request:**
- **Content-Type:** `application/json`
- **Body:**
```json
{
  "video_id": "87c0282b-95eb-4bf0-937c-ff68975fa0d8"
}
```

**Example (cURL):**
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"video_id": "87c0282b-95eb-4bf0-937c-ff68975fa0d8"}'
```

**Example (JavaScript):**
```javascript
const response = await fetch('http://localhost:8000/api/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    video_id: '87c0282b-95eb-4bf0-937c-ff68975fa0d8'
  })
});

const result = await response.json();
```

**Success Response (200):**
```json
{
  "id": "result-87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "status": "accident",
  "confidence": 0.847,
  "timestamp": "2024-02-10T14:30:15.123456",
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
  }
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| id | string | Result identifier |
| status | string | Detection result (`accident` or `no_accident`) |
| confidence | float | Confidence score (0.0-1.0) |
| timestamp | string | Analysis timestamp (ISO 8601) |
| details | object | Detailed analysis information |

**Details Object:**

| Field | Type | Description |
|-------|------|-------------|
| spatialFeatures | string | YOLOv8 detection summary |
| temporalFeatures | string | LSTM temporal analysis |
| frameCount | int | Number of frames analyzed |
| duration | string | Video duration |
| temporalStability | float | TCA stability score (0.0-1.0) |
| spikeFiltered | boolean | Whether spikes were filtered |
| eventFrames | array | Accident event frame ranges [[start, end]] |
| maxConfidence | float | Maximum frame confidence |
| meanConfidence | float | Average frame confidence |

**Error Responses:**

**404 Not Found** - Video not found
```json
{
  "detail": "Video not found"
}
```

**500 Internal Server Error** - Analysis failed
```json
{
  "detail": "Analysis failed: [error message]"
}
```

---

## 💬 Get AI Explanation

### `GET /api/explanation/{result_id}`

Get AI-generated explanation for an analysis result.

**Parameters:**
- `result_id` (path): Result ID from analyze endpoint

**Example (cURL):**
```bash
curl http://localhost:8000/api/explanation/result-87c0282b-95eb-4bf0-937c-ff68975fa0d8
```

**Example (JavaScript):**
```javascript
const response = await fetch(
  `http://localhost:8000/api/explanation/${resultId}`
);

const data = await response.json();
```

**Success Response (200):**
```json
{
  "explanation": "# Analysis Explanation\n\n## Overview\nBased on the spatio-temporal analysis, our model detected: **accident** with 84.70% confidence.\n\n## Spatial Analysis\nThe YOLOv8 object detection model analyzed individual frames to identify vehicles, their positions, and spatial relationships.\n\n**Detected Features:** Detected 245 objects across 150 frames\n\n## Temporal Analysis\nThe system processed frame sequences to understand movement patterns over time.\n\n**Observed Patterns:** Temporal stability: 0.82\n\n## Model Architecture\nOur hybrid approach combines:\n- **YOLOv8**: Real-time object detection for spatial features\n- **LSTM**: Temporal pattern recognition\n- **TCA**: Novel confidence aggregation algorithm\n\n## Analysis Details\n- **Frames Analyzed:** 150\n- **Video Duration:** 15.0 seconds\n- **Confidence Score:** 84.70%\n- **Temporal Stability:** 0.82\n\nThe confidence score represents the model's certainty in this classification, derived from spatial and temporal feature analysis."
}
```

**Error Responses:**

**404 Not Found** - Result not found
```json
{
  "detail": "Result not found. Please analyze the video first."
}
```

**500 Internal Server Error** - Explanation generation failed
```json
{
  "detail": "Failed to generate explanation: [error message]"
}
```

---

## 🔄 Complete Workflow

### 1. Upload Video
```javascript
// Upload
const uploadResponse = await fetch('/api/upload', {
  method: 'POST',
  body: formData
});
const { video_id } = await uploadResponse.json();
```

### 2. Analyze Video
```javascript
// Analyze
const analyzeResponse = await fetch('/api/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ video_id })
});
const result = await analyzeResponse.json();
```

### 3. Get Explanation
```javascript
// Get explanation
const explanationResponse = await fetch(`/api/explanation/${result.id}`);
const { explanation } = await explanationResponse.json();
```

---

## 🔒 CORS Configuration

**Allowed Origins:**
```
http://localhost:5173
http://localhost:3000
```

Configure in `Backend/.env`:
```env
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

---

## ⏱️ Rate Limits

Currently no rate limiting implemented.

**Recommended for production:**
- 10 uploads per minute per IP
- 20 analyze requests per minute per IP
- 30 explanation requests per minute per IP

---

## 📊 Response Times

| Endpoint | Average Time |
|----------|--------------|
| `/health` | < 10ms |
| `/api/upload` | 1-5s (depends on file size) |
| `/api/analyze` | 5-15s (depends on video length) |
| `/api/explanation` | 2-5s (with Groq API) |

---

## 🐛 Error Handling

All errors follow this format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

**HTTP Status Codes:**
- `200` - Success
- `400` - Bad Request (invalid input)
- `404` - Not Found (resource doesn't exist)
- `413` - Payload Too Large (file too big)
- `500` - Internal Server Error (server-side error)

---

## 📝 Request/Response Examples

### Full Upload & Analyze Flow

**1. Upload Request:**
```http
POST /api/upload HTTP/1.1
Host: localhost:8000
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

------WebKitFormBoundary
Content-Disposition: form-data; name="video"; filename="test.mp4"
Content-Type: video/mp4

[binary video data]
------WebKitFormBoundary--
```

**1. Upload Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "video_id": "87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "message": "Video uploaded successfully",
  "filename": "test.mp4",
  "size": 15728640
}
```

**2. Analyze Request:**
```http
POST /api/analyze HTTP/1.1
Host: localhost:8000
Content-Type: application/json

{
  "video_id": "87c0282b-95eb-4bf0-937c-ff68975fa0d8"
}
```

**2. Analyze Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": "result-87c0282b-95eb-4bf0-937c-ff68975fa0d8",
  "status": "accident",
  "confidence": 0.847,
  "timestamp": "2024-02-10T14:30:15.123456",
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
  }
}
```

---

## 🔗 Interactive Documentation

FastAPI provides interactive API documentation:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

---

## 📚 Related Files

- `app/api/v1/routes/video.py` - Route handlers
- `app/api/v1/schemas/video.py` - Request/response schemas
- `app/services/inference_service.py` - Analysis logic

---

**API Version:** 1.0.0  
**Base URL:** http://localhost:8000  
**Documentation:** http://localhost:8000/docs
