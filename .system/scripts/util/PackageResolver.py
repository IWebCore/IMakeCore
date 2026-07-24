import os
from typing import Any
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
        mgr = self.env.getProviderManager()
        root_reqs = self._collect_requirements(mgr)
        if not root_reqs:
            return

        root_refs = list(self.app_data.all_packages())
        result = self._run_resolver(mgr, root_refs, root_reqs)
        self._apply_results(root_refs, result)

    # ── Step 1: Collect root requirements ────────────────────────────────

    def _collect_requirements(self, mgr) -> list[Requirement]:
        reqs: list[Requirement] = []
        for ref in self.app_data.all_packages():
            if ref.skip:
                continue
            if ref.forceCandidate is not None:
                self._handle_force_candidate(ref, reqs, mgr)
                continue
            reqs.append(Requirement(ref.lib_name, ref.version_range))
        return reqs

    def _handle_force_candidate(self, ref, reqs, mgr):
        """Set real_package from forceCandidate, add its deps as requirements."""
        ref.real_package = ref.forceCandidate.pkg
        for dep in ref.forceCandidate.pkg.getDependency(provider_mgr=mgr):
            if dep.lib_name.isValid():
                reqs.append(Requirement(dep.lib_name, dep.versionSpec))

    # ── Step 2: Run SAT resolver ─────────────────────────────────────────

    def _run_resolver(self, mgr, root_refs, root_reqs) -> Any:
        provider = ResolveLibProvider(mgr, app_packages=root_refs)
        resolver = Resolver(provider, BaseReporter())
        try:
            return resolver.resolve(root_reqs)
        except ResolutionImpossible as e:
            print("ERROR: Dependency resolution failed — "
                  "no compatible version combination found.")
            if hasattr(e, 'causes'):
                for cause in e.causes:
                    print(f"  - {cause}")
            exit(1)

    # ── Step 3: Apply resolved results ───────────────────────────────────

    def _apply_results(self, root_refs, result):
        resolved = {k: v for k, v in result.mapping.items()}
        root_keys = {ref.lib_name.fullName() for ref in root_refs}
        self._assign_to_roots(root_refs, resolved)
        self._create_externals(result.mapping, root_keys)

    def _assign_to_roots(self, root_refs, resolved: dict[str, Any]):
        """Set real_package on root refs from resolved candidates."""
        for ref in root_refs:
            if ref.real_package is not None:
                continue
            key = ref.lib_name.fullName()
            if key in resolved:
                ref.real_package = resolved[key].pkg

    def _create_externals(self, mapping, root_keys: set[str]):
        """Create external RefPackage entries for transitive dependencies."""
        for lib_name_str, candidate in mapping.items():
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
