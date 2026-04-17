"""Aplikační konfigurace — načítá se z .env přes pydantic-settings."""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # ----- Aplikace -----
    app_env: str = "development"
    app_timezone: str = "Europe/Prague"
    app_base_url: str = "http://localhost:3000"

    # ----- Backend -----
    backend_port: int = 8000
    backend_log_level: str = "INFO"
    backend_secret_key: str = "change-me"
    backend_cors_origins: str = "http://localhost:3000"

    # ----- DB -----
    database_url: str = "sqlite:///./data/app.db"
    chroma_persist_dir: str = "./data/chroma"

    # ----- Claude -----
    claude_cli_path: str = "/usr/bin/claude"
    claude_session_timeout: int = 300
    claude_max_tokens: int = 8192

    # ----- Embedding -----
    embedding_model: str = "intfloat/multilingual-e5-small"
    embedding_device: str = "cpu"

    # ----- Whisper -----
    whisper_model: str = "small"
    whisper_device: str = "cpu"
    whisper_compute_type: str = "int8"

    # ----- Google -----
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"
    google_scopes: str = (
        "https://www.googleapis.com/auth/calendar,"
        "https://www.googleapis.com/auth/drive.file"
    )
    google_account_email: str = ""
    gdrive_root_folder: str = "Realitní asistent"

    # ----- SearXNG -----
    searxng_url: str = "http://searxng:8080"
    searxng_secret: str = "change-me"
    searxng_result_limit: int = 10

    # ----- Weather -----
    weather_lat: float = 50.6167
    weather_lon: float = 14.5667
    weather_location_name: str = "Zahrádky"

    # ----- Scheduler -----
    scheduler_timezone: str = "Europe/Prague"
    briefing_cron_hour: int = 7
    briefing_cron_minute: int = 0
    news_scrape_interval_minutes: int = 120
    calendar_sync_interval_minutes: int = 15

    # ----- Šifrování PII -----
    pii_encryption_key: str = ""

    # ----- Odvozené vlastnosti -----
    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.backend_cors_origins.split(",") if o.strip()]

    @property
    def google_scopes_list(self) -> list[str]:
        return [s.strip() for s in self.google_scopes.split(",") if s.strip()]

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def data_dir(self) -> Path:
        path = Path("./data").resolve()
        path.mkdir(parents=True, exist_ok=True)
        return path


@lru_cache
def get_settings() -> Settings:
    return Settings()
