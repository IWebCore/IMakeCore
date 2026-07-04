import sys
from scripts.data import *
from scripts.data.AppData import AppData
from scripts.util.PackageResolver import PackageResolver
from scripts.MakeUtils import *

if __name__ == '__main__':
    appPath = sys.argv[1]
    packType = sys.argv[2]

    env = EnvConfig(appPath, packType)
    app_data = AppData(appPath)

    resolver = PackageResolver(app_data, env)
    resolver.resolve_all()

    all_pkgs = app_data.all_packages()

    MakeUtils.checkPackageDependencies(all_pkgs)
    MakeUtils.createDumpJson(all_pkgs, env)
    MakeUtils.createIncludeFile(packType, all_pkgs, env)

    app_data.save_cache()
