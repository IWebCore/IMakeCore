
import os
from packaging.version import *
from packaging.specifiers import *
from scripts.data.AppPackage import AppPackage
from scripts.Utils import Utils

class LibPackage:
    class Dependency:
        def __init__(self, name:str, version:str):
            self.version = version
            self.versionSpec = Utils.parseVersionSpecifier(version)

            value = name.split("/")
            if len(value) == 2:
                self.group = value[0]
                self.name = value[1]
            else:
                self.group = "IWebCore"
                self.name = value[0]
        def matchLib(self, libPackage):
            return self.group == libPackage.group \
                and self.name == libPackage.name \
                and self.versionSpec.contains(Version(libPackage.version))
    
    def __init__(self, path:str):
        self.name = ""
        self.group = ""
        self.version = ""
        self.summary = ""
        self.path = path
        self.dependencies: List[LibPackage.Dependency] = []
        self.success = True

        try:
            self.loadPackage()
        except:
            self.success = False

    def __str__(self):
        return f"{self.group}@{self.name}@{self.version}"
    
    def loadPackage(self):
        path= os.path.join(self.path, "package.json")
        if not os.path.exists(path):
            self.success = False
            return
        
        self.json = Utils.loadJson(path)
        self.name = self.json.get("name")
        self.group = self.json.get("group")
        self.version = self.json.get("version")
        self.summary = self.json.get("summary")
        self.description = self.json.get("description")

        dependencies = self.json.get("dependencies", {})
        for key, value in dependencies.items():
            dep = LibPackage.Dependency(key, value)
            self.dependencies.append(dep)
    
    def checkPackage(self):
        pass
        
    def isMatch(self, appPackage:AppPackage):
        return self.group == appPackage.group \
            and self.name == appPackage.name    \
            and appPackage.versionSpec.contains(self.version)
