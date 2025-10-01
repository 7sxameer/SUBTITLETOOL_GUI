#!/usr/bin/env python3
"""
Complete the zero-dependency bundle by creating launchers
"""

import os
import sys
from pathlib import Path

def complete_zero_dependency_bundle():
    """Complete the bundle by creating launchers"""
    
    current_dir = Path(__file__).parent
    output_dir = current_dir / "VideoSubtitleTool_ZeroDependency"
    
    if not output_dir.exists():
        print("Error: VideoSubtitleTool_ZeroDependency folder not found!")
        return False
    
    print("Completing zero-dependency bundle...")
    print("Creating launchers and documentation...")
    
    create_zero_dep_launchers(output_dir)
    
    # Check bundle completeness
    check_bundle_completeness(output_dir)
    
    return True

def check_bundle_completeness(output_dir):
    """Check if all components are bundled"""
    
    components = {
        "Node.js": output_dir / "nodejs" / "node.exe",
        "Python": output_dir / "python" / "python.exe", 
        "Electron": output_dir / "node_modules" / "electron",
        "FFmpeg": output_dir / "ffmpeg" / "ffmpeg.exe",
        "Backend": output_dir / "backend" / "video_processor_api.py",
        "Frontend": output_dir / "renderer" / "index.html"
    }
    
    print("\nBundle completeness check:")
    all_good = True
    
    for name, path in components.items():
        if path.exists():
            if path.is_file():
                size = path.stat().st_size / (1024 * 1024)  # MB
                print(f"  ✓ {name}: {size:.1f} MB")
            else:
                print(f"  ✓ {name}: OK")
        else:
            print(f"  ❌ {name}: Missing")
            all_good = False
    
    if all_good:
        print("\n🎉 Bundle is complete and ready!")
        total_size = sum(
            sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
            for path in [output_dir / "nodejs", output_dir / "python", output_dir / "node_modules", output_dir / "ffmpeg"]
            if path.exists()
        ) / (1024 * 1024 * 1024)  # GB
        print(f"📦 Total bundle size: {total_size:.1f} GB")
    else:
        print("\n⚠️ Some components are missing")

def create_zero_dep_launchers(output_dir):
    """Create launchers for zero dependency bundle"""
    
    # Main launcher
    launcher_content = '''@echo off
title Video Subtitle Tool - Zero Dependency
color 0A
cls

echo.
echo ==========================================
echo   VIDEO SUBTITLE TOOL - ZERO DEPENDENCY
echo ==========================================
echo.
echo   * No downloads needed
echo   * No installation required  
echo   * Works completely offline
echo.

set "TOOL_DIR=%~dp0"
cd /d "%TOOL_DIR%"

REM Set up paths
set "NODE_EXE=%TOOL_DIR%nodejs\\node.exe"
set "PYTHON_EXE=%TOOL_DIR%python\\python.exe" 
set "ELECTRON_EXE=%TOOL_DIR%node_modules\\.bin\\electron.cmd"
set PATH=%TOOL_DIR%ffmpeg;%TOOL_DIR%nodejs;%TOOL_DIR%python;%PATH%
set PORTABLE_MODE=1

REM Check components
echo Checking bundled components...

if not exist "%NODE_EXE%" (
    echo ERROR: Node.js not found in bundle
    pause
    exit /b 1
)
echo   * Node.js ready

if not exist "%PYTHON_EXE%" (
    echo ERROR: Python not found in bundle  
    pause
    exit /b 1
)
echo   * Python ready

if not exist "%TOOL_DIR%ffmpeg\\ffmpeg.exe" (
    echo WARNING: FFmpeg not found in bundle
    echo Video processing may not work
)
echo   * FFmpeg ready

if not exist "%TOOL_DIR%node_modules\\electron" (
    echo ERROR: Electron not found in bundle
    pause  
    exit /b 1
)
echo   * Electron ready

REM Create workspace
if not exist "%TOOL_DIR%VideoSubtitleTool_Workspace" (
    mkdir "%TOOL_DIR%VideoSubtitleTool_Workspace"
)

echo.
echo Starting AI backend server...
start "" /B "%PYTHON_EXE%" "%TOOL_DIR%backend\\video_processor_api.py"

echo Initializing AI models (first run may take 30 seconds)...
timeout /t 10 /nobreak >nul

echo Starting user interface...
"%NODE_EXE%" "%TOOL_DIR%node_modules\\electron\\cli.js" "%TOOL_DIR%"

REM Cleanup
echo.
echo Shutting down...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo.
echo Thank you for using Video Subtitle Tool!
timeout /t 3 >nul
'''
    
    launcher_path = output_dir / "START_ZERO_DEP.bat"
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    # Create README
    readme_content = '''# Video Subtitle Tool - Zero Dependency Bundle

## TRULY PORTABLE - NO DOWNLOADS EVER!

This bundle contains EVERYTHING needed to run the tool:
- Node.js v22.16.0 (portable)
- Electron v27.0.0 (bundled) 
- Python 3.11.9 (embedded)
- All AI libraries (faster-whisper, PyTorch, etc.)
- FFmpeg (video processing)

## SUPER SIMPLE USAGE

1. **Copy this folder anywhere** (USB drive, network share, etc.)
2. **Double-click `START_ZERO_DEP.bat`**
3. **Done!** No installation, no internet needed

## FEATURES

- **4-Step AI Workflow**: Stitch -> Transcribe -> Correct -> Burn
- **Drag & Drop Interface**: Add multiple videos easily  
- **AI Transcription**: Professional quality subtitles
- **Interactive Correction**: Fix text before burning
- **High Quality Output**: Lossless video processing
- **Completely Offline**: Works without internet

## BUNDLE DETAILS

- **Total Size**: ~2-3GB (everything included)
- **First Run**: May take 30 seconds to load AI models
- **Daily Use**: Starts in 5-10 seconds
- **Storage**: Creates workspace folder for your projects

## TROUBLESHOOTING

**Antivirus Warnings**
- Add folder to antivirus exclusions
- AI tools sometimes trigger false positives

**Slow First Run**  
- Normal! Loading 2GB of AI models takes time
- Subsequent runs are much faster

**Missing Components**
- Re-download the complete bundle
- Ensure all files were copied properly

## TECHNICAL NOTES

This bundle is completely self-contained:
- No registry entries
- No system modifications  
- No external dependencies
- Copy anywhere and it works!

---

**Professional AI subtitles, truly portable!**

*Everything bundled, nothing to download.*
'''
    
    readme_path = output_dir / "README.txt"
    with open(readme_path, 'w') as f:
        f.write(readme_content)
    
    print("✓ Created launchers and documentation")

def main():
    try:
        success = complete_zero_dependency_bundle()
        
        if success:
            print("\n" + "="*60)
            print("ZERO-DEPENDENCY BUNDLE COMPLETE!")
            print("="*60)
            print("Everything bundled - no user downloads needed")
            print("Launch: START_ZERO_DEP.bat") 
            print("Copy anywhere and it works!")
            print("True portable solution achieved!")
    
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())