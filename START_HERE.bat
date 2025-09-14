@echo off
title Video Subtitle Tool - Multi-Video Processing

REM Get the directory where this batch file is located
set "TOOL_DIR=%~dp0"
cd /d "%TOOL_DIR%"

echo ========================================
echo    Video Subtitle Tool v2.0
echo    Multi-Video AI-Powered Processing
echo    Perfect for Dzine Lipsync Workflows
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not found in PATH!
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo [INFO] Python found - checking dependencies...

REM Check if required packages are installed
python -c "import tkinter" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] tkinter not found! Please install Python with tkinter support.
    pause
    exit /b 1
)

python -c "import subprocess, os, json, threading, time" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Basic Python modules missing!
    pause
    exit /b 1
)

REM Check for faster-whisper
python -c "from faster_whisper import WhisperModel" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] faster-whisper not installed. Installing now...
    echo This may take a few minutes...
    pip install faster-whisper
    if errorlevel 1 (
        echo [ERROR] Failed to install faster-whisper
        echo Please check your internet connection and try again
        pause
        exit /b 1
    )
    echo [SUCCESS] faster-whisper installed successfully!
)

REM Check for tkinterdnd2 (for drag & drop support)
python -c "import tkinterdnd2" >nul 2>&1
if errorlevel 1 (
    echo [WARNING] tkinterdnd2 not installed. Installing for drag & drop support...
    pip install tkinterdnd2
    if errorlevel 1 (
        echo [WARNING] Failed to install tkinterdnd2. Drag & drop will not be available.
        echo You can still use the 'Add Videos' button for multi-video processing.
        echo Continue in 3 seconds...
        timeout /t 3 >nul
    ) else (
        echo [SUCCESS] tkinterdnd2 installed successfully! Drag & drop enabled.
    )
)

REM Check for FFmpeg
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
    echo - Or download from: https://www.gyan.dev/ffmpeg/builds/
    echo.
    set /p continue="Continue anyway? (y/n): "
    if /i not "%continue%"=="y" exit /b 1
)

echo [INFO] Starting Video Subtitle Tool...
echo.

REM Run the application from Program Files folder
python "Program Files\video_subtitle_tool.py"

REM Check if there was an error
if errorlevel 1 (
    echo.
    echo [ERROR] The application encountered an error.
    echo Check the error messages above for details.
    echo.
    pause
) else (
    echo.
    echo [INFO] Application closed normally.
)

exit /b 0