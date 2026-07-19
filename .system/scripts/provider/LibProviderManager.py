from __future__ import annotations
from typing import Any
from scripts.data.LibName import LibName
from scripts.provider.LocalLibProvider import LocalLibProvider
from scripts.provider.SystemLibProvider import SystemLibProvider
from scripts.provider.RemoteLibProvider import RemoteLibProvider


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
        pkgs = self._locals.findPackages(lib_name)
        if pkgs:
            return pkgs
        pkgs = self._system.findPackages(lib_name)
        if pkgs:
            return pkgs
        return self._remote.findPackages(lib_name)
