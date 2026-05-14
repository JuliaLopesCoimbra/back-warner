import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.super_fa_answer_event import SuperFaAnswerEvent


class SuperFaAnswerHistoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_event(
        self,
        *,
        question_id: uuid.UUID,
        question_prompt: str,
        choice_letter: str,
        choice_text: str,
        is_correct: bool,
    ) -> SuperFaAnswerEvent:
        ev = SuperFaAnswerEvent(
            super_fa_question_id=question_id,
            question_prompt=question_prompt,
            choice_letter=choice_letter.upper()[:1],
            choice_text=choice_text[:500],
            is_correct=is_correct,
        )
        self._session.add(ev)
        self._session.commit()
        self._session.refresh(ev)
        return ev

    def count_all(self) -> int:
        n = self._session.scalar(select(func.count()).select_from(SuperFaAnswerEvent))
        return int(n or 0)

    def list_recent(self, limit: int, offset: int) -> Sequence[SuperFaAnswerEvent]:
        stmt = (
            select(SuperFaAnswerEvent)
            .order_by(SuperFaAnswerEvent.attempted_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return self._session.scalars(stmt).all()
