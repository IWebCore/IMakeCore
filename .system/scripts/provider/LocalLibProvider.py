from __future__ import annotations
import os
from typing import Any
from packaging.version import Version
from scripts.data.LibPackage import LibPackage
from scripts.data.LibName import LibName
from scripts.provider.LibProvider import LibProvider


class LocalLibProvider(LibProvider):
    def __init__(self, lib_store_path: str):
        self._packages: list[LibPackage] = []
        self._scan(lib_store_path)

    def _scan(self, lib_store_path: str) -> None:
        if not os.path.exists(lib_store_path):
            return
        for entry in os.listdir(lib_store_path):
            pkg_dir = os.path.join(lib_store_path, entry)
            if not os.path.isdir(pkg_dir):
                continue
            pkg_json = os.path.join(pkg_dir, "package.json")
            if not os.path.exists(pkg_json):
                continue
            try:
                lib = LibPackage.fromFolder(pkg_dir)
                lib.position = "local"
                self._packages.append(lib)
            except Exception:
                pass

    def appendLibs(self, lp: LibPackage) -> None:
        lp.position = "local"
        self._packages.append(lp)

    def containLib(self, lib_name: LibName) -> bool:
        return any(p.lib_name.fullName() == lib_name.fullName() for p in self._packages)

    def findRealLibName(self, lib_name: LibName) -> LibName | None:
        for p in self._packages:
            if p.lib_name.name == lib_name.name and p.lib_name.is_global:
                return p.lib_name
        return None

    def findPackages(self, lib_name: LibName) -> list[LibPackage]:
        result = [p for p in self._packages if p.lib_name.fullName() == lib_name.fullName()]
        result.sort(key=lambda x: Version(x.version), reverse=True)
        return result
