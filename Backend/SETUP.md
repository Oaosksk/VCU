# Backend Setup Guide

## Prerequisites
- Python 3.11.9
- uv (Python package manager)

## Installation Steps

### 1. Install uv
```bash
# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Setup Project
```bash
cd backend

# Create virtual environment
uv venv

# Activate virtual environment
# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies (super fast with uv!)
uv pip install -e .

# Install dev dependencies (optional)
uv pip install -e ".[dev]"
```

### 3. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your settings (optional)
```

### 4. Initialize
```bash
# Initialize database
python scripts/init_db.py

# Download ML models
python scripts/download_models.py
```

### 5. Run Server
```bash
# Development mode (with auto-reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

API will be available at: http://localhost:8000

## Testing
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test
pytest tests/api/test_video_routes.py
```

## Common uv Commands
```bash
# Add new dependency
uv pip install package-name

# Remove dependency
uv pip uninstall package-name

# Update all dependencies
uv pip install --upgrade -e .

# List installed packages
uv pip list
```

## Troubleshooting

### Port already in use
```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# macOS/Linux
lsof -ti:8000 | xargs kill -9
```

### Virtual environment issues
```bash
# Remove and recreate
rm -rf .venv
uv venv
```
