#!/usr/bin/env python3
"""
Complete Video-to-Voice Cloning Pipeline
All-in-one script: Video → Audio → Transcription → Translation → Voice Cloning
"""

import os
import sys
import logging
import subprocess
import tempfile

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def check_dependencies():
    """Check if all required dependencies are installed"""
    print("🔍 Checking dependencies...")

    missing_deps = []

    try:
        from TTS.api import TTS

        print("✅ TTS (Coqui) - Available")
    except ImportError:
        missing_deps.append("TTS")
        print("❌ TTS (Coqui) - Missing")

    try:
        from googletrans import Translator

        print("✅ Google Translator - Available")
    except ImportError:
        missing_deps.append("googletrans==4.0.0rc1")
        print("❌ Google Translator - Missing")

    try:
        import whisper

        print("✅ OpenAI Whisper - Available")
    except ImportError:
        missing_deps.append("openai-whisper")
        print("❌ OpenAI Whisper - Missing")

    # Check transformers version
    try:
        import transformers

        version = transformers.__version__
        print(f"✅ Transformers v{version} - Available")

        # Check if version is compatible
        major, minor = map(int, version.split(".")[:2])
        if major > 4 or (major == 4 and minor > 35):
            print("⚠️ Transformers version might be too new for TTS")
            print("   Recommended: pip install transformers==4.33.0")
    except ImportError:
        missing_deps.append("transformers==4.33.0")
        print("❌ Transformers - Missing")

    # Check FFmpeg
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            print("✅ FFmpeg - Available")
        else:
            print("❌ FFmpeg - Not working properly")
            missing_deps.append("ffmpeg")
    except Exception:
        print("❌ FFmpeg - Not found")
        missing_deps.append("ffmpeg")

    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("📦 Install Python packages with:")
        python_deps = [dep for dep in missing_deps if dep != "ffmpeg"]
        if python_deps:
            print(f"   pip install {' '.join(python_deps)}")
        if "ffmpeg" in missing_deps:
            print("   Install FFmpeg from https://ffmpeg.org/download.html")
        return False

    print("✅ All dependencies are available!")
    return True


def extract_audio_from_video(video_path, output_path="extracted_audio.wav"):
    """Extract audio from video using FFmpeg"""
    print(f"\n📹 STEP 1: Extracting audio from video...")
    print(f"   Video: {video_path}")
    print(f"   Output: {output_path}")

    try:
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

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

        print(f"   Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0 and os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   ✅ Audio extracted successfully ({file_size} bytes)")
            return True
        else:
            print(f"   ❌ Audio extraction failed: {result.stderr}")
            return False

    except Exception as e:
        print(f"   ❌ Audio extraction error: {e}")
        return False


def transcribe_audio(audio_path):
    """Transcribe audio to text using Whisper"""
    print(f"\n🎤 STEP 2: Transcribing audio to text...")
    print(f"   Audio: {audio_path}")

    try:
        import whisper

        print("   Loading Whisper model...")
        model = whisper.load_model("base")

        print("   Transcribing audio...")
        result = model.transcribe(audio_path)

        text = result["text"].strip()
        language = result.get("language", "unknown")

        print(f"   ✅ Transcription completed")
        print(f"   Detected language: {language}")
        print(f"   Text: {text}")

        return {"success": True, "text": text, "language": language}

    except Exception as e:
        print(f"   ❌ Transcription failed: {e}")
        return {"success": False, "error": str(e)}


def translate_text(text, target_language="en", source_language="auto"):
    """Translate text using Google Translate"""
    print(f"\n🌍 STEP 3: Translating text...")
    print(f"   From: {source_language} → To: {target_language}")
    print(f"   Text: {text}")

    try:
        from googletrans import Translator

        if source_language == target_language:
            print("   ✅ No translation needed - languages match")
            return {
                "success": True,
                "original": text,
                "translated": text,
                "source_language": source_language,
                "target_language": target_language,
                "was_translated": False,
            }

        translator = Translator()
        result = translator.translate(text, src=source_language, dest=target_language)

        print(f"   ✅ Translation completed")
        print(f"   Original: {text}")
        print(f"   Translated: {result.text}")

        return {
            "success": True,
            "original": text,
            "translated": result.text,
            "source_language": result.src,
            "target_language": target_language,
            "was_translated": True,
        }

    except Exception as e:
        print(f"   ❌ Translation failed: {e}")
        return {
            "success": False,
            "original": text,
            "translated": text,
            "error": str(e),
            "was_translated": False,
        }


