"""SQLAlchemy engine and session management."""

from __future__ import annotations

import logging
from collections.abc import Generator
from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Declarative base for all ORM models."""


def _ensure_sqlite_parent(database_url: str) -> None:
    if not database_url.startswith("sqlite:///"):
        return
    if database_url == "sqlite:///:memory:":
        return
    raw = database_url.removeprefix("sqlite:///")
    # Windows absolute paths may arrive as /C:/... from SQLAlchemy — normalize
    path = Path(raw)
    if raw.startswith("/") and len(raw) > 2 and raw[2] == ":":
        path = Path(raw[1:])
    path.parent.mkdir(parents=True, exist_ok=True)


def create_db_engine(database_url: str | None = None):
    settings = get_settings()
    url = database_url or settings.resolved_database_url
    _ensure_sqlite_parent(url)

    connect_args = {}
    if url.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(url, connect_args=connect_args, future=True)

    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


engine = create_db_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def init_db() -> None:
    """Create all tables. Import models so metadata is registered."""
    # Import side-effect: register models on Base.metadata
    from app import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
