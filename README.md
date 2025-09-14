# Video Subtitle Tool - Multi-Video Processing

A professional AI-powered video subtitle generator with **multi-video processing capabilities**. Perfect for processing Dzine Lipsync videos or any collection of video clips.

## 🚀 Quick Start

Just clone the repo, navigate to the repo folder, and double-click the **START_HERE.bat** file - the application will run automatically!

## ✨ Features

### 🎥 Multi-Video Processing
- **Drag & Drop Support**: Simply drag multiple video files into the application
- **Batch Selection**: Use the "Add Videos" button to select multiple files at once
- **Sequential Processing**: Each video is transcribed separately in order
- **Automatic Stitching**: Videos are combined into a single file automatically
- **Consolidated Subtitles**: Creates one SRT file with proper timing for the final video
- **Status Tracking**: Real-time status updates for each video in your queue

### 🤖 AI-Powered Transcription
- Multiple AI model options (tiny, base, small, medium, large-v3)
- High-quality subtitle generation
- Support for multiple languages
- Professional-grade accuracy

### 🎬 Video Processing
- **Optimized 4-Step Workflow**: Stitch → Transcribe → Correct → Burn
- **AI Transcription**: High-quality subtitle generation with ~80% accuracy
- **Smart Correction**: Optional transcript input to improve accuracy to near 100%
- **Automatic video concatenation** using FFmpeg
- **Professional subtitle burning** directly into video
- **Multiple quality settings** and output formats

## 📋 Perfect for Dzine Lipsync Workflows

This tool is specifically enhanced for **Dzine Lipsync** video processing:

1. **Multiple Dialogue Clips**: Add all your individual dialogue clips
2. **Sequential Processing**: Videos are processed in order to maintain dialogue flow
3. **Automatic Stitching**: All clips are combined into one final video
4. **Synchronized Subtitles**: Single SRT file with perfect timing for the combined video
5. **Final Output**: One video file with burned-in subtitles ready for use

## 🎯 How to Use

1. **Setup Workspace**: Configure where your processed videos will be saved
2. **Add Videos**: Drag & drop or browse to add multiple video files
3. **Select AI Model**: Choose the transcription quality level
4. **Process**: Click "Process Videos & Generate Subtitles"
5. **Wait**: The optimized 4-step workflow will:
   - **Step 1**: Stitch all videos together into one file
   - **Step 2**: Transcribe the combined video once (efficient!)
   - **Step 3**: Get original transcript input to correct AI errors (optional)
   - **Step 4**: Burn corrected subtitles into the final video

## 📁 File Structure

The tool creates:
- `combined_video_[timestamp].srt` - Final subtitle file
- `combined_video_[timestamp]_with_subtitles.mp4` - Final video with subtitles

## 🛠️ Requirements

- Windows (tested)
- FFmpeg (auto-detected from common installation paths)
- Python dependencies (handled automatically by START_HERE.bat)

## 🔧 Advanced Features

- **Fallback Processing**: If drag & drop isn't available, manual file selection works
- **Error Recovery**: Individual video failures won't stop the entire process
- **Progress Tracking**: See which videos are processing, completed, or failed
- **Quality Options**: Choose between speed and accuracy
- **Professional Output**: High-quality video encoding settings

---

*Enhanced for multi-video workflows and Dzine Lipsync processing*
