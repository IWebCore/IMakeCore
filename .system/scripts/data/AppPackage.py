import os
from packaging.version import *
from packaging.specifiers import *
from scripts.Utils import Utils

class AppPackage:
    def __init__(self,  name:str, version:str, group:str, path:str, url:str, scope:str):
        self.name = name.strip()
        self.version = version.strip()
        self.group = group.strip()
        self.name = name.strip()
        self.group = group.strip()
        self.path = path.strip()
        self.url = url
        self.scope = scope
        self.autoScan = False
        self.libPackage = None  # LibPackage object
        self.versionSpec = Utils.parseVersionSpecifier(self.version)
        
        self.checkArgument()

    @classmethod
    def fromJson(cls, package_info):
        name = package_info.get('name')
        version = package_info.get('version', '1.0.0')  # default version to 1.0.0
        group = package_info.get('group', "IWebCore")
        path = package_info.get('path', '')
        url = package_info.get('url')
        scope = package_info.get('scope', 'any')  # default scope to global
        return AppPackage(name, version, group, path, url, scope)

    @classmethod
    def fromString(cls, value:str):
        name :str
        version:str
        group:str
        parts = value.split('@')
        if len(parts) != 2:
            version = ""
        
        groupName = parts[0].split('/')
        if len(groupName) != 2:
            group = "IWebCore"
            name = groupName[0]
        else:
            group = groupName[0]
            name = groupName[1]

        return AppPackage(name, version, group, "", "", "any")
            
    def checkArgument(self):
        if len(self.name) == 0:
            print("Package name cannot be empty")
            exit(1)
        
        if len(self.group) == 0:
            print("Package group cannot be empty")
            exit(1)

        if self.scope not in ["any", "global", "local"]:
            print("Package scope must be any, global or local")
            exit(1)
    
    def __str__(self):
        return f"Package(name={self.name}, version={self.version}, group={self.group}, path={self.path})"
