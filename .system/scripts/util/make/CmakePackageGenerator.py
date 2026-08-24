from __future__ import annotations

import os
from typing import Any

from scripts.util.make.MakePackageGenerator import MakePackageGenerator


class CmakePackageGenerator(MakePackageGenerator):
    """CMake (.cmake) package generator."""

    _comment = "#"
    _lib_suffix = "cmake"
    condition_file_name = "imakecore_condition.cmake"

    _CHAIN_HEADER = """\
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################
"""

    _CHAIN_ENTRY = "\n# {publisher}@{name}@{version}\n# {summary}\ninclude({path})\n"

    _SUPPORT_LIB_TEMPLATE = """\
# {publisher}@{name}@{version} — DO NOT EDIT
cmake_minimum_required(VERSION 3.16)
project({safe_target} LANGUAGES CXX)

add_library({safe_target} {lib_type})
set_target_properties({safe_target} PROPERTIES LINKER_LANGUAGE CXX)
set_target_properties({safe_target} PROPERTIES
    ARCHIVE_OUTPUT_DIRECTORY "{out_dir}"
{output_dirs})

{defines}set(IMAKECORE_ROOT_DIR "${{CMAKE_CURRENT_SOURCE_DIR}}")
include($ENV{{ICMakeCore}})
ICmakeCoreInit({safe_target})
{post_build}"""

    _SUPPORT_PROJECT_TEMPLATE = """\
# SYSTEM AUTO GENERATED DO NOT EDIT!!!
# {project_name} support subdirs project

cmake_minimum_required(VERSION 3.16)
project({project_name}_Support)

include({condition})

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
            f'set(current_lib_path "{lib_path}")\n\n',
            self._include_dirs_section(paths["includes"]),
            self._definitions_section(paths["definitions"]),
            self._target_sources_section(paths["headers"]),
        ]

        if mode in ("static", "dynamic"):
            if mode == "dynamic" and paths.get("dynamic_definition"):
                sections.append(self._definitions_section(paths["dynamic_definition"]))
            sections.append(self._lib_link_section(pkg))
        else:
            sections.append(self._target_sources_section((paths["headers"] or []) + (paths["sources"] or [])))
        sections.append(self._ui_section(paths["uis"]))
        sections.append(self._resources_section(paths["resources"]))
        sections.append(self._precompile_section(paths["precompile_headers"]))

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
        return "CMakeLists.txt"

    def support_lib_content(self, lp: Any, mode: str, pkg_dir: str) -> str:
        safe_name = lp.name.replace(".", "_")
        safe_ver = lp.version.replace(".", "_")
        safe_target = f"{lp.publisher}@{safe_name}@{safe_ver}".replace("@", "_")
        out_dir = f"${{CMAKE_CURRENT_SOURCE_DIR}}/${{CMAKE_SYSTEM_PROCESSOR}}-${{CMAKE_SYSTEM_NAME}}-{mode}"

        output_dirs = ""
        defines = ""
        post_build = ""
        if mode == "dynamic":
            output_dirs = (
                f'    LIBRARY_OUTPUT_DIRECTORY "{out_dir}"\n'
                f'    RUNTIME_OUTPUT_DIRECTORY "{out_dir}"\n'
            )
            detail = self._get_support_detail(lp)
            if detail:
                defines = "".join(
                    f"target_compile_definitions({safe_target} PRIVATE {d})\n"
                    for d in detail.get_dynamic_definition()
                )
            defines += "\n"
            post_build = (
                f"\nadd_custom_command(TARGET {safe_target} POST_BUILD\n"
                f'    COMMAND ${{CMAKE_COMMAND}} -E make_directory "${{CMAKE_CURRENT_SOURCE_DIR}}/../../.bin"\n'
                f'    COMMAND ${{CMAKE_COMMAND}} -E copy_if_different "$<TARGET_FILE:{safe_target}>" "${{CMAKE_CURRENT_SOURCE_DIR}}/../../.bin/"\n'
                ")\n"
            )

        return self._SUPPORT_LIB_TEMPLATE.format(
            publisher=lp.publisher, name=lp.name, version=lp.version,
            safe_target=safe_target, lib_type="STATIC" if mode == "static" else "SHARED",
            out_dir=out_dir, output_dirs=output_dirs, defines=defines, post_build=post_build,
        )

    def support_project_filename(self, project_name: str) -> str:
        return "CMakeLists.txt"

    def support_project_content(self, project_name: str, lib_packages: list[Any]) -> str:
        subdirs = "".join(f"add_subdirectory({d} {d}_build)\n" for d in self._support_dir_names(lib_packages))
        return self._SUPPORT_PROJECT_TEMPLATE.format(
            project_name=project_name, condition=self.condition_file_name, subdirs=subdirs,
        )

    # ── per-package section builders ────────────────────────────────────────

    @staticmethod
    def _target_sources_section(files: list[str]) -> str:
        if not files:
            return ""
        body = "".join(f'    "${{current_lib_path}}/{f}"\n' for f in files)
        return f"target_sources(${{IMAKECORE_TARGET}} PRIVATE\n{body})\n\n"

    @staticmethod
    def _include_dirs_section(includes: list[str]) -> str:
        if not includes:
            return ""
        entries = [
            f'    "${{current_lib_path}}"' if inc == "." else f'    "${{current_lib_path}}/{inc}"'
            for inc in includes
        ]
        return f"target_include_directories(${{IMAKECORE_TARGET}} PRIVATE\n" + "\n".join(entries) + "\n)\n\n"

    @staticmethod
    def _definitions_section(definitions: list[str]) -> str:
        if not definitions:
            return ""
        body = "".join(f"    {d}\n" for d in definitions)
        return f"target_compile_definitions(${{IMAKECORE_TARGET}} PRIVATE\n{body})\n\n"

    @staticmethod
    def _ui_section(uis: list[str]) -> str:
        if not uis:
            return ""
        body = "".join(f'qt_wrap_ui(${{IMAKECORE_TARGET}} "${{current_lib_path}}/{u}")\n' for u in uis)
        return f"set(CMAKE_AUTOUIC ON)\n{body}\n"

    @staticmethod
    def _resources_section(resources: list[str]) -> str:
        if not resources:
            return ""
        body = "".join(f'qt_add_resources(${{IMAKECORE_TARGET}} "${{current_lib_path}}/{r}")\n' for r in resources)
        return f"set(CMAKE_AUTORCC ON)\n{body}\n"

    @staticmethod
    def _precompile_section(precompile_headers: list[str]) -> str:
        if not precompile_headers:
            return ""
        body = "".join(f'    "${{current_lib_path}}/{ph}"\n' for ph in precompile_headers)
        return f"target_precompile_headers(${{IMAKECORE_TARGET}} PRIVATE\n{body})\n\n"

    @classmethod
    def _lib_link_section(cls, pkg: Any) -> str:
        lp = cls._get_lp(pkg)
        if lp is None:
            return ""
        mode = getattr(pkg, "mode", "static")
        pkg_dir = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
        safe_name = lp.publisher.replace("@", "_") + "_" + lp.name.replace(".", "_") + "_" + lp.version.replace(".", "_")
        lib_path = f"${{CMAKE_CURRENT_LIST_DIR}}/../.support/{pkg_dir}/${{CMAKE_SYSTEM_PROCESSOR}}-${{CMAKE_SYSTEM_NAME}}-{mode}"

        def link(name: str) -> str:
            return f'    target_link_libraries(${{IMAKECORE_TARGET}} PRIVATE "{lib_path}/{name}")'

        if mode == "dynamic":
            lines = (
                "if(MSVC)\n"
                f"{link(f'{safe_name}.lib')}\n"
                "elseif(MINGW)\n"
                f"{link(f'lib{safe_name}.a')}\n"
                "elseif(APPLE)\n"
                f"{link(f'lib{safe_name}.dylib')}\n"
                "else()\n"
                f"{link(f'lib{safe_name}.so')}\n"
                "endif()\n"
            )
        else:
            lines = (
                "if(MSVC)\n"
                f"{link(f'{safe_name}.lib')}\n"
                "else()\n"
                f"{link(f'lib{safe_name}.a')}\n"
                "endif()\n"
            )
        return lines + "\n"
