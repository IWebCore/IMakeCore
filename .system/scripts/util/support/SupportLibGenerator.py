import os
import json


class SupportLibGenerator:
    def __init__(self, lib_packages, pack_type, env):
        self.lib_packages = lib_packages
        self.pack_type = pack_type
        self.env = env
        self.support_dir = os.path.normpath(os.path.join(env.appPath, ".support"))

    def generate_all(self):
        os.makedirs(self.support_dir, exist_ok=True)
        for p in self.lib_packages:
            self.generate_one(p)

    def generate_one(self, p):
        lp = getattr(p, "real_package", None)
        if lp is None:
            return
        mode = getattr(p, "mode", "static")
        dir_name = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
        pkg_dir = os.path.join(self.support_dir, dir_name)
        os.makedirs(pkg_dir, exist_ok=True)

        self._write_packages_json(pkg_dir, lp)
        self._write_project_file(pkg_dir, lp, dir_name, mode, p)

    def _write_packages_json(self, pkg_dir, lp):
        data = {"packages": {f"{lp.publisher}/{lp.name}": "*"}}
        path = os.path.join(pkg_dir, "packages.json")
        with open(path, "wt", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _write_project_file(self, pkg_dir, lp, dir_name, mode, p):
        if self.pack_type == "qmake":
            content = self._qmake_pro(lp, mode)
            fname = f"{dir_name}.pro"
        else:
            content = self._cmake_cmakelists(lp, mode, p, pkg_dir)
            fname = "CMakeLists.txt"
        path = os.path.join(pkg_dir, fname)
        with open(path, "wt", encoding="utf-8") as f:
            f.write(content)

    @staticmethod
    def _qmake_pro(lp, mode):
        return f"""# {lp.publisher}@{lp.name}@{lp.version} — DO NOT EDIT
TEMPLATE = lib
CONFIG += {'staticlib' if mode == 'static' else 'dll'}
TARGET = {lp.publisher}@{lp.name}@{lp.version}

include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)

DESTDIR = $$PWD/$${{QMAKE_HOST.arch}}-pc-$${{QMAKE_HOST.os}}-$${{QMAKE_SPEC}}-{mode}
"""

    def _cmake_cmakelists(self, lp, mode, p, pkg_dir):
        safe_name = lp.name.replace(".", "_")
        safe_ver = lp.version.replace(".", "_")
        full_target = f"{lp.publisher}@{safe_name}@{safe_ver}"
        safe_target = full_target.replace("@", "_")
        lib_type = "STATIC" if mode == "static" else "SHARED"

        lines = []
        lines.append(f"# {lp.publisher}@{lp.name}@{lp.version} — DO NOT EDIT")
        lines.append("cmake_minimum_required(VERSION 3.16)")
        lines.append(f"project({safe_target} LANGUAGES CXX)")
        lines.append("")
        lines.append(f"add_library({safe_target} {lib_type})")
        lines.append(f"set_target_properties({safe_target} PROPERTIES LINKER_LANGUAGE CXX)")
        lines.append(f"set_target_properties({safe_target} PROPERTIES")
        lines.append(f'    ARCHIVE_OUTPUT_DIRECTORY "${{CMAKE_CURRENT_SOURCE_DIR}}/${{CMAKE_SYSTEM_PROCESSOR}}-${{CMAKE_SYSTEM_NAME}}-{mode}"')
        lines.append(")")
        lines.append("")
        lines.append('set(IMAKECORE_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}")')
        lines.append("include($ENV{ICMakeCore})")
        lines.append(f"ICmakeCoreInit({safe_target})")

        return "\n".join(lines) + "\n"
