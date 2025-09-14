# Multi-Video Processing Enhancement

## Overview

The Video Subtitle Tool has been enhanced with comprehensive **multi-video processing capabilities**, specifically designed for **Dzine Lipsync workflows** and batch video processing.

## 🆕 New Features

### 1. Multi-Video Selection
- **Drag & Drop Support**: Drag multiple video files directly into the application
- **Batch File Browser**: Select multiple videos at once using the "Add Videos" button
- **Real-time Video List**: Visual list showing all selected videos with status indicators

### 2. Optimized 3-Step Processing Workflow
1. **Step 1 - Video Stitching**: All videos are combined into a single file first
2. **Step 2 - Transcription**: The combined video is transcribed once (more efficient)
3. **Step 3 - Subtitle Burning**: Subtitles are burned into the final video

**Benefits of the new workflow:**
- **More Efficient**: Only one transcription pass instead of multiple
- **Better Performance**: Reduced processing time and memory usage
- **Simpler Logic**: No complex timing adjustments between clips
- **Higher Accuracy**: Transcription works on the final combined audio

### 3. Enhanced User Interface
- **Larger Window**: Increased to 900x750 to accommodate the video list
- **Video Status Tracking**: Each video shows its current status (Pending, Processing, Done, Error)
- **Progress Indicators**: Real-time updates showing which video is being processed
- **Video Count Display**: Shows total number of videos in queue

### 4. Robust Error Handling
- **Individual Video Failures**: One failed video won't stop the entire process
- **Fallback Stitching**: Multiple stitching methods for maximum compatibility
- **Detailed Error Messages**: Specific suggestions for different types of failures
- **Graceful Degradation**: Works even if drag & drop libraries aren't available

## 🎬 Perfect for Dzine Lipsync

This enhancement specifically addresses the Dzine Lipsync workflow:

### The Problem
- Dzine Lipsync creates one video file per dialogue line
- Users need to manually stitch videos together
- Subtitles need to be synchronized across the combined video
- Processing each video individually was time-consuming

### The Solution
1. **Batch Import**: Add all dialogue videos at once
2. **Order Preservation**: Videos are processed in the order they're added
3. **Automatic Timing**: Subtitles are perfectly timed for the stitched result
4. **Single Output**: One final video with burned-in subtitles

## 🔧 Technical Implementation

### New Dependencies
- `tkinterdnd2>=0.3.0` - For drag & drop functionality (optional)

### New Methods
- `browse_videos()` - Multi-file selection dialog
- `on_drop()` - Handles drag & drop events
- `add_video_to_list()` - Adds videos to processing queue
- `remove_video_from_list()` - Removes videos from queue
- `clear_video_list()` - Clears entire video list
- `update_video_list_display()` - Updates UI video list
- `get_video_duration()` - Gets video duration using FFmpeg
- `process_multiple_videos()` - Main multi-video processing logic
- `stitch_videos()` - Concatenates videos using FFmpeg
- `stitch_videos_reencoding()` - Fallback stitching with re-encoding

### Enhanced Processing Flow

```
New Optimized Workflow (v2.1):
1. Stitch all videos together using FFmpeg
2. Load AI model once
3. Transcribe the combined video
4. Generate SRT file from transcription
5. Burn subtitles into the combined video
6. Clean up temporary files

Benefits:
- Single transcription pass (faster)
- No timing adjustments needed
- Better audio continuity
- Reduced memory usage
- Simpler error handling
```

### FFmpeg Video Concatenation

The tool uses two stitching methods:

1. **Stream Copy Method** (Fast):
   ```bash
   ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
   ```

2. **Re-encoding Method** (Compatible):
   ```bash
   ffmpeg -i video1 -i video2 ... -filter_complex "[0:v][0:a][1:v][1:a]...concat=n=N:v=1:a=1[outv][outa]" -map "[outv]" -map "[outa]" output.mp4
   ```

## 📋 User Guide

### Adding Videos
1. **Drag & Drop**: Simply drag video files into the application window
2. **Browse Button**: Click "Add Videos" and select multiple files
3. **Remove Individual**: Click the 🗑️ button next to any video
4. **Clear All**: Use the "Clear All" button to start over

### Processing Queue
- Videos are processed in the order they appear in the list
- Each video shows its current status with color-coded indicators:
  - ⏳ **Waiting**: Video is queued for processing
  - 🔄 **Processing**: Currently being transcribed
  - ✅ **Done**: Successfully processed
  - ❌ **Error**: Processing failed

### Output Files
The tool creates:
- `combined_video_YYYYMMDD_HHMMSS.srt` - Complete subtitle file
- `combined_video_YYYYMMDD_HHMMSS_with_subtitles.mp4` - Final video with subtitles

## 🛠️ Troubleshooting

### Common Issues

1. **Drag & Drop Not Working**
   - Install tkinterdnd2: `pip install tkinterdnd2`
   - Use "Add Videos" button as alternative

2. **Video Stitching Fails**
   - Ensure all videos have similar formats
   - Check available disk space
   - Try videos with simpler file paths

3. **FFmpeg Not Found**
   - Install FFmpeg and add to system PATH
   - Or place FFmpeg in one of the auto-detected paths

4. **Memory Issues with Large Videos**
   - Use smaller AI model (tiny or base)
   - Process fewer videos at once
   - Ensure sufficient RAM is available

### Error Recovery
- Individual video failures don't stop the entire process
- Partial results are saved even if some steps fail
- Detailed error messages provide specific guidance

## 🔮 Future Enhancements

Potential future improvements:
- Video preview thumbnails in the list
- Custom video ordering (drag to reorder)
- Batch subtitle editing
- Multiple output format options
- Progress bars for individual videos
- Resume interrupted processing

## 📝 Changelog

### Version 2.0 - Multi-Video Processing
- ✅ Added drag & drop support
- ✅ Multi-video selection and management
- ✅ Sequential video processing
- ✅ Automatic video stitching
- ✅ Combined subtitle generation
- ✅ Enhanced error handling
- ✅ Improved UI for video management
- ✅ Dzine Lipsync workflow optimization

### Compatibility
- ✅ Backward compatible with single-video processing
- ✅ Graceful degradation when drag & drop unavailable
- ✅ Existing configuration and workspace settings preserved