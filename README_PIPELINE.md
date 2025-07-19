# Complete Video-to-Voice Cloning Pipeline

This guide shows you how to run the complete application starting from video input, through audio extraction, transcription, translation, and finally voice cloning.

## 🎬 Complete Pipeline Overview

```
Video File → Audio Extraction → Transcription → Translation → Voice Cloning → Final Audio
```

## 📋 Prerequisites

### 1. Python Dependencies

```bash
# Core dependencies
pip install TTS torch googletrans==4.0.0rc1

# Additional dependencies for full pipeline
pip install openai-whisper ffmpeg-python pydub
```

### 2. FFmpeg Installation

**Windows:**

1. Download FFmpeg from https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg\`
3. Add `C:\ffmpeg\bin` to your system PATH

**Mac/Linux:**

```bash
# Mac
brew install ffmpeg

# Linux
sudo apt install ffmpeg
```

## 🚀 Quick Start

### Option 1: Automated Setup (Windows)

```cmd
setup_pipeline.bat
```

### Option 2: Manual Setup

1. Install dependencies:

   ```bash
   pip install TTS torch googletrans==4.0.0rc1 openai-whisper ffmpeg-python pydub
   ```

2. Run the pipeline:
   ```bash
   python video_pipeline.py
   ```

## 📁 File Structure

```
voice-cloning/
├── video_pipeline.py           # 🎬 Complete video-to-voice pipeline
├── video_to_voice_pipeline.py  # 🎬 Alternative comprehensive pipeline
├── app/services/voice-clone.py # 🗣️ Core voice cloning with translation
├── setup_pipeline.bat          # 🔧 Windows setup script
├── reference_audio.wav         # 🎤 Your reference voice (required)
└── README_PIPELINE.md          # 📖 This guide
```

## 🎯 How to Use

### Step 1: Prepare Reference Audio

1. Record or obtain a 10-30 second audio clip of the target voice
2. Save it as `reference_audio.wav` in the project directory
3. Ensure good audio quality (clear, minimal background noise)

### Step 2: Run the Pipeline

**Interactive Mode:**

```bash
python video_pipeline.py
```

**Programmatic Usage:**

```python
from video_pipeline import run_video_to_voice_pipeline

run_video_to_voice_pipeline(
    video_path="input_video.mp4",
    reference_audio="reference_audio.wav",
    target_language="fr",  # French
    output_name="final_output.wav"
)
```

### Step 3: Pipeline Steps Explained

1. **📹 Audio Extraction**

   - Extracts audio from your video file
   - Converts to WAV format (22050 Hz, mono)
   - Uses FFmpeg for reliable extraction

2. **🎤 Transcription**

   - Uses OpenAI Whisper to convert speech to text
   - Automatically detects the language
   - Provides high-quality transcription

3. **🌍 Translation**

   - Translates text to your target language
   - Uses Google Translate API
   - Maintains context and meaning

4. **🗣️ Voice Cloning**
   - Clones the reference voice
   - Synthesizes the translated text
   - Outputs high-quality audio

## 🎯 Usage Examples

### Example 1: French Video to English Voice Clone

```bash
# Input: French video, English reference voice
# Output: English speech in the reference voice
python video_pipeline.py
> Video file: french_video.mp4
> Target language: en
```

### Example 2: English Video to Spanish Voice Clone

```bash
# Input: English video, Spanish reference voice
# Output: Spanish speech in the reference voice
python video_pipeline.py
> Video file: english_video.mp4
> Target language: es
```

### Example 3: Same Language Voice Clone

```bash
# Input: English video, different English voice
# Output: Same content in the new voice
python video_pipeline.py
> Video file: english_video.mp4
> Target language: en
```

## 🔧 Advanced Configuration

### Custom Model Selection

Edit `video_pipeline.py` or `app/services/voice-clone.py`:

```python
# Change TTS model
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts", progress_bar=True, gpu=False)

# Change Whisper model
model = whisper.load_model("medium")  # Options: tiny, base, small, medium, large
```

### Batch Processing

```python
videos = ["video1.mp4", "video2.mp4", "video3.mp4"]
for video in videos:
    run_video_to_voice_pipeline(
        video_path=video,
        reference_audio="reference_audio.wav",
        target_language="fr",
        output_name=f"output_{video.replace('.mp4', '.wav')}"
    )
```

## 🎵 Output Files

The pipeline generates several files:

- `temp_extracted_audio.wav` - Extracted audio (deleted after processing)
- `video_cloned_speech.wav` - Final cloned voice output
- Console logs showing progress and results

## 🔍 Troubleshooting

### Common Issues

1. **FFmpeg not found**

   ```
   ❌ FFmpeg not found. Please install FFmpeg first.
   ```

   **Solution:** Install FFmpeg and add to PATH

2. **Reference audio not found**

   ```
   ❌ Reference audio not found: reference_audio.wav
   ```

   **Solution:** Provide a valid reference audio file

3. **Import errors**

   ```
   ❌ Cannot import voice cloning functions
   ```

   **Solution:** Run from the correct directory, install dependencies

4. **Video file not found**
   ```
   ❌ Video file not found: input.mp4
   ```
   **Solution:** Provide correct video file path

### Performance Tips

- **GPU Acceleration:** Set `gpu=True` in voice cloning if you have a CUDA-compatible GPU
- **Model Size:** Use larger Whisper models for better transcription accuracy
- **Audio Quality:** Use high-quality reference audio for better voice cloning
- **Video Length:** Process shorter videos first to test the pipeline

## 🌍 Supported Languages

**Translation:** 100+ languages supported by Google Translate

**Common language codes:**

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

## 📊 Quality Factors

### For Best Results:

1. **Reference Audio:** 10-30 seconds, clear, minimal background noise
2. **Video Quality:** Clear speech, not too much background noise
3. **Language Match:** Better results when source and target languages are similar
4. **Text Length:** Shorter texts generally produce better results

### Expected Processing Time:

- Audio extraction: ~30 seconds
- Transcription: ~1-2 minutes (depends on audio length)
- Translation: ~5-10 seconds
- Voice cloning: ~2-5 minutes (depends on text length)

## 🎉 Success Indicators

When the pipeline completes successfully, you'll see:

```
✅ PIPELINE COMPLETED SUCCESSFULLY!
📁 Original video: input_video.mp4
📄 Transcribed text: Hello, this is a test video
📄 Translated text: Bonjour, ceci est une vidéo de test
🎵 Final cloned speech: video_cloned_speech.wav
```

## 🔄 Alternative Workflows

### 1. Text-Only Voice Cloning

```bash
python app/services/voice-clone.py
```

### 2. Translation-Only

```python
from app.services.voice_clone import translate_text
result = translate_text("Hello world", "fr", "en")
```

### 3. Audio-Only Transcription

```python
from video_pipeline import transcribe_with_whisper
result = transcribe_with_whisper("audio.wav")
```

This complete pipeline gives you maximum flexibility to process videos with voice cloning and translation capabilities!
