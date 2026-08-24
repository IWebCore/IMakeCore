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
    def getGenerator(pack_type: str) -> Any:
        """Return the package generator registered for ``pack_type``."""
        entry = MakeUtils._GENERATORS.get(pack_type)
        if entry is None:
            raise ValueError(f"Unknown packType: {pack_type}")
        return entry[0]

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

        # xmake: also emit a machine-readable JSON for the on_load (script-domain) hook.
        if pack_type == "xmake":
            import json
            json_path = os.path.join(env.appPath, ".package.xmake.json")
            json_content = json.dumps(gen.post_process_json(packages, env), indent=2)
            with open(json_path, "w", encoding="utf-8") as f:
                f.write(json_content)

        if os.path.exists(out_path):
            with open(out_path, "r", encoding="utf-8") as f:
                if f.read() == content:
                    exit(0)

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(content)
