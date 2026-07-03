"""
GlobalData.py — System-level config parser for IMAKECORE.
Provides libstore paths, server URLs, and user info from IMAKECORE_ROOT/.data/config.json.
Shared between updateDb.py and EnvConfig.py.
"""
import os
import sys
from scripts.Utils import Utils


class GlobalData:
    def __init__(self):
        self.imakecore_root = os.getenv("IMAKECORE_ROOT")
        if not self.imakecore_root:
            print("ERROR: IMAKECORE_ROOT environment variable is not set.")
            sys.exit(1)

        self.config = {}
        self.sys_data_path = os.path.join(self.imakecore_root, ".data")
        self.sys_lib_store = os.path.normpath(os.path.join(self.imakecore_root, ".lib"))
        self.servers = []
        self.libstores = []
        self.user_name = "local"

        self._load()

    def _load(self):
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

    def _resolve_store_path(self, path):
        if os.path.isabs(path):
            return os.path.normpath(path)
        return os.path.normpath(os.path.join(self.imakecore_root, path))

    def get_sys_lib_store(self):
        return self.sys_lib_store

    def get_libstores(self):
        return self.libstores

    def get_servers(self):
        return self.servers

    def get_user_name(self):
        return self.user_name
