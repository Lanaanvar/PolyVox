@echo off
echo 🧪 Quick Workflow Test
echo ===================
echo.
echo This will test your setup and run a sample workflow
echo.
echo Required files:
echo - test_clip.mp4 (your video file)
echo - reference_audio.wav (your reference voice)
echo.
pause
echo.
echo Running test...
.venv\Scripts\python.exe test_workflow.py
pause
