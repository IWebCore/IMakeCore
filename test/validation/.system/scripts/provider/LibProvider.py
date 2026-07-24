from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class LibProvider(ABC):
    @abstractmethod
    def containLib(self, lib_name: Any) -> bool: ...

    @abstractmethod
    def findRealLibName(self, lib_name: Any) -> Any | None: ...

    @abstractmethod
    def findPackages(self, lib_name: Any) -> list[Any]: ...
