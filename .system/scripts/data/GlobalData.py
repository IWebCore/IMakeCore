"""
GlobalData.py — System-level config parser for IMAKECORE.
Provides libstore paths, server URLs, and user info from IMAKECORE_ROOT/.data/config.json.
Shared between updateDb.py and EnvConfig.py.
"""
from __future__ import annotations

import json
import os
import sys
from typing import Any
from scripts.Utils import Utils


class GlobalData:
    def __init__(self) -> None:
        self.imakecore_root = os.getenv("IMAKECORE_ROOT", "").strip()
        if not self.imakecore_root:
            print("ERROR: IMAKECORE_ROOT environment variable is not set.")
            sys.exit(1)

        self.sys_data_path = os.path.join(self.imakecore_root, ".data")

        self.config: dict[str, Any] = self._loadConfig()
        self.sys_lib_store: str = self._parseSysLibStore()
        self.libstores: list[str] = self._parseLibStores()
        self.servers: list[str] = self._parseServers()
        self.user_name: str = self._parseUserName()

    def _loadConfig(self) -> dict[str, Any]:
        config_path = os.path.join(self.sys_data_path, "config.json")
        if not os.path.exists(config_path):
            os.makedirs(self.sys_data_path, exist_ok=True)
            default = {"globalLibStore": ".lib", "libstores": [], "servers": [], "user": "local"}
            with open(config_path, "w", encoding="utf-8") as f:
                json.dump(default, f, indent=2)
            return default
        return Utils.loadJson(config_path)

    def _parseSysLibStore(self) -> str:
        return self._resolve_store_path(
            self.config.get("globalLibStore", ".lib")
        )

    def _parseLibStores(self) -> list[str]:
        stores = [self._resolve_store_path(ls) for ls in self.config.get("libstores", [])]
        stores.append(self.sys_lib_store)
        return [ls for ls in stores if os.path.exists(ls)]

    def _parseServers(self) -> list[str]:
        return self.config.get("servers", [])

    def _parseUserName(self) -> str:
        return self.config.get("user", "local")

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
