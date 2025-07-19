#!/usr/bin/env python3
"""
Run Voice Cloning Application
Simple script to run the voice cloning with translation
"""

import os
import sys
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
        )
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def check_reference_audio():
    """Check if reference audio file exists"""
    reference_files = [
        "reference_audio.wav",
        "reference_audio.mp3",
        "reference_audio.m4a",
    ]

    for ref_file in reference_files:
        if os.path.exists(ref_file):
            print(f"✅ Found reference audio: {ref_file}")
            return ref_file

    print("⚠️ No reference audio file found!")
    print("📄 Please provide a reference audio file:")
    print("   1. Record a short audio clip (10-30 seconds) of the target voice")
    print("   2. Save it as 'reference_audio.wav' in the current directory")
    print("   3. Supported formats: .wav, .mp3, .m4a")
    return None


def run_voice_cloning():
    """Run the voice cloning application"""
    # Import here to avoid import errors before dependencies are installed
    try:
        from app.services.translate import translation_service
        from app.services.voice_clone import voice_clone_service
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all dependencies are installed")
        return False

    print("🎬 Voice Cloning Application")
    print("=" * 50)

    # Check reference audio
    reference_audio = check_reference_audio()
    if not reference_audio:
        return False

    # Initialize voice cloning service
    print("🔧 Initializing voice cloning model...")
    try:
        voice_clone_service.initialize_model()
    except Exception as e:
        print(f"❌ Failed to initialize model: {e}")
        return False

    # Define texts to process
    texts_to_process = [
        {
            "text": "Hello, I am trying to clone a text into a voice",
            "translate_to": "fr",
            "output": "cloned_speech_french.wav",
            "description": "English to French",
        },
        {
            "text": "Technology is amazing and voice cloning is the future",
            "translate_to": "es",
            "output": "cloned_speech_spanish.wav",
            "description": "English to Spanish",
        },
        {
            "text": "This is a direct voice cloning without translation",
            "translate_to": None,
            "output": "cloned_speech_direct.wav",
            "description": "Direct cloning (no translation)",
        },
    ]

    successful_outputs = []

    # Process each text
    for i, item in enumerate(texts_to_process, 1):
        print(f"\n🗣️ Processing {i}/{len(texts_to_process)}: {item['description']}")
        print(f"   Text: {item['text']}")

        try:
            result = voice_clone_service.synthesize_with_cloned_voice(
                text=item["text"],
                reference_audio=reference_audio,
                output_path=item["output"],
                translate_text=item["translate_to"] is not None,
                target_language=item["translate_to"] or "en",
                source_language="auto",
            )

            if result["success"]:
                print(f"   ✅ Success: {item['output']}")
                if result["was_translated"]:
                    print(f"   📄 Translated: {result['synthesized_text']}")
                successful_outputs.append(item["output"])
            else:
                print(f"   ❌ Failed: {result['error']}")

        except Exception as e:
            print(f"   ❌ Error: {e}")

    # Summary
    print(f"\n📊 Summary:")
    print(f"   ✅ Successful: {len(successful_outputs)}")
    print(f"   ❌ Failed: {len(texts_to_process) - len(successful_outputs)}")

    if successful_outputs:
        print(f"\n🎵 Generated audio files:")
        for output in successful_outputs:
            print(f"   - {output}")
        print(f"\n🎉 Play the audio files to hear the results!")

    # Cleanup
    voice_clone_service.cleanup()

    return len(successful_outputs) > 0


def main():
    """Main function"""
    print("🚀 Voice Cloning Application Launcher")
    print("=" * 50)

    # Check if we should install dependencies
    if not os.path.exists("requirements.txt"):
        print("❌ requirements.txt not found!")
        return

    # Option to install dependencies
    install_deps = input("📦 Install/update dependencies? (y/N): ").strip().lower()
    if install_deps in ["y", "yes"]:
        if not install_dependencies():
            print("❌ Cannot continue without dependencies")
            return

    # Run the application
    try:
        success = run_voice_cloning()
        if success:
            print("\n🎉 Application completed successfully!")
        else:
            print("\n❌ Application failed")
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        logger.error(f"Application error: {e}")


if __name__ == "__main__":
    main()
