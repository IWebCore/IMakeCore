"""
SQLAlchemy engine, session factory, and ORM models for IMakeCore package database.

Database location: .system/db/package.db
"""
from __future__ import annotations

import os
from typing import Any
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Text, JSON, UniqueConstraint
from sqlalchemy.orm import declarative_base, sessionmaker, Session

_engine: Any = None


def get_engine() -> Any:
    """Lazily create and return the SQLAlchemy engine."""
    global _engine
    if _engine is None:
        db_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "db")
        db_path = os.path.normpath(os.path.join(db_dir, "package.db"))
        os.makedirs(db_dir, exist_ok=True)
        _engine = create_engine(f"sqlite:///{db_path}", echo=False)
    return _engine


Base = declarative_base()


def get_session() -> Session:
    """Create and return a new SQLAlchemy session."""
    return sessionmaker(bind=get_engine())()


class LibPackageTable(Base):
    __tablename__ = "lib_package"
    __table_args__ = (
        UniqueConstraint("publisher", "name", "version", name="uq_lib_package"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    publisher = Column(String(200), default="")
    name = Column(String(200), nullable=False)
    is_global = Column(Boolean, default=True)
    version = Column(String(50), nullable=False)
    summary = Column(Text, default="")
    mode = Column(String(50), default="sources")
    path = Column(String(1000), default="")
    dependencies = Column(JSON, default=[])

    def __repr__(self) -> str:
        return f"<LibPackageTable {self.publisher}/{self.name}@{self.version}>"


class LibPackageDetailTable(Base):
    __tablename__ = "lib_package_detail"
    __table_args__ = (
        UniqueConstraint("group", "name", "version", name="uq_lib_package_detail"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(1000), default="")
    name = Column(String(200), nullable=False)
    group = Column(String(200), default="")
    version = Column(String(50), nullable=False)
    headers = Column(Text, default="")
    sources = Column(Text, default="")
    uis = Column(Text, default="")
    resources = Column(Text, default="")
    definitions = Column(Text, default="")
    includes = Column(Text, default="")
    precompile_headers = Column(Text, default="")
    dynamic_definition = Column(Text, default="")

    SEP: str = ";"

    def __repr__(self) -> str:
        return f"<LibPackageDetailTable {self.group}/{self.name}@{self.version}>"

    @classmethod
    def list_to_str(cls, file_list: list[str]) -> str:
        if not file_list:
            return ""
        return cls.SEP.join(file_list)

    @classmethod
    def str_to_list(cls, file_str: str | None) -> list[str]:
        if not file_str or not file_str.strip():
            return []
        return [f for f in file_str.split(cls.SEP) if f.strip()]

    def get_headers(self) -> list[str]:
        return self.str_to_list(self.headers)

    def get_sources(self) -> list[str]:
        return self.str_to_list(self.sources)

    def get_uis(self) -> list[str]:
        return self.str_to_list(self.uis)

    def get_resources(self) -> list[str]:
        return self.str_to_list(self.resources)

    def get_definitions(self) -> list[str]:
        return self.str_to_list(self.definitions)

    def get_includes(self) -> list[str]:
        return self.str_to_list(self.includes)

    def get_precompile_headers(self) -> list[str]:
        return self.str_to_list(self.precompile_headers)

    def get_dynamic_definition(self) -> list[str]:
        return self.str_to_list(self.dynamic_definition)

    @classmethod
    def from_scan_result(cls, scan_result: Any, path: str, name: str, group: str, version: str) -> LibPackageDetailTable:
        detail = cls()
        detail.path = path
        detail.name = name
        detail.group = group
        detail.version = version
        detail.headers = cls.list_to_str(scan_result.headers)
        detail.sources = cls.list_to_str(scan_result.sources)
        detail.uis = cls.list_to_str(scan_result.uis)
        detail.resources = cls.list_to_str(scan_result.resources)
        detail.definitions = cls.list_to_str(getattr(scan_result, "definitions", []))
        detail.includes = cls.list_to_str(getattr(scan_result, "includes", ["."]))
        detail.precompile_headers = cls.list_to_str(getattr(scan_result, "precompile_headers", []))
        detail.dynamic_definition = cls.list_to_str(getattr(scan_result, "dynamic_definition", []))
        return detail
