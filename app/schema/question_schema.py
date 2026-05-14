from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ShuffledOption(BaseModel):
    """Uma alternativa na tela, com letra A–D na ordem exibida (já embaralhada)."""

    letter: Literal["A", "B", "C", "D"]
    text: str = Field(max_length=500)


class QuestionShufflePublic(BaseModel):
    """Pergunta com alternativas em ordem aleatória; use `layout_token` ao responder."""

    id: UUID
    prompt: str
    options: list[ShuffledOption] = Field(
        min_length=4,
        max_length=4,
        description="Sempre 4 itens, letras A–D na ordem mostrada ao jogador.",
    )
    layout_token: str = Field(
        description="Token assinado que descreve o embaralhamento desta rodada."
    )


class AnswerSubmit(BaseModel):
    choice: Literal["A", "B", "C", "D"] = Field(
        description="Letra da alternativa tocada na tela (após embaralhamento)."
    )
    layout_token: str = Field(description="Token recebido junto com a mesma pergunta.")
    participant_id: UUID | None = Field(
        default=None,
        description="Opcional: se informado e a resposta estiver correta, soma 1 ponto ao participante.",
    )


class AnswerResult(BaseModel):
    """Não revela qual era a correta quando `correct` é false."""

    correct: bool = Field(
        description="True se a escolha na tela corresponde à única resposta correta no banco."
    )


class AnswerHistoryEntry(BaseModel):
    id: UUID
    answered_at: datetime
    participant_id: UUID | None
    participant_nickname: str | None = None
    question_id: UUID | None
    question_prompt: str
    choice_letter: str
    choice_text: str
    is_correct: bool


class AnswerHistoryResponse(BaseModel):
    items: list[AnswerHistoryEntry]
    total: int
    limit: int
    offset: int


class SuperFaAnswerHistoryEntry(BaseModel):
    id: UUID
    attempted_at: datetime
    super_fa_question_id: UUID | None
    question_prompt: str
    choice_letter: str
    choice_text: str
    is_correct: bool


class SuperFaAnswerHistoryResponse(BaseModel):
    items: list[SuperFaAnswerHistoryEntry]
    total: int
    limit: int
    offset: int
