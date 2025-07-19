# Complete Video-to-Voice Cloning Workflow

This implementation provides a complete workflow for processing MP4 videos through audio extraction, transcription, translation, and voice cloning using Coqui TTS models.

## 🎬 Workflow Overview

```
MP4 Video Input → Audio Extraction → Transcription → Translation → TTS + Voice Cloning
```

### Step-by-Step Process:

1. **📹 Audio Extraction**: Extract audio from MP4 video using FFmpeg
2. **🎤 Transcription**: Convert speech to text using OpenAI Whisper
3. **🌍 Translation**: Translate text to target language using Google Translate
4. **🗣️ Voice Cloning**: Synthesize speech using Coqui TTS with reference audio

## 🚀 Quick Start

### Prerequisites

1. **Install Dependencies:**

```bash
pip install TTS torch googletrans==4.0.0rc1 openai-whisper ffmpeg-python pydub
```

2. **Install FFmpeg:**
   - Windows: Download from https://ffmpeg.org/ and add to PATH
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

### Required Files

1. **Video Input**: Place your MP4 video file (e.g., `test_clip.mp4`)
2. **Reference Audio**: Create `reference_audio.wav` (10-30 seconds of the target voice)

### Usage

#### Option 1: Run Example Script (Easiest)

**Windows:**

```cmd
run_workflow.bat
```

**Linux/Mac:**

```bash
python example_workflow.py
```

#### Option 2: Use in Your Code

```python
from app.services.voice_clone import complete_video_to_voice_workflow

result = complete_video_to_voice_workflow(
    video_path="input_video.mp4",
    reference_audio_path="reference_audio.wav",
    target_language="en",  # or "fr", "es", "de", etc.
    output_path="outputs/cloned_voice.wav"
)

if result["success"]:
    print(f"✅ Success! Output: {result['final_output']}")
    print(f"📄 Transcribed: {result['original_text']}")
    if result['was_translated']:
        print(f"📄 Translated: {result['final_text']}")
else:
    print(f"❌ Error: {result['error']}")
```

## 📊 Function Parameters

### `complete_video_to_voice_workflow()`

| Parameter              | Type | Description                                 | Default             |
| ---------------------- | ---- | ------------------------------------------- | ------------------- |
| `video_path`           | str  | Path to input MP4 video file                | Required            |
| `reference_audio_path` | str  | Path to reference audio for voice cloning   | Required            |
| `target_language`      | str  | Target language code (en, fr, es, de, etc.) | "en"                |
| `output_path`          | str  | Path for final cloned voice output          | "cloned_speech.wav" |
| `source_language`      | str  | Source language code or "auto"              | "auto"              |
| `cleanup_temp_files`   | bool | Whether to delete temporary files           | True                |

### Return Value

The function returns a detailed result dictionary:

```python
{
    "success": bool,                    # Overall success status
    "final_output": str,                # Path to final output file
    "original_text": str,               # Transcribed text
    "final_text": str,                  # Final text (translated or original)
    "was_translated": bool,             # Whether translation occurred
    "detected_language": str,           # Auto-detected language
    "target_language": str,             # Target language
    "error": str,                       # Error message if failed
    "steps": {                          # Detailed step results
        "audio_extraction": {...},
        "transcription": {...},
        "translation": {...},
        "voice_cloning": {...}
    }
}
```

## 🌍 Supported Languages

The workflow supports 100+ languages through Google Translate. Common codes:

- English: `en`
- French: `fr`
- Spanish: `es`
- German: `de`
- Italian: `it`
- Portuguese: `pt`
- Chinese: `zh`
- Japanese: `ja`
- Korean: `ko`
- Russian: `ru`
- Arabic: `ar`
- Hindi: `hi`

## 🎯 Examples

### Basic Usage

```python
# English video → French voice clone
result = complete_video_to_voice_workflow(
    video_path="english_video.mp4",
    reference_audio_path="french_voice_reference.wav",
    target_language="fr",
    output_path="outputs/french_cloned.wav"
)
```

