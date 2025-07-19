import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from decouple import config
import uvicorn

from .api.routes import router
from .services.whisper_transcribe import whisper_service
from .services.tts import tts_service
from .services.voice_clone import voice_clone_service
from .utils.helpers import file_manager, job_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("dubbing.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Configuration
DEBUG = config("DEBUG", default=False, cast=bool)
HOST = config("HOST", default="0.0.0.0")
PORT = config("PORT", default=8000, cast=int)

# Create necessary directories
UPLOAD_DIR = config("UPLOAD_DIR", default="uploads")
OUTPUT_DIR = config("OUTPUT_DIR", default="outputs")
TEMP_DIR = config("TEMP_DIR", default="temp")

for directory in [UPLOAD_DIR, OUTPUT_DIR, TEMP_DIR]:
    os.makedirs(directory, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("Starting Dubbing API server...")

    # Print startup message
    logger.info("=" * 50)
    logger.info("🎬 Dubbing API Server Started")
    logger.info("=" * 50)
    logger.info(f"🌐 Server running on: http://{HOST}:{PORT}")
    logger.info(f"📚 API Documentation: http://{HOST}:{PORT}/docs")
    logger.info(f"🔄 Interactive API: http://{HOST}:{PORT}/redoc")
    logger.info("=" * 50)

    # Initialize services
    try:
        # Initialize Whisper service
        logger.info("Initializing Whisper service...")
        whisper_service.load_model("base")

        # Initialize TTS service
        logger.info("Initializing TTS service...")
        # TTS service is initialized in __init__

        # Initialize voice cloning service
        logger.info("Initializing voice cloning service...")
        # Voice cloning service will be initialized on first use to avoid long startup times
        logger.info("Voice cloning service will be initialized on first use")

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Error initializing services: {e}")
        logger.warning("Some services may not be available")

    yield

    # Cleanup on shutdown
    logger.info("Shutting down Dubbing API server...")
    logger.info("=" * 50)
    logger.info("🛑 Dubbing API Server Shutting Down")
    logger.info("=" * 50)

    try:
        # Cleanup services
        whisper_service.cleanup()
        voice_clone_service.cleanup()

        logger.info("Services cleaned up successfully")

    except Exception as e:
        logger.error(f"Error during cleanup: {e}")


# Create FastAPI app
app = FastAPI(
    title="Dubbing API",
    description="""
    A comprehensive API for foreign language to English dubbing automation.
    
    Features:
    - Audio extraction from video files
    - Speech-to-text transcription using Whisper
    - Text translation to English
    - Text-to-speech synthesis with Google Cloud TTS
    - Voice cloning capabilities
    - Complete dubbing workflow automation
    """,
    version="1.0.0",
    lifespan=lifespan,
    debug=DEBUG,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc) if DEBUG else "An error occurred",
        },
    )


# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests"""
    logger.info(f"{request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response


# Include API routes
app.include_router(router)


# Health check endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Dubbing API is running",
        "version": "1.0.0",
        "status": "healthy",
    }


# Serve static files (for output files)
if os.path.exists(OUTPUT_DIR):
    app.mount("/outputs", StaticFiles(directory=OUTPUT_DIR), name="outputs")


if __name__ == "__main__":
    # Run the server
    uvicorn.run("app.main:app", host=HOST, port=PORT, reload=DEBUG, log_level="info")
