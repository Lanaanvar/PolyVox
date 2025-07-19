#!/usr/bin/env python3
"""
Simple Voice Cloning with Translation
Complete standalone application
"""

import os
import sys
import logging

# Add current directory to path to import from app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import TTS
        from googletrans import Translator
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("📦 Please install dependencies:")
        print("   pip install TTS torch googletrans==4.0.0rc1")
        return False

def main():
    """Main function"""
    print("🎬 Simple Voice Cloning with Translation")
    print("=" * 50)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Import the voice cloning function
    try:
        from app.services.voice_clone import synthesize_with_cloned_voice, batch_process
    except ImportError:
        print("❌ Cannot import voice cloning functions")
        print("Make sure you're running this from the project root directory")
        return
    
    # Configuration
    REFERENCE_AUDIO = "reference_audio.wav"
    
    # Check if reference audio exists
    if not os.path.exists(REFERENCE_AUDIO):
        print(f"⚠️ Reference audio not found: {REFERENCE_AUDIO}")
        print("Please provide a reference audio file (10-30 seconds of target voice)")
        return
    
    print(f"✅ Reference audio found: {REFERENCE_AUDIO}")
    print()
    
    # Example texts and languages
    examples = [
        {
            "text": "Hello, I am trying to clone a text into a voice",
            "translate_to": "fr",
            "output": "cloned_speech_french.wav",
            "description": "🇫🇷 English to French"
        },
        {
            "text": "Technology is amazing and voice cloning is the future",
            "translate_to": "es",
            "output": "cloned_speech_spanish.wav", 
            "description": "🇪🇸 English to Spanish"
        },
        {
            "text": "This is a direct voice cloning without translation",
            "translate_to": None,
            "output": "cloned_speech_direct.wav",
            "description": "🗣️ Direct cloning (no translation)"
        }
    ]
    
    successful_outputs = []
    
    # Process each example
    for i, example in enumerate(examples, 1):
        print(f"\n{example['description']}")
        print(f"Text: {example['text']}")
        
        try:
            result = synthesize_with_cloned_voice(
                text=example["text"],
                reference_audio=REFERENCE_AUDIO,
                output_path=example["output"],
                translate_to=example["translate_to"],
                source_language="en"
            )
            
            if result["success"]:
                print(f"✅ Success: {example['output']}")
                if result["was_translated"]:
                    print(f"📄 Translated: {result['final_text']}")
                successful_outputs.append(example["output"])
            else:
                print(f"❌ Failed: {result['error']}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # Batch processing example
    print(f"\n� Batch Processing Example")
    batch_texts = [
        "Welcome to our application",
        "This is a test of voice cloning", 
        "Thank you for using our service"
    ]
    
    try:
        batch_results = batch_process(
            texts=batch_texts,
            reference_audio=REFERENCE_AUDIO,
            translate_to="de",  # German
            source_language="en"
        )
        
        batch_success = all(r["success"] for r in batch_results)
        if batch_success:
            print("✅ Batch processing completed successfully")
            successful_outputs.extend([f"cloned_speech_{i+1}.wav" for i in range(len(batch_texts))])
        else:
            print("❌ Some batch processing failed")
            
    except Exception as e:
        print(f"❌ Batch processing error: {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"✅ Successful outputs: {len(successful_outputs)}")
    print(f"❌ Failed outputs: {len(examples) + 1 - len(successful_outputs)}")
    
    if successful_outputs:
        print(f"\n🎵 Generated audio files:")
        for output in successful_outputs:
            if os.path.exists(output):
                print(f"   - {output}")
        print(f"\n� Play the audio files to hear the results!")
    
    print("\n✨ Voice cloning process completed!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Application interrupted by user")
    except Exception as e:
        print(f"\n❌ Application error: {e}")
        logger.error(f"Application error: {e}")
