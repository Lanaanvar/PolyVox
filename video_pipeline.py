#!/usr/bin/env python3
"""
Video-to-Voice Cloning with Integrated Services
Uses existing voice-clone.py with additional video processing
"""

import os
import sys
import logging
import subprocess
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_ffmpeg():
    """Check if FFmpeg is available"""
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


def extract_audio_simple(
    video_path: str, output_path: str = "extracted_audio.wav"
) -> bool:
    """
    Simple audio extraction using FFmpeg

    Args:
        video_path: Path to input video
        output_path: Path to output audio file

    Returns:
        True if successful, False otherwise
    """
    try:
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return False

        print(f"[INFO] Extracting audio from: {video_path}")

        # Use FFmpeg to extract audio
        cmd = [
            "ffmpeg",
            "-i",
            video_path,
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "22050",
            "-y",  # Overwrite output file
            output_path,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"[✅] Audio extracted: {output_path} ({file_size} bytes)")
            return True
        else:
            print(f"❌ Audio extraction failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"❌ Audio extraction error: {e}")
        return False


def transcribe_with_whisper(audio_path: str) -> dict:
    """
    Transcribe audio using Whisper

    Args:
        audio_path: Path to audio file

    Returns:
        Dictionary with transcription results
    """
    try:
        import whisper

        print(f"[INFO] Loading Whisper model...")
        model = whisper.load_model("base")

        print(f"[INFO] Transcribing audio: {audio_path}")
        result = model.transcribe(audio_path)

        text = result["text"].strip()
        language = result.get("language", "unknown")

        print(f"[✅] Transcription completed")
        print(f"[INFO] Detected language: {language}")
        print(f"[INFO] Text: {text}")

        return {"success": True, "text": text, "language": language}

    except ImportError:
        print("❌ Whisper not installed. Install with: pip install openai-whisper")
        return {"success": False, "error": "Whisper not installed"}
    except Exception as e:
        print(f"❌ Transcription failed: {e}")
        return {"success": False, "error": str(e)}


def run_video_to_voice_pipeline(
    video_path: str,
    reference_audio: str = "reference_audio.wav",
    target_language: str = "en",
    output_name: str = "video_cloned_speech.wav",
):
    """
    Complete pipeline from video to voice cloning

    Args:
        video_path: Path to input video
        reference_audio: Path to reference audio for voice cloning
        target_language: Target language for translation
        output_name: Output filename
    """
    print("🎬 VIDEO-TO-VOICE CLONING PIPELINE")
    print("=" * 50)

    # Check dependencies
    if not check_ffmpeg():
        print("❌ FFmpeg not found. Please install FFmpeg first.")
        return

    # Check if reference audio exists
    if not os.path.exists(reference_audio):
        print(f"❌ Reference audio not found: {reference_audio}")
        return

    # Step 1: Extract audio from video
    print(f"\n📹 Step 1: Extracting audio from video...")
    extracted_audio = "temp_extracted_audio.wav"

    if not extract_audio_simple(video_path, extracted_audio):
        print("❌ Audio extraction failed")
        return

    # Step 2: Transcribe audio (optional - if you want to use the original video's audio content)
    print(f"\n🎤 Step 2: Transcribing audio to text...")
    transcription = transcribe_with_whisper(extracted_audio)

    if not transcription["success"]:
        print("❌ Transcription failed, using manual text input")
        text_to_clone = input("📝 Enter text to clone: ").strip()
        if not text_to_clone:
            print("❌ No text provided")
            return
        source_language = "auto"
    else:
        text_to_clone = transcription["text"]
        source_language = transcription["language"]

    # Step 3: Translation (if needed)
    print(f"\n🌍 Step 3: Translation...")

    # Check if translation is needed
    if target_language != source_language:
        print(f"[INFO] Translating from {source_language} to {target_language}")
        try:
            from googletrans import Translator

            translator = Translator()

            translation_result = translator.translate(
                text_to_clone, src=source_language, dest=target_language
            )
            translated_text = translation_result.text

            print(f"[INFO] Original: {text_to_clone}")
            print(f"[INFO] Translated: {translated_text}")

            final_text = translated_text
            was_translated = True

        except Exception as e:
            print(f"[WARNING] Translation failed: {e}. Using original text.")
            final_text = text_to_clone
            was_translated = False
    else:
        print(f"[INFO] No translation needed - languages match")
        final_text = text_to_clone
        was_translated = False

    # Step 4: Voice cloning
    print(f"\n🗣️ Step 4: Voice cloning...")

    try:
        from TTS.api import TTS

        print("[INFO] Loading Coqui TTS model (voice cloning)...")
        tts = TTS(
            model_name="tts_models/en/multi-dataset/tortoise-v2",
            progress_bar=True,
            gpu=False,
        )

        print("[INFO] Generating cloned speech...")
        tts.tts_to_file(
            text=final_text, speaker_wav=reference_audio, file_path=output_name
        )

        # Create result similar to voice-clone.py format
        result = {
            "success": True,
            "original_text": text_to_clone,
            "final_text": final_text,
            "output_path": output_name,
            "was_translated": was_translated,
            "translation_result": None,
        }

        if result["success"]:
            print(f"\n✅ PIPELINE COMPLETED SUCCESSFULLY!")
            print(f"📁 Original video: {video_path}")
            print(f"📄 Transcribed text: {result['original_text']}")
            if result["was_translated"]:
                print(f"📄 Translated text: {result['final_text']}")
            print(f"🎵 Final cloned speech: {result['output_path']}")

            # Clean up temporary file
            if os.path.exists(extracted_audio):
                os.remove(extracted_audio)

        else:
            print(f"❌ Voice cloning failed: {result['error']}")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure TTS and googletrans are installed:")
        print("pip install TTS torch googletrans==4.0.0rc1")
    except Exception as e:
        print(f"❌ Voice cloning error: {e}")


def main():
    """Main function"""
    print("🚀 Video-to-Voice Cloning Pipeline")
    print("=" * 50)

    # Example usage
    video_path = input("📹 Enter video file path: ").strip()

    if not video_path:
        # Use default example paths for testing
        example_videos = ["test_video.mp4", "sample.mp4", "input.mp4"]

        for example in example_videos:
            if os.path.exists(example):
                video_path = example
                print(f"Using example video: {video_path}")
                break

        if not video_path:
            print("❌ No video file specified")
            return

    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return

    # Check reference audio
    reference_audio = "reference_audio.wav"
    if not os.path.exists(reference_audio):
        ref_input = input("🎤 Enter reference audio path: ").strip()
        if ref_input and os.path.exists(ref_input):
            reference_audio = ref_input
        else:
            print("❌ Reference audio is required")
            return

    # Get target language
    target_language = input(
        "🌍 Target language (en/fr/es/de/etc.) [default: en]: "
    ).strip()
    if not target_language:
        target_language = "en"

    # Run pipeline
    run_video_to_voice_pipeline(
        video_path=video_path,
        reference_audio=reference_audio,
        target_language=target_language,
        output_name="video_cloned_speech.wav",
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        logger.error(f"Pipeline error: {e}")
