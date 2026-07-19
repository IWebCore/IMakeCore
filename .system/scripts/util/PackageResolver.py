import os
from packaging.version import Version
from packaging.specifiers import SpecifierSet
from resolvelib import BaseReporter, Resolver
from resolvelib.resolvers.exceptions import ResolutionImpossible
from scripts.data.LibPackage import LibPackage
from scripts.data.RefPackage import RefPackage
from scripts.data.LibName import LibName
from scripts.Utils import Utils
from scripts.provider.ResolveLibProvider import Requirement, ResolveLibProvider
from scripts.util.download.UrlPackageDownload import UrlPackageDownload
from scripts.util.download.GitPackageDownload import GitPackageDownload


class PackageResolver:
    def __init__(self, app_data, env):
        self.app_data = app_data
        self.env = env

    def resolve_all(self):
        for ref in self.app_data.packages:
            self._resolve_with_cache(ref)
        self._resolve_transitive()

    def _resolve_with_cache(self, ref):
        cached = self.app_data.get_cached(ref)
        if cached is not None and os.path.exists(cached.path):
            ref.real_package = cached
            return
        self.resolve_one(ref)

    def resolve_one(self, ref):
        self._resolve_publisher(ref)

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

    def _resolve_transitive(self):
        root_reqs: list[Requirement] = []
        mgr = self.env.getProviderManager()
        for ref in self.app_data.packages:
            if not ref.real_package or not ref.real_package.success:
                continue
            for dep in ref.real_package.getDependency(provider_mgr=mgr):
                if not dep.lib_name.isValid():
                    continue
                root_reqs.append(Requirement(dep.lib_name, dep.versionSpec))

        if not root_reqs:
            return

        provider = ResolveLibProvider(self.env.getProviderManager())
        reporter = BaseReporter()
        resolver = Resolver(provider, reporter)

        try:
            result = resolver.resolve(root_reqs)
            for lib_name_str, candidate in result.mapping.items():
                lib_name = LibName(lib_name_str)
                existing = self._find_existing(lib_name, candidate.version)
                if existing is not None:
                    continue
                ext = RefPackage()
                ext.lib_name = candidate.lib_name
                ext.version = candidate.version
                ext.version_range = Utils.parseVersionSpecifier(candidate.version)
                ext.origin = "default"
                ext._is_external = True
                ext.real_package = candidate.pkg
                self.app_data.external_packages.append(ext)

        except ResolutionImpossible as e:
            print("ERROR: Dependency resolution failed — no compatible version combination found.")
            if hasattr(e, 'causes'):
                for cause in e.causes:
                    print(f"  - {cause}")
            exit(1)

    def _resolve_publisher(self, ref):
        """If lib_name lacks publisher, query provider manager to resolve it.
        If still not found, report error."""
        if ref.lib_name.publisher:
            return
        mgr = self.env.getProviderManager()
        real = mgr.findRealLibName(ref.lib_name)
        if real is None:
            print(f"ERROR: Cannot resolve publisher for package '{ref.lib_name.name}'."
                  f" The package cannot be resolved.")
            exit(1)
        ref.lib_name = real

    def _find_existing(self, lib_name, version):
        for ref in self.app_data.all_packages():
            lp = ref.real_package
            if lp and lp.lib_name == lib_name and lp.version == version:
                return ref
        return None

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

    def _find_in_project_libs(self, ref):
        lib_name = ref.lib_name
        pkgs = self.env.getProviderManager().getLocalProvider().findPackages(lib_name)
        matching = [lib for lib in pkgs if lib.isMatch(ref)]
        matching.sort(key=lambda x: Version(x.version), reverse=True)
        return matching[0] if matching else None

    def _find_in_env_libs(self, ref):
        lib_name = ref.lib_name
        pkgs = self.env.getProviderManager().getSystemProvider().findPackages(lib_name)
        for lib in pkgs:
            if ref.version_range.contains(Version(lib.version)):
                return lib
        return None
