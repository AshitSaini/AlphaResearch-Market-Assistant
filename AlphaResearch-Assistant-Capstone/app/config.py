"""Core configuration management"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application Info
    APP_NAME: str = os.getenv("APP_NAME", "AlphaResearch Assistant")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    PROJECT_VERSION: str = os.getenv("APP_VERSION", "1.0.0")

    # API Configuration
    FASTAPI_HOST: str = os.getenv("FASTAPI_HOST", "0.0.0.0")
    FASTAPI_PORT: int = int(os.getenv("FASTAPI_PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDING_MODEL: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    
    # Vector Database
    CHROMA_DB_PATH: str = os.getenv("CHROMA_DB_PATH", "./data/embeddings/chroma_db")
    CHROMA_COLLECTION_NAME: str = os.getenv("CHROMA_COLLECTION_NAME", "broking_knowledge_base")
    
    # Document Processing
    DOCUMENT_UPLOAD_PATH: str = os.getenv("DOCUMENT_UPLOAD_PATH", "./data/documents/uploads")
    MAX_DOCUMENT_SIZE_MB: int = int(os.getenv("MAX_DOCUMENT_SIZE_MB", "50"))
    ALLOWED_DOCUMENT_TYPES: str = os.getenv(
        "ALLOWED_DOCUMENT_TYPES",
        "pdf,txt,docx,xlsx,csv,yaml,json,md"
    )
    
    # RAG Configuration
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "500"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "100"))
    SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.6"))
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))
    
    # Agent Configuration
    AGENT_MAX_ITERATIONS: int = int(os.getenv("AGENT_MAX_ITERATIONS", "10"))
    AGENT_TIMEOUT_SECONDS: int = int(os.getenv("AGENT_TIMEOUT_SECONDS", "60"))
    ENABLE_AGENT_REASONING: bool = os.getenv("ENABLE_AGENT_REASONING", "true").lower() == "true"
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "./logs/application.log")
    
    # CORS
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./data/broking_assistant.db")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

settings = Settings()

# Ensure required directories exist
Path(settings.DOCUMENT_UPLOAD_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.CHROMA_DB_PATH).mkdir(parents=True, exist_ok=True)
Path(settings.LOG_FILE_PATH).parent.mkdir(parents=True, exist_ok=True)
