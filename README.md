# Simple Voice Cloning with Translation

## Why TTS.py is Redundant

You're absolutely right! The `tts.py` file is redundant because:

1. **Voice Cloning Model Does Both**: The Coqui TTS model in `voice-clone.py` already handles both TTS and voice cloning
2. **Better Functionality**: Voice cloning can clone ANY voice from a reference audio, while Google Cloud TTS only provides standard voices
3. **Integrated Solution**: Having translation + voice cloning in one place is simpler and more efficient

## Simplified Architecture

```
voice-cloning/
├── app/services/voice-clone.py  # ✅ Complete solution (Translation + Voice Cloning)
├── app/services/tts.py          # ❌ Redundant - can be removed
├── simple_voice_clone.py        # ✅ Standalone script to run everything
├── simple_requirements.txt      # ✅ Only essential dependencies
└── README.md                    # ✅ This file
```

## Quick Start

### 1. Install Dependencies

```bash
pip install TTS torch googletrans==4.0.0rc1
```

### 2. Add Reference Audio

Place a 10-30 second audio clip of the target voice as `reference_audio.wav`

### 3. Run the Application

```bash
python simple_voice_clone.py
```

## What the Application Does

1. **Translation**: Translates your text to any target language
2. **Voice Cloning**: Clones the voice from your reference audio
3. **Speech Generation**: Creates speech in the cloned voice with translated text

## Examples

The application includes these examples:

- 🇫🇷 English to French + Voice Cloning
- 🇪🇸 English to Spanish + Voice Cloning
- 🗣️ Direct Voice Cloning (no translation)
- 📦 Batch Processing

## Usage

### Direct Usage

```python
from app.services.voice_clone import synthesize_with_cloned_voice

result = synthesize_with_cloned_voice(
    text="Hello, how are you?",
    reference_audio="reference_audio.wav",
    output_path="output.wav",
    translate_to="fr",  # French
    source_language="en"
)
```

### Batch Processing

```python
from app.services.voice_clone import batch_process

results = batch_process(
    texts=["Hello", "How are you?", "Goodbye"],
    reference_audio="reference_audio.wav",
    translate_to="es",  # Spanish
    source_language="en"
)
```

## Why This is Better Than TTS.py

| Feature       | voice-clone.py | tts.py                    |
| ------------- | -------------- | ------------------------- |
| Voice Cloning | ✅ Yes         | ❌ No                     |
| Custom Voices | ✅ Any voice   | ❌ Only standard voices   |
| Translation   | ✅ Integrated  | ❌ Separate service       |
| Dependencies  | ✅ Simple      | ❌ Complex (Google Cloud) |
| Setup         | ✅ Easy        | ❌ Requires credentials   |

## Files You Can Remove

Since the voice cloning model handles everything, you can safely remove:

- `app/services/tts.py` (redundant)
- `integrated_app.py` (too complex)
- `run_app.py` (too complex)
- `run_app.bat` (too complex)
- `requirements.txt` (too many dependencies)

## Keep It Simple

The entire application is now in just two files:

1. `app/services/voice-clone.py` - Core functionality
2. `simple_voice_clone.py` - Easy-to-use wrapper

This is much simpler, more maintainable, and more efficient!
