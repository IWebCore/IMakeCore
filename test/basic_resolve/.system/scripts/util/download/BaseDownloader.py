import os
from scripts.data.LibPackage import LibPackage


class BaseDownloader:
    def __init__(self, ref_package, target_dir, env):
        self.ref = ref_package
        self.target_dir = target_dir
        self.env = env
        self.lib_package = None

    def execute(self):
        if os.path.exists(self.target_dir):
            if self._check_conflict():
                self._build_lib_package()
                return True
        if not self.download():
            return False
        if not self.validate():
            return False
        self._build_lib_package()
        return True

    def download(self):
        raise NotImplementedError

    def validate(self):
        raise NotImplementedError

    def get_lib_package(self):
        return self.lib_package

    def _check_conflict(self):
        pkg_json = os.path.join(self.target_dir, "package.json")
        if not os.path.exists(pkg_json):
            return self.ref.resolve is not None
        return True

    def _build_lib_package(self):
        pkg_json = os.path.join(self.target_dir, "package.json")
        if os.path.exists(pkg_json):
            self.lib_package = LibPackage(self.target_dir)
        elif self.ref.resolve:
            self.lib_package = LibPackage._virtual_from_resolve(
                self.target_dir, self.ref.name,
                self.ref.publisher or "local",
                self.ref.version or "default",
                self.ref.resolve
            )
        if self.lib_package:
            self.ref.real_package = self.lib_package
