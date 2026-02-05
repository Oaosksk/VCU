@echo off
echo Installing backend dependencies...
uv pip install -e .
echo.
echo Installation complete!
echo.
echo To run the server:
echo uvicorn app.main:app --reload
pause
