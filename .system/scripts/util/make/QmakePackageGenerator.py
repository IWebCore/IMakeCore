from __future__ import annotations

import os
from typing import Any

from scripts.util.make.MakePackageGenerator import MakePackageGenerator


class QmakePackageGenerator(MakePackageGenerator):
    """qmake (.pri / .pro) package generator."""

    _comment = "#"
    _lib_suffix = "pri"
    condition_file_name = "imakecore_condition.pri"

    _CHAIN_HEADER = """\
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################

# inclue packages.json to project
OTHER_FILES += packages.json 

"""

    _CHAIN_ENTRY = "\n# {publisher}@{name}@{version}\n# {summary}\ninclude({path})\n"

    _SUPPORT_LIB_TEMPLATE = """\
# {publisher}@{name}@{version} — DO NOT EDIT
TEMPLATE = lib
CONFIG += {lib_config}
TARGET = {target}
{defines}
include($$(IQMakeCore))
IQMakeCoreInit()
include($$PWD/.package.pri)

DESTDIR = $$PWD/$${{QMAKE_HOST.arch}}-pc-$${{QMAKE_HOST.os}}-$${{QMAKE_SPEC}}-{mode}
{post_link}"""

    _POST_LINK_TEMPLATE = """
CONFIG(dll) {
    win32:  QMAKE_POST_LINK += $$quote(cmd /c copy /y $$shell_path($$DESTDIR/$${TARGET}.dll) $$shell_path($$PWD/../../.bin/))
    linux:  QMAKE_POST_LINK += cp -f $$shell_path($$DESTDIR/lib$${TARGET}.so*) $$shell_path($$PWD/../../.bin/)
    macx:   QMAKE_POST_LINK += cp -f $$shell_path($$DESTDIR/lib$${TARGET}.dylib) $$shell_path($$PWD/../../.bin/)
}
"""

    _SUPPORT_PROJECT_TEMPLATE = """\
# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# {project_name} support subdirs project

include({condition})

TEMPLATE = subdirs
CONFIG += ordered

{subdirs}
"""

    # ── virtual interface ───────────────────────────────────────────────────

    def generate(self, pkg: Any, env: Any) -> str:
        lp = self._get_lp(pkg)
        if lp is None:
            return ""
        output_path = self._per_package_path(lp, env)

        detail = self._get_detail_from_db(lp.publisher, lp.name, lp.version)
        if detail is None:
            print(f"  [WARN] No detail record for {lp.publisher}/{lp.name}@{lp.version}. Run updateDb.py first.")
            return ""

        paths = self._get_file_paths(detail)
        if paths is None:
            return ""

        mode = getattr(pkg, "mode", "default")
        lib_path = self._normalize_path(lp.path)

        sections = [
            self._header_comment(lp),
            f'current_lib_path = "{lib_path}"\n\n',
            self._includes_section(paths["includes"]),
            self._definitions_section(paths["definitions"]),
            self._continuation_section("HEADERS", paths["headers"], "    $$current_lib_path/{item}"),
        ]

        if mode in ("static", "dynamic"):
            if mode == "dynamic" and paths.get("dynamic_definition"):
                sections.append(self._definitions_section(paths["dynamic_definition"]))
            sections.append(self._lib_link_section(pkg))
        else:
            sections.append(self._continuation_section("SOURCES", paths["sources"], "    $$current_lib_path/{item}"))
            sections.append(self._continuation_section("FORMS", paths["uis"], "    $$current_lib_path/{item}"))
            sections.append(self._continuation_section("RESOURCES", paths["resources"], "    $$current_lib_path/{item}"))

        sections.append(self._single_section("PRECOMPILED_HEADER", paths["precompile_headers"], "$$current_lib_path/{item}"))

        return self._write_if_changed(output_path, "".join(sections))

    def post_process(self, packages: list[Any], env: Any) -> str:
        parts = [self._CHAIN_HEADER]
        for p in packages:
            path = self.generate(p, env)
            if not path:
                continue
            lp = self._get_lp(p)
            parts.append(self._CHAIN_ENTRY.format(
                publisher=lp.publisher, name=lp.name, version=lp.version,
                summary=lp.summary, path=os.path.normpath(path).replace(os.sep, "/"),
            ))
        return "".join(parts)

    def support_lib_filename(self, dir_name: str) -> str:
        return f"{dir_name}.pro"

    def support_lib_content(self, lp: Any, mode: str, pkg_dir: str) -> str:
        target = f"{lp.publisher}@{lp.name}@{lp.version}"
        defines = ""
        post_link = ""
        if mode == "dynamic":
            detail = self._get_support_detail(lp)
            if detail:
                defines = "".join(f"DEFINES += {d}\n" for d in detail.get_dynamic_definition())
            post_link = self._POST_LINK_TEMPLATE
        return self._SUPPORT_LIB_TEMPLATE.format(
            publisher=lp.publisher, name=lp.name, version=lp.version,
            lib_config="staticlib" if mode == "static" else "dll",
            target=target, defines=defines, mode=mode, post_link=post_link,
        )

    def support_project_filename(self, project_name: str) -> str:
        return f"{project_name}_Support.pro"

    def support_project_content(self, project_name: str, lib_packages: list[Any]) -> str:
        subdirs = "".join(
            f"SUBDIRS += {os.path.join(d, f'{d}.pro')}\n"
            for d in self._support_dir_names(lib_packages)
        )
        return self._SUPPORT_PROJECT_TEMPLATE.format(
            project_name=project_name, condition=self.condition_file_name, subdirs=subdirs,
        )

    # ── per-package section builders ────────────────────────────────────────

    @staticmethod
    def _includes_section(includes: list[str]) -> str:
        if not includes:
            return ""
        entries = []
        for i, inc in enumerate(includes):
            suffix = " \\" if i < len(includes) - 1 else ""
            path = "$$current_lib_path" if inc == "." else f"$$current_lib_path/{inc}"
            entries.append(f"    {path}{suffix}")
        return "INCLUDEPATH += \\\n" + "\n".join(entries) + "\n\n"

    @staticmethod
    def _definitions_section(definitions: list[str]) -> str:
        if not definitions:
            return ""
        return "".join(f"DEFINES += {d}\n" for d in definitions) + "\n"

    @staticmethod
    def _continuation_section(keyword: str, items: list[str], template: str) -> str:
        if not items:
            return ""
        entries = []
        for i, item in enumerate(items):
            suffix = " \\" if i < len(items) - 1 else ""
            entries.append(f"{template.format(item=item)}{suffix}")
        return f"{keyword} += \\\n" + "\n".join(entries) + "\n\n"

    @staticmethod
    def _single_section(keyword: str, items: list[str], template: str) -> str:
        if not items:
            return ""
        return "".join(f"{keyword} = {template.format(item=item)}\n" for item in items) + "\n"

    @classmethod
    def _lib_link_section(cls, pkg: Any) -> str:
        lp = cls._get_lp(pkg)
        if lp is None:
            return ""
        mode = getattr(pkg, "mode", "static")
        pkg_dir = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
        target = f"{lp.publisher}@{lp.name}@{lp.version}"
        arch_path = f"$$PWD/../.support/{pkg_dir}/$${{QMAKE_HOST.arch}}-pc-$${{QMAKE_HOST.os}}-$${{QMAKE_SPEC}}-{mode}"
        if mode == "dynamic":
            lines = (
                f"win32-msvc*: LIBS += {arch_path}/{target}.lib\n"
                f"win32-g++:  LIBS += {arch_path}/lib{target}.a\n"
                f"macx: LIBS += {arch_path}/lib{target}.dylib\n"
                f"linux: LIBS += {arch_path}/lib{target}.so\n"
            )
        else:
            lines = (
                f"win32-msvc*: LIBS += {arch_path}/{target}.lib\n"
                f"else:        LIBS += {arch_path}/lib{target}.a\n"
            )
        return lines + "\n"
