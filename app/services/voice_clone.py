"""
Voice cloning service with TTS models and complete workflow integration
"""

import os
import logging
from TTS.api import TTS
from googletrans import Translator
from .audio_extraction import audio_extraction_service
from .whisper_transcribe import whisper_service
from .translate import translation_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()


def translate_text(text, target_language="en", source_language="auto"):
    """
    Translate text to target language

    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'en', 'fr', 'es')
        source_language: Source language code or 'auto' for auto-detection

    Returns:
        dict: Translation result with original and translated text
    """
    try:
        if not text or not text.strip():
            return {
                "original": text,
                "translated": text,
                "success": False,
                "error": "Empty text",
            }

        print(f"[INFO] Translating text from {source_language} to {target_language}...")
        result = translator.translate(text, src=source_language, dest=target_language)

        translation_result = {
            "original": text,
            "translated": result.text,
            "source_language": result.src,
            "target_language": target_language,
            "success": True,
            "error": None,
        }

        print(f"[INFO] Translation completed: {result.text}")
        return translation_result

    except Exception as e:
        error_msg = f"Translation failed: {e}"
        logger.error(error_msg)
        print(f"[ERROR] {error_msg}")
        return {
            "original": text,
            "translated": text,
            "success": False,
            "error": error_msg,
        }


def synthesize_with_cloned_voice(
    text,
    reference_audio_path="reference_audio.wav",
    output_path="cloned_speech.wav",
    translate_to=None,
    source_language="auto",
    language="en",
):
    """
    Synthesize speech with cloned voice using Coqui XTTS

    Args:
        text: Text to synthesize
        reference_audio_path: Path to reference audio file
        output_path: Output file path
        translate_to: Target language code for translation (None for no translation)
        source_language: Source language code
        language: TTS language

    Returns:
        dict: Result with success status and details
    """
    try:
        if reference_audio_path and not os.path.exists(reference_audio_path):
            error_msg = f"Reference audio not found at: {reference_audio_path}"
            print(f"[ERROR] {error_msg}")
            return {"success": False, "error": error_msg}

        # Translate text if requested
        final_text = text
        translation_result = None

        if translate_to:
            translation_result = translate_text(text, translate_to, source_language)
            if translation_result["success"]:
                final_text = translation_result["translated"]
            else:
                print(
                    f"[WARNING] Translation failed: {translation_result['error']}. Using original text."
                )

        print("[INFO] Loading XTTS voice cloning model...")

        try:
            tts = TTS(
                model_name="tts_models/multilingual/multi-dataset/xtts_v2",
                progress_bar=True,
                gpu=False,
            )
        except Exception as e:
            error_msg = f"Failed to load XTTS model: {e}"
            print(f"[ERROR] {error_msg}")
            return {"success": False, "error": error_msg}

        print("[INFO] Generating cloned speech using XTTS...")

        tts.tts_to_file(
            text=final_text,
            speaker_wav=reference_audio_path,
            file_path=output_path,
            language=language,
        )

        print(f"[✅] Cloned voice saved at: {output_path}")

        return {
            "success": True,
            "original_text": text,
            "final_text": final_text,
            "output_path": output_path,
            "was_translated": translate_to is not None,
            "translation_result": translation_result,
        }

    except Exception as e:
        error_msg = f"Voice cloning failed: {e}"
        logger.error(error_msg)
        print(f"[ERROR] {error_msg}")
        return {"success": False, "error": error_msg}


class VoiceCloneService:
    """Voice cloning service"""

    def __init__(self):
        self.tts_model = None
        self._initialized = False

    def initialize(self):
        """Initialize the voice cloning service"""
        try:
            # Service will be initialized on first use to avoid long startup times
            self.tts_model = True  # Dummy for compatibility
            self._initialized = True
            logger.info("Voice cloning service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize voice cloning service: {e}")
            self._initialized = False

    def cleanup(self):
        """Cleanup resources"""
        try:
            self.tts_model = None
            self._initialized = False
            logger.info("Voice cloning service cleaned up")
        except Exception as e:
            logger.error(f"Error during voice cloning cleanup: {e}")


