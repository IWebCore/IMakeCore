import os
import shutil
from scripts.Utils import Utils
from scripts.data.AppPackage import AppPackage

class AppConfig:
    def __init__(self, path : str):
        self.path = path
        self.success = False
        self.packages : list[AppPackage] = []

        jsonPath = os.path.join(self.path, "packages.json")
        if not os.path.exists(jsonPath):
            srcPath = os.path.join(os.getenv("IMAKECORE_ROOT"), ".data", "packages.json")
            shutil.copyfile(srcPath, jsonPath)
        
        self.json = Utils.loadJson(jsonPath)
        self.localLibStore = self.json.get("localLibStore", os.path.join(self.path, ".lib"))
        self.forceLocal = self.json.get("forceLocal", False)

        self.loadPackages()

        
    def loadPackages(self):
        forceLocal = self.json.get("forceLocal", False)
        if 'packages' in self.json:
            packages = self.json['packages']
            for key, value in packages.items():
                if isinstance(value, str):
                    pkg = AppPackage.fromNameVersion(key, value, forceLocal)
                    if not pkg.skip:
                        self.packages.append(pkg)
                elif isinstance(value, dict):
                    pkg = AppPackage.fromNameConfig(key, value, forceLocal)
                    if not pkg.skip:
                        self.packages.append(pkg)
                else:
                    print("Invalid package info: ", key, value)
                    exit(1)

        else:
            print("packages.json does not contain a 'packages' field. please check the format.")
            exit(1)
