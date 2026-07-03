import os
from scripts.util.make.MakePackageGenerator import MakePackageGenerator


class CmakePackageGenerator(MakePackageGenerator):

    def generate(self, pkg, env):
        lp = pkg.libPackage
        output_path = self._lib_output_path(lp, env, "cmake")

        detail = self._get_detail_from_db(lp.publisher, lp.name, lp.version)
        if detail is None:
            print(f"  [WARN] No detail record for {lp.publisher}/{lp.name}@{lp.version}. Run updateDb.py first.")
            return ""

        paths = self._get_file_paths(detail)
        if paths is None:
            return ""

        lib_path = self._normalize_path(lp.path)
        lines = self._header_comment(lp)
        lines.append(f'set(current_lib_path "{lib_path}")')
        lines.append("")

        self._emit_include_dirs(lines, paths["includes"])
        self._emit_definitions(lines, paths["definitions"])
        self._emit_sources(lines, paths["headers"], paths["sources"])
        self._emit_ui(lines, paths["uis"])
        self._emit_resources(lines, paths["resources"])
        self._emit_precompile(lines, paths["precompile_headers"])

        content = "\n".join(lines) + "\n"
        return self._write_if_changed(output_path, content)

    @staticmethod
    def _emit_include_dirs(lines, includes):
        if not includes:
            return
        lines.append("target_include_directories(${IMAKECORE_TARGET} PRIVATE")
        for inc in includes:
            entry = '"${current_lib_path}"' if inc == "." else f'"${{current_lib_path}}/{inc}"'
            lines.append(f"    {entry}")
        lines.append(")")
        lines.append("")

    @staticmethod
    def _emit_definitions(lines, definitions):
        if not definitions:
            return
        lines.append("target_compile_definitions(${IMAKECORE_TARGET} PRIVATE")
        for d in definitions:
            lines.append(f"    {d}")
        lines.append(")")
        lines.append("")

    @staticmethod
    def _emit_sources(lines, headers, sources):
        all_files = (headers or []) + (sources or [])
        if not all_files:
            return
        lines.append("target_sources(${IMAKECORE_TARGET} PRIVATE")
        for f in all_files:
            lines.append(f'    "${{current_lib_path}}/{f}"')
        lines.append(")")
        lines.append("")

    @staticmethod
    def _emit_ui(lines, uis):
        if not uis:
            return
        lines.append("set(CMAKE_AUTOUIC ON)")
        for u in uis:
            lines.append(f'qt_wrap_ui(${{IMAKECORE_TARGET}} "${{current_lib_path}}/{u}")')
        lines.append("")

    @staticmethod
    def _emit_resources(lines, resources):
        if not resources:
            return
        lines.append("set(CMAKE_AUTORCC ON)")
        for r in resources:
            lines.append(f'qt_add_resources(${{IMAKECORE_TARGET}} "${{current_lib_path}}/{r}")')
        lines.append("")

    @staticmethod
    def _emit_precompile(lines, precompile_headers):
        if not precompile_headers:
            return
        lines.append("target_precompile_headers(${IMAKECORE_TARGET} PRIVATE")
        for ph in precompile_headers:
            lines.append(f'    "${{current_lib_path}}/{ph}"')
        lines.append(")")
        lines.append("")

    def post_process(self, packages, env):
        result = """\
###################################
# SYSTEM CONFIGURED, DO NOT EDIT!!!
###################################\n"""
        for p in packages:
            path = self.generate(p, env)
            if not path:
                continue
            path = os.path.normpath(path).replace(os.sep, "/")
            result += f"\n# {p.libPackage.publisher}@{p.libPackage.name}@{p.libPackage.version}\n"
            result += f"# {p.libPackage.summary}\n"
            result += "include(" + path + ")\n"

        return result
