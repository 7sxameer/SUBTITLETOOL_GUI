#!/usr/bin/env python3
"""
Video Subtitle Tool - Professional Modern GUI Application
Double-click to run! Creates workspace folder and processes videos.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import threading
import time
from faster_whisper import WhisperModel
import subprocess

class VideoSubtitleTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Subtitle Tool")
        self.root.geometry("800x650")  # Reduced height
        self.root.resizable(True, True)
        
        # Modern color scheme
        self.colors = {
            'primary': '#2563eb',      # Blue
            'primary_dark': '#1d4ed8', # Darker blue
            'secondary': '#64748b',    # Gray
            'success': '#059669',      # Green
            'warning': '#d97706',      # Orange
            'error': '#dc2626',        # Red
            'background': '#f8fafc',   # Light gray
            'surface': '#ffffff',      # White
            'text_primary': '#1e293b', # Dark gray
            'text_secondary': '#64748b' # Medium gray
        }
        
        # Configure root window
        self.root.configure(bg=self.colors['background'])
        
        # Configuration file path
        self.config_file = "tool_config.json"
        
        # Variables
        self.workspace_folder = tk.StringVar()
        self.video_file = tk.StringVar()
        self.model_choice = tk.StringVar(value="small")
        self.processing = False
        
        # Setup modern styling
        self.setup_styles()
        
        # Load or create configuration
        self.load_config()
        
        # Setup UI first
        self.setup_ui()
        
        # Update workspace display
        self.update_workspace_display()
        
        # Check if first-time setup is needed
        if not self.workspace_folder.get() or not os.path.exists(self.workspace_folder.get()):
            self.root.after(500, self.first_time_setup)  # Delay to ensure UI is ready
    
    def setup_styles(self):
        """Setup modern TTK styles"""
        style = ttk.Style()
        
        # Configure theme
        style.theme_use('clam')  # Modern base theme
        
        # Configure styles
        style.configure('Title.TLabel', 
                       font=('Segoe UI', 24, 'bold'),
                       foreground=self.colors['primary'],
                       background=self.colors['background'])
        
        style.configure('Subtitle.TLabel', 
                       font=('Segoe UI', 12),
                       foreground=self.colors['text_secondary'],
                       background=self.colors['background'])
        
        style.configure('Heading.TLabel', 
                       font=('Segoe UI', 14, 'bold'),
                       foreground=self.colors['text_primary'],
                       background=self.colors['background'])
        
        style.configure('Body.TLabel', 
                       font=('Segoe UI', 11),
                       foreground=self.colors['text_primary'],
                       background=self.colors['background'])
        
        style.configure('Success.TLabel', 
                       font=('Segoe UI', 11),
                       foreground=self.colors['success'],
                       background=self.colors['background'])
        
        style.configure('Error.TLabel', 
                       font=('Segoe UI', 11),
                       foreground=self.colors['error'],
                       background=self.colors['background'])
        
        # Modern button styles
        style.configure('Primary.TButton',
                       font=('Segoe UI', 12, 'bold'),
                       foreground='white',
                       background=self.colors['primary'],
                       borderwidth=0,
                       focuscolor='none',
                       relief='flat')
        
        style.map('Primary.TButton',
                 background=[('active', self.colors['primary_dark']),
                           ('pressed', self.colors['primary_dark'])])
        
        style.configure('Secondary.TButton',
                       font=('Segoe UI', 10),
                       foreground=self.colors['text_primary'],
                       background=self.colors['surface'],
                       borderwidth=1,
                       focuscolor='none',
                       relief='flat')
        
        # Modern frame styles
        style.configure('Card.TFrame',
                       background=self.colors['surface'],
                       borderwidth=1,
                       relief='flat')
        
        style.configure('Main.TFrame',
                       background=self.colors['background'])
        
        # Modern labelframe style
        style.configure('Card.TLabelframe',
                       background=self.colors['surface'],
                       borderwidth=1,
                       relief='flat',
                       labeloutside=False)
        
        style.configure('Card.TLabelframe.Label',
                       font=('Segoe UI', 12, 'bold'),
                       foreground=self.colors['text_primary'],
                       background=self.colors['surface'])
        
        # Modern entry and radiobutton styles
        style.configure('Modern.TEntry',
                       fieldbackground=self.colors['surface'],
                       borderwidth=1,
                       relief='flat')
        
        style.configure('Modern.TRadiobutton',
                       font=('Segoe UI', 11),
                       foreground=self.colors['text_primary'],
                       background=self.colors['surface'],
                       focuscolor='none')
        
        # Progress bar style
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['primary'],
                       troughcolor=self.colors['background'],
                       borderwidth=0,
                       lightcolor=self.colors['primary'],
                       darkcolor=self.colors['primary'])
    
    def load_config(self):
        """Load configuration from JSON file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    self.workspace_folder.set(config.get('workspace_folder', ''))
        except Exception:
            pass
    
    def save_config(self):
        """Save configuration to JSON file"""
        try:
            config = {
                'workspace_folder': self.workspace_folder.get()
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception:
            pass
    
    def first_time_setup(self):
        """First-time setup dialog - simplified"""
        result = messagebox.askyesno(
            "Welcome to Video Subtitle Tool", 
            "🎬 Welcome to Video Subtitle Tool!\n\n"
            "This tool creates subtitles for your videos using AI.\n\n"
            "First, you need to set up a workspace folder where your\n"
            "subtitle files and processed videos will be saved.\n\n"
            "Would you like to set up your workspace now?"
        )
        
        if result:
            self.setup_workspace()
        else:
            messagebox.showinfo("Setup Later", "You can set up your workspace anytime using the 'Set Up Workspace' button.")
    
    def setup_ui(self):
        """Setup modern professional UI with scrollable content"""
        # Create canvas for scrolling if needed
        canvas = tk.Canvas(self.root, bg=self.colors['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Main.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Main container with padding
        main_container = ttk.Frame(scrollable_frame, style='Main.TFrame')
        main_container.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Header section
        header_frame = ttk.Frame(main_container, style='Main.TFrame')
        header_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Title with icon
        title_frame = ttk.Frame(header_frame, style='Main.TFrame')
        title_frame.pack(fill=tk.X)
        
        ttk.Label(title_frame, text="🎬", font=('Segoe UI', 32)).pack(side=tk.LEFT, padx=(0, 15))
        
        title_text_frame = ttk.Frame(title_frame, style='Main.TFrame')
        title_text_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(title_text_frame, text="Video Subtitle Tool", 
                 style='Title.TLabel').pack(anchor=tk.W)
        ttk.Label(title_text_frame, text="AI-powered subtitle generation with professional results", 
                 style='Subtitle.TLabel').pack(anchor=tk.W)
        
        # Content area with cards
        content_frame = ttk.Frame(main_container, style='Main.TFrame')
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Workspace card
        workspace_card = ttk.LabelFrame(content_frame, text="  📁 Workspace Configuration  ", 
                                      style='Card.TLabelframe', padding=20)
        workspace_card.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(workspace_card, text="Output Directory", style='Body.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.workspace_display = ttk.Label(workspace_card, text="Not configured", 
                                         style='Error.TLabel')
        self.workspace_display.pack(anchor=tk.W, pady=(0, 15))
        
        workspace_btn_frame = ttk.Frame(workspace_card, style='Card.TFrame')
        workspace_btn_frame.pack(fill=tk.X)
        
        ttk.Button(workspace_btn_frame, text="📁 Configure Workspace", 
                  command=self.setup_workspace, style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Video selection card
        video_card = ttk.LabelFrame(content_frame, text="  🎥 Video Selection  ", 
                                  style='Card.TLabelframe', padding=20)
        video_card.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(video_card, text="Select Video File", style='Body.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        video_input_frame = ttk.Frame(video_card, style='Card.TFrame')
        video_input_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.video_entry = ttk.Entry(video_input_frame, textvariable=self.video_file, 
                                   style='Modern.TEntry', font=('Segoe UI', 11))
        self.video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 15))
        
        ttk.Button(video_input_frame, text="Browse Files", 
                  command=self.browse_video, style='Secondary.TButton').pack(side=tk.RIGHT)
        
        # Model selection card - make it more compact
        model_card = ttk.LabelFrame(content_frame, text="  🤖 AI Model Configuration  ", 
                                  style='Card.TLabelframe', padding=15)
        model_card.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(model_card, text="Choose AI Model", style='Body.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        models_frame = ttk.Frame(model_card, style='Card.TFrame')
        models_frame.pack(fill=tk.X)
        
        models = [
            ("tiny", "Tiny", "Fastest (39MB)"),
            ("base", "Base", "Balanced (74MB)"),
            ("small", "Small", "RECOMMENDED (244MB)"),
            ("medium", "Medium", "High accuracy (769MB)"),
            ("large-v3", "Large-v3", "Maximum accuracy (3GB)")
        ]
        
        for i, (value, name, desc) in enumerate(models):
            model_frame = ttk.Frame(models_frame, style='Card.TFrame')
            model_frame.pack(fill=tk.X, pady=2)
            
            rb = ttk.Radiobutton(model_frame, text=f"{name} - {desc}", variable=self.model_choice, 
                               value=value, style='Modern.TRadiobutton')
            rb.pack(side=tk.LEFT)
            
            # Highlight recommended option with a separate label
            if value == "small":
                highlight_label = ttk.Label(model_frame, text=" ⭐ RECOMMENDED", 
                                          style='Success.TLabel')
                highlight_label.pack(side=tk.LEFT, padx=(5, 0))
        
        # Processing section
        processing_card = ttk.LabelFrame(content_frame, text="  🚀 Processing  ", 
                                       style='Card.TLabelframe', padding=20)
        processing_card.pack(fill=tk.X, pady=(0, 20))
        
        # Process button - make it prominent
        self.process_btn = ttk.Button(processing_card, text="🚀 Generate Subtitles", 
                                     command=self.start_processing, style='Primary.TButton')
        self.process_btn.pack(pady=(10, 20))
        
        # Progress section in the same card
        ttk.Label(processing_card, text="Progress", style='Body.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.progress = ttk.Progressbar(processing_card, mode='indeterminate', 
                                      style='Modern.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(processing_card, text="Ready to process videos", 
                                     style='Body.TLabel')
        self.status_label.pack(anchor=tk.W)
        
        # Configure grid weights for responsiveness
        main_container.columnconfigure(0, weight=1)
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    def update_workspace_display(self):
        """Update the workspace display label with modern styling"""
        workspace = self.workspace_folder.get()
        if workspace and os.path.exists(workspace):
            self.workspace_display.configure(text=workspace, style='Success.TLabel')
        else:
            self.workspace_display.configure(text="Not configured - please set up workspace", 
                                           style='Error.TLabel')
    
    def setup_workspace(self):
        """Setup or change workspace folder with confirmation"""
        # First show explanation
        result = messagebox.askokcancel(
            "Set Up Workspace", 
            "🎬 Video Subtitle Tool Workspace Setup\n\n"
            "This will create a folder called 'VideoSubtitleTool' where:\n"
            "• Your subtitle files (.srt) will be saved\n"
            "• Your processed videos will be saved\n\n"
            "Choose a location (like Desktop, Documents, etc.) and\n"
            "the tool will create the workspace folder there.\n\n"
            "Click OK to choose the location."
        )
        
        if not result:
            return
            
        folder = filedialog.askdirectory(title="Choose Where to Create Workspace Folder")
        if folder:
            # Create a subfolder for the tool
            tool_folder = os.path.join(folder, "VideoSubtitleTool")
            try:
                os.makedirs(tool_folder, exist_ok=True)
                self.workspace_folder.set(tool_folder)
                self.save_config()
                self.update_workspace_display()
                
                # Show success with option to open folder
                result = messagebox.askyesno("Workspace Created!", 
                    f"✅ Workspace set up successfully!\n\n"
                    f"📁 Location: {tool_folder}\n\n"
                    f"Your subtitle files and videos will be saved here.\n\n"
                    f"Would you like to open the folder to see it?")
                
                if result:
                    os.startfile(tool_folder)
                    
            except Exception as e:
                messagebox.showerror("Error", f"Cannot create folder: {str(e)}")
    
    def change_workspace(self):
        """Change workspace folder (same as setup_workspace)"""
        self.setup_workspace()
    
    def browse_video(self):
        """Browse for video file"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=filetypes
        )
        if filename:
            self.video_file.set(filename)
    
    def start_processing(self):
        """Start processing in background thread"""
        if self.processing:
            return
        
        video_file = self.video_file.get().strip()
        workspace = self.workspace_folder.get().strip()
        
        if not video_file or not os.path.exists(video_file):
            messagebox.showerror("Error", "Please select a valid video file!")
            return
        
        if not workspace or not os.path.exists(workspace):
            messagebox.showerror("Error", "Workspace folder not found! Please change workspace.")
            return
        
        self.processing = True
        self.process_btn.config(text="⏳ Processing...", state="disabled")
        self.progress.start(10)
        self.status_label.config(text="Processing video...")
        
        # Start processing in background
        thread = threading.Thread(target=self.process_video, daemon=True)
        thread.start()
    
    def process_video(self):
        """Process video in background thread"""
        try:
            video_file = self.video_file.get().strip()
            workspace = self.workspace_folder.get().strip()
            model_size = self.model_choice.get()
            
            # Generate output paths
            base_name = os.path.splitext(os.path.basename(video_file))[0]
            srt_file = os.path.join(workspace, f"{base_name}.srt")
            output_video = os.path.join(workspace, f"{base_name}_with_subtitles.mp4")
            
            self.update_status("Loading AI model...")
            
            # Load model
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            
            self.update_status("Transcribing video...")
            
            # Transcribe
            segments, info = model.transcribe(video_file, beam_size=5)
            segments_list = list(segments)
            
            self.update_status("Creating subtitle file...")
            
            # Generate SRT
            self.generate_srt(segments_list, srt_file)
            
            self.update_status("Burning subtitles into video...")
            
            # Burn subtitles
            success = self.burn_subtitles(video_file, srt_file, output_video)
            
            if success:
                self.root.after(0, lambda: self.processing_complete(srt_file, output_video, workspace))
            else:
                raise Exception("Failed to burn subtitles")
                
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.processing_failed(error_msg))
    
    def update_status(self, message):
        """Update status label from background thread with modern styling"""
        self.root.after(0, lambda: self.status_label.configure(text=message))
    
    def processing_complete(self, srt_file, output_video, workspace):
        """Called when processing completes successfully with modern styling"""
        self.processing = False
        self.process_btn.config(text="🚀 Generate Subtitles", state="normal")
        self.progress.stop()
        self.status_label.configure(text="✅ Processing completed successfully!")
        
        success_msg = f"🎉 Video processing completed successfully!\n\n📝 Subtitle file: {os.path.basename(srt_file)}\n🎬 Video with subtitles: {os.path.basename(output_video)}\n\n📁 Saved in: {workspace}\n\nWould you like to open the folder to view your files?"
        
        result = messagebox.askyesno("Success!", success_msg)
        if result:
            os.startfile(workspace)
    
    def processing_failed(self, error_msg):
        """Called when processing fails - show detailed error with modern styling"""
        self.processing = False
        self.process_btn.config(text="🚀 Generate Subtitles", state="normal")
        self.progress.stop()
        self.status_label.configure(text="❌ Processing failed")
        
        # Show detailed error with suggestions
        detailed_msg = f"Processing failed with error:\n\n{error_msg}\n\n"
        
        if "FFmpeg" in error_msg:
            detailed_msg += "💡 Suggestions:\n• Make sure FFmpeg is installed\n• Try a video file with a simpler path (no commas or special characters)\n• Check if the video file is not corrupted"
        elif "subtitles" in error_msg.lower():
            detailed_msg += "💡 Suggestions:\n• The SRT file was created successfully\n• The issue is with burning subtitles into video\n• Try moving your video to a folder with a simple name (like C:\\Videos\\)\n• Avoid file paths with commas, apostrophes, or special characters"
        
        messagebox.showerror("Processing Failed", detailed_msg)
    
    def format_time_srt(self, seconds):
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = seconds % 60
        milliseconds = int((seconds - int(seconds)) * 1000)
        seconds = int(seconds)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def generate_srt(self, segments, output_file):
        """Generate SRT subtitle file"""
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, segment in enumerate(segments, 1):
                f.write(f"{i}\n")
                f.write(f"{self.format_time_srt(segment.start)} --> {self.format_time_srt(segment.end)}\n")
                f.write(f"{segment.text.strip()}\n\n")
    
    def find_ffmpeg(self):
        """Find FFmpeg executable"""
        username = os.environ.get('USERNAME', '')
        ffmpeg_paths = [
            'ffmpeg',
            rf'C:\Users\{username}\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-8.0-full_build\bin\ffmpeg.exe',
            r'C:\ffmpeg\bin\ffmpeg.exe',
            r'C:\Program Files\ffmpeg\bin\ffmpeg.exe',
            rf'C:\Users\{username}\scoop\apps\ffmpeg\current\bin\ffmpeg.exe',
            r'C:\ProgramData\chocolatey\lib\ffmpeg\tools\ffmpeg\bin\ffmpeg.exe'
        ]
        
        for path in ffmpeg_paths:
            try:
                result = subprocess.run([path, '-version'], capture_output=True, text=True)
                if result.returncode == 0:
                    return path
            except:
                continue
        return None
    
    def burn_subtitles(self, video_file, subtitle_file, output_file):
        """Burn subtitles with high quality settings - fixed corruption issue"""
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
                self.update_status(f"Attempting subtitle burn method {i}/3...")
                
                if subtitle_approach == "temp_approach":
                    # Method 3: Copy SRT to a temp file with simple name
                    import shutil
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
                        
                        print(f"DEBUG Method {i}: Using temp file approach with stable encoding")
                        print(f"DEBUG Settings: CRF 18, medium preset, yuv420p pixel format")
                        
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
                        print(f"Method {i} temp approach failed: {str(temp_error)}")
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
                    
                    print(f"DEBUG Method {i}: {subtitle_approach[:50]}...")
                    
                    result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode == 0:
                    print(f"SUCCESS with method {i} - using stable encoding settings")
                    return True
                else:
                    print(f"Method {i} failed: {result.stderr[:300]}...")
                    continue
            
            # If all methods failed, raise detailed error
            raise Exception(f"All subtitle burning methods failed. The SRT file was created successfully, but video encoding failed. Try moving your video to a folder with a simple name like C:\\Videos\\ and avoid spaces or special characters in the filename.")
            
        except Exception as e:
            print(f"Burn subtitles error: {str(e)}")
            raise e

def main():
    root = tk.Tk()
    app = VideoSubtitleTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()