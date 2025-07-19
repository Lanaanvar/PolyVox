import os
import asyncio
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import ValidationError
import io

from ..models.schemas import (
    DubbingRequest,
    DubbingResult,
    JobStatus,
    ApiResponse,
    TranscriptionResult,
    VoiceCloningRequest,
    AudioFormat,
    ProcessingStatus,
    HealthCheck,
)
from ..services.audio_extraction import audio_extraction_service
from ..services.whisper_transcribe import whisper_service
from ..services.translate import translation_service
from ..services.tts import tts_service
from ..services.voice_clone import voice_clone_service, synthesize_with_cloned_voice
from ..utils.helpers import (
    file_manager,
    job_manager,
    ValidationUtils,
    ErrorHandler,
    format_duration,
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/v1", tags=["dubbing"])

# Maximum file size (200MB)
MAX_FILE_SIZE = 200 * 1024 * 1024


@router.get("/health", response_model=HealthCheck)
async def health_check():
    """Health check endpoint"""
    try:
        services_status = {
            "audio_extraction": True,
            "whisper_transcription": whisper_service.model is not None,
            "translation": True,
            "tts": tts_service.client is not None,
            "voice_cloning": voice_clone_service.tts_model is not None,
        }

        return HealthCheck(
            status="healthy",
            version="1.0.0",
            timestamp=datetime.now().isoformat(),
            services=services_status,
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Health check failed")


@router.post("/dub", response_model=DubbingResult)
async def create_dubbing_job(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    source_language: str = Form("auto"),
    target_language: str = Form("en"),
    tts_voice: str = Form("en-US-Wavenet-D"),
    speaking_rate: float = Form(1.0),
    pitch: float = Form(0.0),
    volume_gain_db: float = Form(0.0),
    use_voice_cloning: bool = Form(False),
    preserve_original_timing: bool = Form(True),
    reference_audio: Optional[UploadFile] = File(None),
):
    """
    Create a new dubbing job

    Args:
        file: Input video/audio file
        source_language: Source language code
        target_language: Target language code
        tts_voice: TTS voice name
        speaking_rate: Speaking rate
        pitch: Pitch adjustment
        volume_gain_db: Volume gain
        use_voice_cloning: Whether to use voice cloning
        preserve_original_timing: Whether to preserve original timing
        reference_audio: Reference audio for voice cloning

    Returns:
        DubbingResult with job information
    """
    try:
        # Validate file size
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f}MB",
            )

        # Create job
        job_id = job_manager.create_job("dubbing")

        # Save uploaded file
        input_path = file_manager.create_temp_file(
            suffix=f".{file.filename.split('.')[-1]}"
        )

        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        # Save reference audio if provided
        reference_path = None
        if use_voice_cloning and reference_audio:
            reference_path = file_manager.create_temp_file(
                suffix=f".{reference_audio.filename.split('.')[-1]}"
            )

            with open(reference_path, "wb") as buffer:
                ref_content = await reference_audio.read()
                buffer.write(ref_content)

        # Create request object
        request = DubbingRequest(
            source_language=source_language,
            target_language=target_language,
            tts_voice=tts_voice,
            speaking_rate=speaking_rate,
            pitch=pitch,
            volume_gain_db=volume_gain_db,
            use_voice_cloning=use_voice_cloning,
            preserve_original_timing=preserve_original_timing,
        )

        # Start background processing
        background_tasks.add_task(
            process_dubbing_job, job_id, input_path, reference_path, request
        )

        # Return initial result
        return DubbingResult(
            job_id=job_id,
            status=ProcessingStatus.PENDING,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating dubbing job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str):
    """Get job status"""
    try:
        job = job_manager.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        return JobStatus(
            job_id=job_id,
            status=job["status"],
            progress=job.get("progress", 0.0),
            current_step=job.get("current_step", "unknown"),
            estimated_completion=job.get("estimated_completion"),
            error_message=job.get("error_message"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job status: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/jobs/{job_id}/result", response_model=DubbingResult)
async def get_job_result(job_id: str):
    """Get job result"""
    try:
        job = job_manager.get_job(job_id)

        if not job:
            raise HTTPException(status_code=404, detail="Job not found")

        if job["status"] not in ["completed", "failed"]:
            raise HTTPException(status_code=202, detail="Job not completed yet")

        return DubbingResult(
            job_id=job_id,
            status=job["status"],
            transcription=job.get("transcription"),
            translation=job.get("translation"),
            tts_audio_url=job.get("tts_audio_url"),
            final_video_url=job.get("final_video_url"),
            processing_time=job.get("processing_time"),
            error_message=job.get("error_message"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting job result: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/transcribe", response_model=TranscriptionResult)
async def transcribe_audio(
    file: UploadFile = File(...),
    language: str = Form("auto"),
    model_size: str = Form("base"),
):
    """
    Transcribe audio file

    Args:
        file: Audio file to transcribe
        language: Source language code
        model_size: Whisper model size

    Returns:
        TranscriptionResult with transcription segments
    """
    try:
        # Validate file size
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024):.0f}MB",
            )

        # Save uploaded file
        input_path = file_manager.create_temp_file(
            suffix=f".{file.filename.split('.')[-1]}"
        )

        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)

        try:
            # Extract audio if video file
            validation_result = audio_extraction_service.validate_file(input_path)

            if validation_result["valid"] and validation_result["type"] == "video":
                # Extract audio
                extraction_result = audio_extraction_service.extract_audio_from_video(
                    input_path
                )
                audio_path = extraction_result.audio_file_path
            else:
                audio_path = input_path

            # Transcribe audio
            result = whisper_service.transcribe_audio(
                audio_path,
                language=language if language != "auto" else None,
                model_size=model_size,
            )

            return result

        finally:
            # Clean up files
            file_manager.cleanup_file(input_path)
            if "audio_path" in locals() and audio_path != input_path:
                file_manager.cleanup_file(audio_path)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error transcribing audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/translate")
