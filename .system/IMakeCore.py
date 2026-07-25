from __future__ import annotations

import sys, os
import subprocess
from typing import Any

# IMAKECORE_SYSTEM overrides the .system/ directory location (for testing).
# Falls back to the directory containing this file.
_sys_dir = os.getenv("IMAKECORE_SYSTEM") or os.path.dirname(os.path.abspath(__file__))
if _sys_dir not in sys.path:
    sys.path.insert(0, _sys_dir)

from scripts.data import *
from scripts.data.AppData import AppData
from scripts.util.PackageResolver import PackageResolver
from scripts.MakeUtils import *
from scripts.util.support.SupportProjectFileGenerator import SupportProjectFileGenerator
from scripts.util.support.SupportLibGenerator import SupportLibGenerator

def _validate_header_only_modes(packages: list) -> None:
    """Header-only packages must use mode='source' (or default), never static/dynamic."""
    for ref in packages:
        user_mode = getattr(ref, "mode", "default")
        lp = getattr(ref, "real_package", None)
        if lp is None or not lp.is_header_only():
            continue
        if user_mode in ("static", "dynamic"):
            print(f"ERROR: Package '{lp.name}' is header-only (no sources/ui/resources)."
                  f" Cannot use mode='{user_mode}'. Use mode='source' or omit the mode field.")
            exit(1)
        if user_mode == "default":
            ref.mode = "source"


def _validate_dynamic_definitions(packages: list) -> None:
    """Dynamic-mode packages must declare dynamicDefinition in their resolve config."""
    for ref in packages:
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


def _validate_dependencies(packages: list) -> None:
    """Every declared dependency must be present in the resolved package set."""
    resolved = []
    for ref in packages:
        lp = getattr(ref, "real_package", None)
        if lp is not None:
            resolved.append(lp)

    for ref in packages:
        lp = getattr(ref, "real_package", None)
        if lp is None:
            continue
        for dep in lp.getDependency():
            if any(dep.matchLib(other) for other in resolved):
                continue
            print(f"ERROR: Package '{lp.name}' requires"
                  f" {dep.lib_name.fullName()} {dep.version},"
                  f" but it is not in the resolved package list.")
            exit(1)


def _validate_static_dependencies(packages: list) -> None:
    """Static libraries cannot depend on non-header-only source libraries.

    Dependencies of a static library may be static, dynamic, or
    header-only.  A source-mode library that contains .cpp files is
    forbidden because it would pull object files into the static
    archive, breaking the build.
    """
    ref_by_name: dict[str, Any] = {}
    for ref in packages:
        lp = getattr(ref, "real_package", None)
        if lp is not None and not ref.skip:
            ref_by_name[ref.lib_name.fullName()] = ref

    for ref in packages:
        if getattr(ref, "mode", "default") != "static":
            continue
        lp = getattr(ref, "real_package", None)
        if lp is None:
            continue
        for dep in lp.getDependency():
            dep_ref = ref_by_name.get(dep.lib_name.fullName())
            if dep_ref is None:
                continue

            dep_mode = getattr(dep_ref, "mode", "default")
            if dep_mode not in ("source", "default"):
                continue

            dep_lp = getattr(dep_ref, "real_package", None)
            if dep_lp is None:
                continue
            if dep_lp.is_header_only():
                continue

            print(f"ERROR: Static package '{lp.name}' depends on"
                  f" '{dep_lp.name}' ({dep_mode} mode), which is a source"
                  f" library containing .cpp files.  Static libraries"
                  f" cannot depend on source libraries.  Use mode='static'"
                  f" or mode='dynamic' for '{dep_lp.name}', or make it"
                  f" header-only.")
            exit(1)


def _generate_outputs(packages: list, app_path: str, pack_type: str, env) -> None:
    """Produce all build artefacts: lib files, include chain."""
    lib_pkgs = [r for r in packages
                if getattr(r, "mode", "default") in ("static", "dynamic")]
    if lib_pkgs:
        SupportLibGenerator(lib_pkgs, pack_type, env).generate_all()

    project_name = os.path.basename(os.path.abspath(app_path))
    SupportProjectFileGenerator(project_name, lib_pkgs, pack_type, env).generate()

    MakeUtils.createIncludeFile(pack_type, packages, env)


def _ensure_db() -> None:
    """Create the package database if it does not exist or is empty."""
    root = os.getenv("IMAKECORE_ROOT", "").strip()
    db_path = os.path.join(root, ".db", "package.db") if root else ""
    lock_path = os.path.join(root, ".db", ".lock") if root else ""

    if db_path and os.path.exists(db_path) and os.path.getsize(db_path) > 0:
        return  # DB exists and has content

    update_py = os.path.join(_sys_dir, "updateDb.py")
    if not os.path.exists(update_py):
        return  # can't init — let resolution fail naturally

    # File lock to prevent concurrent updateDb.py runs (e.g. IDE loads 35 projects)
    try:
        fd = os.open(lock_path, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        os.close(fd)
    except FileExistsError:
        # Another process is already initializing — wait for it
        import time
        for _ in range(30):  # wait up to 30 seconds
            time.sleep(1)
            if os.path.exists(db_path) and os.path.getsize(db_path) > 0:
                return
        return  # timeout — let resolution try anyway

    try:
        print("Initializing package database...")
        result = subprocess.run(
            [sys.executable, "-B", update_py],
            env={**os.environ, "IMAKECORE_ROOT": root},
            capture_output=True, text=True,
        )
        if result.returncode != 0:
            print(f"ERROR: Failed to initialize database:\n{result.stderr}")
            exit(1)
    finally:
        if os.path.exists(lock_path):
            os.remove(lock_path)


# ── Entry point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    app_path = sys.argv[1]
    pack_type = sys.argv[2]

    _ensure_db()

    env = EnvConfig(app_path, pack_type)
    app_data = AppData(app_path, env)

    PackageResolver(app_data, env).resolve_all()
    all_pkgs = app_data.packages

    _validate_header_only_modes(all_pkgs)
    _validate_dynamic_definitions(all_pkgs)
    _validate_dependencies(all_pkgs)
    _validate_static_dependencies(all_pkgs)
    _generate_outputs(all_pkgs, app_path, pack_type, env)

    app_data.save_cache()
