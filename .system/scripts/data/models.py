"""
SQLAlchemy engine, session factory, and ORM models for IMakeCore package database.

Database location: ``$IMAKECORE_ROOT/.db/package.db``
"""
from __future__ import annotations

import os
from typing import Any
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session

_engine: Any = None


def get_engine() -> Any:
    """Lazily create and return the SQLAlchemy engine.

    Database path: ``$IMAKECORE_ROOT/.db/package.db``.
    Falls back to ``.system/db/`` if the env var is not set.
    """
    global _engine
    if _engine is None:
        imakecore_root = os.getenv("IMAKECORE_ROOT", "").strip()
        if imakecore_root:
            db_dir = os.path.normpath(os.path.join(imakecore_root, ".db"))
        else:
            db_dir = os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "..", "..", "db"
            )
        db_path = os.path.normpath(os.path.join(db_dir, "package.db"))
        os.makedirs(db_dir, exist_ok=True)
        _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    return _engine


Base = declarative_base()


def get_session() -> Session:
    """Create and return a new SQLAlchemy session."""
    return sessionmaker(bind=get_engine())()
