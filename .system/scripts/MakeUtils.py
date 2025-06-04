import os
import shutil
from typing import List
from scripts.data import *

class MakeUtils:

    @staticmethod
    def createIncludeFile(packType:str, package:list[AppPackage], env : EnvConfig):
        content : str
        path : str
        if packType == "qmake":
            content = MakeUtils.qmakePostProcess(package, env)
            path = os.path.join(env.appPath, ".package.pri")
        elif packType == "cmake":
            content = MakeUtils.cmakePostProcess(package)
            path = os.path.join(env.appPath, ".package.cmake")

        if os.path.exists(path):
            with open(path, "rt") as oldFile:
                if oldFile.read() == content:
                    exit(0)
        
        with open(path, "wt") as newFile:
            newFile.write(content)


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
    
    staticmethod
    def createQMakeAutoScanPackage(pkg:AppPackage, env : EnvConfig) -> str:
        path = os.path.join(env.appLibPath, pkg.group+"@"+pkg.name+ "@" + pkg.version +".pri")
        content = f"""\
imakecore_current_lib_dir = "{os.path.normpath(pkg.libPackage.path).replace(os.sep, "/")}"
autoCachePackage()
"""
        if os.path.exists(path):
            with open(path, "rt") as file:
                if file.read() == content:
                    return path

        with open(path, "wt") as file:
            file.write(content)

        return path
        
    @staticmethod
    def qmakePostProcess(package:list[AppPackage], env : EnvConfig) -> str:
        str = """\
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################

# inclue packages.json to project
OTHER_FILES += packages.json 
 
"""
        for p in package:
            path = ""
            if p.libPackage.autoScan == False:
                path = os.path.join(p.libPackage.path, p.name+".pri")
            else:
                path = MakeUtils.createQMakeAutoScanPackage(p, env)
            str += f"\n# {p.libPackage.group}/{p.libPackage.name}@{p.libPackage.version}\n"
            str += f"# {p.libPackage.summary}\n"
            str += "include(" + path +")\n"

        return str
