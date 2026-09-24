import os
import base64
import tempfile
import logging
from app.config import settings

logger = logging.getLogger(__name__)


def speech_to_text_from_bytes(audio_bytes: bytes) -> dict:
    """
    Convert audio bytes to text using Azure AI Speech SDK.
    Returns dict with 'text' and 'confidence'.
    """
    try:
        import azure.cognitiveservices.speech as speechsdk

        if not settings.AZURE_SPEECH_KEY:
            raise ValueError("AZURE_SPEECH_KEY is not configured")

        speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION
        )
        speech_config.speech_recognition_language = settings.AZURE_SPEECH_LANGUAGE

        # Write audio bytes to a temp file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            audio_config = speechsdk.AudioConfig(filename=tmp_path)
            recognizer = speechsdk.SpeechRecognizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            result = recognizer.recognize_once()

            if result.reason == speechsdk.ResultReason.RecognizedSpeech:
                return {
                    "text": result.text,
                    "confidence": 0.95,
                    "success": True
                }
            elif result.reason == speechsdk.ResultReason.NoMatch:
                logger.warning("No speech recognized in audio")
                return {"text": "", "confidence": 0.0, "success": False, "error": "No speech detected"}
            else:
                logger.error(f"Speech recognition cancelled: {result.cancellation_details.reason}")
                return {"text": "", "confidence": 0.0, "success": False, "error": str(result.cancellation_details.reason)}
        finally:
            os.unlink(tmp_path)

    except ImportError:
        logger.error("azure-cognitiveservices-speech not installed")
        return {"text": "", "confidence": 0.0, "success": False, "error": "Speech SDK not installed"}
    except Exception as e:
        logger.error(f"Speech-to-text error: {e}")
        return {"text": "", "confidence": 0.0, "success": False, "error": str(e)}


def text_to_speech_base64(text: str, voice: str = None) -> str:
    """
    Convert text to speech using Azure AI Speech and return base64-encoded WAV.
    Returns empty string on failure.
    """
    try:
        import azure.cognitiveservices.speech as speechsdk

        if not settings.AZURE_SPEECH_KEY:
            raise ValueError("AZURE_SPEECH_KEY is not configured")

        speech_config = speechsdk.SpeechConfig(
            subscription=settings.AZURE_SPEECH_KEY,
            region=settings.AZURE_SPEECH_REGION
        )
        speech_config.speech_synthesis_voice_name = voice or settings.AZURE_TTS_VOICE

        # Synthesize to in-memory audio
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            audio_config = speechsdk.AudioConfig(filename=tmp_path)
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=audio_config
            )
            result = synthesizer.speak_text_async(text).get()

            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                with open(tmp_path, "rb") as f:
                    audio_data = f.read()
                return base64.b64encode(audio_data).decode("utf-8")
            else:
                logger.error(f"TTS failed: {result.cancellation_details.reason}")
                return ""
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    except ImportError:
        logger.error("azure-cognitiveservices-speech not installed")
        return ""
    except Exception as e:
        logger.error(f"Text-to-speech error: {e}")
        return ""


def get_speech_service_status() -> bool:
    """Check if Azure Speech service is configured and reachable."""
    return bool(settings.AZURE_SPEECH_KEY and settings.AZURE_SPEECH_REGION)
