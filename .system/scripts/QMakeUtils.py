import os
import shutil
from typing import List
from scripts.data import *

class QMakeUtils:
    @staticmethod
    def qmakePostProcess(package:list[AppPackage], env:EnvConfig):
        packagePri = os.path.join(env.appPath, ".package.pri")
        cachePath = os.path.join(env.appCachePath, ".package.pri")

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

        if os.path.exists(cachePath) and os.path.exists(packagePri):
            with open(cachePath, 'rt') as f:
                if f.read() == str:
                    return
                
        with open(packagePri, "wt") as f:
            f.write(str)
            
        shutil.copy(packagePri, cachePath)
