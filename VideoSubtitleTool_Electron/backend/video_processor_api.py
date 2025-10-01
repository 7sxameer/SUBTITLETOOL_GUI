"""
Video Processor API - Exact Implementation of Original GUI Workflow
Replicates the 4-step process: Stitch → Transcribe → Correct → Burn
"""

from faster_whisper import WhisperModel
import os
import subprocess
import time
import re
import shutil
from difflib import SequenceMatcher
from typing import List, Tuple, Optional, Callable

def safe_print(message):
    """Safe print function that handles Unicode characters"""
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback to ASCII-only printing
        print(message.encode('ascii', 'replace').decode('ascii'))

# SRT Correction Functions (EXACT from original GUI)
def clean_text_for_comparison(text):
    """Remove punctuation and normalize text for character counting and comparison"""
    cleaned = re.sub(r'[？！。、？!.,\s\-―「」『』（）()[\]""''・?]', '', text)
    return cleaned

def extract_dialogue_from_original(original_text):
    """Extract just the dialogue part, removing speaker names like 'Riku：' or 'Kai：'"""
    dialogue_only = re.sub(r'^[A-Za-z]+：\s*', '', original_text.strip())
    return dialogue_only

def similarity_ratio(text1, text2):
    """Calculate similarity ratio between two texts"""
    return SequenceMatcher(None, text1, text2).ratio()

def find_last_character_match_advanced(srt_clean, original_segment, base_length):
    """Advanced character boundary matching with better search algorithm"""
    srt_last_char = srt_clean[-1] if srt_clean else ""
    best_match = None
    best_similarity = 0
    best_end_pos = base_length
    
    for offset in range(-10, 25):
        test_end = base_length + offset
        if test_end <= 0 or test_end > len(original_segment):
            continue
            
        segment_slice = original_segment[:test_end]
        segment_clean = clean_text_for_comparison(segment_slice)
        
        if not segment_clean:
            continue
            
        similarity = similarity_ratio(srt_clean, segment_clean)
        length_ratio = min(len(segment_clean), len(srt_clean)) / max(len(segment_clean), len(srt_clean)) if max(len(segment_clean), len(srt_clean)) > 0 else 0
        last_char_bonus = 0.2 if segment_clean and segment_clean[-1] == srt_last_char else 0
        combined_score = similarity + (length_ratio * 0.1) + last_char_bonus
        
        if combined_score > best_similarity:
            best_similarity = combined_score
            best_match = segment_slice
            best_end_pos = test_end
    
    if best_match:
        extended_end = best_end_pos
        while extended_end < len(original_segment):
            next_char = original_segment[extended_end]
            if re.match(r'[？！。、？!.,\s\-―「」『』（）()[\]""''・?…]', next_char):
                extended_end += 1
            else:
                break
        
        final_segment = original_segment[:extended_end]
        final_clean = clean_text_for_comparison(final_segment)
        return extended_end, final_segment, final_clean
    
    segment_slice = original_segment[:base_length]
    segment_clean = clean_text_for_comparison(segment_slice)
    return base_length, segment_slice, segment_clean

