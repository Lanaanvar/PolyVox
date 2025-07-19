#!/usr/bin/env python3
"""
Simplified workflow that imports TTS only when needed to avoid import issues
"""

import os
import sys


def test_imports():
    """Test imports one by one"""
    print("🧪 Testing imports...")

    # Test basic imports first
    try:
        import torch

        print("✅ PyTorch imported successfully")
    except Exception as e:
        print(f"❌ PyTorch import error: {e}")
        return False

    try:
        import whisper

        print("✅ Whisper imported successfully")
    except Exception as e:
        print(f"❌ Whisper import error: {e}")
        return False

    try:
        from googletrans import Translator

        print("✅ Google Translate imported successfully")
    except Exception as e:
        print(f"❌ Google Translate import error: {e}")
        return False

    try:
        import ffmpeg

        print("✅ FFmpeg imported successfully")
    except Exception as e:
        print(f"❌ FFmpeg import error: {e}")
        return False

    # Test TTS last as it's the most problematic
    try:
        from TTS.api import TTS

        print("✅ TTS imported successfully")
        return True
    except Exception as e:
        print(f"❌ TTS import error: {e}")
        print(f"   Detailed error: {type(e).__name__}: {e}")
        return False


def simple_workflow_without_services(
    video_path="test_clip.mp4",
    reference_audio_path="reference_audio.wav",
    target_language="en",
    output_path="outputs/simple_cloned_voice.wav",
):
    """
    Simplified workflow that doesn't rely on the services modules
    """
    print("🎬 SIMPLIFIED VIDEO-TO-VOICE CLONING WORKFLOW")
    print("=" * 60)
    print(f"📹 Input Video: {video_path}")
    print(f"🎤 Reference Audio: {reference_audio_path}")
    print(f"🌍 Target Language: {target_language}")
    print(f"🎵 Output: {output_path}")
    print("=" * 60)

    try:
        # Check if files exist
        if not os.path.exists(video_path):
            print(f"❌ Video file not found: {video_path}")
            return {"success": False, "error": "Video file not found"}

        if not os.path.exists(reference_audio_path):
            print(f"❌ Reference audio not found: {reference_audio_path}")
            return {"success": False, "error": "Reference audio not found"}

        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Step 1: Extract audio from video
        print("\n📹 STEP 1: Extracting audio from video...")
        import ffmpeg

        temp_audio = "temp_extracted_audio.wav"
        try:
            (
                ffmpeg.input(video_path)
                .audio.output(temp_audio, acodec="pcm_s16le", ac=1, ar="22050")
                .overwrite_output()
                .run(quiet=True)
            )
            print(f"✅ Audio extracted: {temp_audio}")
        except Exception as e:
            print(f"❌ Audio extraction failed: {e}")
            return {"success": False, "error": f"Audio extraction failed: {e}"}

        # Step 2: Transcribe audio
        print("\n🎤 STEP 2: Transcribing audio...")
        import whisper

        model = whisper.load_model("base")
        result = model.transcribe(temp_audio)
        transcribed_text = result["text"].strip()
        detected_language = result.get("language", "unknown")

        print(f"✅ Transcription completed")
        print(f"   Detected language: {detected_language}")
        print(f"   Text: {transcribed_text}")

        # Step 3: Translation (if needed)
        print(f"\n🌍 STEP 3: Translation...")
        final_text = transcribed_text
        was_translated = False

        if detected_language != target_language:
            try:
                from googletrans import Translator

                translator = Translator()

                translation = translator.translate(
                    transcribed_text, src=detected_language, dest=target_language
                )
                final_text = translation.text
                was_translated = True

                print(f"✅ Translation completed")
                print(f"   Original: {transcribed_text}")
                print(f"   Translated: {final_text}")

            except Exception as e:
                print(f"⚠️ Translation failed: {e}")
                print("   Using original text")
        else:
            print(f"✅ No translation needed - languages match")

        # Step 4: Voice cloning
        print(f"\n🗣️ STEP 4: Voice cloning...")
        try:
            from TTS.api import TTS

            # Try different models
            models_to_try = [
                "tts_models/multilingual/multi-dataset/xtts_v2",
                "tts_models/en/vctk/vits",
                "tts_models/en/ljspeech/tacotron2-DDC",
            ]

            tts = None
            for model_name in models_to_try:
                try:
                    print(f"   Trying model: {model_name}")
                    tts = TTS(model_name=model_name, progress_bar=False, gpu=False)
                    print(f"   ✅ Loaded: {model_name}")
                    break
                except Exception as model_error:
                    print(f"   ⚠️ Model {model_name} failed: {model_error}")
                    continue

            if tts is None:
                raise RuntimeError("No TTS model could be loaded")

            # Generate speech
            print("   Generating speech...")
            if "xtts_v2" in model_name:
                tts.tts_to_file(
                    text=final_text,
                    speaker_wav=reference_audio_path,
                    file_path=output_path,
                    language=target_language,
                )
            else:
                # Fallback for other models
                try:
                    tts.tts_to_file(
                        text=final_text,
                        speaker_wav=reference_audio_path,
                        file_path=output_path,
                    )
                except:
                    tts.tts_to_file(text=final_text, file_path=output_path)

            print(f"✅ Voice cloning completed: {output_path}")

        except Exception as e:
            print(f"❌ Voice cloning failed: {e}")
            return {"success": False, "error": f"Voice cloning failed: {e}"}

        # Cleanup
        try:
            if os.path.exists(temp_audio):
                os.remove(temp_audio)
                print(f"🧹 Cleaned up: {temp_audio}")
        except:
            pass

        # Success!
        print(f"\n🎉 WORKFLOW COMPLETED SUCCESSFULLY!")
        print(f"📁 Input Video: {video_path}")
        print(f"📄 Transcribed: {transcribed_text}")
        if was_translated:
            print(f"📄 Translated: {final_text}")
        print(f"🎵 Final Output: {output_path}")

        return {
            "success": True,
            "final_output": output_path,
            "original_text": transcribed_text,
            "final_text": final_text,
            "was_translated": was_translated,
            "detected_language": detected_language,
            "target_language": target_language,
        }

    except Exception as e:
        print(f"\n❌ Workflow failed: {e}")
        import traceback

        traceback.print_exc()
        return {"success": False, "error": str(e)}


def main():
    """Main function"""
    print("🎬 Simple Video-to-Voice Cloning Test")
    print("=" * 50)

    # Test imports first
    if not test_imports():
        print("\n❌ Import test failed. Cannot continue.")
        return

    print(f"\n✅ All imports successful! Starting workflow...")

    # Check for required files
    video_file = "test_clip.mp4"
    reference_file = "reference_audio.wav"

    if not os.path.exists(video_file):
        print(f"❌ Video file missing: {video_file}")
        return

    if not os.path.exists(reference_file):
        print(f"❌ Reference audio missing: {reference_file}")
        return

    # Run the simplified workflow
    result = simple_workflow_without_services(
        video_path=video_file,
        reference_audio_path=reference_file,
        target_language="en",
        output_path="outputs/simple_test_output.wav",
    )

    if result["success"]:
        print(f"\n🎉 SUCCESS! Check your output file: {result['final_output']}")
    else:
        print(f"\n❌ FAILED: {result['error']}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n⏹️ Interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback

        traceback.print_exc()

    input("\nPress Enter to exit...")
