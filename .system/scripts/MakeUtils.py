import os
import shutil
from typing import List
from scripts.data import *

class MakeUtils:

    @staticmethod
    def createIncludeFile(packType:str, package:list[AppPackage]):
        if packType == "qmake":
            return MakeUtils.qmakePostProcess(package)
        elif packType == "cmake":
            return MakeUtils.cmakePostProcess(package)

    @staticmethod
    def checkPackageDependencies(libs:list[AppPackage]):
        for lib in libs:
            dep : LibPackage.Dependency
            for dep in lib.libPackage.dependencies:
                cond = False
                for lib2 in libs:
                    if dep.matchLib(lib2.libPackage):
                        cond = True
                        break
                if not cond:
                    print(f"Package {lib.group}/{lib.name} requires {dep.group}/{dep.name} version {dep.version} but it is not found in the list of packages.")
                    exit(1)

    @staticmethod
    def cmakePostProcess(package:list[AppPackage]) -> str:

        str = """\
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################\n"""

        for p in package:
            path = os.path.join(p.libPackage.path, p.name+".cmake")
            path = os.path.normpath(path)
            print(path)
            path = path.replace("\\", "/")
            str += f"\n# {p.libPackage.group}/{p.libPackage.name}@{p.libPackage.version}\n"
            str += f"# {p.libPackage.summary}\n"
            str += "include(" + path +")\n"

        return str
    
    @staticmethod
    def qmakePostProcess(package:list[AppPackage]) -> str:
        str = """\
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################

# inclue packages.json to project
OTHER_FILES += packages.json 
 
"""
        for p in package:
            path = os.path.join(p.libPackage.path, p.name+".pri")
            str += f"\n# {p.libPackage.group}/{p.libPackage.name}@{p.libPackage.version}\n"
            str += f"# {p.libPackage.summary}\n"
            str += "include(" + path +")\n"

        return str
