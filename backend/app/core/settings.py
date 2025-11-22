from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl
from typing import List

class Settings(BaseSettings):
    # Core
    app_name: str = "Speech Analysis API"
    environment: str = "development"
    database_url: str = "sqlite:///./app.db"  # Override in production

    # Auth / security
    access_token_exp_minutes: int = 15
    refresh_token_exp_days: int = 14

    # CORS
    cors_allow_origins: str = "http://localhost:8501,http://127.0.0.1:8501"
    cors_allow_methods: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: List[str] = ["*"]

    # External API keys
    google_api_key: str | None = None

    # Whisper / model config
    whisper_model_size: str = "tiny"  # can set to base/tiny for faster
    # Telemetry removed (OTLP & Sentry no longer used)

    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()
