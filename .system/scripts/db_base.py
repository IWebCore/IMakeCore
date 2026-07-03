"""
SQLAlchemy engine and session factory for IMakeCore package database.

Database location: .system/db/package.db
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

_engine = None


def get_engine():
    """Lazily create and return the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "db")
        db_path = os.path.normpath(os.path.join(db_dir, "package.db"))
        os.makedirs(db_dir, exist_ok=True)
        _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    return _engine


Base = declarative_base()


def get_session():
    """Create and return a new SQLAlchemy session."""
    return sessionmaker(bind=get_engine())()
