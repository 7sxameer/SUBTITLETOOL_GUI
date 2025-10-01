@echo off
title Quick Setup - Video Subtitle Tool
color 0B

echo.
echo ================================
echo   QUICK SETUP
echo ================================
echo.

echo This will install Python AI libraries.
echo This takes 5-10 minutes and downloads ~2GB.
echo.

set /p choice="Continue? (y/n): "
if /i not "%choice%"=="y" exit /b

echo.
echo Installing AI libraries...
python -m pip install --upgrade pip --user
python -m pip install -r requirements.txt --user

if errorlevel 1 (
    echo.
    echo Installation failed!
    echo Try running as Administrator.
    pause
    exit /b 1
)

echo.
echo Installation completed!
echo You can now run START_TOOL.bat
echo.
pause
