@echo off
echo ================================================
echo Installing PyTorch with GPU (CUDA) support
echo ================================================
echo.

echo Step 1: Uninstalling CPU-only PyTorch...
pip uninstall -y torch torchvision torchaudio

echo.
echo Step 2: Installing GPU-enabled PyTorch (CUDA 11.8)...
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

echo.
echo ================================================
echo Installation complete!
echo Run check_device.py to verify GPU is detected
echo ================================================
pause
