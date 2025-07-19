@echo off
echo Starting Voice Cloning FastAPI Server...
echo.

REM Install missing dependencies
echo Installing FastAPI dependencies...
pip install fastapi uvicorn[standard] python-decouple
echo.

REM Start the FastAPI server
echo Starting server on http://localhost:8000
echo API Documentation will be available at:
echo   - Swagger UI: http://localhost:8000/docs  
echo   - ReDoc: http://localhost:8000/redoc
echo.

python -m app.main

pause
