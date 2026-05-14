from functools import lru_cache

from app.core.config import settings
from app.core.database import engine, ping_db
from app.schema.health_schema import HealthResponse


class HealthRepository:
    def fetch_status(self) -> HealthResponse:
        if engine is None:
            db = "disabled"
        else:
            db = "ok" if ping_db() else "down"
        return HealthResponse(status="ok", service=settings.app_name, database=db)


@lru_cache
def get_health_repository() -> HealthRepository:
    return HealthRepository()
