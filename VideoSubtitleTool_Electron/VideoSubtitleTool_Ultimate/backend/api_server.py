"""
FastAPI Backend for Video Subtitle Tool
Provides REST API for video processing functionality
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
import sys
import threading
import json
from typing import List, Optional
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from faster_whisper import WhisperModel
    from video_processor_api import VideoProcessorAPI
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all dependencies are installed")
    sys.exit(1)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(title="Video Subtitle Tool API", version="2.0.0")

# Enable CORS for Electron frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize video processor
processor = VideoProcessorAPI()

# Pydantic models for EXACT 4-Step Workflow
class ProcessRequest(BaseModel):
    videos: List[str]
    workspace: str
    model: str = "small"

class ProcessResponse(BaseModel):
    success: bool
    message: str = ""
    combined_video: Optional[str] = None
    initial_srt: Optional[str] = None
    base_name: Optional[str] = None
    workspace: Optional[str] = None
    error: Optional[str] = None
    step: str = "initial"  # "initial" for steps 1-2, "correction" for step 3, "final" for step 4

class ApplyCorrectRequest(BaseModel):
    initial_srt: str
    original_transcript: str
    base_name: str
    workspace: str

class SkipCorrectRequest(BaseModel):
    initial_srt: str
    base_name: str
    workspace: str

class CorrectionResponse(BaseModel):
    success: bool
    message: str = ""
    final_srt: Optional[str] = None
    correction_percentage: Optional[float] = None
    error: Optional[str] = None

class BurnSubtitlesRequest(BaseModel):
    combined_video: str
    final_srt: str
    base_name: str
    workspace: str

class BurnSubtitlesResponse(BaseModel):
    success: bool
    message: str = ""
    final_video: Optional[str] = None
    subtitle_burn_failed: bool = False
    error: Optional[str] = None

class StatusResponse(BaseModel):
    status: str
    message: str
    backend_ready: bool = True

# API Routes
@app.get("/", response_model=StatusResponse)
async def root():
    """Health check endpoint"""
    return StatusResponse(
        status="ready",
        message="Video Subtitle Tool API is running",
        backend_ready=True
    )

@app.get("/health", response_model=StatusResponse)
async def health_check():
    """Detailed health check"""
    try:
        # Check if we can load a model (quick test)
        test_model = WhisperModel("tiny", device="cpu", compute_type="int8")
        model_ready = True
        del test_model  # Clean up
    except Exception as e:
        model_ready = False
        logger.error(f"Model check failed: {e}")
    
    return StatusResponse(
        status="ready" if model_ready else "error",
        message="All systems operational" if model_ready else "Model loading failed",
        backend_ready=model_ready
    )

@app.post("/process", response_model=ProcessResponse)
async def process_videos_step_1_2(request: ProcessRequest):
    """EXACT Step 1-2: Stitch videos and transcribe (EXACT workflow from original GUI)"""
    try:
        logger.info(f"Starting EXACT 4-step workflow: {len(request.videos)} videos, model: {request.model}")
        
        # Validate inputs
        if not request.videos:
            raise HTTPException(status_code=400, detail="No videos provided")
        
        if not request.workspace:
            raise HTTPException(status_code=400, detail="No workspace provided")
        
        # Check if all video files exist
        missing_files = []
        for video_path in request.videos:
            if not os.path.exists(video_path):
                missing_files.append(video_path)
        
        if missing_files:
            raise HTTPException(
                status_code=400, 
                detail=f"Video files not found: {', '.join(missing_files)}"
            )
        
        # Create workspace directory if it doesn't exist
        os.makedirs(request.workspace, exist_ok=True)
        
        # Execute EXACT Steps 1-2 from original GUI workflow
        success, workflow_data = processor.process_multiple_videos_exact_workflow(
            video_paths=request.videos,
            workspace=request.workspace,
            model_size=request.model
        )
        
        if success and workflow_data:
            return ProcessResponse(
                success=True,
                message="Steps 1-2 completed: Videos stitched and transcribed. Ready for Step 3: Transcript correction.",
                combined_video=workflow_data.get("combined_video"),
                initial_srt=workflow_data.get("initial_srt"),
                base_name=workflow_data.get("base_name"),
                workspace=workflow_data.get("workspace"),
                step="correction"
            )
        else:
            return ProcessResponse(
                success=False,
                message="Steps 1-2 failed during stitching or transcription",
                error="Failed at Step 1 (Stitching) or Step 2 (Transcription)",
                step="initial"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Steps 1-2 error: {str(e)}")
        return ProcessResponse(
            success=False,
            message="Steps 1-2 failed",
            error=str(e),
            step="initial"
        )

@app.post("/apply-correction", response_model=CorrectionResponse)
async def apply_correction_step_3(request: ApplyCorrectRequest):
    """EXACT Step 3: Apply transcript correction (EXACT workflow from original GUI)"""
    try:
        logger.info("Applying transcript correction (Step 3/4)")
        
        success, final_srt, correction_percentage = processor.apply_transcript_correction_exact(
            initial_srt_file=request.initial_srt,
            original_transcript=request.original_transcript,
            base_name=request.base_name,
            workspace=request.workspace
        )
        
        if success:
            return CorrectionResponse(
                success=True,
                message=f"Step 3 completed: Correction applied ({correction_percentage:.1f}% of subtitles corrected)",
                final_srt=final_srt,
                correction_percentage=correction_percentage
            )
        else:
            return CorrectionResponse(
                success=False,
                message="Step 3 failed: Transcript correction error",
                error="Failed to apply transcript correction"
            )
            
    except Exception as e:
        logger.error(f"Step 3 correction error: {str(e)}")
        return CorrectionResponse(
            success=False,
            message="Step 3 failed",
            error=str(e)
        )

@app.post("/skip-correction", response_model=CorrectionResponse)
async def skip_correction_step_3(request: SkipCorrectRequest):
    """EXACT Step 3 Alternative: Skip transcript correction (EXACT workflow from original GUI)"""
    try:
        logger.info("Skipping transcript correction (Step 3/4)")
        
        success, final_srt = processor.skip_transcript_correction_exact(
            initial_srt_file=request.initial_srt,
            base_name=request.base_name,
            workspace=request.workspace
        )
        
        if success:
            return CorrectionResponse(
                success=True,
                message="Step 3 completed: Correction skipped, using AI-generated subtitles",
                final_srt=final_srt,
                correction_percentage=0.0
            )
        else:
            return CorrectionResponse(
                success=False,
                message="Step 3 failed: Error skipping correction",
                error="Failed to finalize SRT file"
            )
            
    except Exception as e:
        logger.error(f"Step 3 skip error: {str(e)}")
        return CorrectionResponse(
            success=False,
            message="Step 3 failed",
            error=str(e)
        )

@app.post("/burn-subtitles", response_model=BurnSubtitlesResponse)
async def burn_subtitles_step_4(request: BurnSubtitlesRequest):
    """EXACT Step 4: Burn subtitles into video (EXACT workflow from original GUI)"""
    try:
        logger.info("Burning subtitles into video (Step 4/4)")
        
        success, final_output = processor.burn_subtitles_final_step_exact(
            combined_video=request.combined_video,
            final_srt_file=request.final_srt,
            base_name=request.base_name,
            workspace=request.workspace
        )
        
        if success:
            return BurnSubtitlesResponse(
                success=True,
                message="Step 4 completed: Multi-video processing finished successfully! Final video with subtitles created.",
                final_video=final_output
            )
        else:
            return BurnSubtitlesResponse(
                success=False,
                message="Step 4 completed with warnings: Subtitle burning failed, but combined video and SRT available.",
                final_video=final_output,  # Still return the combined video
                subtitle_burn_failed=True,
                error="Subtitle burning failed, but combined video and SRT file are ready"
            )
            
    except Exception as e:
        logger.error(f"Step 4 burn error: {str(e)}")
        return BurnSubtitlesResponse(
            success=False,
            message="Step 4 failed",
            error=str(e)
        )

@app.get("/models")
async def get_available_models():
    """Get list of available Whisper models"""
    models = [
        {
            "name": "tiny",
            "description": "Fastest processing, basic accuracy",
            "size": "~39 MB"
        },
        {
            "name": "base", 
            "description": "Good balance of speed and accuracy",
            "size": "~74 MB"
        },
        {
            "name": "small",
            "description": "Recommended for most users",
            "size": "~244 MB"
        },
        {
            "name": "medium",
            "description": "Better accuracy, slower processing", 
            "size": "~769 MB"
        },
        {
            "name": "large-v3",
            "description": "Best accuracy, slowest processing",
            "size": "~1550 MB"
        }
    ]
    
    return {"models": models}

# Global progress tracking (for future use)
processing_status = {
    "current_task": None,
    "progress": 0,
    "message": "Ready"
}

@app.get("/progress")
async def get_progress():
    """Get current processing progress"""
    return processing_status

def update_progress(task: str, progress: int, message: str):
    """Update processing progress"""
    global processing_status
    processing_status["current_task"] = task
    processing_status["progress"] = progress
    processing_status["message"] = message
    logger.info(f"Progress: {task} - {progress}% - {message}")

# Old endpoint removed - replaced with exact 4-step workflow above

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    logger.info("Video Subtitle Tool API starting up...")
    logger.info(f"Backend ready on http://localhost:8000")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Video Subtitle Tool API shutting down...")
    processor.cleanup()

if __name__ == "__main__":
    print("Starting Video Subtitle Tool API Server...")
    print("Backend will be available on http://localhost:8000")
    
    # Run the server
    uvicorn.run(
        app, 
        host="127.0.0.1", 
        port=8000, 
        log_level="info",
        access_log=True
    )