import os
from scripts.util.make.MakePackageGenerator import MakePackageGenerator


class QmakePackageGenerator(MakePackageGenerator):

    def generate(self, pkg, env):
        lp = pkg.libPackage
        output_path = self._lib_output_path(lp, env, "pri")

        detail = self._get_detail_from_db(lp.publisher, lp.name, lp.version)
        if detail is None:
            print(f"  [WARN] No detail record for {lp.publisher}/{lp.name}@{lp.version}. Run updateDb.py first.")
            return ""

        paths = self._get_file_paths(detail)
        if paths is None:
            return ""

        lib_path = self._normalize_path(lp.path)
        lines = self._header_comment(lp)
        lines.append(f'current_lib_path = "{lib_path}"')
        lines.append("")

        self._emit_includes(lines, paths["includes"])
        self._emit_definitions(lines, paths["definitions"])
        self._emit_continuation(lines, "HEADERS", paths["headers"], '    $$current_lib_path/{item}')
        self._emit_continuation(lines, "SOURCES", paths["sources"], '    $$current_lib_path/{item}')
        self._emit_continuation(lines, "FORMS", paths["uis"], '    $$current_lib_path/{item}')
        self._emit_continuation(lines, "RESOURCES", paths["resources"], '    $$current_lib_path/{item}')
        self._emit_single(lines, paths["precompile_headers"], "PRECOMPILED_HEADER", '$$current_lib_path/{item}')

        content = "\n".join(lines) + "\n"
        return self._write_if_changed(output_path, content)

    @staticmethod
    def _emit_includes(lines, includes):
        if not includes:
            return
        lines.append("INCLUDEPATH += \\")
        for i, inc in enumerate(includes):
            suffix = " \\" if i < len(includes) - 1 else ""
            path = "$$current_lib_path" if inc == "." else f"$$current_lib_path/{inc}"
            lines.append(f"    {path}{suffix}")
        lines.append("")

    @staticmethod
    def _emit_definitions(lines, definitions):
        if not definitions:
            return
        for d in definitions:
            lines.append(f"DEFINES += {d}")
        lines.append("")

    @staticmethod
    def _emit_continuation(lines, keyword, items, template):
        if not items:
            return
        lines.append(f"{keyword} += \\")
        for i, item in enumerate(items):
            suffix = " \\" if i < len(items) - 1 else ""
            lines.append(f"{template.format(item=item)}{suffix}")
        lines.append("")

    @staticmethod
    def _emit_single(lines, items, keyword, template):
        if not items:
            return
        for item in items:
            lines.append(f"{keyword} = {template.format(item=item)}")
        lines.append("")

    def post_process(self, packages, env):
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
            result += f"\n# {p.libPackage.publisher}@{p.libPackage.name}@{p.libPackage.version}\n"
            result += f"# {p.libPackage.summary}\n"
            result += "include(" + path + ")\n"

        return result
