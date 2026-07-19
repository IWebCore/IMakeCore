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
        lib_name = LibName(dep.fullName)
        return cls(lib_name, dep.versionSpec)

    def __eq__(self, other) -> bool:
        if not isinstance(other, Requirement):
            return NotImplemented
        return self.lib_name.fullName() == other.lib_name.fullName()

    def __hash__(self) -> int:
        return hash(self.lib_name.fullName())

    def __repr__(self) -> str:
        return f"Req({self.lib_name.fullName()} {self.version_spec})"


class ResolveLibProvider(AbstractProvider):
    def __init__(self, provider_manager) -> None:
        super().__init__()
        self._mgr = provider_manager
        self._candidate_cache: dict[str, list[Candidate]] = {}

    def identify(self, requirement_or_candidate) -> str:
        if isinstance(requirement_or_candidate, Candidate):
            return requirement_or_candidate.lib_name.fullName()
        if isinstance(requirement_or_candidate, Requirement):
            return requirement_or_candidate.lib_name.fullName()
        if isinstance(requirement_or_candidate, LibName):
            return requirement_or_candidate.fullName()
        return str(requirement_or_candidate)

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
        """Prefer packages with fewer candidates (most constrained first)."""
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

        if identifier not in self._candidate_cache:
            lib_name = LibName(identifier)
            pkgs = self._mgr.findPackages(lib_name)
            self._candidate_cache[identifier] = [Candidate(p) for p in pkgs]

        candidates = self._candidate_cache[identifier]

        result: list[Candidate] = []
        for cand in candidates:
            if (cand.lib_name.fullName(), cand.version) in bad:
                continue
            if all(self.is_satisfied_by(r, cand) for r in requirements):
                result.append(cand)

        result.sort(key=lambda c: Version(c.version), reverse=True)
        return result

    def is_satisfied_by(self, requirement: Any, candidate: Candidate) -> bool:
        spec = self._get_spec_from_requirement(requirement)
        if spec is None:
            return True
        return spec.contains(Version(candidate.version))

    def get_dependencies(self, candidate: Candidate) -> list[Requirement]:
        deps: list[Requirement] = []
        for dep in candidate.pkg.getDependency():
            lib_name = LibName(dep.fullName)
            if not lib_name.isValid():
                continue
            deps.append(Requirement(lib_name, dep.versionSpec))
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
        return self.name == other.name and self.version == other.version

    def __hash__(self) -> int:
        return hash((self.name, self.version))

    def __repr__(self) -> str:
        return f"Candidate({self.name}=={self.version})"
