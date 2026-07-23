from __future__ import annotations

import os
import shutil
import zipfile
import tempfile
import time
from typing import Any
from packaging.version import Version as PkgVersion
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
        self.real_package: Any = None
        self.skip: bool = False
        self._is_external: bool = False

        self.config: dict[str, Any] | None = None

        self.suggestCandidate: Any = None
        self.forceCandidate: Any = None

    # ── Properties ───────────────────────────────────────────────────────

    @property
    def name(self) -> str:
        return self.lib_name.name

    @property
    def publisher(self) -> str:
        return self.lib_name.publisher

    @property
    def is_global(self) -> bool:
        return self.lib_name.is_global

    @property
    def version(self) -> str:
        return self._version

    @version.setter
    def version(self, value: str) -> None:
        self._version = value

    # ── Factory: from packages.json ──────────────────────────────────────

    @classmethod
    def from_package_json(cls, name: str, value: str | dict[str, Any], app_data: Any) -> RefPackage:
        # Step 1: split name
        if "/" in name:
            parts = name.split("/", 1)
            init_publisher = parts[0].strip()
            pkg_name = parts[1].strip()
            is_global = False
        else:
            init_publisher = ""
            pkg_name = name.strip()
            is_global = True

        if isinstance(value, str):
            return cls._from_string_entry(pkg_name, value, app_data, init_publisher, is_global)

        if isinstance(value, dict):
            return cls._from_dict_entry(pkg_name, value, app_data, init_publisher, is_global)

        print(f"ERROR: Invalid package value for '{name}': type {type(value).__name__}.")
        exit(1)

    # ── String entry ─────────────────────────────────────────────────────

    @classmethod
    def _from_string_entry(cls, pkg_name: str, version: str, app_data: Any,
                           init_publisher: str, is_global: bool) -> RefPackage:
        version = version.strip()
        ref = cls()
        ref._version = version
        ref.version_range = Utils.parseVersionSpecifier(version)
        ref.origin = app_data.global_origin
        ref.mode = "default"
        if version == "x":
            ref.skip = True
            return ref

        publisher = init_publisher
        if not publisher:
            publisher = cls._resolve_publisher(pkg_name, app_data)
        ref.lib_name = LibName(pkg_name, publisher=publisher, is_global=is_global)
        return ref

    # ── Dict entry ───────────────────────────────────────────────────────

    @classmethod
    def _from_dict_entry(cls, pkg_name: str, config: dict[str, Any], app_data: Any,
                         init_publisher: str, is_global: bool) -> RefPackage:
        version = config.get("version", "*").strip()
        ref = cls()
        ref._version = version
        ref.version_range = Utils.parseVersionSpecifier(version)
        ref.config = config

        if version == "x":
            ref.skip = True
            return ref

        # Parse basic fields
        pub = config.get("publisher", init_publisher)
        ig = config.get("isGlobal", is_global)
        ref.lib_name = LibName(pkg_name, publisher=pub, is_global=ig)

        if "origin" in config:
            ref.origin = config["origin"]
            if ref.origin not in ("local", "default"):
                print(f"ERROR: Package '{pkg_name}' has invalid origin '{ref.origin}'.")
                exit(1)
        else:
            ref.origin = app_data.global_origin

        if "resolve" in config:
            ref.resolve = config["resolve"]

        ref.mode = config.get("mode", "default")
        if ref.mode not in VALID_MODES:
            print(f"ERROR: Package '{pkg_name}' has invalid mode '{ref.mode}'."
                  f" Must be one of: {', '.join(sorted(VALID_MODES))}.")
            exit(1)

        has_path = "path" in config
        has_url = "url" in config
        has_git = "git" in config
        if sum([has_path, has_url, has_git]) > 1:
            print(f"ERROR: Package '{pkg_name}': url and git are mutually exclusive.")
            exit(1)

        if has_path:
            ref.path = config["path"]

        if has_url:
            ref.url = cls._parse_url(config["url"], pkg_name)

        if has_git:
            ref.git = cls._parse_git(config["git"], pkg_name)

        # Execute path/url/git resolution NOW (before publisher lookup)
        # This ensures the package is registered so publisher can be found
        cls._execute_assemble(ref, app_data)

        # Now resolve publisher if missing (package is registered now)
        if not ref.lib_name.publisher:
            publisher = cls._resolve_publisher(pkg_name, app_data)
            ref.lib_name = LibName(pkg_name, publisher=publisher,
                                   is_global=ref.lib_name.is_global)

        return ref

    # ── Execute assemble (path / url / git) ──────────────────────────────

    @classmethod
    def _execute_assemble(cls, ref: RefPackage, app_data: Any) -> None:
        """Execute download/path resolution so the package is registered."""
        if ref.path:
            cls._assemble_path(ref, app_data)
        elif ref.url:
            cls._assemble_url(ref, app_data)
        elif ref.git:
            cls._assemble_git(ref, app_data)

    @classmethod
    def _assemble_path(cls, ref: RefPackage, app_data: Any) -> None:
        from scripts.data.LibPackage import LibPackage
        from scripts.provider.ResolveLibProvider import Candidate

        resolved = cls._resolve_ref_path(ref.path, app_data.path)
        if not resolved:
            print(f"ERROR: Package '{ref.name}' path '{ref.path}' does not exist.")
            exit(1)
        lp = LibPackage.fromFolder(resolved)
        if not lp.success:
            print(f"ERROR: Failed to load package '{ref.name}' from '{resolved}'.")
            exit(1)
        if not lp.isMatch(ref):
            print(f"ERROR: Package at '{resolved}' does not match '{ref.name}'"
                  f" version {ref.version}.")
            exit(1)
        ref.forceCandidate = Candidate(lp)
        ref.real_package = lp

    @classmethod
    def _assemble_url(cls, ref: RefPackage, app_data: Any) -> None:
        cls._assemble_download(ref, app_data, ref.url, is_git=False)

    @classmethod
    def _assemble_git(cls, ref: RefPackage, app_data: Any) -> None:
        git_info = f"git:{ref.git.url}"
        if ref.git.tag:
            git_info += f" tag={ref.git.tag}"
        elif ref.git.branch:
            git_info += f" branch={ref.git.branch}"
        elif ref.git.hash:
            git_info += f" hash={ref.git.hash}"
        cls._assemble_download(ref, app_data, [git_info], is_git=True)

    @classmethod
    def _assemble_download(cls, ref: RefPackage, app_data: Any,
                           sources: list[str], is_git: bool) -> None:
        import requests
        from scripts.data.models import get_session
        from scripts.data.LibPackageDownload import LibPackageDownload
        from scripts.data.LibPackage import LibPackage
        from scripts.provider.ResolveLibProvider import Candidate

        env = app_data.env
        session = get_session()
        try:
            # Check existing successful download
            for src in sources:
                existing = (session.query(LibPackageDownload)
                            .filter(LibPackageDownload.path_info == src)
                            .first())
                if existing and existing.success:
                    ver = PkgVersion(existing.version)
                    if ref.version_range.contains(ver):
                        lp = LibPackage.fromFolder(existing.target)
                        if lp.success:
                            ref.forceCandidate = Candidate(lp)
                            ref.real_package = lp
                            return

            # Compute target
            publisher = ref.publisher or "local"
            ver = ref.version if ref.version not in ("*", "latest", "default", "") else "default"
            dir_name = f"{publisher}@{ref.name}@{ver}"
            sys_lib = env.sysLibStore if env else os.path.join(
                os.getenv("IMAKECORE_ROOT", ""), ".lib")
            target_dir = os.path.join(sys_lib, dir_name)

            # Insert tracking records
            for src in sources:
                dl = LibPackageDownload(
                    path_info=src, success=False, target="",
                    name=ref.name, publisher=ref.publisher, version=ref.version,
                )
                session.add(dl)
            session.commit()

            # Download
            cache_dir = env.sysCachePath if env else os.path.join(
                os.getenv("IMAKECORE_ROOT", ""), ".cache")
            os.makedirs(cache_dir, exist_ok=True)

            downloaded = False
            for src in sources:
                if cls._download_single(src, cache_dir, target_dir, ref, is_git, session, env):
                    downloaded = True
                    break

            if not downloaded:
                print(f"ERROR: Failed to download package '{ref.name}' from all sources.")
                exit(1)

            lp = LibPackage.fromFolder(target_dir)
            if not lp.success:
                print(f"ERROR: Downloaded package '{ref.name}' is invalid.")
                exit(1)

            ref.forceCandidate = Candidate(lp)
            ref.real_package = lp
        finally:
            session.close()

    @classmethod
    def _download_single(cls, src: str, cache_dir: str, target_dir: str,
                         ref: RefPackage, is_git: bool, session, env) -> bool:
        import requests
        from scripts.data.LibPackageDownload import LibPackageDownload

        if is_git:
            return cls._download_git_src(ref, target_dir, session)

        cache_file = os.path.join(cache_dir, f"{ref.name}_{int(time.time())}.zip")
        try:
            r = requests.get(src, timeout=60)
            if r.status_code != 200:
                return False
            with open(cache_file, "wb") as f:
                f.write(r.content)

            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(cache_file, 'r') as zf:
                    zf.extractall(tmpdir)
                cls._move_and_register(tmpdir, target_dir, ref, src, session, env)
            return True
        except Exception:
            return False
        finally:
            if os.path.exists(cache_file):
                os.remove(cache_file)

    @classmethod
    def _download_git_src(cls, ref: RefPackage, target_dir: str, session) -> bool:
        import subprocess
        from scripts.data.LibPackageDownload import LibPackageDownload
        try:
            os.makedirs(target_dir, exist_ok=True)
            cmd = ["git", "clone", "--depth", "1"]
            if ref.git.branch:
                cmd += ["--branch", ref.git.branch]
            cmd += [ref.git.url, target_dir]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                return False
            if ref.git.tag:
                result = subprocess.run(["git", "checkout", ref.git.tag],
                                        cwd=target_dir, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    return False
            cls._update_dl_record(src=f"git:{ref.git.url}", target=target_dir, ref=ref, session=session)
            return True
        except Exception:
            return False

    @classmethod
    def _move_and_register(cls, tmpdir: str, target_dir: str, ref: RefPackage,
                           src: str, session, env) -> None:
        """Move extracted content and register in DB."""
        from scripts.data.LibPackageDownload import LibPackageDownload

        entries = os.listdir(tmpdir)
        if len(entries) == 1:
            candidate = os.path.join(tmpdir, entries[0])
            if os.path.isdir(candidate) and os.path.exists(
                    os.path.join(candidate, "package.json")):
                src_dir = candidate
            else:
                src_dir = tmpdir
        else:
            src_dir = tmpdir

        pkg_json_path = os.path.join(src_dir, "package.json")
        if not os.path.exists(pkg_json_path):
            print("ERROR: Downloaded content does not contain package.json.")
            exit(1)

        pkg_data = Utils.loadJson(pkg_json_path)
        publisher = pkg_data.get("publisher", ref.publisher or "local")
        name = pkg_data.get("name", ref.name)
        version = pkg_data.get("version", ref.version)

        if not name or not version:
            print("ERROR: Invalid package.json in downloaded content.")
            exit(1)

        dir_name = f"{publisher}@{name}@{version}"
        sys_lib = env.sysLibStore if env else os.path.join(
            os.getenv("IMAKECORE_ROOT", ""), ".lib")
        final_target = os.path.join(sys_lib, dir_name)
        if os.path.exists(final_target):
            shutil.rmtree(final_target)
        shutil.copytree(src_dir, final_target)

        cls._register_in_db(publisher, name, version, final_target, pkg_data)
        cls._update_dl_record(src=src, target=final_target, ref=ref, session=session)

    @classmethod
    def _register_in_db(cls, publisher: str, name: str, version: str,
                        path: str, pkg_data: dict[str, Any]) -> None:
        from scripts.data.models import get_session
        from scripts.data.LibPackage import LibPackage
        from scripts.data.LibPackageDetail import LibPackageDetail

        session_db = get_session()
        try:
            existing = (session_db.query(LibPackage)
                        .filter(LibPackage.publisher == publisher,
                                LibPackage.name == name,
                                LibPackage.version == version)
                        .first())
            if not existing:
                lp = LibPackage(
                    publisher=publisher, name=name, version=version,
                    path=os.path.normpath(path), content=pkg_data,
                    is_global=True, summary=pkg_data.get("summary", ""),
                    mode=pkg_data.get("mode", "sources"),
                )
                session_db.add(lp)
                detail = LibPackageDetail.from_(path)
                if detail is not None:
                    session_db.add(detail)
                session_db.commit()
        finally:
            session_db.close()

    @classmethod
    def _update_dl_record(cls, src: str, target: str, ref: RefPackage, session) -> None:
        from scripts.data.LibPackageDownload import LibPackageDownload
        dl = (session.query(LibPackageDownload)
              .filter(LibPackageDownload.path_info == src)
              .first())
        if dl:
            dl.success = True
            dl.target = target
            dl.name = ref.name
            dl.publisher = ref.publisher
            dl.version = ref.version
            session.commit()

    # ── Publisher resolution ─────────────────────────────────────────────

    @staticmethod
    def _resolve_publisher(pkg_name: str, app_data: Any) -> str:
        """Query LibProviderManager for the publisher of a package name.
        Errors out if not found."""
        if not app_data or not app_data.env:
            print(f"ERROR: Cannot resolve publisher for '{pkg_name}'"
                  f" — no provider manager available.")
            exit(1)
        mgr = app_data.env.getProviderManager()
        temp = LibName(pkg_name)
        real = mgr.findRealLibName(temp)
        if real is None:
            print(f"ERROR: Cannot resolve publisher for package '{pkg_name}'."
                  f" The package cannot be found.")
            exit(1)
        return real.publisher

    # ── Path helpers ─────────────────────────────────────────────────────

    @staticmethod
    def _resolve_ref_path(path: str, base_path: str) -> str | None:
        if not path or not path.strip():
            return None
        if os.path.isabs(path):
            resolved = os.path.normpath(path)
        else:
            resolved = os.path.normpath(os.path.join(base_path, path))
        if not os.path.exists(resolved) or not os.path.isdir(resolved):
            return None
        return resolved

    # ── Parse helpers ────────────────────────────────────────────────────

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
