from __future__ import annotations
import json
import os
from typing import Any
from packaging.version import Version
from scripts.data.LibPackage import LibPackage
from scripts.data.LibName import LibName
from scripts.Utils import Utils
from scripts.provider.LibProvider import LibProvider


class LocalLibProvider(LibProvider):
    def __init__(self, lib_store_path: str):
        self._lib_store_path = os.path.normpath(lib_store_path)
        # key = lib_name.fullName(), value = list[LibPackage] sorted by version desc
        self._packages: dict[str, list[LibPackage]] = {}
        self._cache: dict[str, dict[str, Any]] = {}
        self._cache_path = os.path.normpath(
            os.path.join(os.path.dirname(self._lib_store_path), ".data", "localLibCache.json")
        )
        self._load_cache()
        self._scan()

    # ── Cache ──────────────────────────────────────────────────────────────

    def _load_cache(self) -> None:
        if os.path.exists(self._cache_path):
            try:
                self._cache = Utils.loadJson(self._cache_path)
            except Exception:
                self._cache = {}

    def _save_cache(self) -> None:
        cache_dir = os.path.dirname(self._cache_path)
        os.makedirs(cache_dir, exist_ok=True)
        with open(self._cache_path, "w", encoding="utf-8") as f:
            json.dump(self._cache, f, indent=2, ensure_ascii=False)

    def _update_cache(self, lp: LibPackage) -> None:
        if not lp.path:
            return
        raw = getattr(lp, "json", None) or lp.content
        if raw:
            self._cache[lp.path] = raw
            self._save_cache()

    # ── Internal helpers ───────────────────────────────────────────────────

    def _insert_sorted(self, lp: LibPackage) -> None:
        """Insert lp into _packages dict.

        If an existing entry with the same lib_name + version exists, replace it.
        Otherwise append and keep the list sorted by version descending.
        """
        key = lp.lib_name.fullName()
        lst = self._packages.setdefault(key, [])
        for i, existing in enumerate(lst):
            if existing.lib_name == lp.lib_name and existing.version == lp.version:
                lst[i] = lp
                return
        lst.append(lp)
        lst.sort(key=lambda x: Version(x.version), reverse=True)

    # ── Scanning ───────────────────────────────────────────────────────────

    def _scan(self) -> None:
        if not os.path.exists(self._lib_store_path):
            return
        for entry in os.listdir(self._lib_store_path):
            pkg_dir = os.path.normpath(os.path.join(self._lib_store_path, entry))
            if not os.path.isdir(pkg_dir):
                continue
            pkg_json_path = os.path.join(pkg_dir, "package.json")
            if not os.path.exists(pkg_json_path):
                continue
            try:
                if pkg_dir in self._cache:
                    lib = LibPackage.fromFolderWithJson(pkg_dir, self._cache[pkg_dir])
                else:
                    lib = LibPackage.fromFolder(pkg_dir)
                    self._cache[pkg_dir] = getattr(lib, "json", lib.content)
                    self._save_cache()
                self._insert_sorted(lib)
            except Exception:
                pass

    def appendLibs(self, lp: LibPackage) -> None:
        self._insert_sorted(lp)
        self._update_cache(lp)

    # ── Provider interface ─────────────────────────────────────────────────

    def containLib(self, lib_name: LibName) -> bool:
        key = lib_name.fullName()
        items = self._packages.get(key)
        return items is not None and len(items) > 0

    def findRealLibName(self, lib_name: LibName) -> LibName | None:
        for lst in self._packages.values():
            for p in lst:
                if p.lib_name.name == lib_name.name and p.lib_name.is_global:
                    return p.lib_name
        return None

    def findPackages(self, lib_name: LibName) -> list[LibPackage]:
        return list(self._packages.get(lib_name.fullName(), []))
