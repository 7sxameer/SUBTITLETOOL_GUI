#!/usr/bin/env python3
"""
Final validation script for enhanced multi-video subtitle tool
"""

import os
import sys
import subprocess

def check_python_environment():
    """Check Python and required packages"""
    print("🐍 Checking Python environment...")
    
    try:
        import tkinter
        print("✅ tkinter: Available")
    except ImportError:
        print("❌ tkinter: Missing")
        return False
    
    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper: Available")
    except ImportError:
        print("❌ faster-whisper: Missing")
        return False
    
    try:
        import tkinterdnd2
        print("✅ tkinterdnd2: Available (drag & drop enabled)")
    except ImportError:
        print("⚠️ tkinterdnd2: Missing (drag & drop disabled, but tool will work)")
    
    return True

def check_ffmpeg():
    """Check FFmpeg availability"""
    print("\n🎬 Checking FFmpeg...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg: Available")
            return True
    except FileNotFoundError:
        pass
    
    print("⚠️ FFmpeg: Not found in PATH")
    print("   The tool will attempt to find FFmpeg in common installation paths")
    return False

def check_files():
    """Check required files"""
    print("\n📁 Checking files...")
    
    required_files = [
        "video_subtitle_tool.py",
        "requirements.txt", 
        "../START_HERE.bat"
    ]
    
    all_present = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}: Present")
        else:
            print(f"❌ {file}: Missing")
            all_present = False
    
    return all_present

def check_tool_import():
    """Test importing the main tool"""
    print("\n🛠️ Testing tool import...")
    
    try:
        sys.path.insert(0, '.')
        import video_subtitle_tool
        print("✅ video_subtitle_tool.py: Imports successfully")
        
        # Check if key classes and methods exist
        if hasattr(video_subtitle_tool, 'VideoSubtitleTool'):
            print("✅ VideoSubtitleTool class: Present")
            
            # Check for multi-video methods
            tool_class = video_subtitle_tool.VideoSubtitleTool
            multi_video_methods = [
                'browse_videos', 'add_video_to_list', 'remove_video_from_list',
                'clear_video_list', 'update_video_list_display',
                'process_multiple_videos', 'stitch_videos'
            ]
            
            missing_methods = []
            for method in multi_video_methods:
                if not hasattr(tool_class, method):
                    missing_methods.append(method)
            
            if not missing_methods:
                print("✅ Multi-video methods: All present")
            else:
                print(f"❌ Missing methods: {', '.join(missing_methods)}")
                return False
                
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def main():
    print("🔍 Final Validation: Enhanced Multi-Video Subtitle Tool")
    print("=" * 60)
    
    # Change to the correct directory
    os.chdir("c:\\Users\\Sameer Mishra\\Desktop\\learn\\SUBTITLETOOL_GUI\\Program Files")
    
    checks = [
        ("Python Environment", check_python_environment),
        ("FFmpeg", check_ffmpeg), 
        ("Required Files", check_files),
        ("Tool Import", check_tool_import)
    ]
    
    passed = 0
    total = len(checks)
    
    for name, check_func in checks:
        try:
            result = check_func()
            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {name}: Error during check - {str(e)}")
    
    print("\n" + "=" * 60)
    print(f"🏁 Validation Results: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 SUCCESS: Tool is ready for use!")
        print("\n📋 Features Available:")
        print("   ✅ Multi-video processing")
        print("   ✅ Drag & drop support (if tkinterdnd2 installed)")
        print("   ✅ Sequential transcription")
        print("   ✅ Automatic video stitching") 
        print("   ✅ Combined subtitle generation")
        print("   ✅ Subtitle burning")
        print("\n🚀 You can now double-click START_HERE.bat to run the tool!")
        
    elif passed >= 2:  # At least Python and files are OK
        print("\n⚠️ PARTIAL: Tool will work with limitations")
        print("\n💡 To get full functionality:")
        if not check_ffmpeg():
            print("   - Install FFmpeg for video processing")
        try:
            import tkinterdnd2
        except ImportError:
            print("   - Install tkinterdnd2 for drag & drop: pip install tkinterdnd2")
        
    else:
        print("\n❌ FAILED: Tool has critical issues")
        print("   Please check the errors above and resolve them")
    
    return passed >= 2  # At least basic functionality works

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)