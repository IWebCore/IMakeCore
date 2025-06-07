import os
from packaging.version import *
from packaging.specifiers import *
from scripts.Utils import Utils

class AppPackage:
    def __init__(self,  name:str, version:str, path:str="", url:str="", scope:str="any"):
        self.name = name.strip()
        self.version = version.strip()
        self.path = path.strip()
        self.url = url
        self.scope = scope
        self.libPackage = None  # LibPackage object
        self.versionSpec = Utils.parseVersionSpecifier(self.version)
        
        self.checkArgument()

    @classmethod
    def fromNameVersion(cls, name:str, version:str):
        return AppPackage(name, version)
    
    @classmethod
    def fromNameConfig(cls, name:str, config:dict):
        version = config.get('version', '*')
        path = config.get('path', '')
        url = config.get('url')
        scope = config.get('scope', 'any')
        return AppPackage(name, version, path, url, scope)
            
    def checkArgument(self):
        if len(self.name) == 0:
            print("Package name cannot be empty")
            exit(1)

        if self.scope not in ["any", "global", "local"]:
            print("Package scope must be any, global or local")
            exit(1)
    
    def __str__(self):
        return f"Package(name={self.name}, version={self.version}, path={self.path})"
