from packaging.specifiers import SpecifierSet
from scripts.Utils import Utils

VALID_MODES = {"source", "static", "dynamic", "default"}


class GitRef:
    def __init__(self, url, tag=None, branch=None, hash=None):
        self.url = url
        self.tag = tag
        self.branch = branch
        self.hash = hash


class RefPackage:
    def __init__(self):
        self.name = ""
        self.publisher = ""
        self.is_global = True
        self.version = "*"
        self.version_range = SpecifierSet(">=0")
        self.path = None
        self.url = None
        self.git = None
        self.origin = "default"
        self.mode = "default"
        self.resolve = None
        self.real_package = None
        self.skip = False
        self._is_external = False

    @classmethod
    def from_package_json(cls, name, value, app_data):
        from scripts.data.LibPackage import LibPackage
        publisher, pkg_name, is_global = LibPackage.split_name(name)

        if isinstance(value, str):
            return cls._from_string_impl(pkg_name, value, app_data.global_origin,
                                         publisher, is_global)
        if isinstance(value, dict):
            return cls._from_config_impl(pkg_name, value, app_data.global_origin,
                                         publisher, is_global)
        print(f"ERROR: Invalid package value for '{name}': type {type(value).__name__}.")
        exit(1)

    @classmethod
    def _from_string_impl(cls, name, version, origin, publisher, is_global):
        version = version.strip()
        ref = cls()
        ref.name = name
        ref.publisher = publisher
        ref.is_global = is_global
        ref.version = version
        ref.version_range = Utils.parseVersionSpecifier(version)
        ref.origin = origin
        ref.mode = "default"
        if version == "x":
            ref.skip = True
        return ref

    @classmethod
    def _from_config_impl(cls, name, config, global_origin, publisher, is_global):
        version = config.get("version", "*").strip()
        ref = cls()
        ref.name = name
        ref.version = version
        ref.version_range = Utils.parseVersionSpecifier(version)
        if version == "x":
            ref.skip = True
            return ref

        ref.publisher = config.get("publisher", publisher)
        ref.is_global = config.get("isGlobal", is_global)

        if "origin" in config:
            ref.origin = config["origin"]
            if ref.origin not in ("local", "system", "default"):
                print(f"ERROR: Package '{name}' has invalid origin '{ref.origin}'.")
                exit(1)
        else:
            ref.origin = global_origin

        has_path = "path" in config
        has_url = "url" in config
        has_git = "git" in config
        if sum([has_path, has_url, has_git]) > 1:
            print(f"ERROR: Package '{name}': path, url, and git are mutually exclusive.")
            exit(1)

        if has_path:
            ref.path = config["path"]

        if has_url:
            raw = config["url"]
            if isinstance(raw, str):
                ref.url = [raw]
            elif isinstance(raw, list) and all(isinstance(u, str) for u in raw):
                ref.url = raw
            else:
                print(f"ERROR: Package '{name}' url must be string or list of strings.")
                exit(1)

        if has_git:
            ref.git = cls._parse_git(config["git"], name)

        if "resolve" in config:
            ref.resolve = config["resolve"]

        ref.mode = config.get("mode", "default")
        if ref.mode not in VALID_MODES:
            print(f"ERROR: Package '{name}' has invalid mode '{ref.mode}'."
                  f" Must be one of: {', '.join(sorted(VALID_MODES))}.")
            exit(1)
        return ref

    @staticmethod
    def _parse_git(git_val, name):
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
