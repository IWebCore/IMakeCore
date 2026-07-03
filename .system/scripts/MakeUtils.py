import json
import os
import shutil
from scripts.data import *
from scripts.util.make.QmakePackageGenerator import QmakePackageGenerator
from scripts.util.make.CmakePackageGenerator import CmakePackageGenerator


class MakeUtils:

    _qmake_gen = QmakePackageGenerator()
    _cmake_gen = CmakePackageGenerator()

    @staticmethod
    def createDumpJson(packages, env):
        path = os.path.join(env.appDataPath, "dump.json")
        with open(path, "w") as f:
            json.dump([p.toDict() for p in packages], f, indent=4)

    @staticmethod
    def createIncludeFile(packType, packages, env):
        if packType == "qmake":
            gen = MakeUtils._qmake_gen
            out_path = os.path.join(env.appPath, ".package.pri")
        elif packType == "cmake":
            gen = MakeUtils._cmake_gen
            out_path = os.path.join(env.appPath, ".package.cmake")
        else:
            raise ValueError(f"Unknown packType: {packType}")

        content = gen.post_process(packages, env)

        if os.path.exists(out_path):
            with open(out_path, "rt") as f:
                if f.read() == content:
                    exit(0)

        with open(out_path, "wt") as f:
            f.write(content)

    @staticmethod
    def checkPackageDependencies(libs):
        for lib in libs:
            for dep in lib.libPackage.dependencies:
                if not any(dep.matchLib(l2.libPackage) for l2 in libs):
                    print(f"Package {lib.name} requires {dep.fullName} version {dep.version} "
                          f"but it is not found in the list of packages.")
                    exit(1)

    @staticmethod
    def updatePackageForceLocal(packages, env):
        env.appLibStore = os.path.normpath(env.appLibStore)
        for package in packages:
            if not package.forceLocal:
                continue
            if env.appLibStore in os.path.normpath(package.path):
                continue

            lp = package.libPackage
            new_path = os.path.join(env.appLibStore, f"{lp.publisher}@{lp.name}@{lp.version}")
            old_path = package.path
            package.path = new_path
            lp.path = new_path

            if os.path.exists(new_path):
                continue

            print(f"copy package to local lib store package {package.name}@{lp.version}")
            shutil.copytree(old_path, new_path)
