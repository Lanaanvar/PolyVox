#!/usr/bin/env python3
"""
Example usage of the complete video-to-voice cloning workflow

This demonstrates the workflow:
Video MP4 input → Audio extraction → Transcription → Translation → TTS+Voice cloning
"""

import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), "app"))

from app.services.voice_clone import complete_video_to_voice_workflow


def main():
    """Example usage of the complete workflow"""

    # Example 1: Basic workflow with default settings
    print("Example 1: Basic video-to-voice cloning workflow")
    print("=" * 50)

    video_path = "test_clip.mp4"  # Your input video file
    reference_audio = "reference_audio.wav"  # Your reference voice audio
    output_path = "outputs/cloned_voice_output.wav"
    target_language = "en"  # Target language for translation

    # Check if files exist
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        print("   Please place your MP4 video file in the current directory")
        return

    if not os.path.exists(reference_audio):
        print(f"❌ Reference audio not found: {reference_audio}")
        print("   Please place your reference audio file in the current directory")
        return

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # Run the complete workflow
    result = complete_video_to_voice_workflow(
        video_path=video_path,
        reference_audio_path=reference_audio,
        target_language=target_language,
        output_path=output_path,
        cleanup_temp_files=True,
    )

    # Display results
    if result["success"]:
        print(f"\n🎉 SUCCESS! Workflow completed successfully")
        print(f"📁 Final output: {result['final_output']}")
        print(f"📄 Original text: {result['original_text']}")
        if result["was_translated"]:
            print(f"📄 Translated text: {result['final_text']}")
        print(f"🌍 Detected language: {result['detected_language']}")
        print(f"🎯 Target language: {result['target_language']}")
    else:
        print(f"\n❌ FAILED! Workflow error: {result['error']}")

    # Show detailed step results
    print(f"\n📊 Step Results:")
    for step_name, step_result in result["steps"].items():
        if step_result:
            status = "✅" if step_result.get("success", False) else "❌"
            print(f"   {status} {step_name.replace('_', ' ').title()}")
            if not step_result.get("success", True) and step_result.get("error"):
                print(f"      Error: {step_result['error']}")


def example_batch_processing():
    """Example of batch processing multiple videos"""

    print("\nExample 2: Batch processing multiple videos")
    print("=" * 50)

    videos = [
        {"path": "video1.mp4", "target_lang": "en"},
        {"path": "video2.mp4", "target_lang": "fr"},
        {"path": "video3.mp4", "target_lang": "es"},
    ]

    reference_audio = "reference_audio.wav"

    for i, video_config in enumerate(videos):
        video_path = video_config["path"]
        target_lang = video_config["target_lang"]
        output_path = f"outputs/batch_output_{i+1}_{target_lang}.wav"

        print(f"\nProcessing {video_path} → {target_lang}")

        if not os.path.exists(video_path):
            print(f"   ⚠️ Skipping: Video not found - {video_path}")
            continue

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        result = complete_video_to_voice_workflow(
            video_path=video_path,
            reference_audio_path=reference_audio,
            target_language=target_lang,
            output_path=output_path,
        )

        if result["success"]:
            print(f"   ✅ Success: {output_path}")
        else:
            print(f"   ❌ Failed: {result['error']}")


def example_custom_workflow():
    """Example with custom parameters"""

    print("\nExample 3: Custom workflow with specific settings")
    print("=" * 50)

    result = complete_video_to_voice_workflow(
        video_path="test_clip.mp4",
        reference_audio_path="reference_audio.wav",
        target_language="fr",  # French output
        output_path="outputs/french_cloned_voice.wav",
        source_language="auto",  # Auto-detect source language
        cleanup_temp_files=False,  # Keep temporary files for debugging
    )

    if result["success"]:
        print(f"✅ Custom workflow completed!")
        print(f"📁 Output: {result['final_output']}")

        # Show temp files that were kept
        if result["temp_files"]:
            print(f"🗂️ Temporary files kept:")
            for temp_file in result["temp_files"]:
                if os.path.exists(temp_file):
                    print(f"   - {temp_file}")


if __name__ == "__main__":
    print("🎬 Complete Video-to-Voice Cloning Workflow Examples")
    print("=" * 60)

    try:
        # Run basic example
        main()

        # Uncomment to run batch processing example
        # example_batch_processing()

        # Uncomment to run custom workflow example
        # example_custom_workflow()

    except KeyboardInterrupt:
        print("\n\n⏹️ Workflow interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()
