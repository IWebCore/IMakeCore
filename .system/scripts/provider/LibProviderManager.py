from __future__ import annotations
from typing import Any
from packaging.version import Version
from scripts.data.LibName import LibName
from scripts.provider.LocalLibProvider import LocalLibProvider
from scripts.provider.SystemLibProvider import SystemLibProvider
from scripts.provider.RemoteLibProvider import RemoteLibProvider


class LibProviderManager:
    _instance: LibProviderManager | None = None

    def __init__(self, project_lib_store_path: str):
        self._locals = LocalLibProvider(project_lib_store_path)
        self._system = SystemLibProvider()
        self._remote = RemoteLibProvider()

    @classmethod
    def init(cls, project_lib_store_path: str) -> LibProviderManager:
        if cls._instance is None:
            cls._instance = cls(project_lib_store_path)
        return cls._instance

    @classmethod
    def instance(cls) -> LibProviderManager:
        if cls._instance is None:
            raise RuntimeError(
                "LibProviderManager is not initialized. Call LibProviderManager.init() first."
            )
        return cls._instance

    def getLocalProvider(self) -> LocalLibProvider:
        return self._locals

    def getSystemProvider(self) -> SystemLibProvider:
        return self._system

    def getRemoteProvider(self) -> RemoteLibProvider:
        return self._remote

    def findPackages(self, lib_name: LibName) -> list[Any]:
        local_pkgs = self._locals.findPackages(lib_name)
        system_pkgs = self._system.findPackages(lib_name)
        remote_pkgs = self._remote.findPackages(lib_name)

        # Deduplicate by version: local beats system beats remote.
        seen_versions: set[str] = set()
        result: list[Any] = []

        for pkg in local_pkgs:
            seen_versions.add(pkg.version)
            result.append(pkg)

        for pkg in system_pkgs:
            if pkg.version not in seen_versions:
                seen_versions.add(pkg.version)
                result.append(pkg)

        for pkg in remote_pkgs:
            if pkg.version not in seen_versions:
                seen_versions.add(pkg.version)
                result.append(pkg)

        result.sort(key=lambda p: Version(p.version), reverse=True)
        return result

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
