# 🎬 Video Subtitle Tool - Portable Package

## 📋 What's Included

This is a complete, ready-to-use video subtitle generation tool powered by OpenAI's Whisper AI.

## 🚀 Quick Start

1. **Double-click** `START_HERE.bat`
2. The tool will automatically check and install requirements
3. GUI will open - follow the on-screen instructions

## 📁 Files in this Package

- `START_HERE.bat` - **DOUBLE-CLICK THIS** to start the tool
- `video_subtitle_tool.py` - Main application (GUI version)
- `video_to_subtitles.py` - Command-line version
- `README_TOOL.md` - This file
- `tool_config.json` - Configuration file (created automatically)

## ✨ Features

- **🤖 AI-Powered**: Uses OpenAI's Whisper model for accurate transcription
- **🎯 Professional Quality**: High-quality video encoding with burned subtitles
- **📁 Organized**: Creates dedicated workspace for your projects
- **🎮 Easy to Use**: Modern GUI interface
- **🔄 Auto-Setup**: Automatically installs missing dependencies

## 📋 System Requirements

### Required:
- **Windows 10/11**
- **Python 3.8+** (with tkinter support)
- **Internet connection** (first time only, to download AI models)
- **FFmpeg** (for video processing)

### Optional but Recommended:
- At least 4GB RAM
- 2GB free disk space (for AI models)

## 🛠️ Installation Guide

### If Python is Missing:
1. Download from: https://python.org
2. **IMPORTANT**: Check "Add Python to PATH" during installation
3. Restart your computer
4. Double-click `START_HERE.bat` again

### If FFmpeg is Missing:
Choose one option:

**Option 1: Chocolatey (Easiest)**
1. Open PowerShell as Administrator
2. Install Chocolatey: https://chocolatey.org/install
3. Run: `choco install ffmpeg`

**Option 2: Scoop**
1. Install Scoop: https://scoop.sh
2. Run: `scoop install ffmpeg`

**Option 3: Manual Download**
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin` to your PATH environment variable

## 🎯 How to Use

1. **Start**: Double-click `START_HERE.bat`
2. **Setup Workspace**: Choose where to save your subtitle files
3. **Select Video**: Browse and select your video file
4. **Choose AI Model**: 
   - **Small** (Recommended) - Best balance of speed and accuracy
   - Other options available for different needs
5. **Generate**: Click "🚀 Generate Subtitles"
6. **Wait**: Processing time depends on video length and model choice
7. **Done**: Get both SRT subtitle file and video with burned subtitles

## 📝 Output Files

For each video you process, you get:
- **`.srt` file**: Standard subtitle file for video players
- **`_with_subtitles.mp4`**: New video with permanently embedded subtitles

## 🎛️ AI Model Guide

| Model | Size | Speed | Accuracy | Best For |
|-------|------|--------|----------|----------|
| Tiny | 39MB | ⚡⚡⚡⚡ | ⭐⭐ | Quick tests |
| Base | 74MB | ⚡⚡⚡ | ⭐⭐⭐ | Balanced use |
| **Small** | 244MB | ⚡⚡ | ⭐⭐⭐⭐ | **RECOMMENDED** |
| Medium | 769MB | ⚡ | ⭐⭐⭐⭐⭐ | High accuracy |
| Large-v3 | 3GB | 🐌 | ⭐⭐⭐⭐⭐ | Maximum quality |

## 🔧 Troubleshooting

### "Python not found"
- Install Python from python.org
- Make sure "Add to PATH" was checked during installation
- Restart computer and try again

### "FFmpeg not found" 
- Install FFmpeg using one of the methods above
- Video processing won't work without FFmpeg

### Video processing fails
- Try moving your video to a simple folder path (like C:\Videos\)
- Avoid file names with commas, apostrophes, or special characters
- Make sure the video file isn't corrupted

### Slow processing
- Use "Small" model for best balance
- "Tiny" model for fastest results
- Processing time depends on video length

## 📁 Sharing This Tool

To share with others:
1. Copy this entire folder
2. Send to them via USB, cloud drive, etc.
3. They just need to double-click `START_HERE.bat`
4. Tool will auto-install dependencies

## 💡 Tips

- **First run**: May take a few minutes to download AI models
- **Workspace**: Set up once, use for all your videos  
- **File organization**: Tool keeps everything organized in your chosen workspace
- **Video formats**: Supports MP4, AVI, MOV, MKV, WMV, FLV, WebM, M4V
- **Languages**: AI automatically detects video language

## 🎯 Perfect For

- Social media content creators
- Educational video makers
- Accessibility compliance
- Language learning content
- Meeting recordings
- Podcast video versions

---

**Enjoy creating professional subtitles with AI!** 🎬✨

For support or questions, check the troubleshooting section above.