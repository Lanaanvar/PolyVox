import os
import logging
import whisper
import torch
from typing import Optional, Dict, Any, List
from ..models.schemas import TranscriptionResult, TranscriptionSegment
from ..utils.helpers import ErrorHandler, file_manager

logger = logging.getLogger(__name__)


class WhisperTranscriptionService:
    """Service for speech-to-text transcription using OpenAI Whisper"""

    def __init__(self):
        self.model = None
        self.model_size = "base"  # Default model size
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.supported_languages = [
            "en",
            "zh",
            "de",
            "es",
            "ru",
            "ko",
            "fr",
            "ja",
            "pt",
            "tr",
            "pl",
            "ca",
            "nl",
            "ar",
            "sv",
            "it",
            "id",
            "hi",
            "fi",
            "vi",
            "he",
            "uk",
            "el",
            "ms",
            "cs",
            "ro",
            "da",
            "hu",
            "ta",
            "no",
            "th",
            "ur",
            "hr",
            "bg",
            "lt",
            "la",
            "mi",
            "ml",
            "cy",
            "sk",
            "te",
            "fa",
            "lv",
            "bn",
            "sr",
            "az",
            "sl",
            "kn",
            "et",
            "mk",
            "br",
            "eu",
            "is",
            "hy",
            "ne",
            "mn",
            "bs",
            "kk",
            "sq",
            "sw",
            "gl",
            "mr",
            "pa",
            "si",
            "km",
            "sn",
            "yo",
            "so",
            "af",
            "oc",
            "ka",
            "be",
            "tg",
            "sd",
            "gu",
            "am",
            "yi",
            "lo",
            "uz",
            "fo",
            "ht",
            "ps",
            "tk",
            "nn",
            "mt",
            "sa",
            "lb",
            "my",
            "bo",
            "tl",
            "mg",
            "as",
            "tt",
            "haw",
            "ln",
            "ha",
            "ba",
            "jw",
            "su",
        ]
        self.model_sizes = [
            "tiny",
            "base",
            "small",
            "medium",
            "large",
            "large-v2",
            "large-v3",
        ]

    def load_model(self, model_size: str = "base") -> None:
        """Load Whisper model"""
        try:
            if model_size not in self.model_sizes:
                raise ValueError(f"Invalid model size. Choose from: {self.model_sizes}")

            logger.info(f"Loading Whisper model: {model_size} on device: {self.device}")
            self.model = whisper.load_model(model_size, device=self.device)
            self.model_size = model_size
            logger.info(f"Whisper model {model_size} loaded successfully")

        except Exception as e:
            logger.error(f"Error loading Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}")

    def transcribe_audio(
        self,
        audio_path: str,
        language: Optional[str] = None,
        model_size: str = "base",
        temperature: float = 0.0,
        beam_size: Optional[int] = None,
        best_of: Optional[int] = None,
        patience: Optional[float] = None,
        word_timestamps: bool = False,
        initial_prompt: Optional[str] = None,
    ) -> TranscriptionResult:
        """
        Transcribe audio file using Whisper

        Args:
            audio_path: Path to the audio file
            language: Language code for transcription (auto-detect if None)
            model_size: Whisper model size to use
            temperature: Temperature for sampling
            beam_size: Beam size for beam search
            best_of: Number of candidates to consider
            patience: Patience for beam search
            word_timestamps: Whether to include word-level timestamps
            initial_prompt: Initial prompt for the model

        Returns:
            TranscriptionResult with transcription segments and metadata
        """
        try:
            # Validate input file
            if not os.path.exists(audio_path):
                raise FileNotFoundError(f"Audio file not found: {audio_path}")

            # Load model if not already loaded or if different size requested
            if self.model is None or self.model_size != model_size:
                self.load_model(model_size)

            # Validate language code
            if language and language not in self.supported_languages:
                logger.warning(
                    f"Language {language} not supported. Using auto-detection."
                )
                language = None

            # Prepare transcription options
            options = {
                "language": language,
                "temperature": temperature,
                "word_timestamps": word_timestamps,
                "initial_prompt": initial_prompt,
            }

            # Add optional parameters
            if beam_size is not None:
                options["beam_size"] = beam_size
            if best_of is not None:
                options["best_of"] = best_of
            if patience is not None:
                options["patience"] = patience

            # Perform transcription
            logger.info(f"Transcribing audio: {audio_path}")
            result = self.model.transcribe(audio_path, **options)

            # Process results
            segments = []
            for i, segment in enumerate(result["segments"]):
                transcription_segment = TranscriptionSegment(
                    id=i,
                    start_time=segment["start"],
                    end_time=segment["end"],
                    text=segment["text"].strip(),
                    confidence=segment.get("avg_logprob", 0.0),
                    language=result.get("language"),
                )
                segments.append(transcription_segment)

            # Calculate overall confidence score
            confidence_score = self._calculate_confidence_score(result["segments"])

            # Combine all segment texts
            full_text = " ".join([seg.text for seg in segments])

            transcription_result = TranscriptionResult(
                segments=segments,
                detected_language=result.get("language"),
                total_duration=segments[-1].end_time if segments else 0.0,
                confidence_score=confidence_score,
                success=True,
                error_message=None,
                text=full_text,
                language=result.get("language"),
            )

            logger.info(
                f"Transcription completed. Language: {result.get('language')}, "
                f"Segments: {len(segments)}, Confidence: {confidence_score:.2f}"
            )

            return transcription_result

        except Exception as e:
            logger.error(f"Error transcribing audio: {e}")
            return TranscriptionResult(
                segments=[],
                detected_language=None,
                total_duration=0.0,
                confidence_score=0.0,
                success=False,
                error_message=str(e),
                text="",
                language=None,
            )

    def transcribe_with_segments(
        self,
        audio_path: str,
        segment_duration: float = 30.0,
        language: Optional[str] = None,
        model_size: str = "base",
    ) -> TranscriptionResult:
        """
        Transcribe audio in segments for better performance on long files

        Args:
            audio_path: Path to the audio file
            segment_duration: Duration of each segment in seconds
            language: Language code for transcription
            model_size: Whisper model size to use

        Returns:
            TranscriptionResult with combined transcription segments
        """
        try:
            # Load model if needed
            if self.model is None or self.model_size != model_size:
                self.load_model(model_size)

            # Get audio duration
            from pydub import AudioSegment

            audio = AudioSegment.from_file(audio_path)
            total_duration = len(audio) / 1000.0  # Convert to seconds

            # If audio is short, transcribe normally
            if total_duration <= segment_duration:
                return self.transcribe_audio(audio_path, language, model_size)

            # Split audio into segments
            segments = []
            segment_count = int(total_duration / segment_duration) + 1

            logger.info(f"Transcribing audio in {segment_count} segments")

            for i in range(segment_count):
                start_time = i * segment_duration * 1000  # Convert to milliseconds
                end_time = min((i + 1) * segment_duration * 1000, len(audio))

                # Extract segment
                segment_audio = audio[start_time:end_time]

                # Save segment to temporary file
                temp_path = file_manager.create_temp_file(suffix=".wav")
                segment_audio.export(temp_path, format="wav")

                try:
                    # Transcribe segment
                    segment_result = self.transcribe_audio(
                        temp_path, language, model_size
                    )

                    # Adjust timestamps
                    time_offset = i * segment_duration
                    for seg in segment_result.segments:
                        seg.start_time += time_offset
                        seg.end_time += time_offset
                        seg.id = len(segments)
                        segments.append(seg)

                finally:
                    # Clean up temporary file
                    file_manager.cleanup_file(temp_path)

            # Calculate overall confidence
            confidence_score = (
                sum(seg.confidence for seg in segments) / len(segments)
                if segments
                else 0.0
            )

            result = TranscriptionResult(
                segments=segments,
                detected_language=segments[0].language if segments else None,
                total_duration=total_duration,
                confidence_score=confidence_score,
            )

            logger.info(
                f"Segmented transcription completed. Total segments: {len(segments)}"
            )
            return result

        except Exception as e:
            logger.error(f"Error in segmented transcription: {e}")
            raise RuntimeError(f"Segmented transcription failed: {e}")

    def _calculate_confidence_score(self, segments: List[Dict[str, Any]]) -> float:
        """Calculate overall confidence score from segments"""
        if not segments:
            return 0.0

        # Use average log probability as confidence score
        total_logprob = sum(seg.get("avg_logprob", 0.0) for seg in segments)
        avg_logprob = total_logprob / len(segments)

        # Convert log probability to confidence score (0-1)
        # Log probabilities are typically negative, so we normalize
        confidence = max(0.0, min(1.0, (avg_logprob + 1.0) / 1.0))
        return confidence

    def get_supported_languages(self) -> List[str]:
        """Get list of supported languages"""
        return self.supported_languages.copy()

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the loaded model"""
        return {
            "model_size": self.model_size,
            "device": self.device,
            "loaded": self.model is not None,
            "supported_languages": len(self.supported_languages),
            "available_models": self.model_sizes,
        }

    def detect_language(self, audio_path: str) -> Dict[str, Any]:
        """Detect language from audio file"""
        try:
            if self.model is None:
                self.load_model()

            # Load audio and detect language
            audio = whisper.load_audio(audio_path)
            audio = whisper.pad_or_trim(audio)

            # Make log-Mel spectrogram and move to device
            mel = whisper.log_mel_spectrogram(audio).to(self.device)

            # Detect language
            _, probs = self.model.detect_language(mel)

            # Get top 5 language predictions
            top_languages = sorted(probs.items(), key=lambda x: x[1], reverse=True)[:5]

            return {
                "detected_language": top_languages[0][0],
                "confidence": top_languages[0][1],
                "top_predictions": top_languages,
            }

        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            raise RuntimeError(f"Language detection failed: {e}")

    def cleanup(self) -> None:
        """Clean up resources"""
        if self.model is not None:
            del self.model
            self.model = None
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
            logger.info("Whisper model cleaned up")


# Global instance
whisper_service = WhisperTranscriptionService()

model = whisper.load_model("base")


def transcribe(audio_path):
    result = model.transcribe(audio_path)
    return result["text"]
