from fastapi import Depends

from app.repository.health_repository import HealthRepository, get_health_repository
from app.schema.health_schema import HealthResponse


class HealthService:
    def __init__(self, repository: HealthRepository) -> None:
        self._repository = repository

    def get_status(self) -> HealthResponse:
        return self._repository.fetch_status()


def get_health_service(
    repository: HealthRepository = Depends(get_health_repository),
) -> HealthService:
    return HealthService(repository)
