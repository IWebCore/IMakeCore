"""
LibPackageDetail.py — ORM model for scanned package detail (headers, sources, etc.).
Replaces the old LibPackageDetailTable from models.py.
"""
from __future__ import annotations

import os as _os
from typing import Any
from sqlalchemy import Column, Integer, String, Text, UniqueConstraint
from scripts.data.models import Base, get_session


class LibPackageDetail(Base):
    __tablename__ = "lib_package_detail"
    __table_args__ = (
        UniqueConstraint("publisher", "name", "version", name="uq_lib_package_detail"),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    path = Column(String(1000), default="")
    name = Column(String(200), nullable=False)
    publisher = Column(String(200), default="")
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
        return f"<LibPackageDetail {self.publisher}/{self.name}@{self.version}>"

    # ── List serialization ───────────────────────────────────────────────

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

    def is_header_only(self) -> bool:
        return (len(self.get_sources()) == 0
                and len(self.get_uis()) == 0
                and len(self.get_resources()) == 0)

    @staticmethod
    def fromPath(path: str) -> LibPackageDetail:
        """Scan a package directory and return a LibPackageDetail.
        Loads package.json for resolve config, uses PackageScanner."""
        from scripts.util.scanner.PackageScanner import PackageScanner
        from scripts.Utils import Utils

        pkg_json_path = _os.path.join(path, "package.json")
        resolve_data = {}
        if _os.path.exists(pkg_json_path):
            pkg_data = Utils.loadJson(pkg_json_path)
            resolve_data = pkg_data.get("resolve", {}) or {}

        scanner = PackageScanner(path, resolve_data)
        result = scanner.scan()  # returns LibPackageDetail directly

        # Set metadata from scanned result
        result.path = _os.path.normpath(path)

        # name/publisher/version from package.json if available
        if _os.path.exists(pkg_json_path):
            pkg_data = Utils.loadJson(pkg_json_path)
            result.name = pkg_data.get("name", "")
            result.publisher = pkg_data.get("publisher", "")
            result.version = pkg_data.get("version", "")

        return result

    @staticmethod
    def fromDb(path: str) -> LibPackageDetail | None:
        """Load from DB by path."""
        session = get_session()
        try:
            return session.query(LibPackageDetail).filter_by(path=path).first()
        finally:
            session.close()

    @staticmethod
    def from_(path: str) -> LibPackageDetail:
        """Try DB first, fall back to scan."""
        result = LibPackageDetail.fromDb(path)
        if result is not None:
            return result
        return LibPackageDetail.fromPath(path)
