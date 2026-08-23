from __future__ import annotations

import os
from typing import Any
from scripts.data.GlobalData import GlobalData
from scripts.Utils import Utils
from scripts.provider.LibProviderManager import LibProviderManager


class EnvConfig:
    def __init__(self, appPath: str, makeType: str) -> None:
        self.appPath = appPath
        self.makeType = makeType

        self.appDataPath = os.path.normpath(os.path.join(self.appPath, ".data"))
        self.appLibStore: str = os.path.normpath(os.path.join(self.appPath, ".lib"))
        self.sysPath = os.getenv("IMAKECORE_ROOT", "").strip()
        self.sysCachePath = os.path.normpath(os.path.join(self.sysPath, ".cache"))

        self._global = GlobalData()
        self.global_data = self._global
        self.sysLibStore: str = self._global.get_sys_lib_store()
        self.userName: str = self._global.get_user_name()

        self.appConfig, self.appLibStore = self._loadAppConfig()
        self.servers: list[str] = self._collectServers()
        self.libstores: list[str] = self._collectLibStores()
        self.checkDirectoryExists()
        LibProviderManager.init(self.appLibStore)

    def _loadAppConfig(self) -> tuple[dict[str, Any], str]:
        """Load the project's .data/config.json.

        Returns (config, resolved appLibStore).  When the project has no
        config.json the default appLibStore (project/.lib) is used.
        """
        appConfigJson = os.path.join(self.appDataPath, "config.json")
        if not os.path.exists(appConfigJson):
            return {}, self.appLibStore

        config = Utils.loadJson(appConfigJson)
        lib_store = config.get("localLibStore", self.appLibStore)
        if os.path.isabs(lib_store):
            app_lib_store = os.path.normpath(lib_store)
        else:
            app_lib_store = os.path.normpath(os.path.join(self.appPath, lib_store))
        return config, app_lib_store

    def _collectServers(self) -> list[str]:
        servers = list(self._global.get_servers())
        servers.extend(self.appConfig.get("servers", []))
        return servers

    def _collectLibStores(self) -> list[str]:
        stores = list(self._global.get_libstores())
        stores.append(self.appLibStore)
        for libStore in self.appConfig.get("libstores", []):
            if os.path.isabs(libStore):
                stores.append(os.path.normpath(libStore))
            else:
                stores.append(os.path.normpath(os.path.join(self.appPath, libStore)))
        return stores

    def checkDirectoryExists(self) -> None:
        if not os.path.exists(self.appLibStore):
            os.makedirs(self.appLibStore, exist_ok=True)
        if not os.path.exists(self.sysLibStore):
            os.makedirs(self.sysLibStore, exist_ok=True)
        if not os.path.exists(self.appDataPath):
            os.makedirs(self.appDataPath, exist_ok=True)
        if not os.path.exists(self._global.sys_data_path):
            os.makedirs(self._global.sys_data_path, exist_ok=True)
        if not os.path.exists(self.sysCachePath):
            os.makedirs(self.sysCachePath, exist_ok=True)
        if not os.path.exists(os.path.join(self.appPath, ".support")):
            os.makedirs(os.path.join(self.appPath, ".support"), exist_ok=True)
        if not os.path.exists(os.path.join(self.appPath, ".bin")):
            os.makedirs(os.path.join(self.appPath, ".bin"), exist_ok=True)

        self.libstores = [ls for ls in self.libstores if os.path.exists(ls)]

    def getProviderManager(self) -> LibProviderManager:
        return LibProviderManager.instance()