async def translate_text(
    text: str = Form(...),
    source_language: str = Form("auto"),
    target_language: str = Form("en"),
):
    """
    Translate text

    Args:
        text: Text to translate
        source_language: Source language code
        target_language: Target language code

    Returns:
        Translation result
    """
    try:
        result = translation_service.translate_text(
            text, source_language, target_language
        )

        return result

    except Exception as e:
        logger.error(f"Error translating text: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tts")
async def text_to_speech(
    text: str = Form(...),
    voice_name: str = Form("en-US-Wavenet-D"),
    language_code: str = Form("en-US"),
    speaking_rate: float = Form(1.0),
    pitch: float = Form(0.0),
    volume_gain_db: float = Form(0.0),
):
    """
    Generate speech from text

    Args:
        text: Text to synthesize
        voice_name: TTS voice name
        language_code: Language code
        speaking_rate: Speaking rate
        pitch: Pitch adjustment
        volume_gain_db: Volume gain

    Returns:
        Audio file response
    """
    try:
        # Generate speech
        result = tts_service.synthesize_speech(
            text, voice_name, language_code, speaking_rate, pitch, volume_gain_db
        )

        # Return audio as streaming response
        return StreamingResponse(
            io.BytesIO(result.audio_data),
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"},
        )

    except Exception as e:
        logger.error(f"Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/voice-clone")
async def clone_voice(
    text: str = Form(...),
    reference_audio: UploadFile = File(...),
    target_language: str = Form("en"),
    speed: float = Form(1.0),
):
    """
    Clone voice from reference audio

    Args:
        text: Text to synthesize
        reference_audio: Reference audio file
        target_language: Target language code
        speed: Speech speed

    Returns:
        Audio file response
    """
    try:
        # Save reference audio
        reference_path = file_manager.create_temp_file(
            suffix=f".{reference_audio.filename.split('.')[-1]}"
        )

        with open(reference_path, "wb") as buffer:
            content = await reference_audio.read()
            buffer.write(content)

        try:
            # Clone voice
            result = voice_clone_service.clone_voice(
                text, reference_path, target_language, speed=speed
            )

            # Return audio as streaming response
            return StreamingResponse(
                io.BytesIO(result.cloned_audio_data),
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=cloned_voice.wav"
                },
            )

        finally:
            # Clean up reference audio
            file_manager.cleanup_file(reference_path)

    except Exception as e:
        logger.error(f"Error cloning voice: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-languages")
async def get_supported_languages():
    """Get supported languages"""
    try:
        return {
            "whisper": whisper_service.get_supported_languages(),
            "translation": list(translation_service.get_supported_languages().keys()),
            "tts": list(tts_service.get_supported_languages().keys()),
            "voice_cloning": voice_clone_service.get_supported_languages(),
        }

    except Exception as e:
        logger.error(f"Error getting supported languages: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/supported-voices")
