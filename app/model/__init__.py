"""ORM models — importar tabelas aqui para o metadata do SQLAlchemy."""

from app.model.base import Base
from app.model.draw_result import DrawResult
from app.model.participant import Participant
from app.model.question import Question
from app.model.question_answer_event import QuestionAnswerEvent
from app.model.super_fa_answer_event import SuperFaAnswerEvent
from app.model.super_fa_question import SuperFaQuestion

__all__ = [
    "Base",
    "DrawResult",
    "Participant",
    "Question",
    "QuestionAnswerEvent",
    "SuperFaAnswerEvent",
    "SuperFaQuestion",
]