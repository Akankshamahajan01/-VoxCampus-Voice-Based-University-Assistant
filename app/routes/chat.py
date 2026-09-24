import logging
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db, QueryHistory
from app.foundry import ask_foundry_agent
from app.speech import text_to_speech_base64
from app.models.schemas import TextQueryRequest, TextQueryResponse, QueryHistoryItem

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/query", response_model=TextQueryResponse)
async def text_query(
    request: TextQueryRequest,
    enable_tts: bool = False,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Text-based query endpoint.
    Accepts typed questions and returns AI-generated responses.
    Optionally converts response to speech.
    """
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="Query cannot be empty")

    # Get AI response
    ai_result = ask_foundry_agent(query)
    response_text = ai_result.get("response", "I'm sorry, I could not process your query.")
    category = ai_result.get("category", "general")

    # Optional TTS
    audio_base64 = ""
    if enable_tts:
        audio_base64 = text_to_speech_base64(response_text)

    # Save to history
    try:
        history = QueryHistory(
            user_id=user_id,
            query_text=query,
            response_text=response_text,
            query_type="text",
            category=category
        )
        db.add(history)
        db.commit()
    except Exception as e:
        logger.warning(f"Failed to save text query history: {e}")

    return TextQueryResponse(
        query=query,
        response_text=response_text,
        category=category,
        audio_base64=audio_base64 if enable_tts else None
    )


@router.get("/history", response_model=list[QueryHistoryItem])
async def get_history(
    limit: int = 20,
    query_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get recent query history (last 20 by default)."""
    query = db.query(QueryHistory).order_by(QueryHistory.created_at.desc())
    if query_type in ("voice", "text"):
        query = query.filter(QueryHistory.query_type == query_type)
    return query.limit(limit).all()


@router.delete("/history")
async def clear_history(db: Session = Depends(get_db)):
    """Clear all query history."""
    db.query(QueryHistory).delete()
    db.commit()
    return {"message": "History cleared successfully"}


@router.get("/suggestions")
async def get_suggestions():
    """Return sample questions students can ask."""
    return {
        "suggestions": [
            "What B.Tech programs are available?",
            "What is the fee for CSE program?",
            "How do I apply for admission?",
            "When are the end-term exams?",
            "What scholarships are available?",
            "What documents do I need for admission?",
            "Who is the head of CSE department?",
            "What is the grading system?",
            "When do classes start for new students?",
            "Is hostel facility available?"
        ]
    }