async def get_supported_voices():
    """Get supported TTS voices"""
    try:
        return tts_service.get_supported_voices()

    except Exception as e:
        logger.error(f"Error getting supported voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """Delete a job"""
    try:
        success = job_manager.delete_job(job_id)

        if not success:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"message": "Job deleted successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting job: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Background task functions
async def process_dubbing_job(
    job_id: str, input_path: str, reference_path: Optional[str], request: DubbingRequest
):
    """Process dubbing job in background"""
    try:
        # Update job status
        job_manager.update_job(
            job_id,
            status=ProcessingStatus.PROCESSING,
            progress=0.0,
            current_step="Starting processing",
        )

        # Step 1: Extract audio
        job_manager.update_job(job_id, progress=10.0, current_step="Extracting audio")

        validation_result = audio_extraction_service.validate_file(input_path)

        if validation_result["valid"] and validation_result["type"] == "video":
            extraction_result = audio_extraction_service.extract_audio_from_video(
                input_path
            )
            audio_path = extraction_result.audio_file_path
        else:
            audio_path = input_path

        # Step 2: Transcribe
        job_manager.update_job(job_id, progress=30.0, current_step="Transcribing audio")

        transcription = whisper_service.transcribe_audio(
            audio_path,
            language=(
                request.source_language if request.source_language != "auto" else None
            ),
        )

        # Step 3: Translate
        job_manager.update_job(job_id, progress=50.0, current_step="Translating text")

        translations = translation_service.translate_segments(
            transcription.segments, request.source_language, request.target_language
        )

        # Step 4: Generate speech
        job_manager.update_job(job_id, progress=70.0, current_step="Generating speech")

        if request.use_voice_cloning and reference_path:
            # Use voice cloning
            tts_results = []
            for translation in translations:
                if translation.translated_text.strip():
                    clone_result = voice_clone_service.clone_voice(
                        translation.translated_text,
                        reference_path,
                        request.target_language,
                    )
                    tts_results.append(clone_result)
        else:
            # Use regular TTS
            tts_results = tts_service.synthesize_translations(
                translations,
                request.tts_voice,
                request.target_language,
                request.speaking_rate,
                request.pitch,
                request.volume_gain_db,
            )

        # Step 5: Combine and finalize
        job_manager.update_job(job_id, progress=90.0, current_step="Finalizing")

        # Save results (placeholder - implement actual file saving)
        tts_audio_url = f"/api/v1/jobs/{job_id}/audio"
        final_video_url = f"/api/v1/jobs/{job_id}/video"

        # Complete job
        job_manager.update_job(
            job_id,
            status=ProcessingStatus.COMPLETED,
            progress=100.0,
            current_step="Completed",
            transcription=transcription,
            translation=translations,
            tts_audio_url=tts_audio_url,
            final_video_url=final_video_url,
            processing_time=60.0,  # Placeholder
        )

        # Clean up
        file_manager.cleanup_file(input_path)
        if audio_path != input_path:
            file_manager.cleanup_file(audio_path)
        if reference_path:
            file_manager.cleanup_file(reference_path)

    except Exception as e:
        logger.error(f"Error processing dubbing job {job_id}: {e}")

        # Update job with error
        job_manager.update_job(
            job_id, status=ProcessingStatus.FAILED, error_message=str(e)
        )

        # Clean up on error
        try:
            file_manager.cleanup_file(input_path)
            if "audio_path" in locals() and audio_path != input_path:
                file_manager.cleanup_file(audio_path)
            if reference_path:
                file_manager.cleanup_file(reference_path)
        except:
            pass


@router.post("/voice-clone-simple")
async def voice_clone_simple(
    text: str = Form(...),
    reference_audio: UploadFile = File(...),
    output_filename: str = Form("cloned_speech.wav"),
):
    """
    Simple voice cloning endpoint using your preferred method

    Args:
        text: Text to synthesize
        reference_audio: Reference audio file for voice cloning
        output_filename: Name for the output file

    Returns:
        Cloned audio file
    """
    try:
        # Save uploaded reference audio
        reference_path = file_manager.create_temp_file(
            suffix=f".{reference_audio.filename.split('.')[-1]}"
        )

        with open(reference_path, "wb") as buffer:
            content = await reference_audio.read()
            buffer.write(content)

        # Create output path
        output_path = file_manager.create_temp_file(suffix=".wav")

        # Perform voice cloning using your function
        success = synthesize_with_cloned_voice(text, reference_path, output_path)

        if not success:
            raise HTTPException(status_code=500, detail="Voice cloning failed")

        # Clean up reference audio
        file_manager.cleanup_file(reference_path)

        # Return the cloned audio file
        return FileResponse(
            output_path, media_type="audio/wav", filename=output_filename
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in simple voice cloning: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Import datetime for health check
from datetime import datetime
