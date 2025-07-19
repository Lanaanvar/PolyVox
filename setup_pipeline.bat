@echo off
echo.
echo ==========================================
echo   Video-to-Voice Cloning Pipeline Setup
echo ==========================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

echo Choose an option:
echo.
echo 1. Install all dependencies
echo 2. Run video pipeline
echo 3. Run simple voice cloning
echo 4. Install dependencies and run pipeline
echo 5. Exit
echo.
set /p choice="Enter your choice (1-5): "

if "%choice%"=="1" goto install_deps
if "%choice%"=="2" goto run_video_pipeline
if "%choice%"=="3" goto run_voice_clone
if "%choice%"=="4" goto install_and_run
if "%choice%"=="5" goto exit
echo Invalid choice. Please try again.
pause
goto :eof

:install_deps
echo.
echo Installing dependencies...
echo.
echo Installing core dependencies...
python -m pip install TTS torch googletrans==4.0.0rc1

echo.
echo Installing additional dependencies for full pipeline...
python -m pip install openai-whisper ffmpeg-python pydub

if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install some dependencies
    echo Please check the error messages above
    pause
    exit /b 1
)

echo.
echo ✅ All dependencies installed successfully!
echo.
echo Additional requirement: FFmpeg
echo Please install FFmpeg from https://ffmpeg.org/download.html
echo and add it to your system PATH
echo.
pause
goto :eof

:run_video_pipeline
echo.
echo Running video-to-voice cloning pipeline...
python video_pipeline.py
pause
goto :eof

:run_voice_clone
echo.
echo Running simple voice cloning...
python app/services/voice-clone.py
pause
goto :eof

:install_and_run
echo.
echo Installing dependencies and running pipeline...
call :install_deps
if %errorlevel% equ 0 (
    echo.
    echo Now running the pipeline...
    python video_pipeline.py
)
pause
goto :eof

:exit
echo.
echo Goodbye!
pause
exit /b 0
