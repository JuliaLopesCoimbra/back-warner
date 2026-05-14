from fastapi import APIRouter, Depends

from app.schema.health_schema import HealthResponse
from app.service.health_service import HealthService, get_health_service

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse)
def health(service: HealthService = Depends(get_health_service)) -> HealthResponse:
    return service.get_status()
