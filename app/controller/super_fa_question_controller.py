from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.schema.question_schema import (
    AnswerResult,
    AnswerSubmit,
    QuestionShufflePublic,
    SuperFaAnswerHistoryResponse,
)
from app.service.super_fa_question_service import (
    SuperFaQuestionService,
    get_super_fa_question_service,
)

router = APIRouter(prefix="/super-fa/questions", tags=["super-fa"])


@router.get("/answer-history", response_model=SuperFaAnswerHistoryResponse)
def super_fa_answer_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    service: SuperFaQuestionService = Depends(get_super_fa_question_service),
) -> SuperFaAnswerHistoryResponse:
    """Histórico de tentativas (Super FA / Super Quiz): pergunta, resposta e horário."""
    return service.list_answer_history(limit, offset)


@router.get("/random", response_model=QuestionShufflePublic)
def random_super_fa_question(
    service: SuperFaQuestionService = Depends(get_super_fa_question_service),
) -> QuestionShufflePublic:
    """Pergunta aleatória da tabela `super_fa_questions`."""
    return service.random_question()


@router.post("/{question_id}/answer", response_model=AnswerResult)
def submit_super_fa_answer(
    question_id: UUID,
    body: AnswerSubmit,
    service: SuperFaQuestionService = Depends(get_super_fa_question_service),
) -> AnswerResult:
    return service.check_answer(question_id, body)
