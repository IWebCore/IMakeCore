from __future__ import annotations

from typing import Any
from packaging.version import Version
from sqlalchemy import Column, Integer, String, Boolean
from scripts.data.models import Base
from scripts.data.LibName import LibName


class LibPackageDownload(Base):
    __tablename__ = "lib_package_download"

    id = Column(Integer, primary_key=True, autoincrement=True)
    path_info = Column(String(2000), default="")
    success = Column(Boolean, default=False)
    target = Column(String(1000), default="")
    name = Column(String(200), nullable=False)
    publisher = Column(String(200), default="")
    version = Column(String(50), nullable=False)

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    def __str__(self) -> str:
        return f"{self.lib_name.fullName()}@{self.version}"

    def __repr__(self) -> str:
        return (f"<LibPackageDownload {self.publisher}/{self.name}@{self.version}"
                f" success={self.success}>")

    # ── lib_name ─────────────────────────────────────────────────────────

    @property
    def lib_name(self) -> LibName:
        if hasattr(self, "_lib_name_cache"):
            return self._lib_name_cache
        ln = LibName(self.name, publisher=self.publisher)
        self._lib_name_cache = ln
        return ln

    @lib_name.setter
    def lib_name(self, value: LibName) -> None:
        self._lib_name_cache = value

    # ── version as packaging Version ─────────────────────────────────────

    @property
    def version_obj(self) -> Version:
        if hasattr(self, "_version_cache") and self._version_cache is not None:
            return self._version_cache
        v = Version(self.version)
        self._version_cache = v
        return v
