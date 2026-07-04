import os

CONDITION_QMAKE = "imakecore_condition.pri"
CONDITION_CMAKE = "imakecore_condition.cmake"


class SupportProjectFileGenerator:
    def __init__(self, project_name, lib_packages, pack_type, env):
        self.project_name = project_name
        self.lib_packages = lib_packages
        self.pack_type = pack_type
        self.env = env
        self.support_dir = os.path.normpath(os.path.join(env.appPath, ".support"))

    def generate(self):
        os.makedirs(self.support_dir, exist_ok=True)
        self._ensure_condition_file()
        if self.pack_type == "qmake":
            content, out_path = self._qmake_content(), os.path.join(self.support_dir, f"{self.project_name}_Support.pro")
        else:
            content, out_path = self._cmake_content(), os.path.join(self.support_dir, "CMakeLists.txt")
        with open(out_path, "wt", encoding="utf-8") as f:
            f.write(content)
        return out_path

    def _ensure_condition_file(self):
        name = CONDITION_QMAKE if self.pack_type == "qmake" else CONDITION_CMAKE
        path = os.path.join(self.support_dir, name)
        if os.path.exists(path):
            return
        if self.pack_type == "qmake":
            content = (
                "# IMAKECORE Condition — user-customizable shared settings\n"
                "# DO NOT DELETE this file. Edit to add shared build config.\n"
                "# Included before all sub-projects.\n"
            )
        else:
            content = (
                "# IMAKECORE Condition — user-customizable shared settings\n"
                "# DO NOT DELETE this file. Edit to add shared build config.\n"
                "# Included before all sub-projects.\n"
            )
        with open(path, "wt", encoding="utf-8") as f:
            f.write(content)

    def _qmake_content(self):
        lines = []
        lines.append("# SYSTEM AUTO GENERATED DO NOT EDIT!!!")
        lines.append(f"# {self.project_name} support subdirs project")
        lines.append("")
        lines.append(f"include({CONDITION_QMAKE})")
        lines.append("")
        lines.append("TEMPLATE = subdirs")
        lines.append("CONFIG += ordered")
        lines.append("")
        for p in self.lib_packages:
            lp = getattr(p, "real_package", None)
            if lp is None:
                continue
            mode = getattr(p, "mode", "static")
            dir_name = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
            sub_dir = os.path.join(dir_name, f"{dir_name}.pro")
            lines.append(f"SUBDIRS += {sub_dir}")
        lines.append("")
        return "\n".join(lines) + "\n"

    def _cmake_content(self):
        lines = []
        lines.append("# SYSTEM AUTO GENERATED DO NOT EDIT!!!")
        lines.append(f"# {self.project_name} support subdirs project")
        lines.append("")
        lines.append("cmake_minimum_required(VERSION 3.16)")
        lines.append(f"project({self.project_name}_Support)")
        lines.append("")
        lines.append(f"include({CONDITION_CMAKE})")
        lines.append("")
        for p in self.lib_packages:
            lp = getattr(p, "real_package", None)
            if lp is None:
                continue
            mode = getattr(p, "mode", "static")
            dir_name = f"{lp.publisher}@{lp.name}@{lp.version}_{mode}"
            lines.append(f"add_subdirectory({dir_name} {dir_name}_build)")
        lines.append("")
        return "\n".join(lines) + "\n"
