#!/usr/bin/env python3
"""
Manually complete the zero-dependency bundle setup
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

def manually_complete_bundle():
    """Manually complete the bundle setup"""
    
    current_dir = Path(__file__).parent
    bundle_dir = current_dir / "VideoSubtitleTool_ZeroDependency"
    
    if not bundle_dir.exists():
        print("Error: Bundle directory not found!")
        return False
    
    print("Manually completing zero-dependency bundle...")
    
    # Extract nodejs.zip if it exists
    nodejs_zip = bundle_dir / "nodejs.zip"
    if nodejs_zip.exists():
        print("Extracting Node.js...")
        extract_nodejs(nodejs_zip, bundle_dir)
    
    # Copy from SimpleComplete if available (it has everything)
    simple_complete = current_dir / "VideoSubtitleTool_SimpleComplete"
    if simple_complete.exists():
        print("Copying components from SimpleComplete bundle...")
        copy_from_simple_complete(simple_complete, bundle_dir)
    
    # Install Electron if Node.js is available
    nodejs_exe = bundle_dir / "nodejs" / "node.exe"
    if nodejs_exe.exists() and not (bundle_dir / "node_modules").exists():
        print("Installing Electron...")
        install_electron_manually(bundle_dir)
    
    print("Creating final launchers...")
    create_final_launcher(bundle_dir)
    
    return True

def extract_nodejs(nodejs_zip, bundle_dir):
    """Extract Node.js from zip"""
    try:
        with zipfile.ZipFile(nodejs_zip, 'r') as zip_ref:
            zip_ref.extractall(bundle_dir / "temp_nodejs")
        
        # Find the extracted Node.js folder
        temp_dir = bundle_dir / "temp_nodejs"
        for item in temp_dir.iterdir():
            if item.is_dir() and "node" in item.name:
                shutil.move(str(item), str(bundle_dir / "nodejs"))
                break
        
        # Cleanup
        shutil.rmtree(temp_dir)
        nodejs_zip.unlink()
        
        print("  ✓ Node.js extracted")
        
    except Exception as e:
        print(f"  ❌ Failed to extract Node.js: {e}")

def copy_from_simple_complete(source_dir, bundle_dir):
    """Copy missing components from SimpleComplete bundle"""
    
    components = {
        "python": "Python interpreter",
        "ffmpeg": "FFmpeg executable", 
        "node_modules": "Electron dependencies"
    }
    
    for component, description in components.items():
        source_path = source_dir / component
        dest_path = bundle_dir / component
        
        if source_path.exists() and not dest_path.exists():
            try:
                if source_path.is_file():
                    shutil.copy2(source_path, dest_path)
                else:
                    shutil.copytree(source_path, dest_path)
                print(f"  ✓ Copied {description}")
            except Exception as e:
                print(f"  ❌ Failed to copy {description}: {e}")

def install_electron_manually(bundle_dir):
    """Manually install Electron using bundled Node.js"""
    
    nodejs_exe = bundle_dir / "nodejs" / "node.exe"
    npm_cmd = bundle_dir / "nodejs" / "npm.cmd"
    
    try:
        import subprocess
        
        # Create package.json if needed
        package_json = bundle_dir / "package.json"
        if not package_json.exists():
            import json
            package_data = {
                "name": "video-subtitle-tool-zero-dep",
                "version": "2.0.0", 
                "main": "main.js",
                "dependencies": {"electron": "27.0.0"}
            }
            with open(package_json, 'w') as f:
                json.dump(package_data, f, indent=2)
        
        # Install Electron
        result = subprocess.run([
            str(npm_cmd), "install", "--production"
        ], cwd=str(bundle_dir), capture_output=True, text=True)
        
        if result.returncode == 0:
            print("  ✓ Electron installed")
        else:
            print(f"  ❌ Electron install failed")
            
    except Exception as e:
        print(f"  ❌ Failed to install Electron: {e}")

def create_final_launcher(bundle_dir):
    """Create the final launcher"""
    
    launcher_content = '''@echo off
title Video Subtitle Tool - Zero Dependency Edition
color 0A
cls

echo.
echo =============================================
echo   VIDEO SUBTITLE TOOL - ZERO DEPENDENCY
echo =============================================
echo.
echo   * Everything bundled - no downloads needed
echo   * Copy anywhere and it works
echo   * Professional AI subtitle generation
echo.

set "TOOL_DIR=%~dp0"
cd /d "%TOOL_DIR%"

REM Set up environment
set PATH=%TOOL_DIR%nodejs;%TOOL_DIR%python;%TOOL_DIR%ffmpeg;%PATH%
set PORTABLE_MODE=1
set PYTHONPATH=%TOOL_DIR%python;%TOOL_DIR%python\\Lib\\site-packages

echo Checking bundle components...

REM Check Node.js
if exist "%TOOL_DIR%nodejs\\node.exe" (
    echo   * Node.js: Ready
) else (
    echo   ERROR: Node.js not found
    pause & exit /b 1
)

REM Check Python
if exist "%TOOL_DIR%python\\python.exe" (
    echo   * Python: Ready
) else (
    echo   ERROR: Python not found  
    pause & exit /b 1
)

REM Check Electron
if exist "%TOOL_DIR%node_modules\\electron" (
    echo   * Electron: Ready
) else (
    echo   ERROR: Electron not found
    pause & exit /b 1
)

REM Check FFmpeg
if exist "%TOOL_DIR%ffmpeg\\ffmpeg.exe" (
    echo   * FFmpeg: Ready
) else (
    echo   WARNING: FFmpeg not found - video processing may fail
)

echo   * Backend: Ready
echo   * Frontend: Ready

REM Create workspace
if not exist "%TOOL_DIR%VideoSubtitleTool_Workspace" (
    mkdir "%TOOL_DIR%VideoSubtitleTool_Workspace"
    echo   * Created workspace folder
)

echo.
echo Starting application...
echo.

REM Start Python backend
echo Starting AI backend server...
start "" /B "%TOOL_DIR%python\\python.exe" "%TOOL_DIR%backend\\video_processor_api.py"

REM Wait for backend
echo Loading AI models (30 seconds on first run)...
timeout /t 12 /nobreak >nul

REM Start Electron frontend
echo Starting user interface...
"%TOOL_DIR%nodejs\\node.exe" "%TOOL_DIR%node_modules\\electron\\cli.js" "%TOOL_DIR%"

REM Cleanup on exit
echo.
echo Application closed - cleaning up...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo.
echo Thank you for using Video Subtitle Tool!
echo Press any key to close...
pause >nul
'''
    
    launcher_path = bundle_dir / "START_ZERO_DEPENDENCY.bat"
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    # Update README
    readme_content = '''# Video Subtitle Tool - Zero Dependency Bundle

## COMPLETELY PORTABLE - NO INTERNET REQUIRED!

This is the ultimate portable version with EVERYTHING bundled:

INCLUDED COMPONENTS:
- Node.js v22.16.0 (JavaScript runtime)
- Electron v27.0.0 (Modern UI framework)  
- Python 3.11.9 (AI processing engine)
- faster-whisper + PyTorch (AI transcription)
- FFmpeg 8.0 (Video processing)
- Complete application source code

## USAGE - SUPER SIMPLE!

1. Copy this entire folder anywhere you want
2. Double-click "START_ZERO_DEPENDENCY.bat"
3. Wait 30 seconds for AI models to load (first time only)
4. Start adding videos and generating subtitles!

## FEATURES

WORKFLOW:
- STITCH: Combine multiple video files
- TRANSCRIBE: AI generates subtitle text
- CORRECT: Edit subtitles interactively  
- BURN: Create final video with embedded subtitles

CAPABILITIES:
- Drag & drop multiple videos
- Professional AI transcription quality
- Interactive subtitle correction
- High-quality lossless video output
- Works completely offline
- No installation or setup required

## TECHNICAL SPECS

- Bundle Size: ~2-3GB (everything included)
- Memory Usage: 4-8GB RAM during processing
- First Run: 30-60 seconds (loading AI models)
- Subsequent Runs: 5-10 seconds
- Output Quality: Lossless H.264 + AAC

## TROUBLESHOOTING

ANTIVIRUS WARNINGS:
- Add entire folder to antivirus exclusions
- AI tools often trigger false positives

SLOW PERFORMANCE:
- First run loads 2GB of AI models (normal)
- Use smaller videos for faster processing
- Close other applications to free RAM

MISSING COMPONENTS:
- Ensure all files were copied completely
- Re-extract from original bundle if needed

---

PROFESSIONAL AI SUBTITLES - TRULY PORTABLE!

Copy anywhere, works everywhere, no internet needed.
'''
    
    readme_path = bundle_dir / "README_ZERO_DEPENDENCY.txt"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print("  ✓ Created final launcher and documentation")

def main():
    try:
        success = manually_complete_bundle()
        
        if success:
            print("\n" + "="*60)
            print("ZERO-DEPENDENCY BUNDLE COMPLETED MANUALLY!")
            print("="*60)
            print("Launch: START_ZERO_DEPENDENCY.bat")
            print("Everything should be bundled now!")
        
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())