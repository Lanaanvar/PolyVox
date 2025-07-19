"""
TTS Service - Wrapper around voice cloning functionality
"""

import logging
from typing import Dict, List, Optional
from .voice_clone import synthesize_with_cloned_voice

logger = logging.getLogger(__name__)


class TTSService:
    """TTS Service using voice cloning model"""

    def __init__(self):
        self.client = True  # Dummy client for compatibility
        self._initialized = False

    def initialize(self):
        """Initialize the TTS service"""
        try:
            self._initialized = True
            logger.info("TTS Service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize TTS service: {e}")
            self._initialized = False

    def synthesize_speech(
        self,
        text: str,
        output_path: str,
        voice: str = "en-US-Wavenet-D",
        speaking_rate: float = 1.0,
        pitch: float = 0.0,
        volume_gain_db: float = 0.0,
        reference_audio: Optional[str] = None,
    ) -> Dict:
        """
        Synthesize speech using voice cloning

        Args:
            text: Text to synthesize
            output_path: Output audio file path
            voice: Voice name (for compatibility)
            speaking_rate: Speaking rate
            pitch: Pitch adjustment
            volume_gain_db: Volume gain
            reference_audio: Reference audio for voice cloning

        Returns:
            Result dictionary
        """
        try:
            if reference_audio:
                # Use voice cloning
                result = synthesize_with_cloned_voice(
                    text=text,
                    reference_audio_path=reference_audio,
                    output_path=output_path,
                    language="en",
                )
            else:
                # Use regular TTS from voice cloning model
                result = synthesize_with_cloned_voice(
                    text=text,
                    reference_audio_path=None,
                    output_path=output_path,
                    language="en",
                )

            return {
                "success": result.get("success", True),
                "output_path": output_path,
                "error": result.get("error"),
            }

        except Exception as e:
            logger.error(f"TTS synthesis failed: {e}")
            return {"success": False, "output_path": output_path, "error": str(e)}

    def get_supported_languages(self) -> Dict[str, str]:
        """Get supported languages"""
        return {
            "en": "English",
            "es": "Spanish",
            "fr": "French",
            "de": "German",
            "it": "Italian",
            "pt": "Portuguese",
            "pl": "Polish",
            "tr": "Turkish",
            "ru": "Russian",
            "nl": "Dutch",
            "cs": "Czech",
            "ar": "Arabic",
            "zh-cn": "Chinese (Simplified)",
            "ja": "Japanese",
            "hu": "Hungarian",
            "ko": "Korean",
        }

    def get_supported_voices(self) -> List[str]:
        """Get supported voices"""
        return [
            "en-US-Wavenet-D",
            "en-US-Wavenet-A",
            "en-US-Wavenet-B",
            "en-US-Wavenet-C",
            "en-GB-Wavenet-A",
            "en-GB-Wavenet-B",
        ]

    def synthesize_translations(
        self, translations: List[Dict], output_dir: str, **kwargs
    ) -> List[Dict]:
        """
        Synthesize multiple translations

        Args:
            translations: List of translation dictionaries
            output_dir: Output directory
            **kwargs: Additional parameters

        Returns:
            List of synthesis results
        """
        results = []

        for i, translation in enumerate(translations):
            output_path = f"{output_dir}/tts_segment_{i}.wav"

            result = self.synthesize_speech(
                text=translation.get("translated", translation.get("text", "")),
                output_path=output_path,
                **kwargs,
            )

            results.append(
                {
                    "segment_id": i,
                    "text": translation.get("translated", translation.get("text", "")),
                    "output_path": output_path,
                    "success": result["success"],
                    "error": result.get("error"),
                }
            )

        return results


# Create singleton instance
tts_service = TTSService()
