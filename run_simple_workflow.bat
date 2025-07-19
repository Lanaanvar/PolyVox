@echo off
echo 🎬 Simple Video-to-Voice Cloning Workflow
echo =====================================
echo.
echo This is a simplified version that avoids import issues
echo by importing libraries only when needed.
echo.
echo Required files:
echo - test_clip.mp4 (your video file)
echo - reference_audio.wav (your reference voice)
echo.
echo Output: outputs/simple_test_output.wav
echo.
pause
echo.
echo Running simplified workflow...
.venv\Scripts\python.exe simple_workflow.py
pause
