from pathlib import Path
from typing import Literal
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory (resolved cleanly across Windows & Linux/Termux)
BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    APP_NAME: str = "Daily Intelligence"
    APP_VERSION: str = "0.1.0"
    APP_ENV: Literal["development", "production", "testing"] = "development"
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    SECRET_KEY: str = "dev-secret-change-in-production-key-32chars"

    # Scheduling
    TIMEZONE: str = "Asia/Kolkata"
    MORNING_BRIEFING_TIME: str = "06:00"
    EVENING_BRIEFING_TIME: str = "18:00"
    AUTO_UPDATE_ENABLED: bool = True

    # Directories
    DATA_DIR: Path = Field(default_factory=lambda: BASE_DIR / "data")
    LOG_DIR: Path = Field(default_factory=lambda: BASE_DIR / "logs")
    LOG_LEVEL: str = "INFO"

    # Database
    DATABASE_URL: str = ""

    # AI Configuration (No-AI fallback by default)
    AI_PROVIDER: Literal["none", "gemini", "ollama", "openai"] = "none"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = "gemini-2.5-flash"
    AI_BASE_URL: str = ""

    # Translation Configuration
    TRANSLATION_PROVIDER: Literal["free", "gemini", "offline"] = "free"

    # Ingestion Controls
    MAX_CONCURRENT_REQUESTS: int = 5
    REQUEST_TIMEOUT_SECONDS: int = 15
    USER_AGENT: str = "DailyIntelligence/1.0 (+http://127.0.0.1:8000; personal intelligence)"

    def model_post_init(self, __context) -> None:
        # Ensure directories exist
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)

        if not self.DATABASE_URL:
            db_path = self.DATA_DIR / "daily_intelligence.db"
            self.DATABASE_URL = f"sqlite:///{db_path.as_posix()}"


settings = Settings()
