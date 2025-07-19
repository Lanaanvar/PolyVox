import os
import logging
import requests
from typing import Optional, Dict, Any, List
from googletrans import Translator, LANGUAGES
from ..models.schemas import TranslationResult, TranscriptionSegment
from ..utils.helpers import ErrorHandler

logger = logging.getLogger(__name__)


class TranslationService:
    """Service for translating text using Google Translate API"""

    def __init__(self):
        self.translator = Translator()
        self.supported_languages = LANGUAGES
        self.language_codes = list(LANGUAGES.keys())
        self.max_text_length = 5000  # Google Translate limit

    def translate_text(
        self, text: str, source_language: str = "auto", target_language: str = "en"
    ) -> TranslationResult:
        """
        Translate text from source language to target language

        Args:
            text: Text to translate
            source_language: Source language code (auto for auto-detection)
            target_language: Target language code

        Returns:
            TranslationResult with translation and metadata
        """
        try:
            # Validate input
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            # Validate language codes
            if target_language not in self.language_codes:
                raise ValueError(f"Unsupported target language: {target_language}")

            if source_language != "auto" and source_language not in self.language_codes:
                raise ValueError(f"Unsupported source language: {source_language}")

            # Handle long text by splitting into chunks
            if len(text) > self.max_text_length:
                return self._translate_long_text(text, source_language, target_language)

            # Perform translation
            logger.info(f"Translating text from {source_language} to {target_language}")
            result = self.translator.translate(
                text, src=source_language, dest=target_language
            )

            # Create result object
            translation_result = TranslationResult(
                original_text=text,
                translated_text=result.text,
                source_language=result.src,
                target_language=target_language,
                confidence_score=self._calculate_confidence_score(result),
            )

            logger.info(
                f"Translation completed. Source: {result.src}, Target: {target_language}"
            )
            return translation_result

        except Exception as e:
            logger.error(f"Error translating text: {e}")
            raise RuntimeError(f"Translation failed: {e}")

    def translate_segments(
        self,
        segments: List[TranscriptionSegment],
        source_language: str = "auto",
        target_language: str = "en",
    ) -> List[TranslationResult]:
        """
        Translate a list of transcription segments

        Args:
            segments: List of transcription segments
            source_language: Source language code
            target_language: Target language code

        Returns:
            List of TranslationResult objects
        """
        try:
            if not segments:
                return []

            results = []

            # Detect source language from first segment if auto
            if source_language == "auto" and segments:
                detected_lang = self.detect_language(segments[0].text)
                source_language = detected_lang["language"]
                logger.info(f"Auto-detected source language: {source_language}")

            # Translate each segment
            for segment in segments:
                if segment.text.strip():
                    try:
                        translation = self.translate_text(
                            segment.text, source_language, target_language
                        )
                        results.append(translation)

                    except Exception as e:
                        logger.error(f"Error translating segment {segment.id}: {e}")
                        # Create fallback result
                        fallback_result = TranslationResult(
                            original_text=segment.text,
                            translated_text=segment.text,  # Keep original if translation fails
                            source_language=source_language,
                            target_language=target_language,
                            confidence_score=0.0,
                        )
                        results.append(fallback_result)
                else:
                    # Empty segment
                    empty_result = TranslationResult(
                        original_text="",
                        translated_text="",
                        source_language=source_language,
                        target_language=target_language,
                        confidence_score=1.0,
                    )
                    results.append(empty_result)

            logger.info(f"Translated {len(results)} segments")
            return results

        except Exception as e:
            logger.error(f"Error translating segments: {e}")
            raise RuntimeError(f"Segment translation failed: {e}")

    def _translate_long_text(
        self, text: str, source_language: str, target_language: str
    ) -> TranslationResult:
        """Translate long text by splitting into chunks"""
        try:
            # Split text into sentences
            sentences = self._split_into_sentences(text)

            # Group sentences into chunks
            chunks = []
            current_chunk = ""

            for sentence in sentences:
                if len(current_chunk + sentence) > self.max_text_length:
                    if current_chunk:
                        chunks.append(current_chunk.strip())
                    current_chunk = sentence
                else:
                    current_chunk += sentence

            if current_chunk:
                chunks.append(current_chunk.strip())

            # Translate each chunk
            translated_chunks = []
            detected_source = source_language

            for chunk in chunks:
                result = self.translator.translate(
                    chunk, src=source_language, dest=target_language
                )
                translated_chunks.append(result.text)

                # Update detected source language
                if source_language == "auto":
                    detected_source = result.src

            # Combine translated chunks
            translated_text = " ".join(translated_chunks)

            return TranslationResult(
                original_text=text,
                translated_text=translated_text,
                source_language=detected_source,
                target_language=target_language,
                confidence_score=0.8,  # Default confidence for chunked translation
            )

        except Exception as e:
            logger.error(f"Error in long text translation: {e}")
            raise RuntimeError(f"Long text translation failed: {e}")

    def _split_into_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        import re

        # Simple sentence splitting - can be improved with proper NLP
        sentences = re.split(r"[.!?]+", text)
        return [s.strip() + "." for s in sentences if s.strip()]

    def _calculate_confidence_score(self, translation_result) -> float:
        """Calculate confidence score for translation"""
        # googletrans doesn't provide confidence scores
        # We'll use heuristics based on text characteristics

        original_text = (
            translation_result.origin if hasattr(translation_result, "origin") else ""
        )
        translated_text = translation_result.text

        # Simple heuristics for confidence
        confidence = 0.8  # Default confidence

        # Lower confidence for very short texts
        if len(original_text) < 10:
            confidence -= 0.2

        # Lower confidence if translation is identical to original
        if original_text == translated_text:
            confidence -= 0.3

        # Lower confidence for very long texts
        if len(original_text) > 1000:
            confidence -= 0.1

        return max(0.0, min(1.0, confidence))

    def detect_language(self, text: str) -> Dict[str, Any]:
        """
        Detect language of the given text

        Args:
            text: Text to detect language for

        Returns:
            Dictionary with detected language information
        """
        try:
            if not text or not text.strip():
                raise ValueError("Text cannot be empty")

            result = self.translator.detect(text)

            return {
                "language": result.lang,
                "confidence": result.confidence,
                "language_name": self.supported_languages.get(result.lang, "Unknown"),
            }

        except Exception as e:
            logger.error(f"Error detecting language: {e}")
            raise RuntimeError(f"Language detection failed: {e}")

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return self.supported_languages.copy()

    def is_language_supported(self, language_code: str) -> bool:
        """Check if language is supported"""
        return language_code in self.language_codes

    def batch_translate(
        self,
        texts: List[str],
        source_language: str = "auto",
        target_language: str = "en",
    ) -> List[TranslationResult]:
        """
        Translate multiple texts in batch

        Args:
            texts: List of texts to translate
            source_language: Source language code
            target_language: Target language code

        Returns:
            List of TranslationResult objects
        """
        try:
            if not texts:
                return []

            results = []

            for i, text in enumerate(texts):
                try:
                    result = self.translate_text(text, source_language, target_language)
                    results.append(result)

                except Exception as e:
                    logger.error(f"Error translating text {i}: {e}")
                    # Create fallback result
                    fallback_result = TranslationResult(
                        original_text=text,
                        translated_text=text,
                        source_language=source_language,
                        target_language=target_language,
                        confidence_score=0.0,
                    )
                    results.append(fallback_result)

            logger.info(f"Batch translated {len(results)} texts")
            return results

        except Exception as e:
            logger.error(f"Error in batch translation: {e}")
            raise RuntimeError(f"Batch translation failed: {e}")

    def translate_with_fallback(
        self,
        text: str,
        source_language: str = "auto",
        target_language: str = "en",
        fallback_service: Optional[str] = None,
    ) -> TranslationResult:
        """
        Translate text with fallback mechanism

        Args:
            text: Text to translate
            source_language: Source language code
            target_language: Target language code
            fallback_service: Fallback service to use if primary fails

        Returns:
            TranslationResult object
        """
        try:
            # Try primary translation
            return self.translate_text(text, source_language, target_language)

        except Exception as e:
            logger.warning(f"Primary translation failed: {e}")

            # Fallback to keeping original text
            if fallback_service is None:
                logger.info("Using fallback: keeping original text")
                return TranslationResult(
                    original_text=text,
                    translated_text=text,
                    source_language=source_language,
                    target_language=target_language,
                    confidence_score=0.0,
                )

            # Additional fallback services can be implemented here
            raise RuntimeError(f"Translation failed with all methods: {e}")

    def get_translation_stats(self) -> Dict[str, Any]:
        """Get translation service statistics"""
        return {
            "supported_languages": len(self.supported_languages),
            "max_text_length": self.max_text_length,
            "service": "Google Translate",
            "features": ["auto_detection", "batch_translation", "fallback"],
        }


# Global instance
translation_service = TranslationService()
translate_service = translation_service  # Alias for backward compatibility
