
import os
from packaging.version import *
from packaging.specifiers import *
from scripts.data.AppPackage import AppPackage
from scripts.Utils import Utils

class LibPackage:
    class Dependency:
        def __init__(self, name:str, version:str):
            self.fullName = name
            self.version = version
            self.versionSpec = Utils.parseVersionSpecifier(version)
            
        def matchLib(self, libPackage):
            if "/" in self.fullName:
                return self.fullName == (libPackage.publisher + "/" + libPackage.name)  \
                        and self.versionSpec.contains(Version(libPackage.version))
            
            return self.fullName == libPackage.name     \
                    and self.versionSpec.contains(Version(libPackage.version))  \
                    and libPackage.isGlobal
                    
    def __init__(self):
        self.name : str = ""
        self.publisher : str = ""
        self.isGlobal : bool = False
        self.version : str = ""
        self.summary : str = ""
        self.autoScan : bool = False
        self.path : str = ""
        self.dependencies : List[LibPackage.Dependency] = []
        self.success : bool = True    

    def __init__(self, path:str):
        self.name : str = ""
        self.publisher : str = ""
        self.isGlobal : bool = False
        self.version : str = ""
        self.summary : str = ""
        self.autoScan : bool = False
        self.path : str = path
        self.dependencies : List[LibPackage.Dependency] = []
        self.success : bool = True

        try:
            self.loadPackage()
        except:
            self.success = False

        if self.success:
            self.checkPackage()

    def __str__(self):
        return f"{self.fullName}@{self.version}"
    
    def loadPackage(self):
        path= os.path.join(self.path, "package.json")
        if not os.path.exists(path):
            self.success = False
            return
        
        self.json = Utils.loadJson(path)
        
        self.publisher = self.json.get("publisher", "")
        self.name = self.json.get("name")
        self.isGlobal = self.json.get("isGlobal", True)
        
        self.version = self.json.get("version")
        self.summary = self.json.get("summary")
        self.autoScan = self.json.get("autoScan", False)
        self.autoScan = self.json.get("autoScan", False)
        dependencies = self.json.get("dependencies", {})
        for key, value in dependencies.items():
            dep = LibPackage.Dependency(key, value)
            self.dependencies.append(dep)
    
    def checkPackage(self):
        if not self.isGlobal and self.publisher == "":
            self.success = False
            assert False, f"Invalid package.json, package {self.name} is not global and publisher is missing. Path:{self.path}"
            
        assert self.name and self.version, f"Invalid package.json, package name or version is missing. Path:{self.path}"

    def isMatch(self, appPackage:AppPackage):
        if "/" in appPackage.name:
            return self.publisher == appPackage.name.split("/")[0]  \
                    and self.name == appPackage.name.split("/")[1]  \
                    and appPackage.versionSpec.contains(self.version)
         
        return self.isGlobal and self.name == appPackage.name and appPackage.versionSpec.contains(self.version)