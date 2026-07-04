import os
import sys
from packaging.version import *
from packaging.specifiers import *
from scripts.data.LibPackage import LibPackage
from scripts.data.GlobalData import GlobalData
from scripts.Utils import Utils

class EnvConfig:
    def __init__(self, appPath:str, makeType:str):
        self.appPath = appPath
        self.makeType = makeType

        self.appConfig = {}
        self.appDataPath = os.path.normpath(os.path.join(self.appPath, ".data"))
        self.appLibStore :str = os.path.normpath(os.path.join(self.appPath, ".lib"))
        self.sysPath = os.getenv("IMAKECORE_ROOT")
        self.sysCachePath = os.path.normpath(os.path.join(self.sysPath, ".cache"))
        self.userName : str = "local"

        self.servers = []
        self.libstores = []
        self.libs : dict[str, list[LibPackage]] = {}

        self._global = GlobalData()
        self.sysLibStore = self._global.get_sys_lib_store()
        self.servers = self._global.get_servers()
        self.libstores = self._global.get_libstores()
        self.userName = self._global.get_user_name()

        self.loadAppConfig()
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

    def checkDirectoryExists(self):
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

        libStores = [ls for ls in self.libstores if os.path.exists(ls)]
        self.libstores = libStores

    def parseLibs(self):
        """Query package metadata from the SQLite database (populated by updateDb.py).
        
        No filesystem scanning — all package data is read from package.db.
        """
        from scripts.data.models import LibPackageTable
        from scripts.data.models import get_session

        try:
            session = get_session()
        except Exception as e:
            print(f"\n  ERROR: Failed to connect to package database: {e}")
            print("  Please run 'python -B .system/scripts/updateDb.py' first to initialize the database.\n")
            sys.exit(1)

        try:
            try:
                rows = session.query(LibPackageTable).all()
            except Exception as e:
                print(f"\n  ERROR: Database table not found: {e}")
                print("  Please run 'python -B .system/scripts/updateDb.py' to create the database tables.\n")
                sys.exit(1)

            for row in rows:
                lib = LibPackage.from_db_row(row)
                if lib.publisher == "":
                    lib.publisher = self.userName
                name = lib.publisher + "/" + lib.name
                if name not in self.libs:
                    self.libs[name] = []
                self.libs[name].append(lib)
        finally:
            session.close()

        for name in self.libs:
            self.libs[name].sort(key=lambda x: Version(x.version), reverse=True)
