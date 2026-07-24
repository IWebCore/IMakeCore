from __future__ import annotations

import sys, os

# Ensure vendored libraries in .system/ take precedence over system-installed copies.
_sys_dir = os.path.dirname(os.path.abspath(__file__))
if _sys_dir not in sys.path:
    sys.path.insert(0, _sys_dir)

from scripts.data import *
from scripts.data.AppData import AppData
from scripts.util.PackageResolver import PackageResolver
from scripts.MakeUtils import *
from scripts.util.support.SupportProjectFileGenerator import SupportProjectFileGenerator
from scripts.util.support.SupportLibGenerator import SupportLibGenerator

if __name__ == '__main__':
    appPath = sys.argv[1]
    packType = sys.argv[2]

    env = EnvConfig(appPath, packType)
    app_data = AppData(appPath, env)

    resolver = PackageResolver(app_data, env)
    resolver.resolve_all()

    all_pkgs = app_data.packages

    for ref in all_pkgs:
        user_mode = getattr(ref, "mode", "default")
        lp = getattr(ref, "real_package", None)
        if lp is not None and lp.is_header_only():
            if user_mode in ("static", "dynamic"):
                print(f"ERROR: Package '{lp.name}' is header-only (no sources/ui/resources)."
                      f" Cannot use mode='{user_mode}'. Use mode='source' or omit the mode field.")
                exit(1)
            if user_mode == "default":
                ref.mode = "source"

    for ref in all_pkgs:
        if getattr(ref, "mode", "default") != "dynamic":
            continue
        lp = getattr(ref, "real_package", None)
        if lp is None:
            continue
        detail = lp.getDetail()
        if detail is None or len(detail.get_dynamic_definition()) == 0:
            print(f"ERROR: Package '{lp.name}' has mode='dynamic' but no dynamicDefinition"
                  f" is defined in its package.json resolve section.")
            exit(1)

    MakeUtils.checkPackageDependencies(all_pkgs)
    MakeUtils.createDumpJson(all_pkgs, env)

    lib_pkgs = [r for r in all_pkgs if getattr(r, "mode", "default") in ("static", "dynamic")]
    if lib_pkgs:
        SupportLibGenerator(lib_pkgs, packType, env).generate_all()

    project_name = os.path.basename(os.path.abspath(appPath))
    SupportProjectFileGenerator(project_name, lib_pkgs, packType, env).generate()

    MakeUtils.createIncludeFile(packType, all_pkgs, env)
    app_data.save_cache()
