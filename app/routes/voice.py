import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session

from app.database import get_db, QueryHistory
from app.speech import speech_to_text_from_bytes, text_to_speech_base64
from app.foundry import ask_foundry_agent
from app.models.schemas import VoiceQueryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/voice", tags=["Voice"])


@router.post("/query", response_model=VoiceQueryResponse)
async def voice_query(
    audio: UploadFile = File(..., description="WAV/WebM audio file from microphone"),
    enable_tts: str = Form(default="true", description="Return TTS audio in response"),
    user_id: int = Form(default=None),
    db: Session = Depends(get_db)
):
    """
    Main voice query endpoint.
    1. Receives audio from browser microphone
    2. Converts speech → text via Azure AI Speech
    3. Sends text to Foundry AI Agent
    4. Converts response → speech via Azure TTS
    5. Returns transcription + text response + audio
    """
    # Read audio bytes
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Empty audio file received")

    # Step 1: Speech → Text
    stt_result = speech_to_text_from_bytes(audio_bytes)
    if not stt_result.get("success") or not stt_result.get("text"):
        raise HTTPException(
            status_code=422,
            detail=stt_result.get("error", "Could not recognize speech. Please speak clearly and try again.")
        )

    transcribed_text = stt_result["text"]
    logger.info(f"Transcribed: {transcribed_text}")

    # Step 2: AI Agent response
    ai_result = ask_foundry_agent(transcribed_text)
    response_text = ai_result.get("response", "I'm sorry, I could not process your query right now.")
    category = ai_result.get("category", "general")

    # Step 3: Text → Speech (optional)
    audio_base64 = ""
    if enable_tts.lower() == "true":
        audio_base64 = text_to_speech_base64(response_text)

    # Step 4: Save to history
    try:
        history = QueryHistory(
            user_id=user_id,
            query_text=transcribed_text,
            response_text=response_text,
            query_type="voice",
            category=category
        )
        db.add(history)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to save voice query history: {e}")

    return VoiceQueryResponse(
        transcribed_text=transcribed_text,
        response_text=response_text,
        audio_base64=audio_base64,
        category=category,
        confidence=stt_result.get("confidence", 0.0)
    )


@router.post("/text-to-speech")
async def convert_text_to_speech(text: str = Form(...)):
    """Convert any text to speech audio (base64 WAV)."""
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    audio_base64 = text_to_speech_base64(text)
    if not audio_base64:
        raise HTTPException(status_code=503, detail="Text-to-speech service unavailable")

    return {"audio_base64": audio_base64, "format": "wav"}
