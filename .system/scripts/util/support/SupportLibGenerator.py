from __future__ import annotations

import os
import json
from typing import Any
from scripts.data.LibPackageDetail import LibPackageDetail
from scripts.data.models import get_session


class SupportLibGenerator:
    def __init__(self, lib_packages: list[Any], pack_type: str, env: Any) -> None:
        self.lib_packages = lib_packages
        self.pack_type = pack_type
        self.env = env
        self.support_dir = os.path.normpath(os.path.join(env.appPath, ".support"))

    def _get_detail(self, lp: Any) -> LibPackageDetail | None:
        session = get_session()
        try:
            return session.query(LibPackageDetail).filter_by(
                publisher=lp.publisher, name=lp.name, version=lp.version
            ).first()
        finally:
            session.close()

    def generate_all(self) -> None:
        os.makedirs(self.support_dir, exist_ok=True)
        for p in self.lib_packages:
            self.generate_one(p)

    def generate_one(self, p: Any) -> None:
        lp = getattr(p, "real_package", None)
        if lp is None:
            return
        mode = getattr(p, "mode", "static")
        dir_name = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
        pkg_dir = os.path.join(self.support_dir, dir_name)
        os.makedirs(pkg_dir, exist_ok=True)

        self._write_packages_json(pkg_dir, lp)
        self._write_project_file(pkg_dir, lp, dir_name, mode, p)

    def _write_packages_json(self, pkg_dir: str, lp: Any) -> None:
        data = {"packages": {f"{lp.publisher}/{lp.name}": "*"}}
        path = os.path.join(pkg_dir, "packages.json")
        with open(path, "wt", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def _write_project_file(self, pkg_dir: str, lp: Any, dir_name: str, mode: str, p: Any) -> None:
        if self.pack_type == "qmake":
            content = self._qmake_pro(lp, mode)
            fname = f"{dir_name}.pro"
        elif self.pack_type == "cmake":
            content = self._cmake_cmakelists(lp, mode, p, pkg_dir)
            fname = "CMakeLists.txt"
        elif self.pack_type == "xmake":
            content = self._xmake_lua(lp, mode, p, pkg_dir)
            fname = "xmake.lua"
        else:
            raise ValueError(f"Unknown pack_type: {self.pack_type!r}")
        path = os.path.join(pkg_dir, fname)
        with open(path, "wt", encoding="utf-8") as f:
            f.write(content)

    def _qmake_pro(self, lp: Any, mode: str) -> str:
        target = f"{lp.publisher}@{lp.name}@{lp.version}"
        pro = f"""# {lp.publisher}@{lp.name}@{lp.version} — DO NOT EDIT
TEMPLATE = lib
CONFIG += {'staticlib' if mode == 'static' else 'dll'}
TARGET = {target}
"""
        if mode == "dynamic":
            detail = self._get_detail(lp)
            if detail:
                for d in detail.get_dynamic_definition():
                    pro += f"DEFINES += {d}\n"

        pro += f"""
include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)

DESTDIR = $$PWD/$${{QMAKE_HOST.arch}}-pc-$${{QMAKE_HOST.os}}-$${{QMAKE_SPEC}}-{mode}
"""
        if mode == "dynamic":
            pro += f"""
CONFIG(dll) {{
    win32:  QMAKE_POST_LINK += $$quote(cmd /c copy /y $$shell_path($$DESTDIR/$${{TARGET}}.dll) $$shell_path($$PWD/../../.bin/))
    linux:  QMAKE_POST_LINK += cp -f $$shell_path($$DESTDIR/lib$${{TARGET}}.so*) $$shell_path($$PWD/../../.bin/)
    macx:   QMAKE_POST_LINK += cp -f $$shell_path($$DESTDIR/lib$${{TARGET}}.dylib) $$shell_path($$PWD/../../.bin/)
}}
"""
        return pro

    def _cmake_cmakelists(self, lp: Any, mode: str, p: Any, pkg_dir: str) -> str:
        safe_name = lp.name.replace(".", "_")
        safe_ver = lp.version.replace(".", "_")
        full_target = f"{lp.publisher}@{safe_name}@{safe_ver}"
        safe_target = full_target.replace("@", "_")
        lib_type = "STATIC" if mode == "static" else "SHARED"

        lines: list[str] = []
        lines.append(f"# {lp.publisher}@{lp.name}@{lp.version} — DO NOT EDIT")
        lines.append("cmake_minimum_required(VERSION 3.16)")
        lines.append(f"project({safe_target} LANGUAGES CXX)")
        lines.append("")
        lines.append(f"add_library({safe_target} {lib_type})")
        lines.append(f"set_target_properties({safe_target} PROPERTIES LINKER_LANGUAGE CXX)")

        out_dir = f"${{CMAKE_CURRENT_SOURCE_DIR}}/${{CMAKE_SYSTEM_PROCESSOR}}-${{CMAKE_SYSTEM_NAME}}-{mode}"
        lines.append(f"set_target_properties({safe_target} PROPERTIES")
        lines.append(f"    ARCHIVE_OUTPUT_DIRECTORY \"{out_dir}\"")
        if mode == "dynamic":
            lines.append(f"    LIBRARY_OUTPUT_DIRECTORY \"{out_dir}\"")
            lines.append(f"    RUNTIME_OUTPUT_DIRECTORY \"{out_dir}\"")
        lines.append(")")
        lines.append("")

        if mode == "dynamic":
            detail = self._get_detail(lp)
            if detail:
                for d in detail.get_dynamic_definition():
                    lines.append(f"target_compile_definitions({safe_target} PRIVATE {d})")
            lines.append("")

        lines.append('set(IMAKECORE_ROOT_DIR "${CMAKE_CURRENT_SOURCE_DIR}")')
        lines.append("include($ENV{ICMakeCore})")
        lines.append(f"ICmakeCoreInit({safe_target})")

        if mode == "dynamic":
            lines.append("")
            lines.append(f"add_custom_command(TARGET {safe_target} POST_BUILD")
            lines.append(f'    COMMAND ${{CMAKE_COMMAND}} -E make_directory "${{CMAKE_CURRENT_SOURCE_DIR}}/../../.bin"')
            lines.append(f'    COMMAND ${{CMAKE_COMMAND}} -E copy_if_different "$<TARGET_FILE:{safe_target}>" "${{CMAKE_CURRENT_SOURCE_DIR}}/../../.bin/"')
            lines.append(")")

        return "\n".join(lines) + "\n"

    def _xmake_lua(self, lp: Any, mode: str, p: Any, pkg_dir: str) -> str:
        safe_name = lp.publisher.replace("@", "_") + "_" + lp.name.replace(".", "_") + "_" + lp.version.replace(".", "_")
        kind = "static" if mode == "static" else "shared"

        lines: list[str] = []
        lines.append(f"-- {lp.publisher}@{lp.name}@{lp.version} — DO NOT EDIT")
        lines.append('local imake = os.getenv("IXMakeCore")')
        lines.append("if imake then")
        lines.append("    includes(imake)")
        lines.append("end")
        lines.append("")
        lines.append(f'target("{safe_name}")')
        lines.append(f'    set_kind("{kind}")')
        lines.append(f'    set_targetdir("$(scriptdir)/$(arch)-$(os)-{mode}")')
        lines.append(f'    set_basename("{safe_name}")')

        if mode == "dynamic":
            detail = self._get_detail(lp)
            if detail:
                for d in detail.get_dynamic_definition():
                    lines.append(f'    add_defines("{d}")')

        lines.append('    add_rules("imakecore")')
        lines.append("")

        return "\n".join(lines) + "\n"
