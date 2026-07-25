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

        self.appConfig: dict[str, Any] = {}
        self.appDataPath = os.path.normpath(os.path.join(self.appPath, ".data"))
        self.appLibStore: str = os.path.normpath(os.path.join(self.appPath, ".lib"))
        self.sysPath = os.getenv("IMAKECORE_ROOT", "").strip()
        self.sysCachePath = os.path.normpath(os.path.join(self.sysPath, ".cache"))
        self.userName: str = "local"

        self.servers: list[str] = []
        self.libstores: list[str] = []

        self._global = GlobalData()
        self.global_data = self._global
        self.sysLibStore = self._global.get_sys_lib_store()
        self.servers = self._global.get_servers()
        self.libstores = self._global.get_libstores()
        self.userName = self._global.get_user_name()

        self.loadAppConfig()
        self.checkDirectoryExists()
        self._provider_manager = LibProviderManager(self.appLibStore)

    def loadAppConfig(self) -> None:
        appConfigJson = os.path.join(self.appDataPath, "config.json")
        if os.path.exists(appConfigJson):
            self.appConfig = Utils.loadJson(appConfigJson)
            self.appLibStore = self.appConfig.get("localLibStore", self.appLibStore)
            if os.path.isabs(self.appLibStore):
                self.appLibStore = os.path.normpath(self.appLibStore)
            else:
                self.appLibStore = os.path.normpath(os.path.join(self.appPath, self.appLibStore))

            self.libstores.append(self.appLibStore)

            libStores = self.appConfig.get("libstores", [])
            for libStore in libStores:
                if os.path.isabs(libStore):
                    libStore = os.path.normpath(libStore)
                else:
                    libStore = os.path.normpath(os.path.join(self.appPath, libStore))
                self.libstores.append(libStore)

            self.servers.extend(self.appConfig.get("servers", []))
        else:
            self.libstores.append(self.appLibStore)

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

        libStores = [ls for ls in self.libstores if os.path.exists(ls)]
        self.libstores = libStores

    def getProviderManager(self) -> LibProviderManager:
        return self._provider_manager
