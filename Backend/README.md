# Accident Detection Backend

Vehicle crash detection system using YOLOv8 + LSTM with FastAPI.

## Quick Start

### 1. Install uv
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Setup
```bash
cd backend

# Create virtual environment
uv venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

### 3. Configure
```bash
cp .env.example .env
# Edit .env as needed
```

### 4. Initialize
```bash
python scripts/init_db.py
python scripts/download_models.py
```

### 5. Run
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be available at http://localhost:8000

## Project Structure

```
backend/
├── app/
│   ├── api/v1/          # API routes & schemas
│   ├── core/            # Configuration
│   ├── db/              # Database models
│   ├── services/        # Business logic
│   ├── ml/              # ML pipeline
│   └── utils/           # Utilities
├── storage/             # File storage
├── tests/               # Test suite
└── scripts/             # Utility scripts
```

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Format code
ruff check app/
```
