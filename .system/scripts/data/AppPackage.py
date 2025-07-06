import os
from packaging.version import *
from packaging.specifiers import *
# from scripts.data.LibPackage import LibPackage
from scripts.Utils import Utils

class AppPackage:
    def __init__(self,  name:str, version:str, path:str="", urls:list[str]="", forceLocal:bool = False):
        self.name = name.strip()
        self.version = version.strip()
        self.path = path.strip()
        self.urls = urls
        self.forceLocal = forceLocal
        self.skip = self.version == "x"
        self.versionSpec = Utils.parseVersionSpecifier(self.version)
        self.libPackage = None  # LibPackage object

        self.checkArgument()

    @classmethod
    def fromNameVersion(cls, name:str, version:str, forceLocal:bool):
        return AppPackage(name, version, forceLocal=forceLocal)
    
    @classmethod
    def fromNameConfig(cls, name:str, config:dict, forceLocal:bool):
        version = config.get('version', '*')    
        urls :list[str] = []
        if "url" in config:
            url = config['url']
            if isinstance(url, str):
                urls.append(url)
            elif isinstance(url, list):
                urls.extend(url)
            else:
                print(f"Invalid url type: {type(url)}")
                exit(1)

        path = config.get('path', "")
        forceLocal = config.get('forceLocal', forceLocal)
        return AppPackage(name, version, path=path, urls = urls,forceLocal=forceLocal)
            
    def checkArgument(self):
        if len(self.name) == 0:
            print("Package name cannot be empty")
            exit(1)

    def __str__(self):
        return f"Package(name={self.name}, version={self.version}, path={self.path})"

    def __dict__(self):
        return {
            "name": self.name,
            "version": self.libPackage.version,
            "path": self.libPackage.path,
            "autoScan" : self.libPackage.autoScan,
            "summary" : self.libPackage.summary,
            "forceLocal":self.forceLocal
        }