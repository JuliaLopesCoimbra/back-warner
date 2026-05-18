import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.model.super_fa_question import SuperFaQuestion


class SuperFaQuestionRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_random(self) -> SuperFaQuestion | None:
        stmt = select(SuperFaQuestion).order_by(func.random()).limit(1)
        return self._session.scalar(stmt)

    def get_n_distinct(self, n: int) -> list[SuperFaQuestion]:
        stmt = select(SuperFaQuestion).order_by(func.random()).limit(n)
        return list(self._session.scalars(stmt))

    def get_by_id(self, qid: uuid.UUID) -> SuperFaQuestion | None:
        return self._session.get(SuperFaQuestion, qid)
