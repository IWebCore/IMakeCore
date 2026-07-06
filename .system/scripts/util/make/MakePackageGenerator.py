from __future__ import annotations

import os
from typing import Any
from scripts.data.models import get_session
from scripts.data.LibPackageDetail import LibPackageDetail


class MakePackageGenerator:

    @staticmethod
    def _normalize_path(p: str) -> str:
        return os.path.normpath(p).replace(os.sep, "/")

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

    @staticmethod
    def _lib_output_path(lp: Any, env: Any, suffix: str) -> str:
        name = f"{lp.publisher}@{lp.name}@{lp.version}.{suffix}"
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

    @staticmethod
    def _header_comment(lp: Any) -> list[str]:
        return [
            "# SYSTEM AUTO GENERATED DO NOT EDIT!!!",
            f"# {lp.publisher}@{lp.name}@{lp.version}",
            f"# {lp.summary or ''}",
            "",
        ]

    def generate(self, pkg: Any, env: Any) -> str:
        raise NotImplementedError

    def post_process(self, packages: list[Any], env: Any) -> str:
        raise NotImplementedError
