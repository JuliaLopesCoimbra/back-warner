import json
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BACK_DIR = Path(__file__).resolve().parents[2]

_CORS_DEFAULTS = ["http://localhost:3000", "http://localhost:3001"]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BACK_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Quiz Totem API"
    # str evita que pydantic_settings tente json.loads() automático em campos list[]
    cors_origins_raw: str | None = Field(default=None, validation_alias="cors_origins")
    database_url: str | None = None
    app_secret: str = "change-me-quiz-layout-secret"

    @property
    def cors_origins(self) -> list[str]:
        raw = self.cors_origins_raw
        if not raw or not raw.strip():
            return _CORS_DEFAULTS
        text = raw.strip()
        if text.startswith("["):
            try:
                return json.loads(text) or _CORS_DEFAULTS
            except json.JSONDecodeError:
                return _CORS_DEFAULTS
        return [x.strip() for x in text.split(",") if x.strip()] or _CORS_DEFAULTS


settings = Settings()
