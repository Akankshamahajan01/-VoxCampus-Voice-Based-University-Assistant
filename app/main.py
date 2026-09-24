from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import logging
import os

from app.config import settings
from app.database import init_db
from app.routes import auth, voice, chat
from app.speech import get_speech_service_status
from app.foundry import get_foundry_status
from app.rag import rag_pipeline
from app.knowledge import get_all_chunks

# ── Logging ───────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s"
)
logger = logging.getLogger(__name__)

# ── App ───────────────────────────────────────────────────────
app = FastAPI(
    title="VoxCampus",
    description="🎙️ Voice-Based University Assistant powered by Azure AI Speech & Microsoft Foundry",
    version=settings.APP_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# ── CORS ──────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────
app.include_router(auth.router,  prefix="/api")
app.include_router(voice.router, prefix="/api")
app.include_router(chat.router,  prefix="/api")

# ── Static Files ──────────────────────────────────────────────
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# ── Startup ───────────────────────────────────────────────────
@app.on_event("startup")
async def startup():
    logger.info("🚀 VoxCampus starting up...")
    init_db()
    logger.info("✅ Database initialized")

    # Build RAG index from knowledge chunks
    chunks = get_all_chunks()
    rag_pipeline.build(chunks)
    logger.info(f"🧠 RAG pipeline ready | mode: {rag_pipeline.get_mode()} | chunks: {len(chunks)}")

    logger.info(f"🎙️  Speech service: {'✅ Ready' if get_speech_service_status() else '⚠️  Not configured'}")
    logger.info(f"🤖 Foundry AI:     {'✅ Ready' if get_foundry_status() else '⚠️  Not configured'}")
    logger.info("🎓 VoxCampus is ready!")

# ── Health ────────────────────────────────────────────────────
@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "services": {
            "speech":  get_speech_service_status(),
            "foundry": get_foundry_status(),
            "rag":     rag_pipeline.get_mode(),
        }
    }

# ── Frontend Routes ───────────────────────────────────────────
@app.get("/")
async def serve_index():
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/auth")
async def serve_auth():
    return FileResponse(os.path.join(frontend_path, "auth.html"))
