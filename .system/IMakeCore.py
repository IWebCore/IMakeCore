import sys
from scripts.data import *
from scripts.LocatePackage import *
from scripts.DownloadPackage import *
from scripts.QMakeUtils import *
from scripts.CMakeUtils import *

def loadPackages(app : AppConfig, env:EnvConfig):
    for package in app.packages:
        if not (LocatePackages(package, env).success \
            or DownloadPackage(package, env).success):
            print(f"Failed to locate or download package: {package.group}/{package.name}")
            exit(1)

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

if __name__ == '__main__':
    appPath = sys.argv[1]
    packType = sys.argv[2]

    jsonPath = os.path.join(appPath, "packages.json")
    tempJsonPath = os.path.join(appPath, ".cache", "packages.json")
    if os.path.exists(jsonPath) and os.path.exists(tempJsonPath):
        with open(jsonPath, "rt") as f:
            with open(tempJsonPath, "rt") as f2:
                if f.read() == f2.read():
                    exit(0)

    env = EnvConfig(appPath, packType)
    app = AppConfig(appPath)

    loadPackages(app, env)
    checkPackageDependencies(app.packages)

    if packType == "qmake":
        QMakeUtils.qmakePostProcess(app.packages, env)
    elif packType == "cmake":
        CMakeUtils.cmakePostProcess(app.packages, env)
    
    shutil.copy(jsonPath, tempJsonPath)
    exit(0)
