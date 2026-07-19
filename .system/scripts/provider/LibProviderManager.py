from __future__ import annotations
from typing import Any
from packaging.version import Version
from scripts.data.LibName import LibName
from scripts.provider.LocalLibProvider import LocalLibProvider
from scripts.provider.SystemLibProvider import SystemLibProvider
from scripts.provider.RemoteLibProvider import RemoteLibProvider

_POSITION_PRIORITY = {"local": 0, "system": 1, "remote": 2}


class LibProviderManager:
    def __init__(self, project_lib_store_path: str):
        self._locals = LocalLibProvider(project_lib_store_path)
        self._system = SystemLibProvider()
        self._remote = RemoteLibProvider()

    def getLocalProvider(self) -> LocalLibProvider:
        return self._locals

    def getSystemProvider(self) -> SystemLibProvider:
        return self._system

    def getRemoteProvider(self) -> RemoteLibProvider:
        return self._remote

    def findPackages(self, lib_name: LibName) -> list[Any]:
        all_pkgs = (
            self._locals.findPackages(lib_name)
            + self._system.findPackages(lib_name)
            + self._remote.findPackages(lib_name)
        )
        all_pkgs.sort(key=lambda p: _POSITION_PRIORITY.get(p.position, 99))
        all_pkgs.sort(key=lambda p: Version(p.version), reverse=True)
        return all_pkgs

    def containLib(self, lib_name: LibName) -> bool:
        return (
            self._locals.containLib(lib_name)
            or self._system.containLib(lib_name)
            or self._remote.containLib(lib_name)
        )

    def findRealLibName(self, lib_name: LibName) -> LibName | None:
        for provider in (self._locals, self._system, self._remote):
            real = provider.findRealLibName(lib_name)
            if real is not None:
                return real
        return None
