from collections.abc import Generator
from typing import Any

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.model import Base  # noqa: F401 — registra metadata (Participant)


def _to_psycopg_url(url: str) -> str:
    if url.startswith("postgresql+psycopg://"):
        return url
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


engine: Engine | None = None
SessionLocal: sessionmaker[Session] | None = None

if settings.database_url:
    engine = create_engine(
        _to_psycopg_url(settings.database_url),
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10,
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db() -> None:
    """Cria tabelas ausentes (MVP). Para produção, prefira Alembic."""
    if engine is None:
        return
    Base.metadata.create_all(bind=engine)
    _ensure_participant_score_column()
    _ensure_score_updated_at_column()


def _ensure_participant_score_column() -> None:
    """Compatibilidade: adiciona coluna score em bancos criados antes do ranking."""
    if engine is None:
        return
    insp = inspect(engine)
    if not insp.has_table("participants"):
        return
    colnames = {c["name"] for c in insp.get_columns("participants")}
    if "score" in colnames:
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE participants ADD COLUMN score INTEGER NOT NULL DEFAULT 0"
            )
        )


def _ensure_score_updated_at_column() -> None:
    """Adiciona score_updated_at para desempate por ordem de conquista."""
    if engine is None:
        return
    insp = inspect(engine)
    if not insp.has_table("participants"):
        return
    colnames = {c["name"] for c in insp.get_columns("participants")}
    if "score_updated_at" in colnames:
        return
    with engine.begin() as conn:
        conn.execute(
            text(
                "ALTER TABLE participants ADD COLUMN score_updated_at TIMESTAMPTZ NOT NULL DEFAULT now()"
            )
        )


def ping_db() -> bool:
    if engine is None:
        return False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False


def get_db() -> Generator[Session, Any, None]:
    if SessionLocal is None:
        raise RuntimeError("DATABASE_URL não configurada")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
