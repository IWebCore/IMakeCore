from __future__ import annotations

from typing import Any
from packaging.specifiers import SpecifierSet
from scripts.Utils import Utils
from scripts.data.LibName import LibName

VALID_MODES: set[str] = {"source", "static", "dynamic", "default"}


class GitRef:
    def __init__(self, url: str, tag: str | None = None, branch: str | None = None, hash: str | None = None) -> None:
        self.url = url
        self.tag = tag
        self.branch = branch
        self.hash = hash


class RefPackage:
    def __init__(self) -> None:
        self.lib_name: LibName = LibName()

        self._version: str = "*"
        self.version_range: SpecifierSet = SpecifierSet(">=0")

        self.path: str | None = None
        self.url: list[str] | None = None
        self.git: GitRef | None = None
        self.origin: str = "default"
        self.mode: str = "default"
        self.resolve: dict[str, Any] | None = None
        self.real_package: Any = None  # LibPackage, deferred import
        self.skip: bool = False
        self._is_external: bool = False

        self.config: dict[str, Any] | None = None

    # ── Read-only properties delegating to lib_name ──────────────────────

    @property
    def name(self) -> str:
        return self.lib_name.name

    @property
    def publisher(self) -> str:
        return self.lib_name.publisher

    @property
    def is_global(self) -> bool:
        return self.lib_name.is_global

    # ── Version property ─────────────────────────────────────────────────

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value

    # ── Factory: from packages.json entry ────────────────────────────────

    @classmethod
    def from_package_json(cls, name: str, value: str | dict[str, Any], app_data: Any) -> RefPackage:
        if "/" in name:
            parts = name.split("/", 1)
            publisher = parts[0].strip()
            pkg_name = parts[1].strip()
            is_global = False
        else:
            publisher = ""
            pkg_name = name.strip()
            is_global = True

        if isinstance(value, str):
            return cls._from_string_impl(pkg_name, value, app_data.global_origin,
                                         publisher, is_global)
        if isinstance(value, dict):
            return cls._from_config_impl(pkg_name, value, app_data.global_origin,
                                         publisher, is_global)
        print(f"ERROR: Invalid package value for '{name}': type {type(value).__name__}.")
        exit(1)

    @classmethod
    def _from_string_impl(cls, name: str, version: str, global_origin: str,
                          publisher: str, is_global: bool) -> RefPackage:
        version = version.strip()
        ref = cls()
        ref.lib_name = LibName(name, publisher=publisher, is_global=is_global)
        ref._version = version
        ref.version_range = Utils.parseVersionSpecifier(version)
        ref.origin = global_origin
        ref.mode = "default"
        if version == "x":
            ref.skip = True
        return ref

    @classmethod
    def _from_config_impl(cls, name: str, config: dict[str, Any], global_origin: str,
                          publisher: str, is_global: bool) -> RefPackage:
        version = config.get("version", "*").strip()
        ref = cls()
        ref._version = version
        ref.version_range = Utils.parseVersionSpecifier(version)
        ref.config = config

        if version == "x":
            ref.skip = True
            return ref

        pub = config.get("publisher", publisher)
        ig = config.get("isGlobal", is_global)
        ref.lib_name = LibName(name, publisher=pub, is_global=ig)

        if "origin" in config:
            ref.origin = config["origin"]
            if ref.origin not in ("local", "default"):
                print(f"ERROR: Package '{name}' has invalid origin '{ref.origin}'.")
                exit(1)
        else:
            ref.origin = global_origin

        if "resolve" in config:
            ref.resolve = config["resolve"]

        ref.mode = config.get("mode", "default")
        if ref.mode not in VALID_MODES:
            print(f"ERROR: Package '{name}' has invalid mode '{ref.mode}'."
                  f" Must be one of: {', '.join(sorted(VALID_MODES))}.")
            exit(1)

        has_path = "path" in config
        has_url = "url" in config
        has_git = "git" in config
        if sum([has_url, has_git]) > 1:
            print(f"ERROR: Package '{name}': url and git are mutually exclusive.")
            exit(1)

        if has_path:
            ref.path = config["path"]

        if has_url:
            ref.url = cls._parse_url(config["url"], name)

        if has_git:
            ref.git = cls._parse_git(config["git"], name)

        return ref

    @staticmethod
    def _parse_git(git_val: str | dict[str, Any], name: str) -> GitRef:
        if isinstance(git_val, str):
            return GitRef(url=git_val)
        if isinstance(git_val, dict):
            url = git_val.get("url")
            if not url:
                print(f"ERROR: Package '{name}' git config missing 'url'.")
                exit(1)
            return GitRef(url=url, tag=git_val.get("tag"),
                          branch=git_val.get("branch"), hash=git_val.get("hash"))
        print(f"ERROR: Package '{name}' git must be string or object with 'url'.")
        exit(1)

    @staticmethod
    def _parse_url(raw: str | list[str], name: str) -> list[str]:
        if isinstance(raw, str):
            return [raw]
        elif isinstance(raw, list) and all(isinstance(u, str) for u in raw):
            return raw
        else:
            print(f"ERROR: Package '{name}' url must be string or list of strings.")
            exit(1)
