
import os
from packaging.version import *
from packaging.specifiers import *
from scripts.data.AppPackage import AppPackage
from scripts.Utils import Utils

class LibPackage:
    class Dependency:
        def __init__(self, name:str, version:str):
            self.name = name
            self.version = version
            self.versionSpec = Utils.parseVersionSpecifier(version)
            
        def matchLib(self, libPackage):
            return self.name == libPackage.name and self.versionSpec.contains(Version(libPackage.version))
    
    def __init__(self, path:str):
        self.name = ""
        self.version = ""
        self.summary = ""
        self.autoScan = False
        self.path = path
        self.dependencies: List[LibPackage.Dependency] = []
        self.success = True

        try:
            self.loadPackage()
        except:
            self.success = False

        if self.success:
            self.checkPackage()

    def __str__(self):
        return f"{self.name}@{self.version}"
    
    def loadPackage(self):
        path= os.path.join(self.path, "package.json")
        if not os.path.exists(path):
            self.success = False
            return
        
        self.json = Utils.loadJson(path)
        self.name = self.json.get("name")
        self.version = self.json.get("version")
        self.summary = self.json.get("summary")
        self.autoScan = self.json.get("autoScan", False)
        dependencies = self.json.get("dependencies", {})
        for key, value in dependencies.items():
            dep = LibPackage.Dependency(key, value)
            self.dependencies.append(dep)
    
    def checkPackage(self):
        assert self.name and self.version, f"Invalid package.json, package name or version is missing. Path:{self.path}"

    def isMatch(self, appPackage:AppPackage):
        return self.name == appPackage.name and appPackage.versionSpec.contains(self.version)
