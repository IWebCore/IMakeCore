from __future__ import annotations

import os
from typing import Any
from scripts.util.make.MakePackageGenerator import MakePackageGenerator


class XmakePackageGenerator(MakePackageGenerator):

    @staticmethod
    def _get_lp(pkg: Any) -> Any:
        return getattr(pkg, "real_package", None) or getattr(pkg, "libPackage", None)

    @staticmethod
    def _header_comment(lp: Any) -> list[str]:
        return [
            "-- SYSTEM AUTO GENERATED DO NOT EDIT!!!",
            f"-- {lp.publisher}@{lp.name}@{lp.version}",
            f"-- {lp.summary or ''}",
            "",
        ]

    def generate(self, pkg: Any, env: Any) -> str:
        lp = self._get_lp(pkg)
        if lp is None:
            return ""
        output_path = self._lib_output_path(lp, env, "xmake")

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
        lines.append(f'local current_lib_path = "{lib_path}"')
        lines.append("")

        self._emit_include_dirs(lines, paths["includes"])
        self._emit_definitions(lines, paths["definitions"])
        self._emit_headerfiles(lines, paths["headers"])

        if mode in ("static", "dynamic"):
            if mode == "dynamic" and paths.get("dynamic_definition"):
                for d in paths["dynamic_definition"]:
                    lines.append(f'add_defines("{d}")')
                lines.append("")
            self._emit_lib_link(lines, pkg, env)
        else:
            self._emit_sources(lines, paths["headers"], paths["sources"])
        self._emit_files(lines, paths["uis"])
        self._emit_files(lines, paths["resources"])
        self._emit_precompile(lines, paths["precompile_headers"])

        content = "\n".join(lines) + "\n"
        return self._write_if_changed(output_path, content)

    @staticmethod
    def _emit_lib_link(lines: list[str], pkg: Any, env: Any) -> None:
        lp = XmakePackageGenerator._get_lp(pkg)
        if lp is None:
            return
        mode = getattr(pkg, "mode", "static")
        pkg_dir = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
        safe_name = lp.publisher.replace("@", "_") + "_" + lp.name.replace(".", "_") + "_" + lp.version.replace(".", "_")
        link_dir = f"$(scriptdir)/../.support/{pkg_dir}/$(arch)-$(os)-{mode}"
        lines.append(f'add_linkdirs("{link_dir}")')
        if mode == "dynamic":
            lines.append('if is_plat("windows") then')
            lines.append(f'    add_links("{safe_name}")')
            lines.append('elseif is_plat("macosx") then')
            lines.append(f'    add_links("{safe_name}")')
            lines.append('else')
            lines.append(f'    add_links("{safe_name}")')
            lines.append('end')
        else:
            lines.append('if is_plat("windows") then')
            lines.append(f'    add_links("{safe_name}")')
            lines.append('else')
            lines.append(f'    add_links("{safe_name}")')
            lines.append('end')
        lines.append("")

    @staticmethod
    def _emit_include_dirs(lines: list[str], includes: list[str]) -> None:
        if not includes:
            return
        for inc in includes:
            if inc == ".":
                lines.append("add_includedirs(current_lib_path)")
            else:
                norm = XmakePackageGenerator._normalize_path(inc)
                lines.append(f'add_includedirs(current_lib_path .. "/{norm}")')
        lines.append("")

    @staticmethod
    def _emit_definitions(lines: list[str], definitions: list[str]) -> None:
        if not definitions:
            return
        for d in definitions:
            lines.append(f'add_defines("{d}")')
        lines.append("")

    @staticmethod
    def _emit_headerfiles(lines: list[str], headers: list[str]) -> None:
        if not headers:
            return
        for h in headers:
            norm = XmakePackageGenerator._normalize_path(h)
            lines.append(f'add_headerfiles(current_lib_path .. "/{norm}")')
        lines.append("")

    @staticmethod
    def _emit_sources(lines: list[str], headers: list[str] | None, sources: list[str] | None) -> None:
        all_files = (headers or []) + (sources or [])
        if not all_files:
            return
        for f in all_files:
            norm = XmakePackageGenerator._normalize_path(f)
            lines.append(f'add_files(current_lib_path .. "/{norm}")')
        lines.append("")

    @staticmethod
    def _emit_files(lines: list[str], items: list[str]) -> None:
        if not items:
            return
        for f in items:
            norm = XmakePackageGenerator._normalize_path(f)
            lines.append(f'add_files(current_lib_path .. "/{norm}")')
        lines.append("")

    @staticmethod
    def _emit_precompile(lines: list[str], precompile_headers: list[str]) -> None:
        if not precompile_headers:
            return
        for ph in precompile_headers:
            norm = XmakePackageGenerator._normalize_path(ph)
            lines.append(f'set_pcxxheader(current_lib_path .. "/{norm}")')
        lines.append("")

    def post_process(self, packages: list[Any], env: Any) -> str:
        result = """\
-- SYSTEM CONFIGURED, DO NOT EDIT!!!
"""
        for p in packages:
            path = self.generate(p, env)
            if not path:
                continue
            path = os.path.normpath(path).replace(os.sep, "/")
            lp = self._get_lp(p)
            result += f"\n-- {lp.publisher}@{lp.name}@{lp.version}\n"
            result += f"-- {lp.summary}\n"
            result += f'includes("{path}")\n'

        return result

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
