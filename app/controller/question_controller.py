from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.schema.question_schema import (
    AnswerHistoryResponse,
    AnswerResult,
    AnswerSubmit,
    QuestionShufflePublic,
)
from app.service.question_service import QuestionService, get_question_service

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("/answer-history", response_model=AnswerHistoryResponse)
def answer_history(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    participant_id: UUID | None = Query(
        default=None,
        description="Filtrar por participante (opcional).",
    ),
    service: QuestionService = Depends(get_question_service),
) -> AnswerHistoryResponse:
    """Histórico de respostas: pergunta, texto da opção escolhida, acerto e data/hora."""
    return service.list_answer_history(limit, offset, participant_id)


@router.get("/random", response_model=QuestionShufflePublic)
def random_question(
    service: QuestionService = Depends(get_question_service),
) -> QuestionShufflePublic:
    """Pergunta aleatória; alternativas A–D vêm em ordem aleatória a cada chamada."""
    return service.random_question()


@router.post("/{question_id}/answer", response_model=AnswerResult)
def submit_answer(
    question_id: UUID,
    body: AnswerSubmit,
    service: QuestionService = Depends(get_question_service),
) -> AnswerResult:
    """Valida a letra tocada na tela usando o mesmo embaralhamento do `layout_token`."""
    return service.check_answer(question_id, body)
