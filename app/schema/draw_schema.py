import uuid
from datetime import datetime

from pydantic import BaseModel


class DrawRecordRequest(BaseModel):
    winner_nickname: str
    winner_score: int
    participant_count: int


class DrawResultEntry(BaseModel):
    model_config = {"from_attributes": True}

    id: uuid.UUID
    winner_nickname: str
    winner_score: int
    participant_count: int
    drawn_at: datetime


class DrawHistoryResponse(BaseModel):
    items: list[DrawResultEntry]
    total: int
    limit: int
    offset: int
