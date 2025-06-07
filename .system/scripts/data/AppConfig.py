import os
import shutil
from scripts.Utils import Utils
from scripts.data.AppPackage import AppPackage

class AppConfig:
    def __init__(self, path : str):
        self.path = path
        self.success = False
        self.packages = []

        jsonPath = os.path.join(self.path, "packages.json")
        if not os.path.exists(jsonPath):
            srcPath = os.path.join(os.getenv("IMAKECORE_ROOT"), ".data", "packages.json")
            shutil.copyfile(srcPath, jsonPath)
        
        self.json = Utils.loadJson(jsonPath)
        self.loadPackages()

        
    def loadPackages(self):
        if 'packages' in self.json:
            packages = self.json['packages']
            for key, value in packages.items():
                if isinstance(value, str):
                    self.packages.append(AppPackage.fromNameVersion(key, value))
                elif isinstance(value, dict):
                    self.packages.append(AppPackage.fromNameConfig(key, value))
                else:
                    print("Invalid package info: ", value)
                    exit(1)

        else:
            print("packages.json does not contain a 'packages' field. please check the format.")
            exit(1)
