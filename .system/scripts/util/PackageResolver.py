import os
from packaging.version import Version
from scripts.data.LibPackage import LibPackage
from scripts.util.download.UrlPackageDownload import UrlPackageDownload
from scripts.util.download.GitPackageDownload import GitPackageDownload


class PackageResolver:
    def __init__(self, app_data, env):
        self.app_data = app_data
        self.env = env
        self._project_libs = None

    def resolve_all(self):
        for ref in self.app_data.packages:
            self._resolve_with_cache(ref)
        self._resolve_external_deps()

    def _resolve_with_cache(self, ref):
        cached = self.app_data.get_cached(ref)
        if cached is not None and os.path.exists(cached.path):
            ref.real_package = cached
            return
        self.resolve_one(ref)

    def resolve_one(self, ref):
        if ref.path:
            target = self._resolve_path(ref)
            if target is None:
                print(f"ERROR: Package '{ref.name}' path '{ref.path}' does not exist.")
                exit(1)
            lib = LibPackage.fromFolder(target)
            if not lib.success:
                print(f"ERROR: Failed to load package '{ref.name}' from '{target}'.")
                exit(1)
            if not lib.isMatch(ref):
                print(f"ERROR: Package at '{target}' does not match '{ref.name}' version {ref.version}.")
                exit(1)
            ref.real_package = lib
            return

        if ref.origin == "local":
            lib = self._find_in_project_libs(ref)
            if lib is None:
                print(f"ERROR: Package '{ref.name}' not found in project local library. Origin is 'local'.")
                exit(1)
            ref.real_package = lib
            return

        if ref.origin == "system":
            lib = self._find_in_env_libs(ref)
            if lib is None:
                print(f"ERROR: Package '{ref.name}' not found in system package index. Run updateDb.py first.")
                exit(1)
            ref.real_package = lib
            return

        lib = self._find_in_project_libs(ref) or self._find_in_env_libs(ref)
        if lib is not None:
            ref.real_package = lib
            return

        if ref.url is not None:
            self._download_url(ref)
        elif ref.git is not None:
            self._download_git(ref)
        else:
            print(f"ERROR: Package '{ref.name}' version '{ref.version}' not found and no download source.")
            exit(1)

    def _resolve_path(self, ref):
        if not ref.path or not ref.path.strip():
            return None
        if os.path.isabs(ref.path):
            resolved = os.path.normpath(ref.path)
        else:
            resolved = os.path.normpath(os.path.join(self.app_data.path, ref.path))
        if not os.path.exists(resolved):
            return None
        if not os.path.isdir(resolved):
            return None
        return resolved

    # 这个函数应该在 path, git， url 中使用， 在 发现 git / url 的时候，直接使用这个路径查找，如果没有找到，则考虑下载。
    def _compute_target_dir(self, ref):
        publisher = ref.publisher or "local"
        ver = ref.version if ref.version not in ("*", "latest", "default", "") else "default"
        dir_name = f"{publisher}@{ref.name}@{ver}"
        base = self.env.sysLibStore if ref.origin == "system" else self.env.appLibStore
        return os.path.join(base, dir_name)

    def _download_url(self, ref):
        target = self._compute_target_dir(ref)
        downloader = UrlPackageDownload(ref, target, self.env)
        if not downloader.execute():
            print(f"ERROR: Failed to download '{ref.name}' from {ref.url}.")
            exit(1)
        if ref.real_package is None:
            print(f"ERROR: Downloaded package '{ref.name}' is invalid.")
            exit(1)

    def _download_git(self, ref):
        target = self._compute_target_dir(ref)
        downloader = GitPackageDownload(ref, target, self.env)
        if not downloader.execute():
            print(f"ERROR: Failed to clone git repo for '{ref.name}'.")
            exit(1)
        if ref.real_package is None:
            print(f"ERROR: Cloned package '{ref.name}' is invalid.")
            exit(1)

    # 这个考虑在 AppData 中实现这个内容，并且缓存 projectLibs.
    def _get_project_libs(self):
        if self._project_libs is not None:
            return self._project_libs
        result = []
        lib_dir = self.env.appLibStore
        if os.path.exists(lib_dir):
            for entry in os.listdir(lib_dir):
                pkg_dir = os.path.join(lib_dir, entry)
                if not os.path.isdir(pkg_dir):
                    continue
                pkg_json = os.path.join(pkg_dir, "package.json")
                if not os.path.exists(pkg_json):
                    continue
                lib = LibPackage.fromFolder(pkg_dir)
                if lib.success:
                    result.append(lib)
        self._project_libs = result
        return result

    def _find_in_project_libs(self, ref):
        matching = [lib for lib in self._get_project_libs() if lib.isMatch(ref)]
        matching.sort(key=lambda x: Version(x.version), reverse=True)
        return matching[0] if matching else None

    def _find_in_env_libs(self, ref):
        key = f"{ref.publisher}/{ref.name}"
        if key in self.env.libs:
            for lib in self.env.libs[key]:
                if ref.version_range.contains(Version(lib.version)):
                    return lib
        for k, libs in self.env.libs.items():
            if k.endswith(ref.name):
                for lib in libs:
                    if ref.version_range.contains(Version(lib.version)):
                        return lib
        return None

    def _resolve_external_deps(self):
        seen = set()
        changed = True
        max_iter = 100
        iteration = 0
        while changed and iteration < max_iter:
            changed = False
            iteration += 1
            for ref in self.app_data.all_packages():
                if not ref.real_package or not ref.real_package.success:
                    continue
                for dep in ref.real_package.getDependency():
                    dep_key = f"{dep.fullName}@{dep.version}"
                    if dep_key in seen:
                        continue
                    seen.add(dep_key)
                    if self._is_dep_satisfied(dep):
                        continue
                    ext = RefPackage()
                    ext.name = dep.fullName
                    ext.version = dep.version
                    ext.version_range = dep.versionSpec
                    ext.origin = ref.origin
                    ext._is_external = True
                    self.resolve_one(ext)
                    self.app_data.external_packages.append(ext)
                    changed = True
        if iteration >= max_iter:
            print("ERROR: Circular dependency or too many dependency levels.")
            exit(1)

    def _is_dep_satisfied(self, dep):
        for ref in self.app_data.all_packages():
            if ref.real_package and ref.real_package.success:
                if dep.matchLib(ref.real_package):
                    return True
        return False


from scripts.data.RefPackage import RefPackage
