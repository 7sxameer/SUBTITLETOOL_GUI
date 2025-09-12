@echo off
title Video Subtitle Tool

REM Get the directory where this batch file is located
set "SCRIPT_DIR=%~dp0"

REM Change to the script directory
cd /d "%SCRIPT_DIR%"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Run the video subtitle tool
echo Starting Video Subtitle Tool...
python video_subtitle_tool.py

REM Keep window open if there was an error
if errorlevel 1 (
    echo.
    echo An error occurred. Press any key to exit.
    pause >nul
)