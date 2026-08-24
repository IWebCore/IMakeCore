from __future__ import annotations

import os
from typing import Any
from scripts.util.make.QmakePackageGenerator import QmakePackageGenerator
from scripts.util.make.CmakePackageGenerator import CmakePackageGenerator
from scripts.util.make.XmakePackageGenerator import XmakePackageGenerator


class MakeUtils:
    """Build-system include-chain generator."""

    _GENERATORS = {
        "qmake": (QmakePackageGenerator(), ".package.pri"),
        "cmake": (CmakePackageGenerator(), ".package.cmake"),
        "xmake": (XmakePackageGenerator(), ".package.lua"),
    }

    @staticmethod
    def createIncludeFile(pack_type: str, packages: list[Any], env: Any) -> None:
        """Generate ``.package.pri`` or ``.package.cmake`` include chain.

        Idempotent — if the generated content matches the file on disk,
        the process exits 0 without touching the file.  This avoids
        triggering unnecessary build-system reconfiguration.
        """
        entry = MakeUtils._GENERATORS.get(pack_type)
        if entry is None:
            raise ValueError(f"Unknown packType: {pack_type}")

        gen, filename = entry
        out_path = os.path.join(env.appPath, filename)
        content = gen.post_process(packages, env)

        if os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8") as f:
                if f.read() == content:
                    exit(0)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
