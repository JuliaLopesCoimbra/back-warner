import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.question import Question


class QuestionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def count_all(self) -> int:
        return int(self._session.scalar(select(func.count()).select_from(Question)) or 0)

    def get_random(self) -> Question | None:
        stmt = select(Question).order_by(func.random()).limit(1)
        return self._session.scalar(stmt)

    def get_by_id(self, qid: uuid.UUID) -> Question | None:
        return self._session.get(Question, qid)
