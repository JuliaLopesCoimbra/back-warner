import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.participant import Participant


class ParticipantRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_name(self, name: str) -> Participant | None:
        stmt = (
            select(Participant)
            .where(func.lower(Participant.nickname) == func.lower(name.strip()))
            .limit(1)
        )
        return self._session.scalar(stmt)

    def get_by_id(self, participant_id: uuid.UUID) -> Participant | None:
        return self._session.get(Participant, participant_id)

    def count_all(self) -> int:
        n = self._session.scalar(select(func.count()).select_from(Participant))
        return int(n or 0)

    def list_ranked(self, limit: int, offset: int) -> Sequence[Participant]:
        stmt = (
            select(Participant)
            .order_by(Participant.score.desc(), Participant.nickname.asc())
            .limit(limit)
            .offset(offset)
        )
        return self._session.scalars(stmt).all()

    def list_all_ranked_cap(self, max_rows: int) -> Sequence[Participant]:
        if max_rows <= 0:
            return []
        stmt = (
            select(Participant)
            .order_by(Participant.score.desc(), Participant.nickname.asc())
            .limit(max_rows)
        )
        return self._session.scalars(stmt).all()

    def increment_score(self, participant_id: uuid.UUID, delta: int = 1) -> bool:
        p = self._session.get(Participant, participant_id)
        if p is None:
            return False
        p.score = int(p.score) + delta
        self._session.add(p)
        self._session.commit()
        return True

    def search_by_name(self, query: str, limit: int = 8) -> Sequence[Participant]:
        q = f"%{query.strip().lower()}%"
        stmt = (
            select(Participant)
            .where(func.lower(Participant.nickname).like(q))
            .order_by(Participant.nickname.asc())
            .limit(limit)
        )
        return self._session.scalars(stmt).all()

    def create(self, *, nickname: str) -> Participant:
        p = Participant(nickname=nickname.strip())
        self._session.add(p)
        self._session.commit()
        self._session.refresh(p)
        return p
