import json
from pathlib import Path
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BACK_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACK_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
        env_ignore_empty=True,
    )

    app_name: str = "Quiz Totem API"
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
    ]
    database_url: str | None = None
    app_secret: str = "change-me-quiz-layout-secret"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        defaults = ["http://localhost:3000", "http://localhost:3001"]
        if value is None:
            return defaults
        if isinstance(value, list):
            return [str(x).strip() for x in value if str(x).strip()] or defaults
        if isinstance(value, str):
            text = value.strip()
            if not text:
                return defaults
            if text.startswith("["):
                return [str(x).strip() for x in json.loads(text) if str(x).strip()] or defaults
            return [x.strip() for x in text.split(",") if x.strip()] or defaults
        raise TypeError("cors_origins must be a list or string")


settings = Settings()
