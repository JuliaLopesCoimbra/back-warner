from fastapi import APIRouter, Depends, Query

from app.schema.participant_schema import (
    DrawCandidatesResponse,
    NameLookupRequest,
    NameLookupResponse,
    ParticipantCreateRequest,
    ParticipantCreateResponse,
    ParticipantSearchResponse,
    RankingResponse,
)
from app.service.participant_service import ParticipantService, get_participant_service

router = APIRouter(prefix="/participants", tags=["participants"])


@router.get("/draw-candidates", response_model=DrawCandidatesResponse)
def draw_candidates(
    service: ParticipantService = Depends(get_participant_service),
) -> DrawCandidatesResponse:
    """Todos os cadastrados com pontuação (maior primeiro), para seleção e sorteio na tela admin."""
    return service.get_draw_candidates()


@router.get("/ranking", response_model=RankingResponse)
def ranking(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    service: ParticipantService = Depends(get_participant_service),
) -> RankingResponse:
    """Lista participantes ordenados por pontuação (maior primeiro), com paginação."""
    return service.get_ranking(limit, offset)


@router.get("/search", response_model=ParticipantSearchResponse)
def search_participants(
    q: str = Query(..., min_length=1, max_length=120),
    limit: int = Query(8, ge=1, le=20),
    service: ParticipantService = Depends(get_participant_service),
) -> ParticipantSearchResponse:
    """Busca parcial por nome (autocomplete)."""
    return service.search(q, limit)


@router.post("/lookup-name", response_model=NameLookupResponse)
def lookup_name(
    body: NameLookupRequest,
    service: ParticipantService = Depends(get_participant_service),
) -> NameLookupResponse:
    return service.lookup_name(body)


@router.post("/register", response_model=ParticipantCreateResponse, status_code=201)
def register_participant(
    body: ParticipantCreateRequest,
    service: ParticipantService = Depends(get_participant_service),
) -> ParticipantCreateResponse:
    return service.register(body)
