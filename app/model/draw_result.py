from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.model.base import Base


class DrawResult(Base):
    """Registro de cada sorteio realizado na tela admin."""

    __tablename__ = "draw_results"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    winner_nickname: Mapped[str] = mapped_column(String(120), nullable=False)
    winner_score: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    participant_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    drawn_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
