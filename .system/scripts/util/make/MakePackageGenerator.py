from __future__ import annotations

import json
import os
from abc import ABC, abstractmethod
from typing import Any

from scripts.data.LibPackageDetail import LibPackageDetail
from scripts.data.models import get_session


class MakePackageGenerator(ABC):
    """Base class for build-system package generators.

    Each build system expresses its concrete behaviour through the virtual
    interface below; the shared orchestration (support-lib store layout,
    support-project scaffolding and the condition file) lives here and
    delegates the content generation to the implementing subclass.

    Virtual interface every generator implements:

    - :meth:`generate` / :meth:`post_process` — per-package include file
      and the include-chain file.
    - :meth:`support_lib_filename` / :meth:`support_lib_content` — the
      per-lib build script inside each ``.support/<lib>`` directory.
    - :meth:`support_project_filename` / :meth:`support_project_content` —
      the ``.support`` sub-projects aggregator.
    - :attr:`condition_file_name` — the user-editable condition file.
    """

    #: comment prefix used in generated files ("#" for qmake/cmake, "--" for xmake)
    _comment = "#"
    #: suffix of the per-package include file stored in the lib store
    _lib_suffix = ""
    #: filename of the user-editable condition file inside ``.support/``
    condition_file_name = ""

    # ── shared helpers ──────────────────────────────────────────────────────

    @classmethod
    def _get_lp(cls, pkg: Any) -> Any:
        return getattr(pkg, "real_package", None) or getattr(pkg, "libPackage", None)

    @staticmethod
    def _normalize_path(path: str) -> str:
        return os.path.normpath(path).replace(os.sep, "/")

    @staticmethod
    def _get_detail_from_db(publisher: str, name: str, version: str) -> LibPackageDetail | None:
        session = get_session()
        try:
            return session.query(LibPackageDetail).filter_by(
                publisher=publisher, name=name, version=version
            ).first()
        finally:
            session.close()

    @staticmethod
    def _get_file_paths(detail: LibPackageDetail | None) -> dict[str, list[str]] | None:
        if detail is None:
            return None
        return {
            "headers": detail.get_headers(),
            "sources": detail.get_sources(),
            "uis": detail.get_uis(),
            "resources": detail.get_resources(),
            "definitions": detail.get_definitions(),
            "includes": detail.get_includes(),
            "precompile_headers": detail.get_precompile_headers(),
            "dynamic_definition": detail.get_dynamic_definition(),
        }

    @classmethod
    def _per_package_path(cls, lp: Any, env: Any) -> str:
        name = f"{lp.publisher}@{lp.name}@{lp.version}.{cls._lib_suffix}"
        return os.path.join(env.appLibStore, name)

    @staticmethod
    def _write_if_changed(path: str, content: str) -> str:
        if os.path.exists(path):
            with open(path, "rt", encoding="utf-8") as f:
                if f.read() == content:
                    return path
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wt", encoding="utf-8") as f:
            f.write(content)
        return path

    @classmethod
    def _header_comment(cls, lp: Any) -> str:
        c = cls._comment
        return (
            f"{c} SYSTEM AUTO GENERATED DO NOT EDIT!!!\n"
            f"{c} {lp.publisher}@{lp.name}@{lp.version}\n"
            f"{c} {lp.summary or ''}\n"
            "\n"
        )

    @staticmethod
    def _get_support_detail(lp: Any) -> LibPackageDetail | None:
        session = get_session()
        try:
            return session.query(LibPackageDetail).filter_by(
                publisher=lp.publisher, name=lp.name, version=lp.version
            ).first()
        finally:
            session.close()

    @staticmethod
    def _support_dir_names(lib_packages: list[Any]) -> list[str]:
        dirs: list[str] = []
        for p in lib_packages:
            lp = getattr(p, "real_package", None)
            if lp is None:
                continue
            mode = getattr(p, "mode", "static")
            dirs.append(f"{lp.publisher}@{lp.name}@{lp.version}_{mode}")
        return dirs

    # ── virtual interface ──────────────────────────────────────────────────

    @abstractmethod
    def generate(self, pkg: Any, env: Any) -> str:
        """Emit the per-package include file; returns its path ("" to skip)."""

    @abstractmethod
    def post_process(self, packages: list[Any], env: Any) -> str:
        """Return the include-chain file content."""

    @abstractmethod
    def support_lib_filename(self, dir_name: str) -> str:
        """Return the build-script filename inside a ``.support/<lib>`` dir."""

    @abstractmethod
    def support_lib_content(self, lp: Any, mode: str, pkg_dir: str) -> str:
        """Return the per-lib build-script content."""

    @abstractmethod
    def support_project_filename(self, project_name: str) -> str:
        """Return the aggregator filename inside ``.support/``."""

    @abstractmethod
    def support_project_content(self, project_name: str, lib_packages: list[Any]) -> str:
        """Return the ``.support`` sub-projects aggregator content."""

    # ── shared support orchestration ───────────────────────────────────────

    def generate_support_libs(self, lib_packages: list[Any], env: Any) -> None:
        """Scaffold ``.support/<lib>`` for every static/dynamic package."""
        support_dir = os.path.normpath(os.path.join(env.appPath, ".support"))
        os.makedirs(support_dir, exist_ok=True)
        for p in lib_packages:
            lp = self._get_lp(p)
            if lp is None:
                continue
            mode = getattr(p, "mode", "static")
            dir_name = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
            pkg_dir = os.path.join(support_dir, dir_name)
            os.makedirs(pkg_dir, exist_ok=True)
            self._write_support_packages_json(pkg_dir, lp)
            self._write_support_lib_file(pkg_dir, lp, dir_name, mode)

    @staticmethod
    def _write_support_packages_json(pkg_dir: str, lp: Any) -> None:
        data = {"packages": {f"{lp.publisher}/{lp.name}": "*"}}
        with open(os.path.join(pkg_dir, "packages.json"), "wt", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _write_support_lib_file(self, pkg_dir: str, lp: Any, dir_name: str, mode: str) -> None:
        content = self.support_lib_content(lp, mode, pkg_dir)
        with open(os.path.join(pkg_dir, self.support_lib_filename(dir_name)), "wt", encoding="utf-8") as f:
            f.write(content)

    def generate_support_project(self, project_name: str, lib_packages: list[Any], env: Any) -> str:
        """Emit the ``.support`` sub-projects aggregator."""
        support_dir = os.path.normpath(os.path.join(env.appPath, ".support"))
        os.makedirs(support_dir, exist_ok=True)
        self._ensure_condition_file(support_dir)
        out_path = os.path.join(support_dir, self.support_project_filename(project_name))
        with open(out_path, "wt", encoding="utf-8") as f:
            f.write(self.support_project_content(project_name, lib_packages))
        return out_path

    def _ensure_condition_file(self, support_dir: str) -> None:
        path = os.path.join(support_dir, self.condition_file_name)
        if os.path.exists(path):
            return
        c = self._comment
        content = (
            f"{c} IMAKECORE Condition — user-customizable shared settings\n"
            f"{c} DO NOT DELETE this file. Edit to add shared build config.\n"
            f"{c} Included before all sub-projects.\n"
        )
        with open(path, "wt", encoding="utf-8") as f:
            f.write(content)