def clone_voice(text, reference_audio, output_path="cloned_speech.wav"):
    """Clone voice using TTS"""
    print(f"\n🗣️ STEP 4: Voice cloning...")
    print(f"   Text: {text}")
    print(f"   Reference: {reference_audio}")
    print(f"   Output: {output_path}")

    try:
        from TTS.api import TTS

        if not os.path.exists(reference_audio):
            raise FileNotFoundError(f"Reference audio not found: {reference_audio}")

        print("   Loading TTS model...")

        # Try voice cloning models that actually work
        voice_cloning_models = [
            "tts_models/multilingual/multi-dataset/xtts_v2",
            "tts_models/en/vctk/vits",
            "tts_models/en/ljspeech/tacotron2-DDC",
        ]

        tts = None
        successful_model = None

        for model_name in voice_cloning_models:
            try:
                print(f"   Trying model: {model_name}")
                tts = TTS(model_name=model_name, progress_bar=True, gpu=False)
                successful_model = model_name
                print(f"   ✅ Successfully loaded: {model_name}")
                break
            except Exception as model_error:
                print(f"   ❌ Model {model_name} failed: {model_error}")
                continue

        if tts is None:
            raise RuntimeError("No compatible TTS model could be loaded")

        print("   Generating cloned speech...")

        # Use different methods based on the model
        if "xtts_v2" in successful_model:
            # XTTS v2 supports voice cloning
            tts.tts_to_file(
                text=text,
                speaker_wav=reference_audio,
                file_path=output_path,
                language="en",
            )
        elif "vits" in successful_model:
            # VITS model - try with speaker_wav
            try:
                tts.tts_to_file(
                    text=text, speaker_wav=reference_audio, file_path=output_path
                )
            except Exception as vits_error:
                print(f"   ⚠️ VITS voice cloning failed: {vits_error}")
                print("   Falling back to regular TTS...")
                tts.tts_to_file(text=text, file_path=output_path)
        else:
            # Regular TTS for other models
            print("   ⚠️ Using regular TTS (voice cloning not supported)")
            tts.tts_to_file(text=text, file_path=output_path)

        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"   ✅ Voice cloning completed ({file_size} bytes)")
            return {"success": True, "output_path": output_path, "file_size": file_size}
        else:
            raise RuntimeError("Output file was not created")

    except Exception as e:
        print(f"   ❌ Voice cloning failed: {e}")
        print(f"   💡 Try: pip install transformers==4.33.0")
        return {"success": False, "error": str(e)}


def complete_pipeline(
    video_path,
    reference_audio,
    target_language="en",
    output_name="final_cloned_speech.wav",
):
    """Run the complete pipeline"""
    print("🎬 COMPLETE VIDEO-TO-VOICE CLONING PIPELINE")
    print("=" * 60)
    print(f"📹 Video: {video_path}")
    print(f"🎤 Reference: {reference_audio}")
    print(f"🌍 Target Language: {target_language}")
    print(f"🎵 Output: {output_name}")
    print("=" * 60)

    # Check if files exist
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False

    if not os.path.exists(reference_audio):
        print(f"❌ Reference audio not found: {reference_audio}")
        return False

    # Step 1: Extract audio
    extracted_audio = "temp_extracted_audio.wav"
    if not extract_audio_from_video(video_path, extracted_audio):
        return False

    # Step 2: Transcribe
    transcription = transcribe_audio(extracted_audio)
    if not transcription["success"]:
        return False

    # Step 3: Translate
    translation = translate_text(
        transcription["text"], target_language, transcription["language"]
    )

    if not translation["success"]:
        print("⚠️ Translation failed, using original text")
        final_text = transcription["text"]
    else:
        final_text = translation["translated"]

    # Step 4: Clone voice
    cloning = clone_voice(final_text, reference_audio, output_name)

    # Clean up temporary file
    if os.path.exists(extracted_audio):
        os.remove(extracted_audio)
        print(f"🧹 Cleaned up temporary file: {extracted_audio}")

    if cloning["success"]:
        print(f"\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print(f"📁 Original video: {video_path}")
        print(f"📄 Transcribed text: {transcription['text']}")
        if translation.get("was_translated", False):
            print(f"📄 Translated text: {translation['translated']}")
        print(f"🎵 Final cloned speech: {cloning['output_path']}")
        return True
    else:
        print(f"\n❌ Pipeline failed at voice cloning step")
        return False


def main():
    """Main function"""
    print("🚀 Video-to-Voice Cloning Pipeline")
    print("=" * 50)

    # Check dependencies first
    if not check_dependencies():
        return

    # Get user input
    video_path = input("\n📹 Enter video file path: ").strip()
    if not video_path:
        print("❌ No video file specified")
        return

    # Check for reference audio
    reference_audio = "reference_audio.wav"
    if not os.path.exists(reference_audio):
        ref_input = input("🎤 Enter reference audio file path: ").strip()
        if ref_input and os.path.exists(ref_input):
            reference_audio = ref_input
        else:
            print("❌ Reference audio is required")
            return

    # Get target language
    target_language = input(
        "🌍 Enter target language (en/fr/es/de/etc.) [default: en]: "
    ).strip()
    if not target_language:
        target_language = "en"

    # Get output filename
    output_name = input(
        "🎵 Enter output filename [default: final_cloned_speech.wav]: "
    ).strip()
    if not output_name:
        output_name = "final_cloned_speech.wav"

    # Run the pipeline
    success = complete_pipeline(
        video_path, reference_audio, target_language, output_name
    )

    if success:
        print(f"\n🎉 All done! Play {output_name} to hear the result!")
    else:
        print(f"\n❌ Pipeline failed. Check the error messages above.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Pipeline interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        logger.error(f"Unexpected error: {e}")
