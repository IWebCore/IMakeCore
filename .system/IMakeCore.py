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
    MakeUtils.createIncludeFile(packType, app.packages, env)
