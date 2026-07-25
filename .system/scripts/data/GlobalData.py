"""
GlobalData.py — System-level config parser for IMAKECORE.
Provides libstore paths, server URLs, and user info from IMAKECORE_ROOT/.data/config.json.
Shared between updateDb.py and EnvConfig.py.
"""
from __future__ import annotations

import os
import sys
from typing import Any
from scripts.Utils import Utils


class GlobalData:
    def __init__(self) -> None:
        self.imakecore_root = os.getenv("IMAKECORE_ROOT", "").strip().strip()
        if not self.imakecore_root:
            print("ERROR: IMAKECORE_ROOT environment variable is not set.")
            sys.exit(1)

        self.config: dict[str, Any] = {}
        self.sys_data_path = os.path.join(self.imakecore_root, ".data")
        self.sys_lib_store = os.path.normpath(os.path.join(self.imakecore_root, ".lib"))
        self.servers: list[str] = []
        self.libstores: list[str] = []
        self.user_name: str = "local"

        self._load()

    def _load(self) -> None:
        config_path = os.path.join(self.sys_data_path, "config.json")
        if not os.path.exists(config_path):
            print(f"ERROR: System config not found at {config_path}")
            sys.exit(1)

        self.config = Utils.loadJson(config_path)

        self.sys_lib_store = self._resolve_store_path(
            self.config.get("globalLibStore", ".lib")
        )

        for ls in self.config.get("libstores", []):
            self.libstores.append(self._resolve_store_path(ls))

        self.libstores.append(self.sys_lib_store)
        self.libstores = [ls for ls in self.libstores if os.path.exists(ls)]

        self.servers = self.config.get("servers", [])
        self.user_name = self.config.get("user", "local")

    def _resolve_store_path(self, path: str) -> str:
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(self.imakecore_root, path))

    def get_sys_lib_store(self) -> str:
        return self.sys_lib_store

    def get_libstores(self) -> list[str]:
        return self.libstores

    def get_servers(self) -> list[str]:
        return self.servers

    def get_user_name(self) -> str:
        return self.user_name
