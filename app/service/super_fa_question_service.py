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
from app.repository.super_fa_answer_history_repository import (
    SuperFaAnswerHistoryRepository,
)
from app.repository.super_fa_question_repository import SuperFaQuestionRepository
from app.schema.question_schema import (
    AnswerResult,
    AnswerSubmit,
    QuestionShufflePublic,
    ShuffledOption,
    SuperFaAnswerHistoryEntry,
    SuperFaAnswerHistoryResponse,
)

logger = logging.getLogger(__name__)


class SuperFaQuestionService:
    def __init__(self, db: Session) -> None:
        self._repo = SuperFaQuestionRepository(db)
        self._history = SuperFaAnswerHistoryRepository(db)

    def random_question(self) -> QuestionShufflePublic:
        q = self._repo.get_random()
        if q is None:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma pergunta Super FA cadastrada. Rode o SQL de seed.",
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

    def session_questions(self, count: int) -> list[QuestionShufflePublic]:
        questions = self._repo.get_n_distinct(count)
        if not questions:
            raise HTTPException(
                status_code=404,
                detail="Nenhuma pergunta Super FA cadastrada. Rode o SQL de seed.",
            )
        result: list[QuestionShufflePublic] = []
        for q in questions:
            texts = [q.option_a, q.option_b, q.option_c, q.option_d]
            perm = [0, 1, 2, 3]
            secrets.SystemRandom().shuffle(perm)
            options: list[ShuffledOption] = []
            for slot, orig_idx in enumerate(perm):
                letter = chr(ord("A") + slot)
                options.append(ShuffledOption(letter=letter, text=texts[orig_idx]))
            token = sign_layout(q.id, perm, settings.app_secret)
            result.append(QuestionShufflePublic(id=q.id, prompt=q.prompt, options=options, layout_token=token))
        return result

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
                question_id=question_id,
                question_prompt=q.prompt,
                choice_letter=body.choice,
                choice_text=choice_text,
                is_correct=ok,
            )
        except Exception:
            logger.exception("Falha ao registrar tentativa Super FA")

        return AnswerResult(correct=ok)

    def list_answer_history(
        self, limit: int, offset: int
    ) -> SuperFaAnswerHistoryResponse:
        limit = min(max(limit, 1), 200)
        offset = max(offset, 0)
        total = self._history.count_all()
        rows = self._history.list_recent(limit, offset)
        items = [
            SuperFaAnswerHistoryEntry(
                id=ev.id,
                attempted_at=ev.attempted_at,
                super_fa_question_id=ev.super_fa_question_id,
                question_prompt=ev.question_prompt,
                choice_letter=ev.choice_letter,
                choice_text=ev.choice_text,
                is_correct=ev.is_correct,
            )
            for ev in rows
        ]
        return SuperFaAnswerHistoryResponse(
            items=items, total=total, limit=limit, offset=offset
        )


def get_super_fa_question_service(db: Session = Depends(get_db)) -> SuperFaQuestionService:
    return SuperFaQuestionService(db)
