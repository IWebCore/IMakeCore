from __future__ import annotations

import os
from typing import Any

from scripts.util.make.MakePackageGenerator import MakePackageGenerator


class XmakePackageGenerator(MakePackageGenerator):
    """xmake (.xmake / xmake.lua) package generator."""

    _comment = "--"
    _lib_suffix = "xmake"
    condition_file_name = "imakecore_condition.xmake"

    _CHAIN_HEADER = "-- SYSTEM CONFIGURED, DO NOT EDIT!!!\n"

    _CHAIN_ENTRY = '\n-- {publisher}@{name}@{version}\n-- {summary}\nincludes("{path}")\n'

    _SUPPORT_LIB_TEMPLATE = """\
-- {publisher}@{name}@{version} — DO NOT EDIT
local imake = os.getenv("IXMakeCore")
if imake then
    includes(imake)
end

target("{safe_name}")
    set_kind("{kind}")
    set_targetdir("{out_dir}/$(arch)-$(os)-{mode}")
    set_basename("{safe_name}")
{defines}    add_rules("imakecore")

"""

    _SUPPORT_PROJECT_TEMPLATE = """\
-- SYSTEM AUTO GENERATED DO NOT EDIT!!!
-- {project_name} support sub-projects

{includes}
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
            f'local current_lib_path = "{lib_path}"\n\n',
            self._include_dirs_section(paths["includes"]),
            self._definitions_section(paths["definitions"]),
            self._headerfiles_section(paths["headers"]),
        ]

        if mode in ("static", "dynamic"):
            if mode == "dynamic" and paths.get("dynamic_definition"):
                sections.append(self._definitions_section(paths["dynamic_definition"]))
            sections.append(self._lib_link_section(pkg))
        else:
            sections.append(self._sources_section(paths["headers"], paths["sources"]))
        sections.append(self._files_section(paths["uis"]))
        sections.append(self._files_section(paths["resources"]))
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

    def package_json(self, pkg: Any, env: Any) -> dict[str, Any] | None:
        """Machine-readable resolved config for xmake's on_load (script domain)."""
        lp = self._get_lp(pkg)
        if lp is None:
            return None
        detail = self._get_detail_from_db(lp.publisher, lp.name, lp.version)
        if detail is None:
            return None
        paths = self._get_file_paths(detail)
        if paths is None:
            return None

        mode = getattr(pkg, "mode", "default")
        lib_path = self._normalize_path(lp.path)

        def resolve(rel: str) -> str:
            return lib_path if rel == "." else f"{lib_path}/{self._normalize_path(rel)}"

        data: dict[str, Any] = {
            "publisher": lp.publisher,
            "name": lp.name,
            "version": lp.version,
            "mode": mode if mode in ("static", "dynamic") else "source",
            "includes": [resolve(inc) for inc in paths["includes"]],
            "definitions": list(paths["definitions"]),
            "headers": [resolve(h) for h in paths["headers"]],
            "sources": [],
            "precompile_headers": [resolve(ph) for ph in paths["precompile_headers"]],
            "links": [],
            "linkdir": "",
        }

        if mode in ("static", "dynamic"):
            if mode == "dynamic":
                data["definitions"] += list(paths.get("dynamic_definition") or [])
            safe_name = (lp.publisher.replace("@", "_") + "_"
                         + lp.name.replace(".", "_") + "_"
                         + lp.version.replace(".", "_"))
            data["links"] = [safe_name]
            data["linkdir"] = f".support/{lp.publisher}@{lp.name}@{lp.version}_{mode}"
        else:
            # source mode: only actual source files go to target:add("files")
            # (script-domain target:add does NOT auto-split headers like the
            # description-domain add_files does; headers are kept separate).
            data["sources"] = [resolve(f) for f in (paths["sources"] or [])]

        return data

    def post_process_json(self, packages: list[Any], env: Any) -> list[dict[str, Any]]:
        result: list[dict[str, Any]] = []
        for p in packages:
            data = self.package_json(p, env)
            if data is not None:
                result.append(data)
        return result

    def support_lib_filename(self, dir_name: str) -> str:
        return "xmake.lua"

    def support_lib_content(self, lp: Any, mode: str, pkg_dir: str) -> str:
        safe_name = lp.publisher.replace("@", "_") + "_" + lp.name.replace(".", "_") + "_" + lp.version.replace(".", "_")
        out_dir = self._normalize_path(pkg_dir)
        defines = ""
        if mode == "dynamic":
            detail = self._get_support_detail(lp)
            if detail:
                defines = "".join(f'    add_defines("{d}")\n' for d in detail.get_dynamic_definition())
        return self._SUPPORT_LIB_TEMPLATE.format(
            publisher=lp.publisher, name=lp.name, version=lp.version,
            safe_name=safe_name, kind="static" if mode == "static" else "shared",
            out_dir=out_dir, mode=mode, defines=defines,
        )

    def support_project_filename(self, project_name: str) -> str:
        return "xmake.lua"

    def support_project_content(self, project_name: str, lib_packages: list[Any]) -> str:
        includes = "".join(f'includes("{d}")\n' for d in self._support_dir_names(lib_packages))
        return self._SUPPORT_PROJECT_TEMPLATE.format(project_name=project_name, includes=includes)

    # ── per-package section builders ────────────────────────────────────────

    @staticmethod
    def _include_dirs_section(includes: list[str]) -> str:
        if not includes:
            return ""
        lines = []
        for inc in includes:
            norm = inc.replace("\\", "/")
            if norm == ".":
                lines.append("add_includedirs(current_lib_path)")
            else:
                lines.append(f'add_includedirs(current_lib_path .. "/{norm}")')
        return "\n".join(lines) + "\n\n"

    @staticmethod
    def _definitions_section(definitions: list[str]) -> str:
        if not definitions:
            return ""
        return "".join(f'add_defines("{d}")\n' for d in definitions) + "\n"

    @staticmethod
    def _headerfiles_section(headers: list[str]) -> str:
        if not headers:
            return ""
        return "".join(f'add_headerfiles(current_lib_path .. "/{h}")\n' for h in headers) + "\n"

    @staticmethod
    def _sources_section(headers: list[str], sources: list[str]) -> str:
        all_files = (headers or []) + (sources or [])
        if not all_files:
            return ""
        return "".join(f'add_files(current_lib_path .. "/{f}")\n' for f in all_files) + "\n"

    @staticmethod
    def _files_section(items: list[str]) -> str:
        if not items:
            return ""
        return "".join(f'add_files(current_lib_path .. "/{f}")\n' for f in items) + "\n"

    @staticmethod
    def _precompile_section(precompile_headers: list[str]) -> str:
        if not precompile_headers:
            return ""
        return "".join(f'set_pcxxheader(current_lib_path .. "/{ph}")\n' for ph in precompile_headers) + "\n"

    @classmethod
    def _lib_link_section(cls, pkg: Any) -> str:
        lp = cls._get_lp(pkg)
        if lp is None:
            return ""
        mode = getattr(pkg, "mode", "static")
        pkg_dir = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
        safe_name = lp.publisher.replace("@", "_") + "_" + lp.name.replace(".", "_") + "_" + lp.version.replace(".", "_")
        link_dir = f"$(scriptdir)/../.support/{pkg_dir}/$(arch)-$(os)-{mode}"

        parts = [f'add_linkdirs("{link_dir}")']
        if mode == "dynamic":
            parts += [
                'if is_plat("windows") then',
                f'    add_links("{safe_name}")',
                'elseif is_plat("macosx") then',
                f'    add_links("{safe_name}")',
                'else',
                f'    add_links("{safe_name}")',
                'end',
            ]
        else:
            parts += [
                'if is_plat("windows") then',
                f'    add_links("{safe_name}")',
                'else',
                f'    add_links("{safe_name}")',
                'end',
            ]
        return "\n".join(parts) + "\n\n"
