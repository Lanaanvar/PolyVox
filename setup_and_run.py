#!/usr/bin/env python3
"""
Setup and Run Voice Cloning Application
Simple script to install dependencies and run the voice cloning app
"""

import os
import sys
import subprocess
import logging


def install_dependencies():
    """Install required dependencies"""
    print("🔧 Installing dependencies...")

    # Core dependencies
    dependencies = [
        "TTS>=0.17.0",
        "torch>=1.13.0",
        "torchaudio>=0.13.0",
        "googletrans==4.0.0rc1",
        "numpy>=1.24.0",
        "requests>=2.31.0",
    ]

    try:
        for dep in dependencies:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

        print("✅ All dependencies installed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False


def check_reference_audio():
    """Check if reference audio exists"""
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
    print("   1. Record a 10-30 second audio clip of the target voice")
    print("   2. Save it as 'reference_audio.wav' in this directory")
    print("   3. Supported formats: .wav, .mp3, .m4a")
    return None


def run_application():
    """Run the voice cloning application"""
    print(" Starting Voice Cloning Application...")

    try:
        # Check if the main app file exists
        if not os.path.exists("voice_clone_app.py"):
            print(" voice_clone_app.py not found!")
            return False

        # Run the application
        subprocess.run([sys.executable, "voice_clone_app.py"])
        return True

    except Exception as e:
        print(f" Error running application: {e}")
        return False


def main():
    """Main function"""
    print(" Voice Cloning Application Setup")
    print("=" * 50)

    # Ask user what to do
    print("\nChoose an option:")
    print("1. Install dependencies and run application")
    print("2. Run application only")
    print("3. Install dependencies only")
    print("4. Exit")

    choice = input("\nEnter your choice (1-4): ").strip()

    if choice == "1":
        # Install dependencies and run
        if install_dependencies():
            if check_reference_audio():
                run_application()
            else:
                print(" Cannot run without reference audio")
        else:
            print(" Cannot continue without dependencies")

    elif choice == "2":
        # Run only
        if check_reference_audio():
            run_application()
        else:
            print(" Cannot run without reference audio")

    elif choice == "3":
        # Install only
        install_dependencies()

    elif choice == "4":
        print(" Goodbye!")
        return

    else:
        print(" Invalid choice")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n Application interrupted by user")
    except Exception as e:
        print(f"\n Setup error: {e}")
        logging.error(f"Setup error: {e}")
