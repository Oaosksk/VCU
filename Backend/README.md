# Accident Detection Backend

Vehicle crash detection system using YOLOv8 + LSTM with ML model database storage.

## Quick Start

```bash
# Install dependencies
uv sync

# Extract features
uv run scripts/extract_features.py

# Train model
uv run scripts/train_lstm.py --epochs 50

# Test inference
uv run scripts/inference_from_db.py
```

## Documentation

See `PORTABILITY_GUIDE.md` for deployment instructions.
