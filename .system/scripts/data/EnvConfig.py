import os
from packaging.version import *
from packaging.specifiers import *
from scripts.data.AppPackage import AppPackage
from scripts.data.LibPackage import LibPackage
from scripts.Utils import Utils

class EnvConfig:
    def __init__(self, appPath:str, makeType:str):
        self.makeType = makeType

        self.appPath = appPath
        self.appConfig = {}
        self.appDataPath = os.path.normpath(os.path.join(self.appPath, ".data"))
        self.appLibStore = os.path.normpath(os.path.join(self.appPath, ".lib"))

        self.sysPath = os.getenv("IMAKECORE_ROOT")
        self.sysConfig = {}
        self.sysCachePath = os.path.normpath(os.path.join(self.sysPath, ".cache"))
        self.sysDataPath = os.path.normpath(os.path.join(self.sysPath, ".data"))
        self.sysLibStore = os.path.normpath(os.path.join(self.sysPath, ".lib"))

        self.servers = []
        self.libstores = []
        self.libs : list[LibPackage] = {}  # key :values

        self.loadAppConfig()
        self.loadSystemConfig()
        self.normalizeLibStores()

        self.checkDirectoryExists()
    
        self.parseLibs()

    def checkDirectoryExists(self):
        if not os.path.exists(self.appDataPath):
            os.makedirs(self.appDataPath, exist_ok=True)

        if not os.path.exists(self.sysDataPath):
            os.makedirs(self.sysDataPath, exist_ok=True)

        if not os.path.exists(self.appLibStore):
            os.makedirs(self.appLibStore, exist_ok=True)
        
        if not os.path.exists(self.sysCachePath):
            os.makedirs(self.sysCachePath, exist_ok=True)

    def loadAppConfig(self):
        appConfigJson = os.path.join(self.appPath, ".data", "config.json")
        if os.path.exists(appConfigJson):
            self.appConfig = Utils.loadJson(appConfigJson)
            self.appLibStore = self.appConfig.get("localLibStore", self.appLibStore)
            self.libstores.append(self.appLibStore)
            self.libstores.extend(self.appConfig.get("libstores", []))
            self.servers.extend(self.appConfig.get("servers", []))
                

    def loadSystemConfig(self):
        sysConfigJson = os.path.join(self.sysPath, ".data", "config.json")
        if os.path.exists(sysConfigJson):
            self.sysConfig = Utils.loadJson(sysConfigJson)
            self.sysLibStore = self.sysConfig.get("globalLibStore", self.sysLibStore)
            self.libstores.extend(self.sysConfig.get("libstores", []))
            self.libstores.append(self.sysLibStore)
            self.servers.extend(self.sysConfig.get("servers", []))

    def normalizeLibStores(self):
        temp : list[str] = []
        for libstore in self.libstores:
            path = libstore.strip()
            if os.path.isabs(path):
                path = os.path.normpath(path)
            else:
                path = os.path.normpath(os.path.join(self.sysPath, ".data", path))

            if os.path.exists(path) and path not in temp:
                temp.append(path)

        self.libstores = temp

    def parseLibs(self):
        for libstore in self.libstores:
            dirs = [d for d in os.listdir(libstore) if os.path.isdir(os.path.join(libstore, d))]
            for dir in dirs:
                path = os.path.join(libstore, dir)
                lib = LibPackage(path)
                if lib.success:
                    if lib.name not in self.libs:
                        self.libs[lib.name] = []
                    self.libs[lib.name].append(lib)
        
        for name in self.libs:
            self.libs[name].sort(key=lambda x: Version(x.version), reverse=True)
