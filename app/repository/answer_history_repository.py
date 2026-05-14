import uuid
from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.participant import Participant
from app.model.question_answer_event import QuestionAnswerEvent


class AnswerHistoryRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create_event(
        self,
        *,
        participant_id: uuid.UUID | None,
        question_id: uuid.UUID,
        question_prompt: str,
        choice_letter: str,
        choice_text: str,
        is_correct: bool,
    ) -> QuestionAnswerEvent:
        ev = QuestionAnswerEvent(
            participant_id=participant_id,
            question_id=question_id,
            question_prompt=question_prompt,
            choice_letter=choice_letter.upper()[:1],
            choice_text=choice_text[:500],
            is_correct=is_correct,
        )
        self._session.add(ev)
        self._session.commit()
        self._session.refresh(ev)
        return ev

    def count_filtered(self, participant_id: uuid.UUID | None) -> int:
        stmt = select(func.count()).select_from(QuestionAnswerEvent)
        if participant_id is not None:
            stmt = stmt.where(QuestionAnswerEvent.participant_id == participant_id)
        return int(self._session.scalar(stmt) or 0)

    def list_filtered(
        self,
        limit: int,
        offset: int,
        participant_id: uuid.UUID | None,
    ) -> Sequence[tuple[QuestionAnswerEvent, str | None]]:
        stmt = (
            select(QuestionAnswerEvent, Participant.nickname)
            .outerjoin(Participant, QuestionAnswerEvent.participant_id == Participant.id)
            .order_by(QuestionAnswerEvent.answered_at.desc())
        )
        if participant_id is not None:
            stmt = stmt.where(QuestionAnswerEvent.participant_id == participant_id)
        stmt = stmt.limit(limit).offset(offset)
        return self._session.execute(stmt).all()
