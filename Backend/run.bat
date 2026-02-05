@echo off
echo Starting Accident Detection API...
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
