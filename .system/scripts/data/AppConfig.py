import os
import shutil
from scripts.Utils import Utils
from scripts.data.AppPackage import AppPackage

class AppConfig:
    def __init__(self, path : str):
        self.path = path
        self.success = False
        self.packages = []

        self.load()

    def load(self):
        jsonPath = os.path.join(self.path, "packages.json")
        if not os.path.exists(jsonPath):
            srcPath = os.path.join(os.getenv("IMAKECORE_ROOT"), ".data", "packages.json")
            shutil.copyfile(srcPath, jsonPath)
        

        self.json = Utils.loadJson(jsonPath)
        self.loadPackages()
        
        
    def loadPackages(self):
        if 'packages' in self.json:
            packages = self.json['packages']
            for item in packages:
                if isinstance(item, str):
                    self.packages.append(AppPackage.fromString(item))
                elif isinstance(item, dict):
                    self.packages.append(AppPackage.fromJson(item))
                else:
                    print("Invalid package info: ", item)
                    exit(1)

        else:
            print("packages.json does not contain a 'packages' field.")
            exit(1)
