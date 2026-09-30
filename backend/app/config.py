from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    # Secrets / deployment settings (from .env or hosting platform)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = ""
    ALLOWED_ORIGINS: str = "*"
    MAX_TEXT_LENGTH: int = 100000

    # RAG settings (easy to tweak)
    MIN_TEXT_LENGTH: int = 200
    CHUNK_SIZE: int = 1500
    CHUNK_OVERLAP: int = 200
    TOP_K: int = 8
    EMBEDDING_MODEL: str = "BAAI/bge-small-en-v1.5"

    @property
    def allowed_origins_list(self) -> list[str]:
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()