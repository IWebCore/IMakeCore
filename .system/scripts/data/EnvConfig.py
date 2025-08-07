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
        self.appLibStore :str = os.path.normpath(os.path.join(self.appPath, ".lib"))
        
        self.sysPath = os.getenv("IMAKECORE_ROOT")
        self.sysConfig = {}
        self.sysCachePath = os.path.normpath(os.path.join(self.sysPath, ".cache"))
        self.sysDataPath = os.path.normpath(os.path.join(self.sysPath, ".data"))
        self.sysLibStore = os.path.normpath(os.path.join(self.sysPath, ".lib"))
        
        self.userName : str = "local"

        self.servers = []
        self.libstores = []
        self.libs : list[LibPackage] = {}  # key :values

        self.loadAppConfig()
        self.loadSystemConfig()
        self.checkDirectoryExists()
    
        self.parseLibs()
        
    def loadAppConfig(self):
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

    def loadSystemConfig(self):
        sysConfigJson = os.path.join(self.sysDataPath, "config.json")
        if os.path.exists(sysConfigJson):
            self.sysConfig = Utils.loadJson(sysConfigJson)
            self.sysLibStore = self.sysConfig.get("globalLibStore", self.sysLibStore)
            if os.path.isabs(self.sysLibStore):
                self.sysLibStore = os.path.normpath(self.sysLibStore)
            else:
                self.sysLibStore = os.path.normpath(os.path.join(self.sysPath, self.sysLibStore))
            
            libStores = self.sysConfig.get("libstores", [])
            for libStore in libStores:
                if os.path.isabs(libStore):
                    libStore = os.path.normpath(libStore)
                else:
                    libStore = os.path.normpath(os.path.join(self.sysPath, libStore))
                self.libstores.append(libStore)
            
            self.userName = self.sysConfig.get("user", "local")
            
            self.libstores.append(self.sysLibStore)
            self.servers.extend(self.sysConfig.get("servers", []))
        else: 
            assert False, "System config file not found"

    def checkDirectoryExists(self):
        
        if not os.path.exists(self.appLibStore):
            os.makedirs(self.appLibStore, exist_ok=True)
        
        if not os.path.exists(self.sysLibStore):
            os.makedirs(self.sysLibStore, exist_ok=True)
        
        if not os.path.exists(self.appDataPath):
            os.makedirs(self.appDataPath, exist_ok=True)

        if not os.path.exists(self.sysDataPath):
            os.makedirs(self.sysDataPath, exist_ok=True)
        
        if not os.path.exists(self.sysCachePath):
            os.makedirs(self.sysCachePath, exist_ok=True)

        libStores : list[str] = []
        for libstore in self.libstores:
            if os.path.exists(libstore):
                libStores.append(libstore)
        self.libstores = libStores

    def parseLibs(self):
        for libstore in self.libstores:
            dirs = [d for d in os.listdir(libstore) if os.path.isdir(os.path.join(libstore, d))]
            for dir in dirs:
                path = os.path.join(libstore, dir)
                lib = LibPackage(path)
                if lib.success:
                    if lib.publisher == "":
                        lib.publisher = self.userName
                    name = lib.publisher + "/" + lib.name
                    if name not in self.libs:
                        self.libs[name] = []
                    self.libs[name].append(lib)
        
        for name in self.libs:
            self.libs[name].sort(key=lambda x: Version(x.version), reverse=True)
