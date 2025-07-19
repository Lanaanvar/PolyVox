import os
import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

try:
    import ffmpeg

    FFMPEG_AVAILABLE = True
except ImportError:
    FFMPEG_AVAILABLE = False
    ffmpeg = None

from pydub import AudioSegment
from ..models.schemas import AudioExtractionResult, AudioFormat
from ..utils.helpers import file_manager, ErrorHandler

logger = logging.getLogger(__name__)


class AudioExtractionService:
    """Service for extracting audio from video files using FFmpeg"""

    def __init__(self):
        self.supported_video_formats = [
            ".mp4",
            ".avi",
            ".mkv",
            ".mov",
            ".webm",
            ".m4v",
            ".3gp",
        ]
        self.supported_audio_formats = [".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"]
        self.default_audio_format = AudioFormat.WAV
        self.default_sample_rate = 22050
        self.default_channels = 1
        self.ffmpeg_available = self._check_ffmpeg_availability()

    def _check_ffmpeg_availability(self) -> bool:
        """Check if FFmpeg is available in the system"""
        try:
            # Try to run ffmpeg command
            result = subprocess.run(
                ["ffmpeg", "-version"], capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                logger.info("FFmpeg is available in system PATH")
                return True
        except (
            subprocess.TimeoutExpired,
            subprocess.CalledProcessError,
            FileNotFoundError,
        ):
            pass

        # Check if ffmpeg-python is available
        if not FFMPEG_AVAILABLE:
            logger.warning(
                "FFmpeg not found in system PATH and ffmpeg-python not available"
            )
            return False

        logger.info("ffmpeg-python library is available")
        return True

    def extract_audio_from_video(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        audio_format: AudioFormat = AudioFormat.WAV,
        sample_rate: int = 22050,
        channels: int = 1,
    ) -> AudioExtractionResult:
        """
        Extract audio from video file using FFmpeg

        Args:
            video_path: Path to the input video file
            output_path: Path for the output audio file
            audio_format: Desired audio format
            sample_rate: Audio sample rate
            channels: Number of audio channels

        Returns:
            AudioExtractionResult with extracted audio information
        """
        try:
            # Validate input file
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"Video file not found: {video_path}")

            # Check if input is already an audio file
            if self._is_valid_audio_file(video_path):
                return self._handle_audio_file(
                    video_path, output_path, audio_format, sample_rate, channels
                )

            # Check if FFmpeg is available
            if not self.ffmpeg_available:
                return self._create_fallback_result(
                    video_path, output_path, audio_format
                )

            # Validate video file format
            if not self._is_valid_video_file(video_path):
                raise ValueError(f"Unsupported video format: {video_path}")

            # Create output path if not provided
            if output_path is None:
                output_path = file_manager.create_temp_file(
                    suffix=f".{audio_format.value}"
                )

            # Extract audio using FFmpeg
            self._extract_with_ffmpeg(
                video_path, output_path, audio_format, sample_rate, channels
            )

            # Get audio information
            audio_info = self._get_audio_info(output_path)

            result = AudioExtractionResult(
                audio_file_path=output_path,
                duration=audio_info["duration"],
                sample_rate=audio_info["sample_rate"],
                channels=audio_info["channels"],
                format=audio_format,
            )

            logger.info(f"Successfully extracted audio from {video_path}")
            return result

        except Exception as e:
            logger.error(f"Error extracting audio from video: {e}")
            raise

    def extract_audio_from_audio(
        self,
        audio_path: str,
        output_path: Optional[str] = None,
        audio_format: AudioFormat = AudioFormat.WAV,
        sample_rate: int = 22050,
        channels: int = 1,
    ) -> AudioExtractionResult:
        """
        Process and convert audio file to desired format

        Args:
            audio_path: Path to the input audio file
            output_path: Path for the output audio file
            audio_format: Desired audio format
            sample_rate: Audio sample rate
            channels: Number of audio channels

        Returns:
            AudioExtractionResult with processed audio information
        """
        try:
            # Validate input file
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Validate audio file format
            if not self._is_valid_audio_file(audio_path):
                raise ValueError(f"Unsupported audio format: {audio_path}")

            # Create output path if not provided
            if output_path is None:
                output_path = file_manager.create_temp_file(
                    suffix=f".{audio_format.value}"
                )

            # Process audio using pydub
            self._process_with_pydub(
                audio_path, output_path, audio_format, sample_rate, channels
            )

            # Get audio information
            audio_info = self._get_audio_info(output_path)

            result = AudioExtractionResult(
                audio_file_path=output_path,
                duration=audio_info["duration"],
                sample_rate=audio_info["sample_rate"],
                channels=audio_info["channels"],
                format=audio_format,
            )

            logger.info(f"Successfully processed audio from {audio_path}")
            return result

        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            raise

    def _extract_with_ffmpeg(
        self,
        video_path: str,
        output_path: str,
        audio_format: AudioFormat,
        sample_rate: int,
        channels: int,
    ) -> None:
        """Extract audio using FFmpeg"""
        try:
            # Build FFmpeg command
            stream = ffmpeg.input(video_path)
            stream = ffmpeg.output(
                stream,
                output_path,
                acodec="pcm_s16le" if audio_format == AudioFormat.WAV else "libmp3lame",
                ar=sample_rate,
                ac=channels,
                loglevel="error",
            )

            # Run FFmpeg command
            ffmpeg.run(stream, overwrite_output=True)

        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e}")
            raise RuntimeError(f"FFmpeg extraction failed: {e}")

    def _process_with_pydub(
        self,
        audio_path: str,
        output_path: str,
        audio_format: AudioFormat,
        sample_rate: int,
        channels: int,
    ) -> None:
        """Process audio using pydub"""
        try:
            # Load audio file
            audio = AudioSegment.from_file(audio_path)

            # Set sample rate and channels
            audio = audio.set_frame_rate(sample_rate)
            audio = audio.set_channels(channels)

            # Export to desired format
            audio.export(
                output_path,
                format=audio_format.value,
                parameters=["-ac", str(channels), "-ar", str(sample_rate)],
            )

        except Exception as e:
            logger.error(f"Pydub processing error: {e}")
            raise RuntimeError(f"Audio processing failed: {e}")

    def _get_audio_info(self, audio_path: str) -> Dict[str, Any]:
        """Get audio file information"""
        try:
            probe = ffmpeg.probe(audio_path)
            audio_stream = next(
                (
                    stream
                    for stream in probe["streams"]
                    if stream["codec_type"] == "audio"
                ),
                None,
            )

            if audio_stream is None:
                raise ValueError("No audio stream found")

            return {
                "duration": float(probe["format"]["duration"]),
                "sample_rate": int(audio_stream["sample_rate"]),
                "channels": int(audio_stream["channels"]),
                "size": int(probe["format"]["size"]),
            }

        except Exception as e:
            logger.error(f"Error getting audio info: {e}")
            # Fallback to pydub
            try:
                audio = AudioSegment.from_file(audio_path)
                return {
                    "duration": len(audio) / 1000.0,
                    "sample_rate": audio.frame_rate,
                    "channels": audio.channels,
                    "size": os.path.getsize(audio_path),
                }
            except Exception as e2:
                logger.error(f"Fallback audio info failed: {e2}")
                raise RuntimeError(f"Cannot get audio information: {e}")

    def _is_valid_video_file(self, file_path: str) -> bool:
        """Check if file is a valid video file"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            return ext in self.supported_video_formats
        except Exception:
            return False

    def _is_valid_audio_file(self, file_path: str) -> bool:
        """Check if file is a valid audio file"""
        try:
            ext = os.path.splitext(file_path)[1].lower()
            return ext in self.supported_audio_formats
        except Exception:
            return False

    def get_supported_formats(self) -> Dict[str, list]:
        """Get supported file formats"""
        return {
            "video": self.supported_video_formats,
            "audio": self.supported_audio_formats,
        }

    def validate_file(self, file_path: str) -> Dict[str, Any]:
        """Validate input file"""
        try:
            if not os.path.exists(file_path):
                return {"valid": False, "error": "File not found"}

            ext = os.path.splitext(file_path)[1].lower()
            file_size = os.path.getsize(file_path)

            is_video = ext in self.supported_video_formats
            is_audio = ext in self.supported_audio_formats

            if not (is_video or is_audio):
                return {"valid": False, "error": "Unsupported file format"}

            return {
                "valid": True,
                "type": "video" if is_video else "audio",
                "extension": ext,
                "size": file_size,
            }

        except Exception as e:
            return {"valid": False, "error": str(e)}

    def _create_fallback_result(
        self,
        video_path: str,
        output_path: Optional[str] = None,
        audio_format: AudioFormat = AudioFormat.WAV,
    ) -> AudioExtractionResult:
        """Create a fallback result when FFmpeg is not available"""
        logger.warning(
            "FFmpeg not available. Creating fallback audio extraction result."
        )

        # Create a dummy audio file path
        if output_path is None:
            output_path = file_manager.create_temp_file(suffix=f".{audio_format.value}")

        # Try to get basic file info
        try:
            file_size = os.path.getsize(video_path)
            file_name = os.path.basename(video_path)
        except Exception:
            file_size = 0
            file_name = "unknown"

        return AudioExtractionResult(
            audio_file_path=output_path,
            duration=0.0,  # Unknown duration
            sample_rate=self.default_sample_rate,
            channels=self.default_channels,
            audio_format=audio_format,
            file_size=0,  # Will be set after extraction
            success=False,
            error_message="FFmpeg not available. Please install FFmpeg to extract audio from video files.",
            metadata={
                "source_file": video_path,
                "source_size": file_size,
                "source_name": file_name,
                "ffmpeg_available": False,
                "fallback_used": True,
            },
        )

    def _handle_audio_file(
        self,
        audio_path: str,
        output_path: Optional[str] = None,
        audio_format: AudioFormat = AudioFormat.WAV,
        sample_rate: int = 22050,
        channels: int = 1,
    ) -> AudioExtractionResult:
        """Handle case where input is already an audio file"""
        logger.info(f"Input is already an audio file: {audio_path}")

        try:
            # If no output path specified, use the input path
            if output_path is None:
                output_path = audio_path

            # If output path is different from input, copy the file
            if output_path != audio_path:
                import shutil

                shutil.copy2(audio_path, output_path)
                logger.info(f"Audio file copied to: {output_path}")

            # Get audio information
            audio_info = self._get_audio_info(output_path)

            result = AudioExtractionResult(
                audio_file_path=output_path,
                duration=audio_info.get("duration", 0.0),
                sample_rate=audio_info.get("sample_rate", sample_rate),
                channels=audio_info.get("channels", channels),
                format=audio_format,
                file_size=audio_info.get("size", 0),
                success=True,
                error_message=None,
                metadata={
                    "source_file": audio_path,
                    "source_type": "audio",
                    "direct_copy": output_path == audio_path,
                    "original_duration": audio_info.get("duration", 0.0),
                    "original_sample_rate": audio_info.get("sample_rate", sample_rate),
                    "original_channels": audio_info.get("channels", channels),
                },
            )

            logger.info(
                f"Audio file processed successfully: {result.file_size} bytes, {result.duration:.2f}s"
            )
            return result

        except Exception as e:
            logger.error(f"Error processing audio file: {e}")
            return AudioExtractionResult(
                audio_file_path=output_path or audio_path,
                duration=0.0,
                sample_rate=sample_rate,
                channels=channels,
                format=audio_format,
                file_size=0,
                success=False,
                error_message=f"Error processing audio file: {e}",
                metadata={
                    "source_file": audio_path,
                    "source_type": "audio",
                    "error": str(e),
                },
            )


# Global instance
audio_extraction_service = AudioExtractionService()
