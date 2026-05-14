from fastapi import Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.participant_repository import ParticipantRepository
from app.schema.participant_schema import (
    DrawCandidateEntry,
    DrawCandidatesResponse,
    NameLookupRequest,
    NameLookupResponse,
    ParticipantCreateRequest,
    ParticipantCreateResponse,
    ParticipantSearchEntry,
    ParticipantSearchResponse,
    ParticipantSummary,
    RankingEntry,
    RankingResponse,
)


class ParticipantService:
    def __init__(self, db: Session) -> None:
        self._repo = ParticipantRepository(db)

    def lookup_name(self, body: NameLookupRequest) -> NameLookupResponse:
        p = self._repo.find_by_name(body.name.strip())
        if p is None:
            return NameLookupResponse(found=False, participant=None)
        return NameLookupResponse(
            found=True,
            participant=ParticipantSummary.model_validate(p),
        )

    def register(self, body: ParticipantCreateRequest) -> ParticipantCreateResponse:
        try:
            p = self._repo.create(nickname=body.nickname)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        except IntegrityError as e:
            raise HTTPException(
                status_code=409, detail="Dados já existem no cadastro"
            ) from e
        return ParticipantCreateResponse.model_validate(p)

    def get_ranking(self, limit: int, offset: int) -> RankingResponse:
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)
        total = self._repo.count_all()
        rows = self._repo.list_ranked(limit, offset)
        items = [
            RankingEntry(
                rank=offset + i + 1,
                id=r.id,
                nickname=r.nickname,
                score=int(r.score),
            )
            for i, r in enumerate(rows)
        ]
        return RankingResponse(
            items=items, total=total, limit=limit, offset=offset
        )

    def search(self, q: str, limit: int) -> ParticipantSearchResponse:
        rows = self._repo.search_by_name(q.strip(), min(max(limit, 1), 20))
        return ParticipantSearchResponse(
            items=[ParticipantSearchEntry.model_validate(r) for r in rows]
        )

    def get_draw_candidates(self) -> DrawCandidatesResponse:
        """Lista completa para sorteio (ordenada por maior pontuação), com teto de segurança."""
        cap = 10_000
        total_registered = self._repo.count_all()
        rows = self._repo.list_all_ranked_cap(min(cap, total_registered))
        items = [
            DrawCandidateEntry(
                id=r.id,
                nickname=r.nickname,
                score=int(r.score),
            )
            for r in rows
        ]
        return DrawCandidatesResponse(items=items, total_registered=total_registered)


def get_participant_service(db: Session = Depends(get_db)) -> ParticipantService:
    return ParticipantService(db)
