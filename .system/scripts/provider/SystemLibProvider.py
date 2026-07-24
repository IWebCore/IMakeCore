from __future__ import annotations
from typing import Any
from packaging.version import Version
from scripts.data.LibPackage import LibPackage
from scripts.data.LibName import LibName
from scripts.data.models import get_session
from scripts.provider.LibProvider import LibProvider


class SystemLibProvider(LibProvider):
    def containLib(self, lib_name: LibName) -> bool:
        return self.findRealLibName(lib_name) is not None

    def findRealLibName(self, lib_name: LibName) -> LibName | None:
        pkgs = self.findPackages(lib_name)
        if pkgs:
            return pkgs[0].lib_name
        return None

    def findPackages(self, lib_name: LibName) -> list[LibPackage]:
        session = get_session()
        try:
            query = session.query(LibPackage)
            if lib_name.publisher:
                query = query.filter(
                    LibPackage.publisher == lib_name.publisher,
                    LibPackage.name == lib_name.name,
                )
            elif lib_name.is_global:
                query = query.filter(
                    LibPackage.name == lib_name.name,
                    LibPackage.is_global == True,
                )
            else:
                return []
            result = list(query.all())
            result.sort(key=lambda x: Version(x.version), reverse=True)
            return result
        finally:
            session.close()
