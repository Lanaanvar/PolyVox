@echo off
echo Complete Video-to-Voice Cloning Workflow
echo =====================================
echo.
echo This workflow processes:
echo 1. MP4 video input
echo 2. Audio extraction
echo 3. Speech transcription
echo 4. Text translation (optional)
echo 5. Voice cloning with reference audio
echo.
echo Required files:
echo - Your video file: test_clip.mp4 (or modify the script)
echo - Reference audio: reference_audio.wav
echo.
echo Output will be saved to: outputs/cloned_voice_output.wav
echo.
pause
echo.
echo Starting workflow...
.venv\Scripts\python.exe example_workflow.py
echo.
pause
