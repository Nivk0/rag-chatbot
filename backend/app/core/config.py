from pydantic_settings import BaseSettings
from functools import lru_cache
import os

class Settings(BaseSettings):
    PROJECT_NAME: str = "Document Chat"
    QDRANT_HOST: str = "localhost"
    QDRANT_PORT: int = 6333
    COLLECTION_NAME: str = "documents"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200
    EMBEDDINGS_MODEL: str = "BAAI/bge-small-en"
    OPENAI_API_KEY: str = os.getenv("key name", "key")  # Add type annotation
    ENABLE_FALLBACK_MODEL: bool = True
    MAX_RETRIES: int = 3

    class Config:
        case_sensitive = True

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
