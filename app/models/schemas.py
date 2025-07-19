from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class AudioFormat(str, Enum):
    MP3 = "mp3"
    WAV = "wav"
    M4A = "m4a"
    FLAC = "flac"


class VideoFormat(str, Enum):
    MP4 = "mp4"
    AVI = "avi"
    MKV = "mkv"
    MOV = "mov"
    WEBM = "webm"


class LanguageCode(str, Enum):
    AUTO = "auto"
    ENGLISH = "en"
    SPANISH = "es"
    FRENCH = "fr"
    GERMAN = "de"
    ITALIAN = "it"
    PORTUGUESE = "pt"
    RUSSIAN = "ru"
    CHINESE = "zh"
    JAPANESE = "ja"
    KOREAN = "ko"
    ARABIC = "ar"
    HINDI = "hi"


class TTSVoice(str, Enum):
    WAVENET_A = "en-US-Wavenet-A"
    WAVENET_B = "en-US-Wavenet-B"
    WAVENET_C = "en-US-Wavenet-C"
    WAVENET_D = "en-US-Wavenet-D"
    WAVENET_E = "en-US-Wavenet-E"
    WAVENET_F = "en-US-Wavenet-F"


class ProcessingStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class DubbingRequest(BaseModel):
    source_language: LanguageCode = LanguageCode.AUTO
    target_language: LanguageCode = LanguageCode.ENGLISH
    tts_voice: TTSVoice = TTSVoice.WAVENET_D
    speaking_rate: float = Field(default=1.0, ge=0.25, le=4.0)
    pitch: float = Field(default=0.0, ge=-20.0, le=20.0)
    volume_gain_db: float = Field(default=0.0, ge=-96.0, le=16.0)
    use_voice_cloning: bool = False
    preserve_original_timing: bool = True


class VoiceCloningRequest(BaseModel):
    reference_audio_duration: Optional[float] = None
    voice_similarity_threshold: float = Field(default=0.8, ge=0.0, le=1.0)
    clone_language: LanguageCode = LanguageCode.ENGLISH


class TranscriptionSegment(BaseModel):
    id: int
    start_time: float
    end_time: float
    text: str
    confidence: float
    language: Optional[str] = None


class TranscriptionResult(BaseModel):
    segments: List[TranscriptionSegment]
    detected_language: Optional[str] = None
    total_duration: float
    confidence_score: float
    success: bool = True
    error_message: Optional[str] = None
    text: Optional[str] = None  # Full text from all segments
    language: Optional[str] = None  # Alias for detected_language


class TranslationResult(BaseModel):
    original_text: str
    translated_text: str
    source_language: str
    target_language: str
    confidence_score: float


class TTSResult(BaseModel):
    audio_data: bytes
    duration: float
    sample_rate: int
    format: AudioFormat
    success: bool = True
    error_message: Optional[str] = None
    audio_file_path: Optional[str] = None


class DubbingResult(BaseModel):
    job_id: str
    status: ProcessingStatus
    transcription: Optional[TranscriptionResult] = None
    translation: Optional[List[TranslationResult]] = None
    tts_audio_url: Optional[str] = None
    final_video_url: Optional[str] = None
    processing_time: Optional[float] = None
    error_message: Optional[str] = None


class JobStatus(BaseModel):
    job_id: str
    status: ProcessingStatus
    progress: float = Field(ge=0.0, le=100.0)
    current_step: str
    estimated_completion: Optional[float] = None
    error_message: Optional[str] = None


class AudioExtractionResult(BaseModel):
    audio_file_path: str
    duration: float
    sample_rate: int
    channels: int
    format: AudioFormat
    file_size: int = 0
    success: bool = True
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class VoiceCloneResult(BaseModel):
    cloned_audio_data: bytes
    similarity_score: float
    processing_time: float
    reference_audio_path: str
    success: bool = True
    error_message: Optional[str] = None
    output_path: Optional[str] = None


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None


class HealthCheck(BaseModel):
    status: str
    version: str
    timestamp: str
    services: Dict[str, bool]
