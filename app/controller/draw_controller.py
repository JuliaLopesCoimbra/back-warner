from fastapi import APIRouter, Depends, Query

from app.schema.draw_schema import DrawHistoryResponse, DrawRecordRequest, DrawResultEntry
from app.service.draw_service import DrawService, get_draw_service

router = APIRouter(prefix="/sorteio", tags=["sorteio"])


@router.post("/record", response_model=DrawResultEntry, status_code=201)
def record_draw(
    body: DrawRecordRequest,
    service: DrawService = Depends(get_draw_service),
) -> DrawResultEntry:
    """Registra o resultado de um sorteio."""
    return service.record(body)


@router.get("/history", response_model=DrawHistoryResponse)
def draw_history(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: DrawService = Depends(get_draw_service),
) -> DrawHistoryResponse:
    """Lista o histórico de sorteios (mais recente primeiro)."""
    return service.get_history(limit, offset)