def parse_srt_file(srt_path):
    """Parse SRT file and return list of subtitle entries"""
    with open(srt_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    blocks = re.split(r'\n\s*\n', content.strip())
    subtitles = []
    
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 3:
            index = lines[0]
            timestamp = lines[1]
            text = '\n'.join(lines[2:])
            subtitles.append({
                'index': int(index),
                'timestamp': timestamp,
                'text': text
            })
    
    return subtitles

class VideoProcessorAPI:
    """Clean video processing backend for API integration"""
    
    def __init__(self):
        self.model = None
        self.current_model_size = None
        
    def format_time_srt(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def generate_srt(self, segments, output_file: str):
        """Generate SRT subtitle file from transcription segments"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                f.write(f"{i}\n")
                f.write(f"{self.format_time_srt(segment.start)} --> {self.format_time_srt(segment.end)}\n")
                f.write(f"{segment.text.strip()}\n\n")

    def find_ffmpeg(self) -> Optional[str]:
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
                result = subprocess.run([path, '-version'], capture_output=True, text=True, 
                                      creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                if result.returncode == 0:
                    return path
            except:
                continue
        return None

    def load_model(self, model_size: str = "small"):
        """Load Whisper model"""
        if self.current_model_size == model_size and self.model is not None:
            return  # Model already loaded
            
        print(f"Loading AI model: {model_size}...")
        try:
            self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
            self.current_model_size = model_size
            print(f"Model '{model_size}' loaded successfully")
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            raise

    def transcribe_video(self, video_path: str, model_size: str = "small") -> Tuple[List, any]:
        """Transcribe video and return segments and info"""
        
        # Load model if needed
        self.load_model(model_size)
        
        print(f"Transcribing video: {os.path.basename(video_path)}")
        
        try:
            # Transcribe
            segments, info = self.model.transcribe(video_path, beam_size=5)
            segments = list(segments)  # Convert generator to list
            
            print(f"Transcription complete: {len(segments)} segments found")
                
            return segments, info
            
        except Exception as e:
            print(f"Transcription error: {str(e)}")
            raise

    def burn_subtitles(self, video_file: str, subtitle_file: str, output_file: str) -> bool:
        """Burn subtitles with high quality settings - EXACT from original GUI"""
        try:
            ffmpeg_cmd = self.find_ffmpeg()
            if not ffmpeg_cmd:
                raise Exception("FFmpeg not found! Please install FFmpeg.")
            
            # Use high quality but stable settings instead of lossless (CRF 0 can cause issues)
            video_settings = [
                '-c:v', 'libx264',
                '-crf', '18',  # High quality instead of lossless (0)
                '-preset', 'medium',  # Medium instead of veryslow
                '-pix_fmt', 'yuv420p',  # Ensure compatibility
                '-profile:v', 'high',  # Use high profile for better compatibility
                '-level:v', '4.0'  # Standard level
            ]
            
            # Try different approaches for handling problematic paths
            subtitle_path_approaches = [
                # Method 1: Properly escape the entire subtitle filter
                f"subtitles='{subtitle_file.replace('\\', '/')}':force_style='FontSize=16'",
                # Method 2: Double quote the path
                f'subtitles="{subtitle_file.replace("\\", "/")}":force_style="FontSize=16"',
                # Method 3: Copy to temp file with simple name
                "temp_approach"
            ]
            
            for i, subtitle_approach in enumerate(subtitle_path_approaches, 1):
                safe_print(f"Attempting subtitle burn method {i}/3...")
                
                if subtitle_approach == "temp_approach":
                    # Method 3: Copy SRT to a temp file with simple name
                    temp_srt = os.path.join(os.path.dirname(subtitle_file), "temp_subtitles.srt")
                    try:
                        shutil.copy2(subtitle_file, temp_srt)
                        vf_filter = "subtitles=temp_subtitles.srt:force_style='FontSize=16'"
                        
                        # Change working directory to subtitle file location
                        original_cwd = os.getcwd()
                        os.chdir(os.path.dirname(subtitle_file))
                        
                        cmd = [
                            ffmpeg_cmd,
                            '-i', video_file,
                            '-vf', vf_filter,
                            *video_settings,
                            '-c:a', 'aac',  # Re-encode audio with AAC for better compatibility
                            '-b:a', '128k',  # Set audio bitrate
                            '-movflags', '+faststart',
                            '-y',
                            output_file
                        ]
                        
                        safe_print(f"DEBUG Method {i}: Using temp file approach with stable encoding")
                        safe_print(f"DEBUG Settings: CRF 18, medium preset, yuv420p pixel format")
                        
                        result = subprocess.run(cmd, capture_output=True, text=True)
                        
                        # Restore original working directory
                        os.chdir(original_cwd)
                        
                        # Clean up temp file
                        if os.path.exists(temp_srt):
                            os.remove(temp_srt)
                            
                    except Exception as temp_error:
                        # Restore working directory if something went wrong
                        try:
                            os.chdir(original_cwd)
                            if os.path.exists(temp_srt):
                                os.remove(temp_srt)
                        except:
                            pass
                        safe_print(f"Method {i} temp approach failed: {str(temp_error)}")
                        continue
                else:
                    # Methods 1 and 2: Try different escaping approaches
                    cmd = [
                        ffmpeg_cmd,
                        '-i', video_file,
                        '-vf', subtitle_approach,
                        *video_settings,
                        '-c:a', 'aac',
                        '-b:a', '128k',
                        '-movflags', '+faststart',
                        '-y',
                        output_file
                    ]
                    
                    safe_print(f"DEBUG Method {i}: {subtitle_approach[:50]}...")
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    safe_print(f"SUCCESS with method {i} - using stable encoding settings")
                    return True
                else:
                    safe_print(f"Method {i} failed: {result.stderr[:300]}...")
                    continue
            
            # If all methods failed, raise detailed error
            raise Exception(f"All subtitle burning methods failed. The SRT file was created successfully, but video encoding failed. Try moving your video to a folder with a simple name like C:\\Videos\\ and avoid spaces or special characters in the filename.")
            
        except Exception as e:
            safe_print(f"Burn subtitles error: {str(e)}")
            raise e

    def stitch_videos(self, video_paths: List[str], output_path: str) -> bool:
        """Stitch multiple videos together using FFmpeg - EXACT from original GUI"""
        try:
            ffmpeg_cmd = self.find_ffmpeg()
            if not ffmpeg_cmd:
                raise Exception("FFmpeg not found! Please install FFmpeg.")
            
            # Create a temporary file list for FFmpeg concat
            temp_dir = os.path.dirname(output_path)
            file_list_path = os.path.join(temp_dir, "video_list.txt")
            
            # Write file list
            with open(file_list_path, 'w', encoding='utf-8') as f:
                for video_path in video_paths:
                    # Escape single quotes and backslashes for FFmpeg
                    escaped_path = video_path.replace('\\', '/').replace("'", "'\\''")
                    f.write(f"file '{escaped_path}'\n")
            
            # Use concat demuxer for faster processing
            cmd = [
                ffmpeg_cmd,
                '-f', 'concat',
                '-safe', '0',
                '-i', file_list_path,
                '-c', 'copy',  # Stream copy for speed
                '-avoid_negative_ts', 'make_zero',
                '-fflags', '+genpts',
                '-y',
                output_path
            ]
            
            safe_print(f"Stitching {len(video_paths)} videos...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Cleanup temp file
            try:
                os.remove(file_list_path)
            except:
                pass
            
            if result.returncode == 0:
                safe_print("Video stitching successful")
                return True
            else:
                safe_print(f"Video stitching failed: {result.stderr}")
                
                # Try alternative method with re-encoding
                safe_print("Trying alternative stitching method...")
                return self.stitch_videos_reencoding(video_paths, output_path)
                
        except Exception as e:
            safe_print(f"Stitch videos error: {str(e)}")
            return False
    
    def stitch_videos_reencoding(self, video_paths: List[str], output_path: str) -> bool:
        """Alternative stitching method with re-encoding (slower but more compatible) - EXACT from original GUI"""
        try:
            ffmpeg_cmd = self.find_ffmpeg()
            if not ffmpeg_cmd:
                return False
            
            # Create filter complex for concatenation
            inputs = []
            filter_parts = []
            
            for i, video_path in enumerate(video_paths):
                inputs.extend(['-i', video_path])
                filter_parts.append(f'[{i}:v][{i}:a]')
            
            filter_complex = ''.join(filter_parts) + f'concat=n={len(video_paths)}:v=1:a=1[outv][outa]'
            
            cmd = [
                ffmpeg_cmd,
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[outv]',
                '-map', '[outa]',
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-preset', 'fast',
                '-crf', '23',
                '-y',
                output_path
            ]
            
            safe_print("Using re-encoding method for stitching...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception:
            return False

    def process_multiple_videos_exact_workflow(self, video_paths: List[str], workspace: str, model_size: str = "small") -> Tuple[bool, dict]:
        """
        EXACT 4-Step Multi-Video Processing Workflow from Original GUI:
        Step 1: Stitch → Step 2: Transcribe → Step 3: Create Initial SRT → Return for User Correction
        Returns: (success, {"combined_video": path, "initial_srt": path, "base_name": name})
        """
        try:
            # Create timestamp for this batch (EXACT naming as original)
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base_name = f"combined_video_{timestamp}"
            
            # Step 1: Stitch all videos together first
            safe_print("Step 1/4: Stitching videos together...")
            combined_video = os.path.join(workspace, f"{base_name}_combined.mp4")
            
            success = self.stitch_videos(video_paths, combined_video)
            if not success:
                raise Exception("Failed to stitch videos together")
            
            # Step 2: Transcribe the combined video
            safe_print("Step 2/4: Loading AI model...")
            self.load_model(model_size)
            
            safe_print("Step 2/4: Transcribing combined video...")
            segments, info = self.transcribe_video(combined_video, model_size)
            
            # Step 3: Create initial SRT file from transcription
            safe_print("Step 2/4: Creating initial subtitle file...")
            initial_srt_file = os.path.join(workspace, f"{base_name}_initial.srt")
            self.generate_srt(segments, initial_srt_file)
            
            # Return for user correction step (Step 3/4)
            return True, {
                "combined_video": combined_video,
                "initial_srt": initial_srt_file,
                "base_name": base_name,
                "workspace": workspace
            }
            
        except Exception as e:
            safe_print(f"Multi-video workflow error: {str(e)}")
            return False, {}
    
    def apply_transcript_correction_exact(self, initial_srt_file: str, original_transcript: str, base_name: str, workspace: str) -> Tuple[bool, str, float]:
        """
        EXACT Step 3: Apply transcript correction like original GUI
        Returns: (success, final_srt_path, correction_percentage)
        """
        try:
            safe_print("Step 3/4: Applying transcript correction...")
            
            # Create corrected SRT file (EXACT naming as original)
            corrected_srt_file = os.path.join(workspace, f"{base_name}.srt")
            correction_percentage = self.correct_srt_with_advanced_matching(
                initial_srt_file, original_transcript, corrected_srt_file
            )
            
            safe_print(f"Step 3/4: Correction applied ({correction_percentage:.1f}% of subtitles corrected)")
            
            # Clean up initial SRT file (EXACT as original)
            try:
                if os.path.exists(initial_srt_file):
                    os.remove(initial_srt_file)
            except:
                pass
            
            return True, corrected_srt_file, correction_percentage
            
        except Exception as e:
            safe_print(f"Correction error: {str(e)}")
            return False, "", 0.0
    
    def skip_transcript_correction_exact(self, initial_srt_file: str, base_name: str, workspace: str) -> Tuple[bool, str]:
        """
        EXACT Step 3 Alternative: Skip correction like original GUI
        Returns: (success, final_srt_path)
        """
        try:
            safe_print("Step 3/4: Correction skipped, using AI-generated subtitles...")
            
            # User skipped correction, use original SRT (EXACT naming as original)
            final_srt_file = os.path.join(workspace, f"{base_name}.srt")
            # Rename initial file to final name (EXACT as original)
            try:
                if os.path.exists(initial_srt_file):
                    os.rename(initial_srt_file, final_srt_file)
            except:
                final_srt_file = initial_srt_file
            
            return True, final_srt_file
            
        except Exception as e:
            safe_print(f"Skip correction error: {str(e)}")
            return False, ""
    
    def burn_subtitles_final_step_exact(self, combined_video: str, final_srt_file: str, base_name: str, workspace: str) -> Tuple[bool, str]:
        """
        EXACT Step 4: Burn subtitles into combined video like original GUI
        Returns: (success, final_output_path)
        """
        try:
            safe_print("Step 4/4: Burning subtitles into combined video...")
            
            # Create final output (EXACT naming as original)
            final_output = os.path.join(workspace, f"{base_name}_with_subtitles.mp4")
            success = self.burn_subtitles(combined_video, final_srt_file, final_output)
            
            if success:
                # Cleanup intermediate combined video (keep the one with subtitles) - EXACT as original
                try:
                    if os.path.exists(combined_video):
                        os.remove(combined_video)
                except:
                    pass
                
                return True, final_output
            else:
                # Even if subtitle burning failed, we have the combined video and SRT
                return False, combined_video
                
        except Exception as e:
            safe_print(f"Final step error: {str(e)}")
            return False, ""

    def correct_srt_with_advanced_matching(self, srt_path: str, original_transcript: str, output_path: str, similarity_threshold: float = 0.40) -> float:
        """Advanced SRT correction with improved character boundary matching - EXACT from original GUI"""
        
        # Extract dialogue only from original transcript
        original_dialogue = extract_dialogue_from_original(original_transcript)
        
        # Parse SRT file
        subtitles = parse_srt_file(srt_path)
        
        safe_print(f"Correcting {len(subtitles)} subtitle entries")
        safe_print(f"Original dialogue length: {len(original_dialogue)} characters")
        
        corrected_subtitles = []
        original_position = 0
        
        for i, subtitle in enumerate(subtitles):
            srt_text = subtitle['text']
            srt_clean = clean_text_for_comparison(srt_text)
            base_char_count = len(srt_clean)
            
            if original_position >= len(original_dialogue) or base_char_count == 0:
                corrected_subtitles.append(subtitle)
                continue
            
            # Get a larger segment for advanced matching
            search_buffer = max(30, base_char_count + 20)
            max_segment_end = min(original_position + search_buffer, len(original_dialogue))
            original_segment = original_dialogue[original_position:max_segment_end]
            
            # Advanced character boundary matching
            actual_end_pos, matched_segment, matched_clean = find_last_character_match_advanced(
                srt_clean, original_segment, base_char_count
            )
            
            # Calculate similarity with bonuses
            similarity = similarity_ratio(srt_clean, matched_clean)
            bonus_score = 0
            
            if len(matched_clean) > 0 and len(srt_clean) > 0:
                length_ratio = min(len(matched_clean), len(srt_clean)) / max(len(matched_clean), len(srt_clean))
                if length_ratio > 0.8:
                    bonus_score += 0.15
                
                matching_chars = sum(1 for a, b in zip(srt_clean, matched_clean) if a == b)
                char_overlap_ratio = matching_chars / max(len(srt_clean), len(matched_clean))
                bonus_score += char_overlap_ratio * 0.20
            
            final_score = similarity + bonus_score
            
            # Decision logic
            should_replace = (final_score >= similarity_threshold or 
                            (similarity >= 0.30 and bonus_score >= 0.20) or
                            (len(matched_clean) > 5 and similarity >= 0.25))
            
            if should_replace:
                corrected_subtitles.append({
                    'index': subtitle['index'],
                    'timestamp': subtitle['timestamp'],
                    'text': matched_segment
                })
                original_position += actual_end_pos
            else:
                corrected_subtitles.append(subtitle)
                advance_amount = min(base_char_count, len(original_dialogue) - original_position)
                original_position += max(1, advance_amount // 2)
        
        # Write corrected SRT file
        with open(output_path, 'w', encoding='utf-8') as f:
            for subtitle in corrected_subtitles:
                f.write(f"{subtitle['index']}\n")
                f.write(f"{subtitle['timestamp']}\n")
                f.write(f"{subtitle['text']}\n\n")
        
        # Calculate correction statistics
        replaced_count = sum(1 for i, sub in enumerate(corrected_subtitles) if sub['text'] != subtitles[i]['text'])
        correction_percentage = (replaced_count/len(subtitles)*100) if subtitles else 0
        
        safe_print(f"SRT Correction complete: {replaced_count}/{len(subtitles)} subtitles corrected ({correction_percentage:.1f}%)")
        return correction_percentage
    
    def parse_srt(self, srt_content: str) -> List[dict]:
        """Parse SRT content into segments"""
        segments = []
        blocks = srt_content.strip().split('\n\n')
        
        for block in blocks:
            if not block.strip():
                continue
                
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                segment = {
                    'index': int(lines[0]),
                    'time': lines[1],
                    'text': '\n'.join(lines[2:])
                }
                segments.append(segment)
        
        return segments
    
    def align_srt_with_transcript(self, srt_segments: List[dict], original_transcript: str) -> List[dict]:
        """
        CORE CORRECTION LOGIC: Align SRT segments with original transcript
        This corrects the ~80% accuracy issue by matching with original text
        """
        safe_print("Applying correction algorithm...")
        
        try:
            # Split original transcript into sentences/phrases
            transcript_lines = [line.strip() for line in original_transcript.split('\n') if line.strip()]
            
            # Simple alignment - match SRT segments to transcript lines
            corrected_segments = []
            
            for i, segment in enumerate(srt_segments):
                if i < len(transcript_lines):
                    # Replace AI-generated text with original transcript text
                    segment['text'] = transcript_lines[i]
                    # Safe print without Unicode characters
                    safe_print(f"Corrected segment {i+1}")
                
                corrected_segments.append(segment)
            
            safe_print(f"Corrected {len(corrected_segments)} segments")
            return corrected_segments
            
        except UnicodeError as e:
            safe_print(f"Unicode encoding issue during correction: {str(e)}")
            # Return original segments if correction fails
            return srt_segments
    
    def generate_corrected_srt(self, segments: List[dict]) -> str:
        """Generate corrected SRT content"""
        srt_content = ""
        for segment in segments:
            srt_content += f"{segment['index']}\n"
            srt_content += f"{segment['time']}\n" 
            srt_content += f"{segment['text']}\n\n"
        return srt_content
    
    def burn_corrected_subtitles(self, video_file: str, corrected_srt_file: str) -> Tuple[bool, str]:
        """
        Final step: Burn the corrected SRT into video
        """
        try:
            base_name = os.path.splitext(video_file)[0]
            final_video = f"{base_name}_with_subtitles.mp4"
            
            print("Starting subtitle burning with corrected SRT...")
            success = self.burn_subtitles(video_file, corrected_srt_file, final_video)
            
            if success:
                print("Complete workflow finished successfully!")
                return True, final_video
            else:
                print("Subtitle burning failed")
                return False, ""
                
        except Exception as e:
            print(f"Error in final burning step: {str(e)}")
            return False, ""

    def cleanup(self):
        """Clean up resources"""
        if self.model:
            del self.model
            self.model = None
            self.current_model_size = None
            print("Model resources cleaned up")