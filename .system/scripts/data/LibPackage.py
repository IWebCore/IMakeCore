from __future__ import annotations

import os
from typing import Any
from packaging.version import *
from packaging.specifiers import *
from sqlalchemy import Column, Integer, String, Boolean, Text, JSON, UniqueConstraint
from scripts.data.models import Base, get_session
from scripts.Utils import Utils
from scripts.data.LibName import LibName


class LibPackage(Base):
    __tablename__ = "lib_package"
    __table_args__ = (UniqueConstraint("publisher", "name", "version", name="uq_lib_package"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    publisher = Column(String(200), default="")
    is_global = Column(Boolean, default=True)
    version = Column(String(50), nullable=False)
    major_version = Column(Integer, default=0)
    minor_version = Column(Integer, default=0)
    patch_version = Column(Integer, default=0)
    summary = Column(Text, default="")
    mode = Column(String(50), default="sources")
    path = Column(String(1000), default="")
    content = Column(JSON, default={})

    success: bool = True

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self._detail_cache: Any = None
        self._supported_modes: list[str] = ["source", "static"]
        self.success: bool = True

    def __str__(self) -> str:
        return f"{self.fullName}@{self.version}"

    def __repr__(self) -> str:
        return f"<LibPackage {self.publisher}/{self.name}@{self.version}>"

    @property
    def fullName(self) -> str:
        if self.publisher:
            return f"{self.publisher}/{self.name}"
        return self.name

    @property
    def isGlobal(self) -> bool:
        return self.is_global

    @isGlobal.setter
    def isGlobal(self, value: bool) -> None:
        self.is_global = value

    # ── Dependency inner class ──────────────────────────────────────────

    class Dependency:
        def __init__(self, name: str, version: str) -> None:
            self.fullName = name
            self.version = version
            self.versionSpec = Utils.parseVersionSpecifier(version)

        def matchLib(self, libPackage: LibPackage) -> bool:
            if "/" in self.fullName:
                return self.fullName == (libPackage.publisher + "/" + libPackage.name) \
                        and self.versionSpec.contains(Version(libPackage.version))

            return self.fullName == libPackage.name \
                    and self.versionSpec.contains(Version(libPackage.version)) \
                    and libPackage.isGlobal

    # ── Static helpers ──────────────────────────────────────────────────

    @staticmethod
    def split_name(name: str) -> tuple[str, str, bool]:
        if "/" in name:
            parts = name.split("/", 1)
            return parts[0].strip(), parts[1].strip(), False
        return "", name.strip(), True

    # ── Factory: from filesystem ────────────────────────────────────────

    def getDependency(self) -> list[Dependency]:
        deps: list[LibPackage.Dependency] = []
        raw = (self.content or {}).get("dependencies", {})
        for k, v in raw.items():
            deps.append(LibPackage.Dependency(k, v))
        return deps

    @staticmethod
    def fromFolder(path: str) -> LibPackage:
        """Read package.json from *path* and return a new LibPackage instance."""
        json_path = os.path.join(path, "package.json")
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"package.json not found in {path}")
        json_data = Utils.loadJson(json_path)
        return LibPackage.fromFolderWithJson(path, json_data)

    @staticmethod
    def fromFolderWithJson(path: str, json_data: dict[str, Any]) -> LibPackage:
        """Build a LibPackage from a directory path and pre-loaded package.json dict."""
        publisher = json_data.get("publisher", "")
        name = json_data.get("name", "")
        version = json_data.get("version", "")
        if not name or not version:
            raise ValueError(f"Invalid package.json at {path}: name and version are required")

        parts = version.split(".")
        major = int(parts[0]) if len(parts) > 0 and parts[0].isdigit() else 0
        minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0

        raw_mode = json_data.get("mode", "sources")
        if isinstance(raw_mode, list):
            mode_str = raw_mode[0] if raw_mode else "sources"
        else:
            mode_str = raw_mode

        lp = LibPackage(
            publisher=publisher,
            name=name,
            is_global=json_data.get("isGlobal", True),
            version=version,
            major_version=major,
            minor_version=minor,
            patch_version=patch,
            summary=json_data.get("summary", ""),
            mode=mode_str,
            path=os.path.normpath(path),
            content=json_data,
        )

        lp.lib_name = LibName(lp.name, publisher=lp.publisher, is_global=lp.isGlobal)
        lp.success = True
        lp.autoScan = False
        lp.json = json_data

        # Validate
        if not lp.isGlobal and lp.publisher == "":
            raise ValueError(
                f"Invalid package.json, package {lp.name} is not global "
                f"and publisher is missing. Path:{path}"
            )

        # Parse supported modes — "sources" is accepted as a synonym for "source"
        supported = ["source", "static"]
        if raw_mode is not None:
            if isinstance(raw_mode, str):
                raw_mode = [raw_mode]
            normalized = []
            for m in raw_mode:
                m_norm = "source" if m == "sources" else m
                if m_norm not in ("source", "static", "dynamic"):
                    raise ValueError(f"ERROR: {lp.name}: invalid mode '{m}' in package.json mode list")
                normalized.append(m_norm)
            supported = normalized if normalized else ["source", "static"]
        lp._supported_modes = supported

        return lp

    # ── Factory: from database ──────────────────────────────────────────

    @staticmethod
    def loadFromDb(name: str, publisher: str = "") -> list[LibPackage]:
        """Query LibPackage from DB by name (and optional publisher).

        If publisher is empty, only return rows where is_global is True.
        """
        session = get_session()
        try:
            query = session.query(LibPackage)
            if publisher:
                query = query.filter(
                    LibPackage.publisher == publisher,
                    LibPackage.name == name,
                )
            else:
                query = query.filter(
                    LibPackage.name == name,
                    LibPackage.is_global == True,
                )
            return list(query.all())
        finally:
            session.close()

    def getDetail(self) -> Any:
        if hasattr(self, "_detail_cache") and self._detail_cache is not None:
            return self._detail_cache
        from scripts.data.LibPackageDetail import LibPackageDetail
        detail = LibPackageDetail.from_(self.path)
        if detail is not None:
            self._detail_cache = detail
        return detail

    def is_header_only(self) -> bool:
        detail = self.getDetail()
        if detail is None:
            return False
        return detail.is_header_only()

    def isMatch(self, package: Any) -> bool:
        """Match against either AppPackage (legacy) or RefPackage."""
        from scripts.data.RefPackage import RefPackage
        if isinstance(package, RefPackage):
            if "/" in package.name:
                matched = (self.publisher == package.name.split("/")[0]
                           and self.name == package.name.split("/")[1]
                           and package.version_range.contains(Version(self.version)))
            else:
                matched = (self.isGlobal and self.name == package.name
                           and package.version_range.contains(Version(self.version)))
            if not matched:
                return False
            user_mode = package.mode if package.mode != "default" else "source"
            return user_mode in getattr(self, "_supported_modes", ["source", "static"])
        if "/" in package.name:
            return (self.publisher == package.name.split("/")[0]
                    and self.name == package.name.split("/")[1]
                    and package.versionSpec.contains(Version(self.version)))
        return (self.isGlobal and self.name == package.name
                and package.versionSpec.contains(Version(self.version)))

    @classmethod
    def _virtual_from_resolve(cls, path: str, name: str, publisher: str | None,
                              version: str | None, resolve: dict[str, Any] | None) -> LibPackage:
        lp = cls(
            name=name,
            publisher=publisher or "local",
            version=version or "default",
            path=os.path.normpath(path),
            is_global=True,
            summary=f"[virtual] {publisher or 'local'}/{name}",
            mode=resolve.get("mode", "sources") if resolve else "sources",
            dependencies=[],
            content={},
        )
        lp._supported_modes = resolve.get("mode", ["source", "static"]) if resolve else ["source", "static"]
        lp._virtual_resolve = resolve
        return lp
