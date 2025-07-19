#!/usr/bin/env python3
"""
Quick test of the video-to-voice cloning workflow
"""

import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "app"))


def test_workflow():
    """Test the complete workflow with your files"""

    print("🎬 Testing Video-to-Voice Cloning Workflow")
    print("=" * 50)

    # Check if required files exist
    video_file = "test_clip.mp4"
    reference_file = "reference_audio.wav"

    print("📋 Checking required files...")

    if not os.path.exists(video_file):
        print(f"❌ Video file missing: {video_file}")
        print("   Please add your MP4 video file and name it 'test_clip.mp4'")
        return False
    else:
        print(f"✅ Video file found: {video_file}")

    if not os.path.exists(reference_file):
        print(f"❌ Reference audio missing: {reference_file}")
        print("   Please add your reference voice audio as 'reference_audio.wav'")
        return False
    else:
        print(f"✅ Reference audio found: {reference_file}")

    # Test import
    try:
        from app.services.voice_clone import complete_video_to_voice_workflow

        print("✅ Workflow function imported successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure you're running from the correct directory")
        return False

    # Test the workflow
    print("\n🚀 Running test workflow...")

    try:
        # Create output directory
        os.makedirs("outputs", exist_ok=True)

        # Run workflow
        result = complete_video_to_voice_workflow(
            video_path=video_file,
            reference_audio_path=reference_file,
            target_language="en",
            output_path="outputs/test_output.wav",
        )

        if result["success"]:
            print(f"\n🎉 TEST SUCCESSFUL!")
            print(f"✅ Output file: {result['final_output']}")
            print(f"📄 Transcribed: {result['original_text']}")
            if result.get("was_translated"):
                print(f"📄 Translated: {result['final_text']}")
            print(
                f"🌍 Language: {result.get('detected_language')} → {result.get('target_language')}"
            )
            return True
        else:
            print(f"\n❌ TEST FAILED: {result['error']}")
            return False

    except Exception as e:
        print(f"\n❌ TEST ERROR: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🧪 Quick Workflow Test")
    print("This will test your setup and run a sample workflow")
    print()

    if test_workflow():
        print("\n✅ Your setup is working perfectly!")
        print("You can now use any of the methods to run the full application.")
    else:
        print("\n❌ Setup needs attention. Please check the messages above.")

    input("\nPress Enter to exit...")
