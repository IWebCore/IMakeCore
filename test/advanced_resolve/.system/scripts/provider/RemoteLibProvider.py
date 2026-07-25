from __future__ import annotations
from typing import Any
from scripts.data.LibName import LibName
from scripts.provider.LibProvider import LibProvider


class RemoteLibProvider(LibProvider):
    def containLib(self, lib_name: LibName) -> bool:
        return False

    def findRealLibName(self, lib_name: LibName) -> None:
        return None

    def findPackages(self, lib_name: LibName) -> list[Any]:
        return []
