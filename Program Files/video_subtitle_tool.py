#!/usr/bin/env python3
"""
Video Subtitle Tool - Professional Modern GUI Application
Double-click to run! Creates workspace folder and processes videos.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import threading
import time
from faster_whisper import WhisperModel
import subprocess
import re
from difflib import SequenceMatcher

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DRAG_DROP_AVAILABLE = True
except ImportError:
    DRAG_DROP_AVAILABLE = False
    DND_FILES = None
    TkinterDnD = None

# SRT Correction Functions (from srt_corrector_v4.py)
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

class VideoSubtitleTool:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Subtitle Tool - Multi-Video Processing")
        self.root.geometry("900x750")  # Increased for multi-video UI
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
        self.video_list = []  # List of video files to process
        self.current_video_index = 0
        self.total_duration = 0  # Total duration for combined SRT timing
        
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
        
        # Video selection card - Multi-video support
        video_card = ttk.LabelFrame(content_frame, text="  🎥 Video Selection (Multi-Video Support)  ", 
                                  style='Card.TLabelframe', padding=20)
        video_card.pack(fill=tk.BOTH, expand=True, pady=(0, 20))
        
        # Instructions
        ttk.Label(video_card, text="Add videos to process (New workflow: Stitch → Transcribe → Correct → Burn)", 
                 style='Body.TLabel').pack(anchor=tk.W, pady=(0, 10))
        
        # Video list frame with scrollbar
        list_frame = ttk.Frame(video_card, style='Card.TFrame')
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        # Create video list with scrollbar
        list_canvas = tk.Canvas(list_frame, height=120, bg=self.colors['surface'])
        list_scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=list_canvas.yview)
        self.video_list_frame = ttk.Frame(list_canvas, style='Card.TFrame')
        
        self.video_list_frame.bind(
            "<Configure>",
            lambda e: list_canvas.configure(scrollregion=list_canvas.bbox("all"))
        )
        
        list_canvas.create_window((0, 0), window=self.video_list_frame, anchor="nw")
        list_canvas.configure(yscrollcommand=list_scrollbar.set)
        
        # Enable drag and drop on the canvas if available
        if DRAG_DROP_AVAILABLE and DND_FILES:
            try:
                list_canvas.drop_target_register(DND_FILES)
                list_canvas.dnd_bind('<<Drop>>', self.on_drop)
            except Exception as e:
                print(f"Drag and drop setup failed: {e}")
        else:
            # Add a note about drag and drop not being available
            note_frame = ttk.Frame(video_card, style='Card.TFrame')
            note_frame.pack(fill=tk.X, pady=(5, 0))
            ttk.Label(note_frame, text="Note: Drag & drop not available. Use 'Add Videos' button.", 
                     style='Body.TLabel').pack(anchor=tk.W)
        
        # Pack canvas and scrollbar
        list_canvas.pack(side="left", fill="both", expand=True)
        list_scrollbar.pack(side="right", fill="y")
        
        # Buttons frame
        buttons_frame = ttk.Frame(video_card, style='Card.TFrame')
        buttons_frame.pack(fill=tk.X)
        
        ttk.Button(buttons_frame, text="📁 Add Videos", 
                  command=self.browse_videos, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(buttons_frame, text="🗑️ Clear All", 
                  command=self.clear_video_list, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        
        # Video count label
        self.video_count_label = ttk.Label(buttons_frame, text="No videos selected", 
                                         style='Body.TLabel')
        self.video_count_label.pack(side=tk.RIGHT)
        
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
        self.process_btn = ttk.Button(processing_card, text="🚀 Process Videos & Generate Subtitles", 
                                     command=self.start_processing, style='Primary.TButton')
        self.process_btn.pack(pady=(10, 20))
        
        # Progress section in the same card
        ttk.Label(processing_card, text="Progress", style='Body.TLabel').pack(anchor=tk.W, pady=(0, 5))
        
        self.progress = ttk.Progressbar(processing_card, mode='indeterminate', 
                                      style='Modern.Horizontal.TProgressbar')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = ttk.Label(processing_card, text="Ready for 4-step processing: Stitch → Transcribe → Correct → Burn", 
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
        """Browse for video file - legacy single video method"""
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
    
    def browse_videos(self):
        """Browse for multiple video files"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv *.flv *.webm *.m4v"),
            ("All files", "*.*")
        ]
        filenames = filedialog.askopenfilenames(
            title="Select Video Files",
            filetypes=filetypes
        )
        if filenames:
            for filename in filenames:
                self.add_video_to_list(filename)
    
    def on_drop(self, event):
        """Handle drag and drop of video files"""
        files = self.root.tk.splitlist(event.data)
        video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm', '.m4v')
        
        for file_path in files:
            if file_path.lower().endswith(video_extensions):
                self.add_video_to_list(file_path)
    
    def add_video_to_list(self, video_path):
        """Add a video to the processing list"""
        if video_path not in [v['path'] for v in self.video_list]:
            video_info = {
                'path': video_path,
                'name': os.path.basename(video_path),
                'status': 'pending',
                'widget': None
            }
            self.video_list.append(video_info)
            self.update_video_list_display()
    
    def remove_video_from_list(self, video_path):
        """Remove a video from the processing list"""
        self.video_list = [v for v in self.video_list if v['path'] != video_path]
        self.update_video_list_display()
    
    def clear_video_list(self):
        """Clear all videos from the processing list"""
        self.video_list = []
        self.update_video_list_display()
    
    def update_video_list_display(self):
        """Update the visual display of the video list"""
        # Clear existing widgets
        for widget in self.video_list_frame.winfo_children():
            widget.destroy()
        
        if not self.video_list:
            # Show empty state
            empty_label = ttk.Label(self.video_list_frame, 
                                  text="📁 Drag & drop videos here or use 'Add Videos' button", 
                                  style='Body.TLabel')
            empty_label.pack(pady=20)
        else:
            # Show video list
            for i, video_info in enumerate(self.video_list):
                video_frame = ttk.Frame(self.video_list_frame, style='Card.TFrame')
                video_frame.pack(fill=tk.X, pady=2, padx=5)
                
                # Video name and status
                name_frame = ttk.Frame(video_frame, style='Card.TFrame')
                name_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
                
                name_label = ttk.Label(name_frame, text=f"{i+1}. {video_info['name']}", 
                                     style='Body.TLabel')
                name_label.pack(anchor=tk.W)
                
                # Status indicator
                status_colors = {
                    'pending': 'text_secondary',
                    'processing': 'warning', 
                    'completed': 'success',
                    'error': 'error'
                }
                status_text = {
                    'pending': '⏳ Waiting',
                    'processing': '🔄 Processing',
                    'completed': '✅ Done',
                    'error': '❌ Error'
                }
                
                status_label = ttk.Label(name_frame, 
                                       text=status_text.get(video_info['status'], 'Unknown'),
                                       style='Body.TLabel')
                status_label.pack(anchor=tk.W)
                
                # Remove button
                remove_btn = ttk.Button(video_frame, text="🗑️", 
                                      command=lambda path=video_info['path']: self.remove_video_from_list(path),
                                      width=3)
                remove_btn.pack(side=tk.RIGHT)
                
                video_info['widget'] = video_frame
        
        # Update count label
        count = len(self.video_list)
        self.video_count_label.configure(text=f"{count} video{'s' if count != 1 else ''} selected")
    
    def get_video_duration(self, video_path):
        """Get duration of a video file using FFmpeg"""
        try:
            ffmpeg_cmd = self.find_ffmpeg()
            if not ffmpeg_cmd:
                return 0.0
            
            cmd = [
                ffmpeg_cmd, '-i', video_path,
                '-f', 'null', '-',
                '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0'
            ]
            
            # Try ffprobe first (more reliable for duration)
            ffprobe_cmd = ffmpeg_cmd.replace('ffmpeg', 'ffprobe')
            probe_cmd = [
                ffprobe_cmd, '-v', 'quiet',
                '-show_entries', 'format=duration',
                '-of', 'csv=p=0',
                video_path
            ]
            
            try:
                result = subprocess.run(probe_cmd, capture_output=True, text=True)
                if result.returncode == 0 and result.stdout.strip():
                    return float(result.stdout.strip())
            except:
                pass
            
            # Fallback to ffmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                # Parse duration from stderr (ffmpeg outputs info there)
                for line in result.stderr.split('\n'):
                    if 'Duration:' in line:
                        duration_str = line.split('Duration:')[1].split(',')[0].strip()
                        time_parts = duration_str.split(':')
                        hours = float(time_parts[0])
                        minutes = float(time_parts[1])
                        seconds = float(time_parts[2])
                        return hours * 3600 + minutes * 60 + seconds
            
            return 0.0
        except Exception:
            return 0.0
    
    def get_transcript_input_dialog(self):
        """Show dialog to get original transcript from user"""
        dialog = tk.Toplevel(self.root)
        dialog.title("Original Transcript Input")
        dialog.geometry("600x500")
        dialog.resizable(True, True)
        dialog.configure(bg=self.colors['background'])
        
        # Center the dialog
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Main frame
        main_frame = ttk.Frame(dialog, style='Main.TFrame', padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(main_frame, text="📝 Original Transcript Correction", 
                               style='Heading.TLabel')
        title_label.pack(pady=(0, 15))
        
        # Instructions
        instructions = ttk.Label(main_frame, 
                                text="The AI transcription is approximately 80% accurate. To improve accuracy,\n"
                                     "please paste your original transcript text below.\n"
                                     "This will be used to correct the generated subtitles.",
                                style='Body.TLabel')
        instructions.pack(pady=(0, 15))
        
        # Text area
        text_frame = ttk.Frame(main_frame, style='Card.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        text_label = ttk.Label(text_frame, text="Original Transcript:", style='Body.TLabel')
        text_label.pack(anchor=tk.W, pady=(0, 5))
        
        # Scrolled text widget
        self.transcript_text = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                        width=70, height=15,
                                                        font=('Consolas', 10))
        self.transcript_text.pack(fill=tk.BOTH, expand=True)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame, style='Main.TFrame')
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Result variable
        self.transcript_result = None
        
        def on_skip():
            self.transcript_result = "skip"
            dialog.destroy()
        
        def on_submit():
            transcript_content = self.transcript_text.get(1.0, tk.END).strip()
            if not transcript_content:
                messagebox.showwarning("Empty Transcript", 
                                     "Please paste your transcript or click Skip to proceed without correction.")
                return
            self.transcript_result = transcript_content
            dialog.destroy()
        
        ttk.Button(button_frame, text="Skip Correction", 
                  command=on_skip, style='Secondary.TButton').pack(side=tk.LEFT)
        
        ttk.Button(button_frame, text="✓ Apply Correction", 
                  command=on_submit, style='Primary.TButton').pack(side=tk.RIGHT)
        
        # Wait for dialog to close
        dialog.wait_window()
        
        return self.transcript_result
    
    def correct_srt_with_advanced_matching(self, srt_path, original_transcript, output_path, similarity_threshold=0.40):
        """Advanced SRT correction with improved character boundary matching"""
        
        # Extract dialogue only from original transcript
        original_dialogue = extract_dialogue_from_original(original_transcript)
        
        # Parse SRT file
        subtitles = parse_srt_file(srt_path)
        
        print(f"Correcting {len(subtitles)} subtitle entries")
        print(f"Original dialogue length: {len(original_dialogue)} characters")
        
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
        
        print(f"SRT Correction complete: {replaced_count}/{len(subtitles)} subtitles corrected ({correction_percentage:.1f}%)")
        return correction_percentage
    
    def start_processing(self):
        """Start processing multiple videos in background thread"""
        if self.processing:
            return
        
        workspace = self.workspace_folder.get().strip()
        
        if not self.video_list:
            messagebox.showerror("Error", "Please add at least one video file!")
            return
        
        if not workspace or not os.path.exists(workspace):
            messagebox.showerror("Error", "Workspace folder not found! Please configure workspace.")
            return
        
        # Validate all videos exist
        invalid_videos = []
        for video_info in self.video_list:
            if not os.path.exists(video_info['path']):
                invalid_videos.append(video_info['name'])
        
        if invalid_videos:
            messagebox.showerror("Error", f"The following video files were not found:\n" + 
                               "\n".join(invalid_videos))
            return
        
        self.processing = True
        self.process_btn.config(text="⏳ Processing Videos (4 Steps)...", state="disabled")
        self.progress.start(10)
        self.status_label.config(text="Starting 4-step workflow: Stitch → Transcribe → Correct → Burn...")
        self.current_video_index = 0
        self.total_duration = 0
        
        # Start processing in background
        thread = threading.Thread(target=self.process_multiple_videos, daemon=True)
        thread.start()
    
    def process_multiple_videos(self):
        """Process multiple videos with new workflow: Stitch -> Transcribe -> Correct -> Burn"""
        try:
            workspace = self.workspace_folder.get().strip()
            model_size = self.model_choice.get()
            
            # Create timestamp for this batch
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            base_name = f"combined_video_{timestamp}"
            
            # Step 1: Stitch all videos together first
            self.update_status("Step 1/4: Stitching videos together...")
            combined_video = os.path.join(workspace, f"{base_name}_combined.mp4")
            
            # Update all video statuses to show stitching in progress
            for video_info in self.video_list:
                video_info['status'] = 'processing'
            self.root.after(0, self.update_video_list_display)
            
            success = self.stitch_videos([v['path'] for v in self.video_list], combined_video)
            
            if not success:
                raise Exception("Failed to stitch videos together")
            
            # Mark all videos as completed for stitching phase
            for video_info in self.video_list:
                video_info['status'] = 'completed'
            self.root.after(0, self.update_video_list_display)
            
            # Step 2: Transcribe the combined video
            self.update_status("Step 2/4: Loading AI model...")
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            
            self.update_status("Step 2/4: Transcribing combined video...")
            segments, info = model.transcribe(combined_video, beam_size=5)
            segments_list = list(segments)
            
            # Step 3: Create initial SRT file from transcription
            self.update_status("Step 2/4: Creating initial subtitle file...")
            initial_srt_file = os.path.join(workspace, f"{base_name}_initial.srt")
            self.generate_srt(segments_list, initial_srt_file)
            
            # Step 3: Get transcript correction from user
            self.update_status("Step 3/4: Waiting for transcript input...")
            
            # Show transcript input dialog on main thread
            transcript_input = None
            dialog_complete = threading.Event()
            
            def show_dialog():
                nonlocal transcript_input
                transcript_input = self.get_transcript_input_dialog()
                dialog_complete.set()
            
            self.root.after(0, show_dialog)
            dialog_complete.wait()  # Wait for dialog to complete
            
            # Process the transcript input
            if transcript_input and transcript_input != "skip":
                self.update_status("Step 3/4: Applying transcript correction...")
                
                # Create corrected SRT file
                corrected_srt_file = os.path.join(workspace, f"{base_name}.srt")
                correction_percentage = self.correct_srt_with_advanced_matching(
                    initial_srt_file, transcript_input, corrected_srt_file
                )
                
                # Use corrected SRT file
                final_srt_file = corrected_srt_file
                
                # Update status with correction info
                self.update_status(f"Step 3/4: Correction applied ({correction_percentage:.1f}% of subtitles corrected)")
                
                # Clean up initial SRT file
                try:
                    if os.path.exists(initial_srt_file):
                        os.remove(initial_srt_file)
                except:
                    pass
                    
            else:
                # User skipped correction, use original SRT
                final_srt_file = os.path.join(workspace, f"{base_name}.srt")
                # Rename initial file to final name
                try:
                    if os.path.exists(initial_srt_file):
                        os.rename(initial_srt_file, final_srt_file)
                except:
                    final_srt_file = initial_srt_file
                
                self.update_status("Step 3/4: Correction skipped, using AI-generated subtitles...")
            
            # Step 4: Burn subtitles into the combined video
            self.update_status("Step 4/4: Burning subtitles into combined video...")
            final_output = os.path.join(workspace, f"{base_name}_with_subtitles.mp4")
            success = self.burn_subtitles(combined_video, final_srt_file, final_output)
            
            if success:
                # Cleanup intermediate combined video (keep the one with subtitles)
                try:
                    if os.path.exists(combined_video):
                        os.remove(combined_video)
                except:
                    pass
                
                self.root.after(0, lambda: self.processing_complete(final_srt_file, final_output, workspace))
            else:
                # Even if subtitle burning failed, we have the combined video and SRT
                self.root.after(0, lambda: self.processing_complete(final_srt_file, combined_video, workspace, 
                                                                  subtitle_burn_failed=True))
                
        except Exception as e:
            error_msg = str(e)
            self.root.after(0, lambda: self.processing_failed(error_msg))
    
    def stitch_videos(self, video_paths, output_path):
        """Stitch multiple videos together using FFmpeg"""
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
            
            print(f"Stitching {len(video_paths)} videos...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Cleanup temp file
            try:
                os.remove(file_list_path)
            except:
                pass
            
            if result.returncode == 0:
                print("Video stitching successful")
                return True
            else:
                print(f"Video stitching failed: {result.stderr}")
                
                # Try alternative method with re-encoding
                self.update_status("Trying alternative stitching method...")
                return self.stitch_videos_reencoding(video_paths, output_path)
                
        except Exception as e:
            print(f"Stitch videos error: {str(e)}")
            return False
    
    def stitch_videos_reencoding(self, video_paths, output_path):
        """Alternative stitching method with re-encoding (slower but more compatible)"""
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
            
            print("Using re-encoding method for stitching...")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return result.returncode == 0
            
        except Exception:
            return False
            
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
    
    def processing_complete(self, srt_file, output_video, workspace, subtitle_burn_failed=False):
        """Called when processing completes successfully with modern styling"""
        self.processing = False
        self.process_btn.config(text="🚀 Process Videos & Generate Subtitles", state="normal")
        self.progress.stop()
        
        # Reset all video statuses
        for video_info in self.video_list:
            if video_info['status'] != 'error':
                video_info['status'] = 'completed'
        self.update_video_list_display()
        
        if subtitle_burn_failed:
            self.status_label.configure(text="⚠️ Processing completed with warnings")
            success_msg = f"🎬 Multi-video processing completed!\n\nWorkflow: ✅ Stitch → ✅ Transcribe → ✅ Correct → ⚠️ Burn\n\n📝 Combined subtitle file: {os.path.basename(srt_file)}\n🎥 Combined video: {os.path.basename(output_video)}\n\n⚠️ Note: Subtitle burning failed, but combined video and SRT file are ready.\nYou can use external software to add subtitles.\n\n📁 Saved in: {workspace}\n\nWould you like to open the folder to view your files?"
        else:
            self.status_label.configure(text="✅ Multi-video processing completed successfully!")
            success_msg = f"🎉 Multi-video processing completed successfully!\n\nWorkflow: ✅ Stitch → ✅ Transcribe → ✅ Correct → ✅ Burn\n\n📝 Final subtitle file: {os.path.basename(srt_file)}\n🎬 Final video with subtitles: {os.path.basename(output_video)}\n\nProcessed {len(self.video_list)} video clips with transcript correction!\n\n📁 Saved in: {workspace}\n\nWould you like to open the folder to view your files?"
        
        result = messagebox.askyesno("Success!", success_msg)
        if result:
            os.startfile(workspace)
    
    def processing_failed(self, error_msg):
        """Called when processing fails - show detailed error with modern styling"""
        self.processing = False
        self.process_btn.config(text="🚀 Process Videos & Generate Subtitles", state="normal")
        self.progress.stop()
        self.status_label.configure(text="❌ 4-step processing failed")
        
        # Reset video statuses
        for video_info in self.video_list:
            if video_info['status'] == 'processing':
                video_info['status'] = 'error'
        self.update_video_list_display()
        
        # Show detailed error with suggestions
        detailed_msg = f"4-step processing workflow failed:\n\n{error_msg}\n\n"
        
        if "stitch" in error_msg.lower():
            detailed_msg += "💡 Failed at Step 1 (Stitching):\n• Check that all video files are valid and not corrupted\n• Ensure videos have compatible formats\n• Try videos with the same resolution and frame rate\n• Check available disk space\n• Ensure FFmpeg is properly installed"
        elif "transcrib" in error_msg.lower():
            detailed_msg += "💡 Failed at Step 2 (Transcription):\n• Check if the combined video contains audio\n• Try using a smaller AI model (like 'tiny' or 'base')\n• Ensure enough system memory is available\n• Check if the video file is not corrupted"
        elif "correction" in error_msg.lower() or "dialog" in error_msg.lower():
            detailed_msg += "💡 Failed at Step 3 (Correction):\n• The transcript input dialog may have encountered an error\n• Try running the process again\n• You can skip the correction step if needed"
        elif "burn" in error_msg.lower() or "subtitle" in error_msg.lower():
            detailed_msg += "💡 Failed at Step 4 (Burning):\n• The SRT file was created successfully\n• Try using external software to add subtitles\n• Check FFmpeg installation and try simpler video paths"
        else:
            detailed_msg += "💡 General suggestions:\n• Check all input files are accessible\n• Ensure sufficient disk space\n• Try processing fewer videos at once\n• Check FFmpeg installation"
        
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
    if DRAG_DROP_AVAILABLE and TkinterDnD:
        try:
            root = TkinterDnD.Tk()
        except Exception:
            # Fallback if TkinterDnD.Tk() fails
            root = tk.Tk()
    else:
        root = tk.Tk()
        if not DRAG_DROP_AVAILABLE:
            messagebox.showinfo("Info", 
                              "Drag & drop functionality not available.\n" +
                              "Install tkinterdnd2 for drag & drop support:\n" +
                              "pip install tkinterdnd2\n\n" +
                              "You can still use the 'Add Videos' button.")
    
    app = VideoSubtitleTool(root)
    root.mainloop()

if __name__ == "__main__":
    main()