@echo off
echo Starting Video-to-Voice Cloning Pipeline...
echo ==========================================
echo.
echo This script will:
echo 1. Extract audio from your video
echo 2. Transcribe the audio to text
echo 3. Translate the text (if needed)
echo 4. Clone voice using reference audio
echo.
echo Make sure you have:
echo - A video file to process
echo - A reference audio file (reference_audio.wav)
echo - Python with required packages installed
echo.
pause
echo.
python complete_pipeline.py
pause
