from __future__ import annotations

from typing import Any
from packaging.version import Version
from packaging.specifiers import SpecifierSet
from resolvelib.providers import AbstractProvider
from scripts.data.LibName import LibName


class Requirement:
    """Hashable requirement carrying both package identity and version constraint."""

    __slots__ = ("lib_name", "version_spec")

    def __init__(self, lib_name: LibName, version_spec: SpecifierSet | None = None) -> None:
        self.lib_name = lib_name
        if version_spec is None:
            self.version_spec = SpecifierSet(">=0")
        else:
            self.version_spec = version_spec

    @classmethod
    def from_dependency(cls, dep) -> Requirement:
        """Create a Requirement from a LibPackage.Dependency object."""
        return cls(dep.lib_name, dep.versionSpec)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Requirement):
            return NotImplemented
        return self.lib_name == other.lib_name

    def __hash__(self) -> int:
        return hash(self.lib_name)

    def __repr__(self) -> str:
        return f"Req({self.lib_name.fullName()} {self.version_spec})"


class ResolveLibProvider(AbstractProvider):
    def __init__(self, provider_manager, app_packages=None) -> None:
        super().__init__()
        self._mgr = provider_manager
        self._candidate_cache: dict[str, list[Candidate]] = {}
        # Build lookup: lib_name.fullName() → RefPackage
        self._ref_map: dict[str, Any] = {}
        if app_packages:
            for ref in app_packages:
                key = ref.lib_name.fullName()
                self._ref_map[key] = ref

    def identify(self, requirement_or_candidate) -> str:
        if isinstance(requirement_or_candidate, Candidate):
            return requirement_or_candidate.lib_name.fullName()
        if isinstance(requirement_or_candidate, Requirement):
            return requirement_or_candidate.lib_name.fullName()
        if isinstance(requirement_or_candidate, LibName):
            return requirement_or_candidate.fullName()
        return str(requirement_or_candidate)

    def _get_ref_for_identifier(self, identifier: str) -> Any:
        return self._ref_map.get(identifier)

    def _get_spec_from_requirement(self, requirement) -> SpecifierSet | None:
        if isinstance(requirement, Requirement):
            return requirement.version_spec
        if hasattr(requirement, "version_spec"):
            return requirement.version_spec
        if hasattr(requirement, "version_range"):
            return requirement.version_range
        return None

    def get_preference(
        self,
        identifier: str,
        resolutions: dict[str, Candidate],
        candidates: list[Candidate],
        information: list[Any],
        backtrack_causes: list[Any],
    ) -> int:
        """forceCandidate → highest priority (0). Otherwise fewer candidates first."""
        ref = self._get_ref_for_identifier(identifier)
        if ref is not None and ref.forceCandidate is not None:
            return 0
        if ref is not None and ref.suggestCandidate is not None:
            return 1
        return len(candidates)

    def find_matches(
        self,
        identifier: str,
        requirements: frozenset[Any],
        incompatibilities: dict[str, frozenset[Candidate]],
    ) -> list[Candidate]:
        bad: set[tuple[str, str]] = set()
        for cand in incompatibilities.get(identifier, frozenset()):
            bad.add((cand.lib_name.fullName(), cand.version))

        # Resolvelib passes requirements as an IteratorMapping;
        # use __getitem__ to retrieve the actual requirement objects
        # for this identifier (iterating yields keys, not values).
        reqs = list(requirements[identifier]) if identifier in requirements else []

        # Check for forceCandidate — must use ONLY this candidate
        ref = self._get_ref_for_identifier(identifier)
        if ref is not None and ref.forceCandidate is not None:
            fc = ref.forceCandidate
            if (fc.lib_name.fullName(), fc.version) not in bad:
                if all(self.is_satisfied_by(r, fc) for r in reqs):
                    return [fc]
            return []

        if identifier not in self._candidate_cache:
            lib_name = LibName(identifier)
            pkgs = self._mgr.findPackages(lib_name)
            self._candidate_cache[identifier] = [Candidate(p) for p in pkgs]

        candidates = self._candidate_cache[identifier]

        result: list[Candidate] = []
        for cand in candidates:
            if (cand.lib_name.fullName(), cand.version) in bad:
                continue
            if all(self.is_satisfied_by(r, cand) for r in reqs):
                result.append(cand)

        # suggestCandidate → put it first (but allow others)
        if ref is not None and ref.suggestCandidate is not None:
            sc = ref.suggestCandidate
            suggested = []
            rest = []
            for c in result:
                if c.lib_name == sc.lib_name and c.version == sc.version:
                    suggested.append(c)
                else:
                    rest.append(c)
            rest.sort(key=lambda c: Version(c.version), reverse=True)
            result = suggested + rest
        else:
            result.sort(key=lambda c: Version(c.version), reverse=True)

        return result

    def is_satisfied_by(self, requirement: Any, candidate: Candidate) -> bool:
        spec = self._get_spec_from_requirement(requirement)
        if spec is None:
            return True
        return spec.contains(Version(candidate.version))

    def get_dependencies(self, candidate: Candidate) -> list[Requirement]:
        # Skip deps for dynamic packages
        ref = self._get_ref_for_identifier(candidate.lib_name.fullName())
        if ref is not None and getattr(ref, "mode", "default") == "dynamic":
            return []

        deps: list[Requirement] = []
        for dep in candidate.pkg.getDependency(provider_mgr=self._mgr):
            if not dep.lib_name.isValid():
                continue
            deps.append(Requirement(dep.lib_name, dep.versionSpec))
        return deps

class Candidate:
    __slots__ = ("pkg", "lib_name", "name", "version")

    def __init__(self, pkg) -> None:
        self.pkg = pkg
        pkg_lib_name = getattr(pkg, "lib_name", None)
        if pkg_lib_name is None:
            pkg_lib_name = LibName(pkg.name, publisher=pkg.publisher, is_global=pkg.is_global)
        self.lib_name: LibName = pkg_lib_name
        self.name: str = pkg_lib_name.fullName()
        self.version: str = pkg.version

    def __eq__(self, other) -> bool:
        if not isinstance(other, Candidate):
            return NotImplemented
        return self.lib_name == other.lib_name and self.version == other.version

    def __hash__(self) -> int:
        return hash((self.lib_name, self.version))

    def __repr__(self) -> str:
        return f"Candidate({self.name}=={self.version})"
