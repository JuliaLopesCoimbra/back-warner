from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.draw_result import DrawResult


class DrawRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, *, winner_nickname: str, winner_score: int, participant_count: int) -> DrawResult:
        r = DrawResult(
            winner_nickname=winner_nickname.strip(),
            winner_score=winner_score,
            participant_count=participant_count,
        )
        self._session.add(r)
        self._session.commit()
        self._session.refresh(r)
        return r

    def count_all(self) -> int:
        n = self._session.scalar(select(func.count()).select_from(DrawResult))
        return int(n or 0)

    def list_recent(self, limit: int, offset: int) -> Sequence[DrawResult]:
        stmt = (
            select(DrawResult)
            .order_by(DrawResult.drawn_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self._session.scalars(stmt).all()