def complete_video_to_voice_workflow(
    video_path,
    reference_audio_path,
    target_language="en",
    output_path="cloned_speech.wav",
    source_language="auto",
    cleanup_temp_files=True,
):
    """
    Complete workflow: Video MP4 → Audio extraction → Transcription → Translation → TTS+Voice cloning

    Args:
        video_path: Path to input MP4 video file
        reference_audio_path: Path to reference audio file for voice cloning
        target_language: Target language code for translation
        output_path: Path for final cloned voice output
        source_language: Source language code (auto for detection)
        cleanup_temp_files: Whether to clean up temporary files

    Returns:
        dict: Complete workflow result with all step details
    """
    workflow_result = {
        "success": False,
        "steps": {
            "audio_extraction": None,
            "transcription": None,
            "translation": None,
            "voice_cloning": None,
        },
        "final_output": None,
        "error": None,
        "temp_files": [],
    }

    try:
        print("🎬 STARTING COMPLETE VIDEO-TO-VOICE CLONING WORKFLOW")
        print("=" * 60)
        print(f"📹 Input Video: {video_path}")
        print(f"🎤 Reference Audio: {reference_audio_path}")
        print(f"🌍 Target Language: {target_language}")
        print(f"🎵 Output: {output_path}")
        print("=" * 60)

        # Step 1: Audio Extraction from Video
        print("\n📹 STEP 1: Extracting audio from video...")

        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        extraction_result = audio_extraction_service.extract_audio_from_video(
            video_path=video_path,
            sample_rate=22050,
            channels=1,
        )

        workflow_result["steps"]["audio_extraction"] = {
            "success": extraction_result.success,
            "audio_path": extraction_result.audio_file_path,
            "duration": extraction_result.duration,
            "sample_rate": extraction_result.sample_rate,
            "error": extraction_result.error_message,
        }

        if not extraction_result.success:
            raise RuntimeError(
                f"Audio extraction failed: {extraction_result.error_message}"
            )

        extracted_audio_path = extraction_result.audio_file_path
        workflow_result["temp_files"].append(extracted_audio_path)

        print(f"✅ Audio extracted: {extracted_audio_path}")
        print(f"   Duration: {extraction_result.duration:.2f}s")

        # Step 2: Transcription of extracted audio
        print("\n🎤 STEP 2: Transcribing audio to text...")

        transcription_result = whisper_service.transcribe_audio(
            audio_path=extracted_audio_path,
            language=None if source_language == "auto" else source_language,
        )

        workflow_result["steps"]["transcription"] = {
            "success": True,
            "text": transcription_result.text,
            "detected_language": transcription_result.detected_language,
            "segments": len(transcription_result.segments),
            "confidence": transcription_result.confidence_score,
        }

        transcribed_text = transcription_result.text
        detected_language = transcription_result.detected_language

        print(f"✅ Transcription completed")
        print(f"   Detected Language: {detected_language}")
        print(f"   Text: {transcribed_text}")

        # Step 3: Translation of transcribed text
        print(f"\n🌍 STEP 3: Translating text to {target_language}...")

        final_text = transcribed_text
        translation_result = None

        # Only translate if target language differs from detected language
        if detected_language != target_language:
            try:
                translation_result = translation_service.translate_text(
                    text=transcribed_text,
                    source_language=detected_language,
                    target_language=target_language,
                )

                workflow_result["steps"]["translation"] = {
                    "success": True,
                    "original": transcribed_text,
                    "translated": translation_result.translated_text,
                    "source_language": translation_result.source_language,
                    "target_language": translation_result.target_language,
                    "confidence": translation_result.confidence_score,
                }

                final_text = translation_result.translated_text
                print(f"✅ Translation completed")
                print(f"   Original: {transcribed_text}")
                print(f"   Translated: {final_text}")

            except Exception as e:
                print(f"⚠️ Translation failed: {e}")
                print("   Using original transcribed text")
                workflow_result["steps"]["translation"] = {
                    "success": False,
                    "error": str(e),
                    "fallback": True,
                }
        else:
            print(f"✅ No translation needed - detected language matches target")
            workflow_result["steps"]["translation"] = {
                "success": True,
                "skipped": True,
                "reason": "Language match",
            }

        # Step 4: Voice cloning with reference audio and translated text
        print(f"\n🗣️ STEP 4: Cloning voice with reference audio...")

        cloning_result = synthesize_with_cloned_voice(
            text=final_text,
            reference_audio_path=reference_audio_path,
            output_path=output_path,
            language=target_language,
        )

        workflow_result["steps"]["voice_cloning"] = cloning_result

        if not cloning_result["success"]:
            raise RuntimeError(f"Voice cloning failed: {cloning_result['error']}")

        print(f"✅ Voice cloning completed: {output_path}")

        # Cleanup temporary files if requested
        if cleanup_temp_files:
            print(f"\n🧹 Cleaning up temporary files...")
            for temp_file in workflow_result["temp_files"]:
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                        print(f"   Deleted: {temp_file}")
                except Exception as e:
                    print(f"   Warning: Could not delete {temp_file}: {e}")

        # Success!
        workflow_result.update(
            {
                "success": True,
                "final_output": output_path,
                "original_text": transcribed_text,
                "final_text": final_text,
                "was_translated": detected_language != target_language,
                "detected_language": detected_language,
                "target_language": target_language,
            }
        )

        print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"📁 Input Video: {video_path}")
        print(f"📄 Transcribed: {transcribed_text}")
        if workflow_result["was_translated"]:
            print(f"📄 Translated: {final_text}")
        print(f"🎵 Final Output: {output_path}")

        return workflow_result

    except Exception as e:
        error_msg = f"Workflow failed: {e}"
        logger.error(error_msg)
        print(f"\n❌ {error_msg}")

        workflow_result.update(
            {
                "success": False,
                "error": error_msg,
            }
        )

        # Attempt cleanup even on failure
        if cleanup_temp_files:
            for temp_file in workflow_result.get("temp_files", []):
                try:
                    if os.path.exists(temp_file):
                        os.remove(temp_file)
                except:
                    pass

        return workflow_result


# Create singleton instance
voice_clone_service = VoiceCloneService()