### Batch Processing

```python
videos = ["video1.mp4", "video2.mp4", "video3.mp4"]
reference = "reference_audio.wav"

for i, video in enumerate(videos):
    result = complete_video_to_voice_workflow(
        video_path=video,
        reference_audio_path=reference,
        target_language="es",
        output_path=f"outputs/batch_{i+1}.wav"
    )
```

### Custom Settings

```python
result = complete_video_to_voice_workflow(
    video_path="input.mp4",
    reference_audio_path="reference.wav",
    target_language="de",
    source_language="en",  # Specify source instead of auto-detect
    cleanup_temp_files=False,  # Keep temp files for debugging
    output_path="outputs/custom_output.wav"
)
```

## 📁 File Structure

```
voice-cloning/
├── example_workflow.py           # 🎬 Complete workflow examples
├── run_workflow.bat            # 🖱️ Windows batch script
├── app/
│   └── services/
│       ├── voice_clone.py      # 🗣️ Enhanced with workflow function
│       ├── audio_extraction.py # 📹 Audio extraction service
│       ├── whisper_transcribe.py # 🎤 Transcription service
│       └── translate.py        # 🌍 Translation service
├── outputs/                    # 📁 Generated output files
├── test_clip.mp4              # 📹 Your input video
└── reference_audio.wav        # 🎤 Your reference voice
```

## 🔧 Advanced Features

### Error Handling

The workflow includes comprehensive error handling:

- Automatic fallback if translation fails
- Detailed error messages for each step
- Graceful cleanup of temporary files

### Temporary File Management

- Temporary extracted audio files are automatically cleaned up
- Option to keep temp files for debugging (`cleanup_temp_files=False`)
- All temp files are tracked in the result dictionary

### Step-by-Step Results

Each workflow step returns detailed results:

- Audio extraction: duration, sample rate, file size
- Transcription: confidence score, detected language, segments
- Translation: confidence score, source/target languages
- Voice cloning: model used, processing time

## 🔍 Troubleshooting

### Common Issues

1. **FFmpeg not found**

   - Install FFmpeg and add to system PATH
   - Test with: `ffmpeg -version`

2. **Video file not found**

   - Check file path and extension
   - Ensure MP4 format is supported

3. **Reference audio issues**

   - Use WAV format for best results
   - 10-30 seconds of clear speech
   - Minimal background noise

4. **Translation errors**

   - Check internet connection
   - Verify language codes are correct
   - Workflow will fallback to original text

5. **Voice cloning failures**
   - Ensure reference audio is high quality
   - Check available disk space
   - Try different TTS models if needed

### Performance Tips

- **GPU Acceleration**: Install CUDA-compatible PyTorch for faster processing
- **Model Selection**: Use larger Whisper models (`medium`, `large`) for better accuracy
- **Audio Quality**: Higher quality reference audio = better voice cloning
- **Video Length**: Process shorter clips first to test setup

## 📊 Expected Processing Times

| Step             | Duration (approx.)                    |
| ---------------- | ------------------------------------- |
| Audio extraction | 10-30 seconds                         |
| Transcription    | 1-3 minutes (depends on audio length) |
| Translation      | 5-15 seconds                          |
| Voice cloning    | 2-5 minutes (depends on text length)  |

**Total:** 3-8 minutes for typical short videos

## ✅ Success Indicators

When the workflow completes successfully:

```
🎉 WORKFLOW COMPLETED SUCCESSFULLY!
📁 Input Video: input_video.mp4
📄 Transcribed: Hello, this is a test video
📄 Translated: Bonjour, ceci est une vidéo de test
🎵 Final Output: outputs/cloned_voice.wav
```

## 🤝 Integration

This workflow integrates seamlessly with:

- FastAPI web applications
- Batch processing scripts
- Jupyter notebooks
- Command-line tools

The `complete_video_to_voice_workflow()` function can be imported and used in any Python project that needs video-to-voice cloning capabilities.

---

This complete workflow provides a production-ready solution for MP4 video to voice cloning with translation support!
