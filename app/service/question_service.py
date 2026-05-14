import logging
import secrets
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.quiz_layout import (
    display_choice_to_option_text,
    display_choice_to_original_letter,
    sign_layout,
    verify_layout,
)
from app.repository.answer_history_repository import AnswerHistoryRepository
from app.repository.participant_repository import ParticipantRepository
from app.repository.question_repository import QuestionRepository
from app.schema.question_schema import (
    AnswerHistoryEntry,
    AnswerHistoryResponse,
    AnswerResult,
    AnswerSubmit,
    QuestionShufflePublic,
    ShuffledOption,
)

logger = logging.getLogger(__name__)


class QuestionService:
    def __init__(self, db: Session) -> None:
        self._repo = QuestionRepository(db)
        self._participants = ParticipantRepository(db)
        self._history = AnswerHistoryRepository(db)

    def random_question(self) -> QuestionShufflePublic:
        q = self._repo.get_random()
        if q is None:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma pergunta cadastrada. Rode o script de seed.",
            )
        texts = [q.option_a, q.option_b, q.option_c, q.option_d]
        perm = [0, 1, 2, 3]
        secrets.SystemRandom().shuffle(perm)
        options: list[ShuffledOption] = []
        for slot, orig_idx in enumerate(perm):
            letter = chr(ord("A") + slot)
            options.append(ShuffledOption(letter=letter, text=texts[orig_idx]))
        token = sign_layout(q.id, perm, settings.app_secret)
        return QuestionShufflePublic(
            id=q.id,
            prompt=q.prompt,
            options=options,
            layout_token=token,
        )

    def check_answer(self, question_id: UUID, body: AnswerSubmit) -> AnswerResult:
        try:
            token_qid, perm = verify_layout(body.layout_token, settings.app_secret)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) from e
        if token_qid != question_id:
            raise HTTPException(
                status_code=400, detail="Token não corresponde a esta pergunta."
            )
        q = self._repo.get_by_id(question_id)
        if q is None:
            raise HTTPException(status_code=404, detail="Pergunta não encontrada.")
        try:
            original_letter = display_choice_to_original_letter(body.choice, perm)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        ok = original_letter.upper() == q.correct_choice.upper()
        texts = [q.option_a, q.option_b, q.option_c, q.option_d]
        try:
            choice_text = display_choice_to_option_text(body.choice, perm, texts)
            self._history.create_event(
                participant_id=body.participant_id,
                question_id=question_id,
                question_prompt=q.prompt,
                choice_letter=body.choice,
                choice_text=choice_text,
                is_correct=ok,
            )
        except Exception:
            logger.exception("Falha ao registrar histórico de resposta")

        if ok and body.participant_id is not None:
            self._participants.increment_score(body.participant_id, 1)
        return AnswerResult(correct=ok)

    def list_answer_history(
        self, limit: int, offset: int, participant_id: UUID | None
    ) -> AnswerHistoryResponse:
        limit = min(max(limit, 1), 200)
        offset = max(offset, 0)
        total = self._history.count_filtered(participant_id)
        rows = self._history.list_filtered(limit, offset, participant_id)
        items = [
            AnswerHistoryEntry(
                id=ev.id,
                answered_at=ev.answered_at,
                participant_id=ev.participant_id,
                participant_nickname=nick,
                question_id=ev.question_id,
                question_prompt=ev.question_prompt,
                choice_letter=ev.choice_letter,
                choice_text=ev.choice_text,
                is_correct=ev.is_correct,
            )
            for ev, nick in rows
        ]
        return AnswerHistoryResponse(
            items=items, total=total, limit=limit, offset=offset
        )


def get_question_service(db: Session = Depends(get_db)) -> QuestionService:
    return QuestionService(db)
