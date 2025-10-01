from faster_whisper import WhisperModel
import os
import subprocess

def format_time_srt(seconds):
    """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    milliseconds = int((seconds - int(seconds)) * 1000)
    seconds = int(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def generate_srt(segments, output_file):
    """Generate SRT subtitle file from transcription segments"""
    with open(output_file, 'w', encoding='utf-8') as f:
        for i, segment in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{format_time_srt(segment.start)} --> {format_time_srt(segment.end)}\n")
            f.write(f"{segment.text.strip()}\n\n")

def find_ffmpeg():
    """Find FFmpeg executable on the system"""
    username = os.environ.get('USERNAME', '')
    ffmpeg_paths = [
        'ffmpeg',  # If it's in PATH
        rf'C:\Users\{username}\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe',
        r'C:\ffmpeg\bin\ffmpeg.exe',
        r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
        rf'C:\Users\{username}\scoop\apps\ffmpeg\current\bin\ffmpeg.exe',
        r'C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe'
    ]
    
    for path in ffmpeg_paths:
        try:
            result = subprocess.run([path, '-version'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
            if result.returncode == 0:
                return path
        except:
            continue
    return None

def burn_subtitles(video_file, subtitle_file, output_file):
    """Burn subtitles into video using FFmpeg with lossless quality"""
    ffmpeg_cmd = find_ffmpeg()
    if not ffmpeg_cmd:
        print(f"\n❌ FFmpeg not found! Please install FFmpeg first.")
        return False
    
    # Use lossless quality settings by default
    video_settings = ['-c:v', 'libx264', '-crf', '0', '-preset', 'veryslow']
    quality_desc = "Lossless (perfect quality)"
    
    # Convert Windows paths to Unix-style for FFmpeg
    subtitle_path_fixed = subtitle_file.replace('\\', '/').replace(':', '\\:')
    
    cmd = [
        ffmpeg_cmd,
        '-i', video_file,
        '-vf', f"subtitles={subtitle_path_fixed}:force_style='FontSize=16'",
        *video_settings,
        '-c:a', 'copy',              # Always copy audio without re-encoding
        '-movflags', '+faststart',   # Optimize for web streaming
        '-y',                        # Overwrite output file
        output_file
    ]
    
    print(f"🎬 Burning subtitles into video...")
    print(f"⚙️  Quality mode: {quality_desc}")
    print(f"⏳ Processing... (higher quality = longer processing time)")
    print(f"DEBUG: subtitle_path_fixed = {subtitle_path_fixed}")
    print(f"DEBUG: Working directory = {os.getcwd()}")
    print(f"DEBUG: Command = {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        if result.returncode == 0:
            return True
        else:
            print(f"❌ FFmpeg error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def process_video_complete(video_file, model_size="small"):
    """
    Complete pipeline: Video → Transcription → SRT → Burned Subtitles (Lossless)
    """
    print(f"🎥 Starting complete video processing pipeline...")
    print(f"📹 Input video: {video_file}")
    
    # Check if video file exists
    if not os.path.exists(video_file):
        print(f"❌ Error: Video file '{video_file}' not found!")
        return False
    
    # Generate output filenames
    base_name = os.path.splitext(video_file)[0]
    srt_file = f"{base_name}.srt"
    output_video = f"{base_name}_with_subtitles.mp4"
    
    print(f"📝 SRT output: {srt_file}")
    print(f"🎬 Final video: {output_video}")
    
    # Step 1: Load Whisper model
    print(f"\n🔄 Step 1: Loading Whisper model ({model_size})...")
    try:
        model = WhisperModel(model_size, device="cpu", compute_type="int8")
        print("✅ Model loaded successfully!")
    except Exception as e:
        print(f"❌ Error loading model: {str(e)}")
        return False
    
    # Step 2: Transcribe video (faster-whisper can handle video directly)
    print(f"\n🔄 Step 2: Transcribing video...")
    try:
        segments, info = model.transcribe(video_file, beam_size=5)
        print(f"✅ Detected language: '{info.language}' with probability {info.language_probability:.2f}")
        
        # Convert generator to list
        segments_list = list(segments)
        print(f"✅ Transcription completed! Found {len(segments_list)} segments")
        
    except Exception as e:
        print(f"❌ Error during transcription: {str(e)}")
        return False
    
    # Step 3: Generate SRT file
    print(f"\n🔄 Step 3: Generating SRT subtitle file...")
    try:
        generate_srt(segments_list, srt_file)
        print(f"✅ SRT file created: {srt_file}")
    except Exception as e:
        print(f"❌ Error creating SRT: {str(e)}")
        return False
    
    # Step 4: Burn subtitles into video
    print(f"\n🔄 Step 4: Burning subtitles into video...")
    try:
        success = burn_subtitles(video_file, srt_file, output_video)
        if success:
            print(f"✅ Video with burned subtitles created!")
            print(f"📁 Final output: {os.path.abspath(output_video)}")
            return True
        else:
            return False
    except Exception as e:
        print(f"❌ Error burning subtitles: {str(e)}")
        return False

def main():
    print("🎬 Complete Video Subtitle Pipeline")
    print("=" * 50)
    
    # Look for video files
    video_folder = "video"
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v']
    
    video_path = input("Enter video file path (or press Enter to browse 'video' folder): ").strip().strip('"')
    
    if not video_path:
        if os.path.exists(video_folder):
            video_files = [f for f in os.listdir(video_folder) if any(f.lower().endswith(ext) for ext in video_extensions)]
            
            if video_files:
                if len(video_files) == 1:
                    video_path = os.path.join(video_folder, video_files[0])
                    print(f"Found video: {video_path}")
                else:
                    print("Multiple video files found:")
                    for i, vf in enumerate(video_files, 1):
                        print(f"{i}. {vf}")
                    
                    try:
                        choice = int(input("Enter the number of the video to process: ")) - 1
                        video_path = os.path.join(video_folder, video_files[choice])
                    except (ValueError, IndexError):
                        print("Invalid choice!")
                        return
            else:
                print(f"No video files found in '{video_folder}' folder!")
                return
        else:
            print(f"'{video_folder}' folder not found!")
            return
    
    # Choose model size
    print(f"\nChoose Whisper model size:")
    print("1. tiny (fastest, least accurate)")
    print("2. base (balanced)")
    print("3. small (RECOMMENDED - best balance of speed and accuracy)")
    print("4. medium (better accuracy, slower)")
    print("5. large-v3 (best accuracy, slowest)")
    
    model_choice = input("Enter choice (1-5, default=3): ").strip()
    model_sizes = {"1": "tiny", "2": "base", "3": "small", "4": "medium", "5": "large-v3"}
    model_size = model_sizes.get(model_choice, "small")
    
    print(f"\n🚀 Starting processing with lossless quality:")
    print(f"   📋 Model: {model_size}")
    print(f"   🎯 Quality: Lossless (perfect quality)")
    print("=" * 50)
    
    # Process the video
    success = process_video_complete(video_path, model_size)
    
    if success:
        print(f"\n🎉 SUCCESS! Complete pipeline finished!")
        print(f"You now have:")
        print(f"  📝 Subtitle file (.srt)")
        print(f"  🎬 Video with burned-in subtitles")
    else:
        print(f"\n❌ Pipeline failed. Please check the errors above.")

if __name__ == "__main__":
    main()