@echo off
echo 🔧 Setting Up Voice Cloning Environment
echo ====================================
echo.
echo This script will:
echo 1. Create/activate virtual environment
echo 2. Install required Python packages
echo 3. Check for FFmpeg
echo 4. Test the installation
echo.
pause

echo.
echo 📦 Step 1: Setting up Python virtual environment...
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists.
)

echo.
echo 📚 Step 2: Installing required packages...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install TTS torch googletrans==4.0.0rc1 openai-whisper ffmpeg-python pydub transformers

echo.
echo 🔍 Step 3: Checking FFmpeg installation...
ffmpeg -version >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ FFmpeg is installed and available
) else (
    echo ❌ FFmpeg not found in PATH
    echo.
    echo Please install FFmpeg:
    echo 1. Download from: https://ffmpeg.org/download.html
    echo 2. Extract to C:\ffmpeg\
    echo 3. Add C:\ffmpeg\bin to your system PATH
    echo.
    echo Or install with chocolatey: choco install ffmpeg
    echo.
)

echo.
echo 📋 Step 4: Checking required files...
if exist "test_clip.mp4" (
    echo ✅ test_clip.mp4 found
) else (
    echo ⚠️  test_clip.mp4 not found - please add your MP4 video file
)

if exist "reference_audio.wav" (
    echo ✅ reference_audio.wav found
) else (
    echo ⚠️  reference_audio.wav not found - please add your reference voice audio
)

echo.
echo 🧪 Step 5: Testing installation...
.venv\Scripts\python.exe -c "
try:
    from TTS.api import TTS
    print('✅ TTS (Coqui) installed correctly')
except Exception as e:
    print(f'❌ TTS error: {e}')

try:
    import whisper
    print('✅ Whisper installed correctly')
except Exception as e:
    print(f'❌ Whisper error: {e}')

try:
    from googletrans import Translator
    print('✅ Google Translate installed correctly')
except Exception as e:
    print(f'❌ Google Translate error: {e}')

try:
    import ffmpeg
    print('✅ FFmpeg Python binding installed correctly')
except Exception as e:
    print(f'❌ FFmpeg Python error: {e}')
"

echo.
echo 🎉 Setup Complete!
echo.
echo Next steps:
echo 1. Add your video file as 'test_clip.mp4'
echo 2. Add your reference voice as 'reference_audio.wav'
echo 3. Run: run_workflow.bat
echo.
echo Or test with: test_setup.bat
echo.
pause
