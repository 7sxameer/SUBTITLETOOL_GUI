# Video Subtitle Tool - Modern UI

A modern Electron-based GUI for the Video Subtitle Tool with an intuitive 4-step workflow for processing multiple video files and generating subtitles with AI-powered transcription and correction.

## ✨ Features

- **Modern UI**: Clean, responsive interface built with Electron
- **4-Step Workflow**: Streamlined process (Stitch → Transcribe → Correct → Burn)
- **Multi-Video Processing**: Handle multiple video files in one go
- **AI-Powered Transcription**: Uses Faster Whisper models for accurate transcription
- **Smart Correction**: AI-powered subtitle correction and timing optimization
- **Real-time Progress**: Live progress tracking with detailed status updates
- **Flexible Output**: Generate SRT files and/or burn subtitles into video
- **Model Selection**: Choose from different Whisper models (tiny, small, medium, large)

## 🚀 Quick Start

### Prerequisites

Before running the application, ensure you have:

1. **Node.js** (v18 or higher)
   - Download from: https://nodejs.org/
   - Verify installation: `node --version`

2. **Python** (v3.9 or higher)
   - Download from: https://www.python.org/
   - Verify installation: `python --version`

3. **FFmpeg** (for video processing)
   - Download from: https://ffmpeg.org/download.html
   - Add to PATH environment variable
   - Verify installation: `ffmpeg -version`

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/7sxameer/SUBTITLETOOL_GUI.git -b newui
   cd SUBTITLETOOL_GUI/VideoSubtitleTool_Electron
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Install Python dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   cd ..
   ```

### Running the Application

1. **Start the application**
   ```bash
   npm start
   ```

   This command will:
   - Start the Python FastAPI backend server
   - Launch the Electron frontend
   - Perform automatic health checks
   - Display "Backend ready" when fully loaded

2. **Wait for startup**
   - The application may take 30-60 seconds to fully start
   - You'll see "Backend health check passed" in the console
   - The UI will show "Backend Status: Ready" when ready to use

## 📖 How to Use

### Step 1: Select Videos
- Click "Select Videos" to choose multiple video files
- Supported formats: MP4, AVI, MOV, MKV, and more
- Selected videos will be displayed in the list

### Step 2: Set Workspace
- Click "Set Workspace" to choose output directory
- All generated files will be saved here
- Choose a location with sufficient storage space

### Step 3: Choose Processing Options
- **Model Selection**: Choose Whisper model (tiny/small/medium/large)
  - `tiny`: Fastest, less accurate
  - `small`: Good balance (recommended)
  - `medium`: Better accuracy, slower
  - `large`: Best accuracy, slowest
- **Processing Mode**: Select your workflow preference

### Step 4: Start Processing

#### 4-Step Workflow (Recommended)
1. **Stitch**: Combines multiple videos into one
2. **Transcribe**: AI transcription using Faster Whisper
3. **Correct**: Interactive correction interface (or skip)
4. **Burn**: Generate final video with embedded subtitles

Click "Start 4-Step Processing" and follow the on-screen prompts.

### Manual Correction (Step 3)
When correction is needed:
- Review the generated transcript
- Make necessary edits in the text area
- Click "Apply Correction" or "Skip Correction"
- The system will show correction percentage

## 📁 Output Files

After processing, you'll find in your workspace:

- `combined_video.mp4`: Stitched video file
- `initial_transcript.srt`: Raw AI-generated subtitles
- `corrected_transcript.srt`: Corrected subtitles (if correction applied)
- `final_video_with_subtitles.mp4`: Video with burned-in subtitles
- Processing logs and temporary files

## ⚙️ Configuration

### Model Performance Guide

| Model  | Speed | Accuracy | VRAM Usage | Recommended For |
|--------|-------|----------|------------|-----------------|
| tiny   | ⭐⭐⭐⭐⭐ | ⭐⭐ | ~1GB | Quick testing |
| small  | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ~2GB | General use |
| medium | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ~5GB | High accuracy |
| large  | ⭐⭐ | ⭐⭐⭐⭐⭐⭐ | ~10GB | Best quality |

### System Requirements

- **CPU**: Multi-core processor (Intel i5/AMD Ryzen 5 or better)
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 5GB free space for models and processing
- **GPU**: Optional - CUDA-compatible GPU for faster processing

## 🔧 Troubleshooting

### Common Issues

1. **"Backend connection failed"**
   - Ensure Python dependencies are installed: `pip install -r backend/requirements.txt`
   - Check if port 8000 is available
   - Try restarting the application

2. **"FFmpeg not found"**
   - Install FFmpeg and add to PATH
   - Restart terminal/command prompt after installation
   - Verify with: `ffmpeg -version`

3. **"Module not found" errors**
   - Run: `pip install -r backend/requirements.txt`
   - Use virtual environment if needed:
     ```bash
     python -m venv venv
     venv\Scripts\activate  # Windows
     pip install -r backend/requirements.txt
     ```

4. **Slow processing**
   - Use smaller Whisper model (tiny/small)
   - Close other applications to free RAM
   - Ensure sufficient disk space

5. **Application won't start**
   - Check Node.js version: `node --version` (need v18+)
   - Try: `npm install` to reinstall dependencies
   - Check console for error messages

### Performance Tips

- **Use SSD storage** for workspace directory
- **Close unused applications** while processing
- **Use appropriate model size** for your hardware
- **Process videos in smaller batches** for large collections

## 🛠️ Development

### Project Structure
```
VideoSubtitleTool_Electron/
├── main.js              # Electron main process
├── package.json         # Node.js dependencies
├── renderer/            # Frontend UI
│   ├── index.html
│   ├── style.css
│   └── app.js
├── backend/             # Python FastAPI server
│   ├── api_server.py
│   ├── requirements.txt
│   └── video_to_subtitles.py
└── README.md
```

### Running in Development Mode
```bash
# Start with developer tools
npm run dev

# Or start manually with dev tools
electron . --dev
```

## 📋 Requirements Files

### Node.js Dependencies (package.json)
- electron: Desktop application framework
- axios: HTTP client for API calls

### Python Dependencies (backend/requirements.txt)
- fastapi: Web API framework
- uvicorn: ASGI server
- faster-whisper: AI transcription
- ctranslate2: Efficient transformer inference
- numpy: Numerical computations
- And other supporting libraries

## 🆘 Support

If you encounter issues:

1. **Check the console output** for error messages
2. **Verify all prerequisites** are installed correctly
3. **Try the troubleshooting steps** above
4. **Create an issue** on GitHub with:
   - Your operating system
   - Python and Node.js versions
   - Complete error message
   - Steps to reproduce

## 📄 License

This project is licensed under the MIT License. See the original repository for full license details.

---

**Note**: This is the modern UI version of the Video Subtitle Tool. The application combines the power of AI transcription with an intuitive interface for professional subtitle generation workflows.