"""Application settings, loaded from environment variables or backend/.env."""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    team_provider_url: str = "https://api.groq.com/openai/v1/chat/completions"
    team_provider_key: str = ""
    team_model: str = ""
    groq_timeout_seconds: float = Field(default=30.0, gt=0)
    groq_max_retries: int = Field(default=2, ge=0, le=5)
    database_path: str = "data/workshop.db"
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    log_level: str = "INFO"

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def groq_models_url(self) -> str:
        """Derive the /models URL from the chat completions URL."""
        base = self.team_provider_url.rsplit("/chat/completions", 1)[0]
        return f"{base}/models"

    @property
    def groq_configured(self) -> bool:
        return bool(self.team_provider_key and self.team_model)


@lru_cache
def get_settings() -> Settings:
    return Settings()
