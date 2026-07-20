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


class PackageResolver:
    def __init__(self, app_data, env):
        self.app_data = app_data
        self.env = env

    def resolve_all(self):
        """Resolve all packages via resolvelib in a single pass."""
        root_reqs: list[Requirement] = []
        mgr = self.env.getProviderManager()

        for ref in self.app_data.all_packages():
            if ref.skip:
                continue

            if ref.forceCandidate is not None:
                ref.real_package = ref.forceCandidate.pkg
                for dep in ref.forceCandidate.pkg.getDependency(provider_mgr=mgr):
                    if dep.lib_name.isValid():
                        root_reqs.append(Requirement(dep.lib_name, dep.versionSpec))
                continue

            root_reqs.append(Requirement(ref.lib_name, ref.version_range))

        if not root_reqs:
            return

        # Snapshot BEFORE external packages are added during resolution
        root_refs = list(self.app_data.all_packages())

        provider = ResolveLibProvider(mgr, app_packages=root_refs)
        reporter = BaseReporter()
        resolver = Resolver(provider, reporter)

        try:
            result = resolver.resolve(root_reqs)
        except ResolutionImpossible as e:
            print("ERROR: Dependency resolution failed — "
                  "no compatible version combination found.")
            if hasattr(e, 'causes'):
                for cause in e.causes:
                    print(f"  - {cause}")
            exit(1)

        # Build lookup
        resolved: dict[str, Any] = {k: v for k, v in result.mapping.items()}
        root_keys = {ref.lib_name.fullName() for ref in root_refs}

        # Assign real_package to root refs from resolved results
        for ref in root_refs:
            if ref.real_package is not None:
                continue
            key = ref.lib_name.fullName()
            if key in resolved:
                ref.real_package = resolved[key].pkg

        # Create external packages for transitive deps not in root refs
        for lib_name_str, candidate in result.mapping.items():
            if lib_name_str in root_keys:
                continue
            ext = RefPackage()
            ext.lib_name = candidate.lib_name
            ext.version = candidate.version
            ext.version_range = Utils.parseVersionSpecifier(candidate.version)
            ext.origin = "default"
            ext._is_external = True
            ext.real_package = candidate.pkg
            self.app_data.external_packages.append(ext)
