@echo off
title Video Subtitle Tool - Ultimate Portable
color 0A
cls

echo.
echo ========================================
echo   VIDEO SUBTITLE TOOL - ULTIMATE
echo ========================================
echo.

set "TOOL_DIR=%~dp0"
cd /d "%TOOL_DIR%"

echo [1/5] Checking system requirements...

REM Check for Node.js
echo   Checking Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Node.js not found!
    echo.
    echo   Please install Node.js first:
    echo   1. Go to: https://nodejs.org
    echo   2. Download LTS version
    echo   3. Install with default settings
    echo   4. Restart this tool
    echo.
    pause
    exit /b 1
)
echo   Node.js: OK

REM Check for Python
echo   Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo   ERROR: Python not found!
    echo.
    echo   Please install Python first:
    echo   1. Go to: https://www.python.org/downloads
    echo   2. Download Python 3.11 or newer
    echo   3. CHECK "Add Python to PATH" during install
    echo   4. Restart this tool
    echo.
    pause
    exit /b 1
)
echo   Python: OK

echo [2/5] Setting up Electron...
if not exist "%TOOL_DIR%node_modules" (
    echo   Installing Electron dependencies...
    npm install --production --silent
    if errorlevel 1 (
        echo   ERROR: Failed to install Electron
        pause
        exit /b 1
    )
)
echo   Electron: Ready

echo [3/5] Setting up AI libraries...
python -c "import faster_whisper" >nul 2>&1
if errorlevel 1 (
    echo   Installing AI libraries (this takes 5-10 minutes)...
    echo   Downloading ~2GB of AI models, please wait...
    python -m pip install faster-whisper ctranslate2 numpy fastapi uvicorn --user --quiet
    if errorlevel 1 (
        echo   ERROR: Failed to install AI libraries
        pause
        exit /b 1
    )
)
echo   AI Libraries: Ready

echo [4/5] Setting up video processing...
ffmpeg -version >nul 2>&1
if errorlevel 1 (
    if not exist "%TOOL_DIR%ffmpeg\ffmpeg.exe" (
        echo   FFmpeg not found, please install manually:
        echo   1. Download from: https://ffmpeg.org/download.html
        echo   2. Add to system PATH, or
        echo   3. Copy ffmpeg.exe to: %TOOL_DIR%ffmpeg\
        echo.
        pause
    )
) else (
    echo   FFmpeg: OK
)

echo [5/5] Starting application...
set PORTABLE_MODE=1
if exist "%TOOL_DIR%ffmpeg\ffmpeg.exe" set PATH=%TOOL_DIR%ffmpeg;%PATH%

echo   Starting AI backend...
start "" /B python "%TOOL_DIR%backend\video_processor_api.py"

echo   Waiting for backend initialization...
timeout /t 8 /nobreak >nul

echo   Launching interface...
"%TOOL_DIR%node_modules\.bin\electron" "%TOOL_DIR%"

REM Cleanup
taskkill /f /im python.exe >nul 2>&1

echo.
echo Application closed. Thank you!
timeout /t 2 >nul
