from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NameLookupRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class ParticipantSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nickname: str


class NameLookupResponse(BaseModel):
    found: bool
    participant: ParticipantSummary | None = None


class ParticipantCreateRequest(BaseModel):
    nickname: str = Field(min_length=2, max_length=120)


class ParticipantCreateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nickname: str
    score: int = 0


class RankingEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    rank: int = Field(ge=1, description="Posição no ranking global (1 = primeiro)")
    id: UUID
    nickname: str
    score: int


class RankingResponse(BaseModel):
    items: list[RankingEntry]
    total: int
    limit: int
    offset: int


class DrawCandidateEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nickname: str
    score: int


class ParticipantSearchEntry(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    nickname: str


class ParticipantSearchResponse(BaseModel):
    items: list[ParticipantSearchEntry]


class DrawCandidatesResponse(BaseModel):
    """Todos os participantes (até limite) ordenados por pontuação, para tela de sorteio."""

    items: list[DrawCandidateEntry]
    total_registered: int
