import sys
from scripts.data import *
from scripts.LocatePackage import *
from scripts.DownloadPackage import *
from scripts.MakeUtils import *

def loadPackages(app : AppConfig, env:EnvConfig):
    for package in app.packages:
        if not (LocatePackages(package, env).success \
            or DownloadPackage(package, env).success):
            print(f"Failed to locate or download package: {package.group}/{package.name}")
            exit(1)

if __name__ == '__main__':
    appPath = sys.argv[1]
    packType = sys.argv[2]

    env = EnvConfig(appPath, packType)
    app = AppConfig(appPath)
    loadPackages(app, env)
    MakeUtils.checkPackageDependencies(app.packages)
    content = MakeUtils.createIncludeFile(packType, app.packages)

    jsonPath = os.path.join(appPath, "packages.json")
    cachedPath = os.path.join(appPath, ".cache", "packages.json")
    
    if os.path.exists(jsonPath) and os.path.exists(cachedPath):
        with open(cachedPath, "rt") as oldFile:
            if oldFile.read() == content:
                exit(0)

    with open(jsonPath, "rt") as newFile:
        newFile.write(content)

    shutil.copy(jsonPath, cachedPath)
    exit(0)
