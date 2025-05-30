import os
from packaging.version import *
from packaging.specifiers import *
from scripts.data.AppPackage import AppPackage
from scripts.data.LibPackage import LibPackage
from scripts.Utils import Utils

class EnvConfig:
    def __init__(self, appPath:str, makeType:str):
        self.appPath = appPath
        self.sysPath = os.getenv("IMAKECORE_ROOT")
        self.makeType = makeType

        self.appCachePath = os.path.normpath(os.path.join(self.appPath, ".cache"))
        self.sysCachePath = os.path.normpath(os.path.join(self.sysPath, ".cache"))
        self.appLibPath = os.path.normpath(os.path.join(self.appPath, ".lib"))
        self.sysLibPath = os.path.normpath(os.path.join(self.sysPath, ".lib"))
        self.appDataPath = os.path.normpath(os.path.join(self.appPath, ".data"))
        self.sysDataPath = os.path.normpath(os.path.join(self.sysPath, ".data"))

        self.servers = []
        self.libstore = []
        self.libs = []
    
        self.checkDirectoryExists()
        self.loadServerConfig()
        self.loadLibStoreConfig()
        self.parseLibs()

    def checkDirectoryExists(self):
        if not os.path.exists(self.appDataPath):
            os.makedirs(self.appDataPath, exist_ok=True)

        if not os.path.exists(self.sysDataPath):
            os.makedirs(self.sysDataPath, exist_ok=True)

        if not os.path.exists(self.appLibPath):
            os.makedirs(self.appLibPath, exist_ok=True)
        
        if not os.path.exists(self.sysLibPath):
            os.makedirs(self.sysLibPath, exist_ok=True)

        if not os.path.exists(self.appCachePath):
            os.makedirs(self.appCachePath, exist_ok=True)

        if not os.path.exists(self.sysCachePath):
            os.makedirs(self.sysCachePath, exist_ok=True)

    def loadServerConfig(self):

        appConfig = os.path.join(self.appPath, ".data", ".SERVER")
        if os.path.exists(appConfig):
            with open(appConfig, "rt") as f:
                for line in f:
                    if line.strip():
                        self.servers.append(line.strip())

        sysConfig = os.path.join(self.sysPath, ".data", ".SERVER")
        if os.path.exists(sysConfig):
            with open(sysConfig, "rt") as f:
                for line in f:
                    if line.strip():
                        self.servers.append(line.strip())
        
    def loadLibStoreConfig(self):
        
        self.libstore.append(os.path.join(self.appPath, ".lib"))

        packageFile = os.path.join(self.appPath, "package.json")
        if os.path.exists(packageFile):
            with open(packageFile, "rt") as f:
                packageInfo = Utils.loadJson(f)
                if "libstore" in packageInfo:
                    for libstore in packageInfo["libstore"]:
                        self.libstore.append(os.path.normpath(os.path.join(libstore)))

        appConfig = os.path.join(self.appPath, ".data", ".LIBSTORE")
        if os.path.exists(appConfig):
            with open(appConfig, "rt") as f:
                for line in f:
                    if line.strip():
                        self.libstore.append(line.strip())

        sysConfig = os.path.join(self.sysPath, ".data", ".LIBSTORE")
        if os.path.exists(sysConfig):
            with open(sysConfig, "rt") as f:
                for line in f:
                    if line.strip():
                        self.libstore.append(line.strip())

        self.libstore.append(os.path.normpath(self.sysPath))
    
    def parseLibs(self):
        for libstore in self.libstore:
            if not os.path.exists(libstore):
                continue
            dirs = [d for d in os.listdir(libstore) if os.path.isdir(os.path.join(libstore, d))]
            for dir in dirs:
                path = os.path.join(libstore, dir)
                projectDirs = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
                for projectDir in projectDirs:
                    lib = LibPackage(os.path.join(path, projectDir))
                    if lib.success:
                        self.libs.append(lib)
