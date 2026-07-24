import os
import shutil
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
    """Resolve package dependency graph via SAT solver.

    Reads root packages from app_data.packages, resolves transitive
    dependencies, and appends external RefPackage entries directly
    to app_data.packages so that the caller sees a single flat list.
    """

    def __init__(self, app_data, env):
        self.app_data = app_data
        self.env = env

    # ── Public API ────────────────────────────────────────────────────

    def resolve_all(self) -> None:
        """Run the full resolution pipeline."""
        root_refs = [r for r in self.app_data.packages if not r.skip]
        if not root_refs:
            return

        mgr = self.env.getProviderManager()
        requirements = self._gather_requirements(mgr, root_refs)
        result = self._solve(mgr, root_refs, requirements)
        self._wire_results(root_refs, result)
        self._handleLocalOrigin()
        self._checkResults()

    # ── Requirements ──────────────────────────────────────────────────

    def _gather_requirements(self, mgr, root_refs: list) -> list[Requirement]:
        """Build initial requirement set from root packages.

        Packages with forceCandidate already have a pinned candidate;
        their transitive deps are expanded directly.
        """
        reqs: list[Requirement] = []
        for ref in root_refs:
            if ref.forceCandidate is not None:
                ref.real_package = ref.forceCandidate.pkg
                for dep in ref.forceCandidate.pkg.getDependency(provider_mgr=mgr):
                    if dep.lib_name.isValid():
                        reqs.append(Requirement(dep.lib_name, dep.versionSpec))
            else:
                reqs.append(Requirement(ref.lib_name, ref.version_range))
        return reqs

    # ── SAT solver ────────────────────────────────────────────────────

    def _solve(self, mgr, root_refs, requirements) -> Any:
        """Run the SAT resolver. Exits on ResolutionImpossible."""
        provider = ResolveLibProvider(mgr, app_packages=root_refs)
        resolver = Resolver(provider, BaseReporter())
        try:
            return resolver.resolve(requirements)
        except ResolutionImpossible as e:
            print("ERROR: Dependency resolution failed — "
                  "no compatible version combination found.")
            if hasattr(e, 'causes'):
                for cause in e.causes:
                    print(f"  - {cause}")
            exit(1)

    # ── Wire results ─────────────────────────────────────────────────

    def _wire_results(self, root_refs, result) -> None:
        """Assign resolved candidates to root refs and add transitive deps.

        Root refs get real_package set.  Transitive dependencies become
        new RefPackage entries appended to app_data.packages.
        """
        root_keys = {ref.lib_name.fullName() for ref in root_refs}
        mapping = result.mapping

        # Bind resolved packages to root refs
        for ref in root_refs:
            if ref.real_package is not None:
                continue
            key = ref.lib_name.fullName()
            if key in mapping:
                ref.real_package = mapping[key].pkg

        # Create entries for transitive-only packages
        for name, candidate in mapping.items():
            if name in root_keys:
                continue
            dep = RefPackage()
            dep.lib_name = candidate.lib_name
            dep.version = candidate.version
            dep.version_range = Utils.parseVersionSpecifier(candidate.version)
            dep.origin = "default"
            dep.real_package = candidate.pkg
            self.app_data.packages.append(dep)

    # ── Post-resolve: static mode propagation ─────────────────────────

    def _checkResults(self) -> None:
        """Propagate 'static' mode to transitive dependencies.

        When a package's mode is 'static', all of its transitive
        dependencies must also be static.  Dependencies explicitly
        pinned to 'dynamic' are left alone; 'source' on a static
        chain is a fatal error.
        """
        mgr = self.env.getProviderManager()

        # Build lookup: lib_name.fullName() → RefPackage
        ref_by_name: dict[str, Any] = {}
        for ref in self.app_data.packages:
            if ref.skip or ref.real_package is None:
                continue
            ref_by_name[ref.lib_name.fullName()] = ref

        # BFS starting from every package already in static mode
        queue: list[Any] = [
            ref for ref in self.app_data.packages
            if not ref.skip and ref.real_package is not None and ref.mode == "static"
        ]
        visited: set[str] = {ref.lib_name.fullName() for ref in queue}

        while queue:
            ref = queue.pop(0)
            lp = ref.real_package

            # Verify the static package itself supports static mode
            supported = getattr(lp, "_supported_modes", ["source", "static"])
            if "static" not in supported:
                print(f"ERROR: Package '{lp.fullName}' has mode='static' but does"
                      f" not support static mode. Supported: {supported}.")
                exit(1)

            for dep in lp.getDependency(provider_mgr=mgr):
                if not dep.lib_name.isValid():
                    continue

                dep_key = dep.lib_name.fullName()
                dep_ref = ref_by_name.get(dep_key)
                if dep_ref is None:
                    continue
                if dep_key in visited:
                    continue

                if dep_ref.mode == "source":
                    print(f"ERROR: Package '{dep_key}' is explicitly set to"
                          f" 'source' mode, but it is a transitive dependency"
                          f" of static package '{ref.lib_name.fullName()}'.")
                    exit(1)

                if dep_ref.mode == "dynamic":
                    # Pinned to dynamic — leave alone, don't recurse
                    visited.add(dep_key)
                    continue

                # mode is "default" — convert to static after validation
                dep_lp = dep_ref.real_package
                dep_supported = getattr(dep_lp, "_supported_modes", ["source", "static"])
                if "static" not in dep_supported:
                    print(f"ERROR: Package '{dep_key}' cannot be set to static mode"
                          f" (required by '{ref.lib_name.fullName()}')."
                          f" Supported modes: {dep_supported}.")
                    exit(1)

                dep_ref.mode = "static"
                visited.add(dep_key)
                queue.append(dep_ref)

    # ── Post-resolve: local origin enforcement ─────────────────────────

    def _handleLocalOrigin(self) -> None:
        """Ensure packages with origin='local' live in the project's .lib/ store.

        If a package with origin='local' is only present in the system
        store, copy it to the project .lib/ directory, register it with
        the LocalLibProvider, and point ref.real_package to the local copy.
        """
        local_provider = self.env.getProviderManager().getLocalProvider()
        sys_lib_store = self.env.sysLibStore
        app_lib_store = self.env.appLibStore

        for ref in self.app_data.packages:
            if ref.origin != "local":
                continue
            lp = ref.real_package
            if lp is None:
                continue

            # Check whether this version already exists in the local provider
            local_pkgs = local_provider.findPackages(ref.lib_name)
            already_local = any(
                p.version == lp.version for p in local_pkgs
            )
            if already_local:
                # Already present — swap real_package to the local copy
                for p in local_pkgs:
                    if p.version == lp.version:
                        ref.real_package = p
                        break
                continue

            # Copy from system lib store to project .lib/
            dir_name = f"{lp.publisher}@{lp.name}@{lp.version}"
            src = os.path.join(sys_lib_store, dir_name)
            dst = os.path.join(app_lib_store, dir_name)

            if not os.path.exists(src):
                print(f"ERROR: Package '{lp.fullName}@{lp.version}' has"
                      f" origin='local' but was not found in system lib"
                      f" store at '{src}'.")
                exit(1)

            if not os.path.exists(dst):
                shutil.copytree(src, dst)

            local_lp = LibPackage.fromFolder(dst)
            local_provider.appendLibs(local_lp)
            ref.real_package = local_lp
