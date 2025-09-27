@echo off
title Video Subtitle Tool - Multi-Video Processing - Auto Setup

REM Get the directory where this batch file is located
set "TOOL_DIR=%~dp0"
cd /d "%TOOL_DIR%"

echo ==========================================
echo    Video Subtitle Tool v2.0 - Auto Setup
echo    Multi-Video AI-Powered Processing
echo    Perfect for Dzine Lipsync Workflows
echo ==========================================
echo.
echo [INFO] Starting automatic dependency check and installation...
echo This may take a few minutes on first run.
echo.

REM Check if Python is available
echo [STEP 1/6] Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not found in PATH!
    echo.
    echo AUTOMATED SOLUTION: Please install Python manually for now.
    echo Download from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
) else (
    echo [SUCCESS] Python found!
)

REM Upgrade pip to latest version
echo [STEP 2/6] Upgrading pip to latest version...
python -m pip install --upgrade pip --quiet

echo [STEP 3/6] Checking core Python modules...
python -c "import tkinter, subprocess, os, json, threading, time" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Core Python modules missing! Your Python installation may be incomplete.
    echo Please reinstall Python with all standard libraries.
    pause
    exit /b 1
)
echo [SUCCESS] Core Python modules found!

echo [STEP 4/6] Installing all required Python packages...
echo This may take several minutes, please wait...

REM Install packages one by one for reliability
echo [INFO] Installing faster-whisper...
python -m pip install faster-whisper --quiet

echo [INFO] Installing tkinterdnd2...
python -m pip install tkinterdnd2 --quiet

echo [INFO] Installing additional packages...
python -m pip install tqdm --quiet
python -m pip install ctranslate2 --quiet
python -m pip install huggingface_hub --quiet
python -m pip install tokenizers --quiet
python -m pip install onnxruntime --quiet
python -m pip install av --quiet

REM Verify critical packages
echo [INFO] Verifying critical package installation...
python -c "from faster_whisper import WhisperModel" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] faster-whisper verification failed. Attempting fresh installation...
    python -m pip install --force-reinstall faster-whisper --quiet
)

python -c "import tkinterdnd2" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] tkinterdnd2 not available. Installing alternative...
    python -m pip install tkinterdnd2 --force-reinstall --quiet
)

echo [SUCCESS] Python packages installation completed!

echo [STEP 5/6] Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] FFmpeg not found!
    echo.
    echo FFmpeg is required for video processing.
    echo Please install FFmpeg from: https://ffmpeg.org
    echo.
    echo You can also install it using:
    echo - Chocolatey: choco install ffmpeg
    echo - Scoop: scoop install ffmpeg
    echo - WinGet: winget install Gyan.FFmpeg
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
) else (
    echo [SUCCESS] FFmpeg found!
)

echo [STEP 6/6] Final system verification...
echo [INFO] Performing final compatibility checks...

echo [INFO] Testing faster-whisper...
python -c "from faster_whisper import WhisperModel; print('✓ faster-whisper: OK')" 2>nul
if errorlevel 1 (
    echo [ERROR] ✗ faster-whisper: FAILED
    pause
    exit /b 1
)

echo [INFO] Testing tkinter...
python -c "import tkinter as tk; print('✓ tkinter: OK')" 2>nul
if errorlevel 1 (
    echo [ERROR] ✗ tkinter: FAILED
    pause
    exit /b 1
)

echo [INFO] Testing tkinterdnd2...
python -c "import tkinterdnd2; print('✓ tkinterdnd2: OK (Drag & Drop enabled)')" 2>nul
if errorlevel 1 (
    echo [WARNING] ! tkinterdnd2: Not available (Manual file selection only)
) else (
    echo [SUCCESS] ✓ tkinterdnd2: OK (Drag & Drop enabled)
)

echo [SUCCESS] ✓ All critical dependencies verified!

echo.
echo ==========================================
echo     🎉 SETUP COMPLETE! 🎉
echo ==========================================
echo All dependencies have been installed and verified!
echo Starting Video Subtitle Tool...
echo.

REM Run the application from Program Files folder
python "Program Files\video_subtitle_tool.py"

REM Check if there was an error
if errorlevel 1 (
    echo.
    echo ==========================================
    echo [ERROR] The application encountered an error.
    echo ==========================================
    echo.
    echo Troubleshooting steps:
    echo 1. Check if all files are present in 'Program Files' folder
    echo 2. Ensure you have internet connection for first-time model download
    echo 3. Try running as Administrator if permission issues occur
    echo 4. Contact support if the problem persists
    echo.
    echo Error details above ^^^
    echo.
    pause
) else (
    echo.
    echo ==========================================
    echo [INFO] Application closed normally.
    echo Thank you for using Video Subtitle Tool!
    echo ==========================================
)

echo.
echo Press any key to exit...
pause >nul
exit /b 0