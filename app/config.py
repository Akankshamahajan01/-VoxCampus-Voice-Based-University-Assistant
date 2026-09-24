import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # App
    APP_NAME: str = "VoxCampus"
    APP_VERSION: str = "1.0.0"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "voxcampus-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Azure AI Speech
    AZURE_SPEECH_KEY: str = os.getenv("AZURE_SPEECH_KEY", "")
    AZURE_SPEECH_REGION: str = os.getenv("AZURE_SPEECH_REGION", "eastus")
    AZURE_SPEECH_LANGUAGE: str = os.getenv("AZURE_SPEECH_LANGUAGE", "en-US")
    AZURE_TTS_VOICE: str = os.getenv("AZURE_TTS_VOICE", "en-US-JennyNeural")

    # Microsoft Foundry / Azure OpenAI
    AZURE_FOUNDRY_ENDPOINT: str = os.getenv("AZURE_FOUNDRY_ENDPOINT", "")
    AZURE_FOUNDRY_API_KEY: str = os.getenv("AZURE_FOUNDRY_API_KEY", "")
    AZURE_FOUNDRY_DEPLOYMENT: str = os.getenv("AZURE_FOUNDRY_DEPLOYMENT", "gpt-4o")
    AZURE_FOUNDRY_API_VERSION: str = os.getenv("AZURE_FOUNDRY_API_VERSION", "2024-02-01")

    # Foundry Agent
    FOUNDRY_AGENT_ID: str = os.getenv("FOUNDRY_AGENT_ID", "")
    FOUNDRY_PROJECT_CONNECTION_STRING: str = os.getenv("FOUNDRY_PROJECT_CONNECTION_STRING", "")

    # Azure AI Search (RAG)
    AZURE_SEARCH_ENDPOINT: str = os.getenv("AZURE_SEARCH_ENDPOINT", "")
    AZURE_SEARCH_KEY: str = os.getenv("AZURE_SEARCH_KEY", "")
    AZURE_SEARCH_INDEX_NAME: str = os.getenv("AZURE_SEARCH_INDEX_NAME", "voxcampus-knowledge")

    # Azure OpenAI Embeddings (for vector RAG — same resource as Foundry)
    AZURE_EMBEDDINGS_DEPLOYMENT: str = os.getenv("AZURE_EMBEDDINGS_DEPLOYMENT", "text-embedding-ada-002")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./voxcampus.db")

settings = Settings()
