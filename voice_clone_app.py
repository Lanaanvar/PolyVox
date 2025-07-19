#!/usr/bin/env python3
"""
Simple Voice Cloning with Translation Integration
Standalone script that combines voice cloning and translation functionality
"""

import os
import logging
from typing import Optional, Dict, Any, List

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Global variables for TTS and translator
tts_model = None
translator = None


def initialize_services():
    """Initialize TTS and translation services"""
    global tts_model, translator

    try:
        # Import and initialize TTS
        from TTS.api import TTS

        print("[INFO] Loading Coqui TTS model...")
        tts_model = TTS(
            model_name="tts_models/en/multi-dataset/tortoise-v2",
            progress_bar=True,
            gpu=False,
        )
        print("[INFO] TTS model loaded successfully")

        # Import and initialize translator
        from googletrans import Translator

        translator = Translator()
        print("[INFO] Translation service initialized")

        return True

    except ImportError as e:
        print(f"[ERROR] Missing dependencies: {e}")
        print("Please install required packages:")
        print("pip install TTS googletrans==4.0.0rc1 torch torchaudio")
        return False
    except Exception as e:
        print(f"[ERROR] Failed to initialize services: {e}")
        return False


def translate_text(
    text: str, target_language: str = "en", source_language: str = "auto"
) -> Dict[str, Any]:
    """
    Translate text to target language

    Args:
        text: Text to translate
        target_language: Target language code (e.g., 'en', 'fr', 'es')
        source_language: Source language code or 'auto' for auto-detection

    Returns:
        dict: Translation result with original and translated text
    """
    global translator

    try:
        if not text or not text.strip():
            return {
                "original": text,
                "translated": text,
                "success": False,
                "error": "Empty text",
            }

        if translator is None:
            return {
                "original": text,
                "translated": text,
                "success": False,
                "error": "Translator not initialized",
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
        logger.error(f"Translation failed: {e}")
        return {"original": text, "translated": text, "success": False, "error": str(e)}


def synthesize_with_cloned_voice(
    text: str,
    reference_audio: str = "reference_audio.wav",
    output_path: str = "cloned_speech.wav",
    translate_to: Optional[str] = None,
    source_language: str = "auto",
) -> Dict[str, Any]:
    """
    Synthesize speech with cloned voice, optionally translating text first

    Args:
        text: Text to synthesize
        reference_audio: Path to reference audio file
        output_path: Output file path
        translate_to: Target language code for translation (None for no translation)
        source_language: Source language code

    Returns:
        dict: Result with success status and details
    """
    global tts_model

    try:
        # Check if reference audio exists
        if not os.path.exists(reference_audio):
            error_msg = f"Reference audio not found at: {reference_audio}"
            print(f"[ERROR] {error_msg}")
            print("⚠️ Please provide a valid reference audio file.")
            return {"success": False, "error": error_msg}

        if tts_model is None:
            error_msg = "TTS model not initialized"
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

        print("[INFO] Generating cloned speech...")
        tts_model.tts_to_file(
            text=final_text, speaker_wav=reference_audio, file_path=output_path
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


def batch_process(
    texts: List[str],
    reference_audio: str = "reference_audio.wav",
    translate_to: Optional[str] = None,
    source_language: str = "auto",
) -> List[Dict[str, Any]]:
    """
    Process multiple texts with voice cloning

    Args:
        texts: List of texts to process
        reference_audio: Path to reference audio file
        translate_to: Target language for translation
        source_language: Source language

    Returns:
        list: List of results for each text
    """
    results = []

    for i, text in enumerate(texts):
        output_path = f"cloned_speech_{i+1}.wav"
        print(f"\n[INFO] Processing text {i+1}/{len(texts)}: {text}")

        result = synthesize_with_cloned_voice(
            text=text,
            reference_audio=reference_audio,
            output_path=output_path,
            translate_to=translate_to,
            source_language=source_language,
        )

        results.append(result)

    return results


def main():
    """Main function with examples"""
    print("🎬 Voice Cloning with Translation")
    print("=" * 50)

    # Initialize services
    if not initialize_services():
        print("❌ Failed to initialize services. Exiting.")
        return

    # Configuration
    REFERENCE_AUDIO = "reference_audio.wav"

    # Check if reference audio exists
    if not os.path.exists(REFERENCE_AUDIO):
        print(f"⚠️ Reference audio not found: {REFERENCE_AUDIO}")
        print("Please provide a reference audio file (10-30 seconds of target voice)")
        print("Save it as 'reference_audio.wav' in the current directory")
        return

    # Example 1: Voice cloning with translation to French
    print("\n🇫🇷 Example 1: English to French + Voice Cloning")
    text1 = "Hello, I am trying to clone a text into a voice"
    result1 = synthesize_with_cloned_voice(
        text=text1,
        reference_audio=REFERENCE_AUDIO,
        output_path="cloned_speech_french.wav",
        translate_to="fr",
        source_language="en",
    )

    # Example 2: Voice cloning with translation to Spanish
    print("\n🇪🇸 Example 2: English to Spanish + Voice Cloning")
    text2 = "Technology is amazing and voice cloning is the future"
    result2 = synthesize_with_cloned_voice(
        text=text2,
        reference_audio=REFERENCE_AUDIO,
        output_path="cloned_speech_spanish.wav",
        translate_to="es",
        source_language="en",
    )

    # Example 3: Direct voice cloning without translation
    print("\n🗣️ Example 3: Direct Voice Cloning (No Translation)")
    text3 = "This is a direct voice cloning without translation"
    result3 = synthesize_with_cloned_voice(
        text=text3,
        reference_audio=REFERENCE_AUDIO,
        output_path="cloned_speech_direct.wav",
        translate_to=None,
    )

    # Example 4: Batch processing
    print("\n📦 Example 4: Batch Processing")
    batch_texts = [
        "Welcome to our application",
        "This is a test of voice cloning",
        "Thank you for using our service",
    ]

    batch_results = batch_process(
        texts=batch_texts,
        reference_audio=REFERENCE_AUDIO,
        translate_to="de",  # German
        source_language="en",
    )

    # Summary
    print("\n📊 Summary:")
    examples = [
        ("French translation + cloning", result1),
        ("Spanish translation + cloning", result2),
        ("Direct cloning", result3),
        ("Batch processing", {"success": all(r["success"] for r in batch_results)}),
    ]

    for name, result in examples:
        status = "✅ Success" if result["success"] else "❌ Failed"
        print(f"   {name}: {status}")

    print("\n🎉 Voice cloning process completed!")
    print("🎵 Play the generated .wav files to hear the results!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        logging.error(f"Application error: {e}")
