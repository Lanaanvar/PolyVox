#!/usr/bin/env python3
"""
Complete Video-to-Voice Cloning Pipeline
Extract audio from video -> Transcribe -> Translate -> Clone Voice
"""

import os
import sys
import logging
import tempfile
from typing import Optional, Dict, Any, List

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed"""
    missing_deps = []

    try:
        import TTS
    except ImportError:
        missing_deps.append("TTS")

    try:
        from googletrans import Translator
    except ImportError:
        missing_deps.append("googletrans==4.0.0rc1")

    try:
        import whisper
    except ImportError:
        missing_deps.append("openai-whisper")

    try:
        import ffmpeg
    except ImportError:
        missing_deps.append("ffmpeg-python")

    try:
        from pydub import AudioSegment
    except ImportError:
        missing_deps.append("pydub")

    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("📦 Install with: pip install " + " ".join(missing_deps))
        return False

    return True


def extract_audio_from_video(
    video_path: str, output_path: str = "extracted_audio.wav"
) -> Dict[str, Any]:
    """
    Extract audio from video file using ffmpeg

    Args:
        video_path: Path to input video file
        output_path: Path to save extracted audio

    Returns:
        Result dictionary with success status and details
    """
    try:
        import ffmpeg

        print(f"[INFO] Extracting audio from: {video_path}")

        # Check if video file exists
        if not os.path.exists(video_path):
            return {"success": False, "error": f"Video file not found: {video_path}"}

        # Extract audio using ffmpeg
        (
            ffmpeg.input(video_path)
            .audio.output(output_path, acodec="pcm_s16le", ac=1, ar="22050")
            .overwrite_output()
            .run(quiet=True)
        )

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(
                f"[✅] Audio extracted successfully: {output_path} ({file_size} bytes)"
            )
            return {"success": True, "output_path": output_path, "file_size": file_size}
        else:
            return {
                "success": False,
                "error": "Audio extraction failed - output file not created",
            }

    except Exception as e:
        error_msg = f"Audio extraction failed: {e}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


def transcribe_audio(audio_path: str, language: str = "auto") -> Dict[str, Any]:
    """
    Transcribe audio to text using Whisper

    Args:
        audio_path: Path to audio file
        language: Language code (auto for auto-detection)

    Returns:
        Result dictionary with transcription and metadata
    """
    try:
        import whisper

        print(f"[INFO] Transcribing audio: {audio_path}")

        # Load Whisper model
        model = whisper.load_model("base")

        # Transcribe audio
        if language == "auto":
            result = model.transcribe(audio_path)
        else:
            result = model.transcribe(audio_path, language=language)

        transcribed_text = result["text"].strip()
        detected_language = result.get("language", "unknown")

        print(f"[✅] Transcription completed")
        print(f"[INFO] Detected language: {detected_language}")
        print(f"[INFO] Transcribed text: {transcribed_text}")

        return {
            "success": True,
            "text": transcribed_text,
            "detected_language": detected_language,
            "segments": result.get("segments", []),
        }

    except Exception as e:
        error_msg = f"Transcription failed: {e}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


def translate_text(
    text: str, target_language: str = "en", source_language: str = "auto"
) -> Dict[str, Any]:
    """
    Translate text using Google Translate

    Args:
        text: Text to translate
        target_language: Target language code
        source_language: Source language code

    Returns:
        Translation result dictionary
    """
    try:
        from googletrans import Translator

        if not text or not text.strip():
            return {"success": False, "error": "Empty text"}

        print(f"[INFO] Translating text from {source_language} to {target_language}")

        translator = Translator()
        result = translator.translate(text, src=source_language, dest=target_language)

        translation_result = {
            "success": True,
            "original": text,
            "translated": result.text,
            "source_language": result.src,
            "target_language": target_language,
        }

        print(f"[✅] Translation completed: {result.text}")
        return translation_result

    except Exception as e:
        error_msg = f"Translation failed: {e}"
        logger.error(error_msg)
        return {
            "success": False,
            "error": error_msg,
            "original": text,
            "translated": text,
        }


def clone_voice(
    text: str, reference_audio: str, output_path: str = "cloned_speech.wav"
) -> Dict[str, Any]:
    """
    Clone voice using TTS model

    Args:
        text: Text to synthesize
        reference_audio: Path to reference audio file
        output_path: Output file path

    Returns:
        Result dictionary
    """
    try:
        from TTS.api import TTS

        print(f"[INFO] Loading TTS model for voice cloning...")
        tts = TTS(
            model_name="tts_models/en/multi-dataset/tortoise-v2",
            progress_bar=True,
            gpu=False,
        )

        print(f"[INFO] Generating cloned speech...")
        tts.tts_to_file(text=text, speaker_wav=reference_audio, file_path=output_path)

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"[✅] Voice cloning completed: {output_path} ({file_size} bytes)")
            return {"success": True, "output_path": output_path, "file_size": file_size}
        else:
            return {
                "success": False,
                "error": "Voice cloning failed - output file not created",
            }

    except Exception as e:
        error_msg = f"Voice cloning failed: {e}"
        logger.error(error_msg)
        return {"success": False, "error": error_msg}


def complete_pipeline(
    video_path: str,
    reference_audio: str,
    target_language: str = "en",
    output_dir: str = "pipeline_output",
) -> Dict[str, Any]:
    """
    Complete pipeline from video to voice cloning

    Args:
        video_path: Path to input video file
        reference_audio: Path to reference audio for voice cloning
        target_language: Target language for translation
        output_dir: Output directory for all generated files

    Returns:
        Complete pipeline result
    """
    print("🎬 COMPLETE VIDEO-TO-VOICE CLONING PIPELINE")
    print("=" * 60)

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    pipeline_result = {
        "success": False,
        "steps": {},
        "final_output": None,
        "error": None,
    }

    try:
        # Step 1: Extract audio from video
        print(f"\n📹 Step 1: Extracting audio from video...")
        extracted_audio = os.path.join(output_dir, "extracted_audio.wav")

        extraction_result = extract_audio_from_video(video_path, extracted_audio)
        pipeline_result["steps"]["audio_extraction"] = extraction_result

        if not extraction_result["success"]:
            pipeline_result["error"] = (
                f"Audio extraction failed: {extraction_result['error']}"
            )
            return pipeline_result

        # Step 2: Transcribe audio to text
        print(f"\n🎤 Step 2: Transcribing audio to text...")

        transcription_result = transcribe_audio(extracted_audio)
        pipeline_result["steps"]["transcription"] = transcription_result

        if not transcription_result["success"]:
            pipeline_result["error"] = (
                f"Transcription failed: {transcription_result['error']}"
            )
            return pipeline_result

        transcribed_text = transcription_result["text"]
        detected_language = transcription_result["detected_language"]

        # Step 3: Translate text (if needed)
        print(f"\n🌍 Step 3: Translating text...")

        if detected_language != target_language:
            translation_result = translate_text(
                transcribed_text, target_language, detected_language
            )
            pipeline_result["steps"]["translation"] = translation_result

            if translation_result["success"]:
                final_text = translation_result["translated"]
            else:
                print(f"[WARNING] Translation failed, using original text")
                final_text = transcribed_text
        else:
            print(f"[INFO] No translation needed - detected language matches target")
            final_text = transcribed_text
            pipeline_result["steps"]["translation"] = {"success": True, "skipped": True}

        # Step 4: Clone voice
        print(f"\n🗣️ Step 4: Cloning voice...")

        cloned_output = os.path.join(output_dir, "final_cloned_speech.wav")

        cloning_result = clone_voice(
            text=final_text, reference_audio=reference_audio, output_path=cloned_output
        )
        pipeline_result["steps"]["voice_cloning"] = cloning_result

        if not cloning_result["success"]:
            pipeline_result["error"] = (
                f"Voice cloning failed: {cloning_result['error']}"
            )
            return pipeline_result

        # Pipeline completed successfully
        pipeline_result["success"] = True
        pipeline_result["final_output"] = cloned_output

        print(f"\n✅ PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"📁 Output directory: {output_dir}")
        print(f"🎵 Final cloned speech: {cloned_output}")

        return pipeline_result

    except Exception as e:
        error_msg = f"Pipeline failed: {e}"
        logger.error(error_msg)
        pipeline_result["error"] = error_msg
        return pipeline_result


def main():
    """Main function with example usage"""
    print("🚀 Video-to-Voice Cloning Pipeline")
    print("=" * 50)

    # Check dependencies
    if not check_dependencies():
        return

    # Get input parameters
    video_path = input("📹 Enter video file path: ").strip()
    if not video_path:
        print("❌ No video file specified")
        return

    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return

    # Check for reference audio
    reference_audio = "reference_audio.wav"
    if not os.path.exists(reference_audio):
        ref_input = input(
            f"🎤 Reference audio not found. Enter path to reference audio file: "
        ).strip()
        if ref_input and os.path.exists(ref_input):
            reference_audio = ref_input
        else:
            print("❌ Reference audio file is required for voice cloning")
            return

    # Get target language
    target_language = input(
        "🌍 Enter target language code (e.g., 'en', 'fr', 'es') [default: en]: "
    ).strip()
    if not target_language:
        target_language = "en"

    # Run complete pipeline
    result = complete_pipeline(
        video_path=video_path,
        reference_audio=reference_audio,
        target_language=target_language,
        output_dir="pipeline_output",
    )

    # Display results
    if result["success"]:
        print(f"\n🎉 SUCCESS! Pipeline completed successfully!")
        print(f"🎵 Final output: {result['final_output']}")
        print(f"📊 Steps completed:")
        for step, step_result in result["steps"].items():
            status = "✅" if step_result["success"] else "❌"
            print(f"   {status} {step.replace('_', ' ').title()}")
    else:
        print(f"\n❌ FAILED: {result['error']}")
        print(f"📊 Steps completed:")
        for step, step_result in result["steps"].items():
            status = "✅" if step_result["success"] else "❌"
            print(f"   {status} {step.replace('_', ' ').title()}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Pipeline error: {e}")
        logger.error(f"Pipeline error: {e}")
