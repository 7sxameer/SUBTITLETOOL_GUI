#!/usr/bin/env python3
"""
Test script for multi-video subtitle tool functionality
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from video_subtitle_tool import VideoSubtitleTool
import tkinter as tk

def test_gui():
    """Test the GUI starts up correctly"""
    try:
        if DRAG_DROP_AVAILABLE:
            from tkinterdnd2 import TkinterDnD
            root = TkinterDnD.Tk()
        else:
            root = tk.Tk()
        
        app = VideoSubtitleTool(root)
        
        # Test adding a mock video to the list
        test_video = "test_video.mp4"
        app.add_video_to_list(test_video)
        
        print(f"✅ GUI test passed!")
        print(f"✅ Video list test passed! Added: {test_video}")
        print(f"✅ Video count: {len(app.video_list)}")
        
        # Clean up
        root.quit()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ GUI test failed: {str(e)}")
        return False

def test_video_list_operations():
    """Test video list operations without GUI"""
    try:
        # Mock root for testing
        root = tk.Tk()
        app = VideoSubtitleTool(root)
        
        # Test adding videos
        test_videos = ["video1.mp4", "video2.mp4", "video3.mp4"]
        for video in test_videos:
            app.add_video_to_list(video)
        
        assert len(app.video_list) == 3, f"Expected 3 videos, got {len(app.video_list)}"
        
        # Test removing a video
        app.remove_video_from_list("video2.mp4")
        assert len(app.video_list) == 2, f"Expected 2 videos after removal, got {len(app.video_list)}"
        
        # Test clearing all
        app.clear_video_list()
        assert len(app.video_list) == 0, f"Expected 0 videos after clear, got {len(app.video_list)}"
        
        print("✅ Video list operations test passed!")
        
        # Clean up
        root.quit()
        root.destroy()
        
        return True
        
    except Exception as e:
        print(f"❌ Video list operations test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🧪 Testing Multi-Video Subtitle Tool...")
    print("=" * 50)
    
    # Import the availability flag
    from video_subtitle_tool import DRAG_DROP_AVAILABLE
    
    print(f"📋 Drag & Drop Available: {DRAG_DROP_AVAILABLE}")
    print()
    
    tests_passed = 0
    total_tests = 2
    
    # Run tests
    if test_video_list_operations():
        tests_passed += 1
    
    if test_gui():
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"🏁 Test Results: {tests_passed}/{total_tests} passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Multi-video functionality is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")