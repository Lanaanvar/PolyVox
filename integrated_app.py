import os
import logging
from TTS.api import TTS
from googletrans import Translator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()


def translate_text(text, target_language="en", source_language="auto"):
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
        logger.error(f"Translation failed: {e}")
        return {"original": text, "translated": text, "success": False, "error": str(e)}


def synthesize_with_cloned_voice(
    text,
    reference_audio="reference_audio.wav",
    output_path="cloned_speech.wav",
    translate_to=None,
    source_language="auto",
):
    try:
        if not os.path.exists(reference_audio):
            error_msg = f"Reference audio not found at: {reference_audio}"
            print(f"[ERROR] {error_msg}")
            print("⚠️ Please provide a valid reference audio file.")
            return {"success": False, "error": error_msg}
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
        print("[INFO] Loading Coqui TTS model (voice cloning)...")
        tts = TTS(
            model_name="tts_models/en/multi-dataset/tortoise-v2",
            progress_bar=True,
            gpu=False,
        )
        print("[INFO] Generating cloned speech...")
        tts.tts_to_file(
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
    texts,
    reference_audio="reference_audio.wav",
    translate_to=None,
    source_language="auto",
):
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


if __name__ == "__main__":
    print("🎬 Voice Cloning with Translation")
    print("=" * 50)
    print("If you haven't already, install dependencies with:")
    print("  pip install TTS torch googletrans==4.0.0rc1")
    REFERENCE_AUDIO = "reference_audio.wav"
    if not os.path.exists(REFERENCE_AUDIO):
        print(f" Reference audio not found: {REFERENCE_AUDIO}")
        print("Please provide a reference audio file (10-30 seconds of target voice)")
        exit(1)
    # Example 1: Voice cloning with translation to French
    print("\n Example 1: English to French + Voice Cloning")
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
    print("\n Example 3: Direct Voice Cloning (No Translation)")
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
        status = "✅ Success" if result["success"] else " Failed"
        print(f"   {name}: {status}")
    print("\n Voice cloning process completed!")
    print(" Play the generated .wav files to hear the results!")
