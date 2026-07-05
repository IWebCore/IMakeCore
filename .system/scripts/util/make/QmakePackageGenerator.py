from __future__ import annotations

import os
from typing import Any
from scripts.util.make.MakePackageGenerator import MakePackageGenerator


class QmakePackageGenerator(MakePackageGenerator):

    @staticmethod
    def _get_lp(pkg: Any) -> Any:
        return getattr(pkg, "real_package", None) or getattr(pkg, "libPackage", None)

    def generate(self, pkg: Any, env: Any) -> str:
        lp = self._get_lp(pkg)
        if lp is None:
            return ""
        output_path = self._lib_output_path(lp, env, "pri")

        detail = self._get_detail_from_db(lp.publisher, lp.name, lp.version)
        if detail is None:
            print(f"  [WARN] No detail record for {lp.publisher}/{lp.name}@{lp.version}. Run updateDb.py first.")
            return ""

        paths = self._get_file_paths(detail)
        if paths is None:
            return ""

        mode = getattr(pkg, "mode", "default")
        lib_path = self._normalize_path(lp.path)
        lines = self._header_comment(lp)
        lines.append(f'current_lib_path = "{lib_path}"')
        lines.append("")

        self._emit_includes(lines, paths["includes"])
        self._emit_definitions(lines, paths["definitions"])
        self._emit_continuation(lines, "HEADERS", paths["headers"], '    $$current_lib_path/{item}')

        if mode in ("static", "dynamic"):
            if mode == "dynamic" and paths.get("dynamic_definition"):
                for d in paths["dynamic_definition"]:
                    lines.append(f"DEFINES += {d}")
            self._emit_lib_link(lines, pkg, env)
        else:
            self._emit_continuation(lines, "SOURCES", paths["sources"], '    $$current_lib_path/{item}')
            self._emit_continuation(lines, "FORMS", paths["uis"], '    $$current_lib_path/{item}')
            self._emit_continuation(lines, "RESOURCES", paths["resources"], '    $$current_lib_path/{item}')

        self._emit_single(lines, paths["precompile_headers"], "PRECOMPILED_HEADER", '$$current_lib_path/{item}')

        content = "\n".join(lines) + "\n"
        return self._write_if_changed(output_path, content)

    @staticmethod
    def _emit_lib_link(lines: list[str], pkg: Any, env: Any) -> None:
        lp = QmakePackageGenerator._get_lp(pkg)
        if lp is None:
            return
        mode = getattr(pkg, "mode", "static")
        pkg_dir = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
        target = f"{lp.publisher}@{lp.name}@{lp.version}"
        arch_path = f"$$PWD/../.support/{pkg_dir}/$${{QMAKE_HOST.arch}}-pc-$${{QMAKE_HOST.os}}-$${{QMAKE_SPEC}}-{mode}"

        if mode == "dynamic":
            lines.append(f'win32-msvc*: LIBS += {arch_path}/{target}.lib')
            lines.append(f'win32-g++:  LIBS += {arch_path}/lib{target}.a')
            lines.append(f'macx: LIBS += {arch_path}/lib{target}.dylib')
            lines.append(f'linux: LIBS += {arch_path}/lib{target}.so')
        else:
            lines.append(f'win32-msvc*: LIBS += {arch_path}/{target}.lib')
            lines.append(f'else:        LIBS += {arch_path}/lib{target}.a')
        lines.append("")

    @staticmethod
    def _emit_includes(lines: list[str], includes: list[str]) -> None:
        if not includes:
            return
        lines.append("INCLUDEPATH += \\")
        for i, inc in enumerate(includes):
            suffix = " \\" if i < len(includes) - 1 else ""
            path = "$$current_lib_path" if inc == "." else f"$$current_lib_path/{inc}"
            lines.append(f"    {path}{suffix}")
        lines.append("")

    @staticmethod
    def _emit_definitions(lines: list[str], definitions: list[str]) -> None:
        if not definitions:
            return
        for d in definitions:
            lines.append(f"DEFINES += {d}")
        lines.append("")

    @staticmethod
    def _emit_continuation(lines: list[str], keyword: str, items: list[str], template: str) -> None:
        if not items:
            return
        lines.append(f"{keyword} += \\")
        for i, item in enumerate(items):
            suffix = " \\" if i < len(items) - 1 else ""
            lines.append(f"{template.format(item=item)}{suffix}")
        lines.append("")

    @staticmethod
    def _emit_single(lines: list[str], items: list[str], keyword: str, template: str) -> None:
        if not items:
            return
        for item in items:
            lines.append(f"{keyword} = {template.format(item=item)}")
        lines.append("")

    def post_process(self, packages: list[Any], env: Any) -> str:
        result = """\
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################

# inclue packages.json to project
OTHER_FILES += packages.json 

"""
        for p in packages:
            path = self.generate(p, env)
            if not path:
                continue
            path = os.path.normpath(path).replace(os.sep, "/")
            lp = self._get_lp(p)
            result += f"\n# {lp.publisher}@{lp.name}@{lp.version}\n"
            result += f"# {lp.summary}\n"
            result += "include(" + path + ")\n"

        return result
