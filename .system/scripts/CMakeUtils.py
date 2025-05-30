import os
import shutil
from typing import List
from scripts.data import *

class CMakeUtils:
    @staticmethod
    def cmakePostProcess(package:list[AppPackage], env:EnvConfig):
        packageCmake = os.path.join(env.appPath, ".package.cmake")
        print(packageCmake)
        cachePath = os.path.join(env.appCachePath, ".package.cmake")

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

        if os.path.exists(cachePath) and os.path.exists(packageCmake):
            with open(cachePath, 'rt') as f:
                if f.read() == str:
                    return
                
        with open(packageCmake, "wt") as f:
            f.write(str)
            
        shutil.copy(packageCmake, cachePath)
