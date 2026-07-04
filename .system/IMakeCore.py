import sys, os
from scripts.data import *
from scripts.data.AppData import AppData
from scripts.data.models import LibPackageDetailTable, get_session
from scripts.util.PackageResolver import PackageResolver
from scripts.MakeUtils import *
from scripts.util.support.SupportProjectFileGenerator import SupportProjectFileGenerator
from scripts.util.support.SupportLibGenerator import SupportLibGenerator

def _is_header_only(ref):
    """Check if a resolved package has zero compilable sources (header-only)."""
    lp = getattr(ref, "real_package", None)
    if lp is None:
        return False
    session = get_session()
    try:
        detail = session.query(LibPackageDetailTable).filter_by(
            group=lp.publisher, name=lp.name, version=lp.version
        ).first()
        if detail is None:
            return False
        return (len(detail.get_sources()) == 0
                and len(detail.get_uis()) == 0
                and len(detail.get_resources()) == 0)
    except Exception:
        return False
    finally:
        session.close()

if __name__ == '__main__':
    appPath = sys.argv[1]
    packType = sys.argv[2]

    env = EnvConfig(appPath, packType)
    app_data = AppData(appPath)

    resolver = PackageResolver(app_data, env)
    resolver.resolve_all()

    all_pkgs = app_data.all_packages()

    for ref in all_pkgs:
        user_mode = getattr(ref, "mode", "default")
        if _is_header_only(ref):
            if user_mode in ("static", "dynamic"):
                lp = getattr(ref, "real_package", None)
                name = getattr(lp, "name", ref.name) if lp else ref.name
                print(f"ERROR: Package '{name}' is header-only (no sources/ui/resources)."
                      f" Cannot use mode='{user_mode}'. Use mode='source' or omit the mode field.")
                exit(1)
            if user_mode == "default":
                ref.mode = "source"

    MakeUtils.checkPackageDependencies(all_pkgs)
    MakeUtils.createDumpJson(all_pkgs, env)

    lib_pkgs = [r for r in all_pkgs if getattr(r, "mode", "default") in ("static", "dynamic")]
    if lib_pkgs:
        SupportLibGenerator(lib_pkgs, packType, env).generate_all()

    project_name = os.path.basename(os.path.abspath(appPath))
    SupportProjectFileGenerator(project_name, lib_pkgs, packType, env).generate()

    MakeUtils.createIncludeFile(packType, all_pkgs, env)
    app_data.save_cache()
