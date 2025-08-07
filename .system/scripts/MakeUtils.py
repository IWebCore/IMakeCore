import json
import os
import shutil
from typing import List
from scripts.data import *
from pathlib import Path

class MakeUtils:

    @staticmethod
    def createDumpJson(packages:list[AppPackage], env : EnvConfig):
        
        path = os.path.join(env.appDataPath,"dump.json")
        with open(path, "w") as f:
            dict_list = [package.toDict() for package in packages]
            json.dump(dict_list, f, indent=4)  # indent 使格式美观

    @staticmethod
    def createIncludeFile(packType:str, package:list[AppPackage], env : EnvConfig):
        content : str
        path : str
        if packType == "qmake":
            content = MakeUtils.qmakePostProcess(package, env)
            path = os.path.join(env.appPath, ".package.pri")
        elif packType == "cmake":
            content = MakeUtils.cmakePostProcess(package, env)
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
                    print(f"Package {lib.name} requires {dep.fullName} version {dep.version} but it is not found in the list of packages.")
                    exit(1)

    @staticmethod
    def updatePackageForceLocal(packages:list[AppPackage], env : EnvConfig):
        env.appLibStore = os.path.normpath(env.appLibStore)
        for package in packages:
            if package.forceLocal:
                if env.appLibStore in os.path.normpath(package.path):
                    continue
                
                newPath = os.path.join(env.appLibStore, package.libPackage.publisher + "@" + package.libPackage.name + "@" + package.libPackage.version)
                oldPath = package.path
                package.path = newPath
                package.libPackage.path = newPath

                if os.path.exists(newPath):
                    continue
                print("copy package to local lib store", f"package {package.name}@{package.libPackage.version}")
                shutil.copytree(oldPath, newPath)

    staticmethod
    def createQMakeAutoScanPackage(pkg:AppPackage, env : EnvConfig) -> str:
        path = os.path.join(env.appLibStore, pkg.libPackage.publisher + "@" + pkg.libPackage.name+ "@" + pkg.libPackage.version +".pri")
        content = f"""\
# SYSTEM AUTO GENERATED DO NOT EDIT!!!
imakecore_current_lib_dir = "{os.path.normpath(pkg.libPackage.path).replace(os.sep, "/")}"
autoLoadPackage()
"""
        if os.path.exists(path):
            with open(path, "rt") as file:
                if file.read() == content:
                    return path

        with open(path, "wt") as file:
            file.write(content)

        return path
    
    @staticmethod
    def createCmakeAutoScanPackage(pkg:AppPackage, env : EnvConfig) -> str:
        path = os.path.join(env.appLibStore,  pkg.libPackage.publisher + "@" + pkg.libPackage.name + "@" + pkg.libPackage.version +".cmake")
        content = f"""\
# SYSTEM AUTO GENERATED DO NOT EDIT!!!
set(imakecore_current_lib_dir "{os.path.normpath(pkg.libPackage.path).replace(os.sep, "/")}")
autoLoadPackage()
"""
        if os.path.exists(path):
            with open(path, "rt") as file:  
                if file.read() == content:
                    return path

        with open(path, "wt") as file:
            file.write(content)

        return path
    
    @staticmethod
    def findQMakeIncludeFilePath(p:AppPackage):
        path = os.path.join(p.libPackage.path, f"{p.libPackage.publisher}@{p.libPackage.name}@{p.version}.pri")
        if os.path.exists(path):
            return path
        
        path = os.path.join(p.libPackage.path, f"{p.name}@{p.version}.pri")
        if os.path.exists(path):
            return path

        path = os.path.join(p.libPackage.path, p.name+".pri")
        if os.path.exists(path):
            return path
        
        path = os.path.join(p.libPackage.path, ".package.pri")
        if os.path.exists(path):
            return path
        
        print(f"Cannot find include file for package {p.name} in {p.libPackage.path}, please check the package files.")
        exit(1)

    @staticmethod
    def findCmakeIncludeFilePath(p:AppPackage):
        path = os.path.join(p.libPackage.path, f"{p.libPackage.publisher}@{p.libPackage.name}@{p.version}.cmake")
        if os.path.exists(path):
            return path
        
        path = os.path.join(p.libPackage.path, f"{p.name}@{p.version}.cmake")
        if os.path.exists(path):
            return 
        
        path = os.path.join(p.libPackage.path, f"{p.name}.cmake")
        if os.path.exists(path):
            return path
        
        path = os.path.join(p.libPackage.path, ".package.cmake")
        if os.path.exists(path):
            return path
        
        print(f"Cannot find include file for package {p.name}@{p.version} in {p.libPackage.path}, please check the package files.")
        exit(1)

    @staticmethod
    def cmakePostProcess(package:list[AppPackage], env: EnvConfig) -> str:

        str = """\
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################\n"""

        for p in package:
            path = ""
            if p.libPackage.autoScan == False:
                path = MakeUtils.findCmakeIncludeFilePath(p)
            else:
                path = MakeUtils.createCmakeAutoScanPackage(p, env)

            path = os.path.normpath(path).replace(os.sep, "/")
            str += f"\n# {p.libPackage.name}@{p.libPackage.version}\n"
            str += f"# {p.libPackage.summary}\n"
            str += "include(" + path +")\n"

        return str
    
    
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
                path = MakeUtils.findQMakeIncludeFilePath(p)
            else:
                path = MakeUtils.createQMakeAutoScanPackage(p, env)
            path = os.path.normpath(path).replace(os.sep, "/")
            str += f"\n# {p.libPackage.publisher}@{p.libPackage.name}@{p.libPackage.version}\n"
            str += f"# {p.libPackage.summary}\n"
            str += "include(" + path +")\n"

        return str
