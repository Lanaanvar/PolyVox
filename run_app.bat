@echo off
echo.
echo ======================================
echo   Voice Cloning Application Launcher
echo ======================================
echo.

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

:: Check if reference audio exists
if not exist "reference_audio.wav" (
    if not exist "reference_audio.mp3" (
        if not exist "reference_audio.m4a" (
            echo.
            echo WARNING: No reference audio file found!
            echo Please provide a reference audio file:
            echo   1. Record a 10-30 second audio clip of the target voice
            echo   2. Save it as 'reference_audio.wav' in this directory
            echo   3. Run this script again
            echo.
            pause
            exit /b 1
        )
    )
)

:: Ask user what to do
echo Choose an option:
echo.
echo 1. Install dependencies and run application
echo 2. Run application only
echo 3. Install dependencies only
echo 4. Exit
echo.
set /p choice="Enter your choice (1-4): "

if "%choice%"=="1" goto install_and_run
if "%choice%"=="2" goto run_only
if "%choice%"=="3" goto install_only
if "%choice%"=="4" goto exit
echo Invalid choice. Please try again.
pause
goto :eof

:install_and_run
echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.
echo Running application...
python run_app.py
pause
goto :eof

:run_only
echo.
echo Running application...
python run_app.py
pause
goto :eof

:install_only
echo.
echo Installing dependencies...
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo.
echo Dependencies installed successfully!
pause
goto :eof

:exit
echo.
echo Goodbye!
pause
exit /b 0
