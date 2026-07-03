"""
PackageScanner.py — Scan a package directory using resolve rules.
Returns a ScanResult object with categorized file lists (all relative paths).
"""
import os
from scripts.util.FileFilter import FileFilter, GitignoreRule


HEADER_SUFFIXES = (".h", ".hpp", ".hxx")
SOURCE_SUFFIXES = (".c", ".cpp", ".cxx", ".c++", ".cc")
RESOURCE_SUFFIXES = (".rcc",)
UI_SUFFIXES = (".ui",)


class ScanResult:
    def __init__(self):
        self.headers = []
        self.sources = []
        self.uis = []
        self.resources = []
        self.definitions = []
        self.includes = []
        self.precompile_headers = []
        self.dynamic_definition = []

    def to_dict(self):
        return {
            "headers": self.headers,
            "sources": self.sources,
            "uis": self.uis,
            "resources": self.resources,
            "definitions": self.definitions,
            "includes": self.includes,
            "precompile_headers": self.precompile_headers,
            "dynamic_definition": self.dynamic_definition,
        }


class PackageScanner:
    def __init__(self, package_path, resolve_data=None):
        self.package_path = os.path.normpath(package_path)
        self.resolve = resolve_data or {}

    def scan(self):
        result = ScanResult()
        root_paths = self._resolve_roots()
        ignore_patterns = self._normalize_list(self.resolve.get("ignore"))
        file_filter = self._build_filter(root_paths, ignore_patterns)

        result.headers = self._get_files("headers", HEADER_SUFFIXES, root_paths, file_filter)
        result.sources = self._get_files("sources", SOURCE_SUFFIXES, root_paths, file_filter)
        result.uis = self._get_files("uis", UI_SUFFIXES, root_paths, file_filter)
        result.resources = self._get_files("resources", RESOURCE_SUFFIXES, root_paths, file_filter)

        ph = self.resolve.get("precompileHeaders")
        if ph is not None:
            result.precompile_headers = [self._resolve_path(p) for p in self._normalize_list(ph)]

        defs = self.resolve.get("definitions")
        if defs is not None:
            result.definitions = self._normalize_list(defs)

        result.includes = self._resolve_includes(root_paths)
        result.dynamic_definition = self._normalize_list(self.resolve.get("dynamicDefinition"))

        self._to_relative(result, self.package_path)
        return result

    def _resolve_roots(self):
        root_raw = self.resolve.get("root", [])
        if not root_raw:
            return [self.package_path]
        if isinstance(root_raw, str):
            root_raw = [root_raw]
        return [self._resolve_path(r) for r in root_raw]

    def _build_filter(self, root_paths, ignore_patterns):
        f = FileFilter()
        if ignore_patterns:
            f.add_rule(GitignoreRule(ignore_patterns))
        return f

    def _get_files(self, category_key, suffixes, root_paths, file_filter):
        explicit = self.resolve.get(category_key)
        if explicit is not None:
            return self._resolve_explicit(self._normalize_list(explicit), root_paths)
        scanned = self._scan_files_in_roots(root_paths, suffixes)
        return file_filter.apply(scanned, root_paths)

    def _resolve_explicit(self, items, root_paths):
        resolved = []
        for item in items:
            found = False
            for root in root_paths:
                candidate = self._resolve_path(item, root)
                if os.path.exists(candidate):
                    resolved.append(candidate)
                    found = True
                    break
            if not found:
                resolved.append(self._resolve_path(item))
        return resolved

    def _scan_files_in_roots(self, roots, suffixes):
        result = []
        for root_dir in roots:
            if not os.path.isdir(root_dir):
                continue
            for walk_root, dirs, files in os.walk(root_dir):
                dirs[:] = [d for d in dirs if d != ".git"]
                for file in files:
                    if file.lower().endswith(suffixes):
                        result.append(os.path.join(walk_root, file))
        return result

    def _resolve_includes(self, root_paths):
        explicit = self.resolve.get("includePaths")
        if explicit is not None:
            return [self._resolve_path(p) for p in self._normalize_list(explicit)]
        if self.resolve.get("root"):
            return list(root_paths)
        return [self.package_path]

    def _resolve_path(self, relative, base_path=None):
        if base_path is None:
            base_path = self.package_path
        if os.path.isabs(relative):
            return os.path.normpath(relative)
        return os.path.normpath(os.path.join(base_path, relative))

    @staticmethod
    def _normalize_list(value):
        if value is None:
            return []
        if isinstance(value, str):
            return [value]
        return list(value)

    @staticmethod
    def _to_relative(result, base):
        def rel(paths):
            if not paths:
                return []
            return [os.path.relpath(p, base).replace(os.sep, "/") for p in paths]
        result.headers = rel(result.headers)
        result.sources = rel(result.sources)
        result.uis = rel(result.uis)
        result.resources = rel(result.resources)
        result.precompile_headers = rel(result.precompile_headers)
        result.includes = rel(result.includes)
