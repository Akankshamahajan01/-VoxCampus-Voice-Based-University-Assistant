from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# ── Auth Schemas ──────────────────────────────────────────────
class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse


# ── Chat / Voice Schemas ──────────────────────────────────────
class TextQueryRequest(BaseModel):
    query: str
    language: Optional[str] = "en"


class VoiceQueryResponse(BaseModel):
    transcribed_text: str
    response_text: str
    audio_base64: Optional[str] = None   # TTS audio as base64
    category: Optional[str] = None
    confidence: Optional[float] = None


class TextQueryResponse(BaseModel):
    query: str
    response_text: str
    category: Optional[str] = None
    audio_base64: Optional[str] = None   # optional TTS


# ── History Schema ────────────────────────────────────────────
class QueryHistoryItem(BaseModel):
    id: int
    query_text: str
    response_text: str
    query_type: str
    category: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# ── Health Schema ─────────────────────────────────────────────
class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    services: dict
