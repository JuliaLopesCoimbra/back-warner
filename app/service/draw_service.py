from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.repository.draw_repository import DrawRepository
from app.schema.draw_schema import DrawHistoryResponse, DrawRecordRequest, DrawResultEntry


class DrawService:
    def __init__(self, db: Session) -> None:
        self._repo = DrawRepository(db)

    def record(self, body: DrawRecordRequest) -> DrawResultEntry:
        r = self._repo.create(
            winner_nickname=body.winner_nickname,
            winner_score=body.winner_score,
            participant_count=body.participant_count,
        )
        return DrawResultEntry.model_validate(r)

    def get_history(self, limit: int, offset: int) -> DrawHistoryResponse:
        limit = min(max(limit, 1), 100)
        offset = max(offset, 0)
        total = self._repo.count_all()
        rows = self._repo.list_recent(limit, offset)
        items = [DrawResultEntry.model_validate(r) for r in rows]
        return DrawHistoryResponse(items=items, total=total, limit=limit, offset=offset)


def get_draw_service(db: Session = Depends(get_db)) -> DrawService:
    return DrawService(db)
