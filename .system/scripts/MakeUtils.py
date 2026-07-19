from __future__ import annotations

import json
import os
import shutil
from typing import Any
from scripts.data import *
from scripts.util.make.QmakePackageGenerator import QmakePackageGenerator
from scripts.util.make.CmakePackageGenerator import CmakePackageGenerator


class MakeUtils:

    _qmake_gen = QmakePackageGenerator()
    _cmake_gen = CmakePackageGenerator()

    @staticmethod
    def _get_lp(pkg: Any) -> Any:
        """Get LibPackage from either AppPackage (.libPackage) or RefPackage (.real_package)."""
        return getattr(pkg, "real_package", None) or getattr(pkg, "libPackage", None)

    @staticmethod
    def createDumpJson(packages: list[Any], env: Any) -> None:
        path = os.path.join(env.appDataPath, "dump.json")
        result: list[dict[str, Any]] = []
        for p in packages:
            lp = MakeUtils._get_lp(p)
            if lp:
                result.append({
                    "name": lp.name, "publisher": lp.publisher,
                    "version": lp.version, "path": lp.path,
                    "summary": lp.summary, "isGlobal": lp.isGlobal,
                })
        with open(path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=4)

    @staticmethod
    def createIncludeFile(packType: str, packages: list[Any], env: Any) -> None:
        if packType == "qmake":
            gen = MakeUtils._qmake_gen
            out_path = os.path.join(env.appPath, ".package.pri")
        elif packType == "cmake":
            gen = MakeUtils._cmake_gen
            out_path = os.path.join(env.appPath, ".package.cmake")
        else:
            raise ValueError(f"Unknown packType: {packType}")

        content = gen.post_process(packages, env)

        if os.path.exists(out_path):
            with open(out_path, "rt", encoding="utf-8") as f:
                if f.read() == content:
                    exit(0)

        with open(out_path, "wt", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def checkPackageDependencies(libs: list[Any]) -> None:
        for lib in libs:
            lp = MakeUtils._get_lp(lib)
            if not lp:
                continue
            for dep in lp.getDependency():
                if not any(dep.matchLib(MakeUtils._get_lp(l2)) for l2 in libs):
                    print(f"Package {lp.name} requires {dep.lib_name.fullName()} version {dep.version} "
                          f"but it is not found in the list of packages.")
                    exit(1)
