from __future__ import annotations

import os
import json
import shutil
import hashlib
import zipfile
import tempfile
import requests
from typing import Any
from datetime import datetime
from packaging.version import Version
from scripts.Utils import Utils
from scripts.data.RefPackage import RefPackage, GitRef
from scripts.data.LibPackage import LibPackage
from scripts.data.LibPackageDownload import LibPackageDownload
from scripts.data.LibPackageDetail import LibPackageDetail
from scripts.data.LibName import LibName
from scripts.data.models import get_session

class AppData:
    def __init__(self, project_path: str, env=None) -> None:
        self.path = project_path
        self.json: dict[str, Any] = {}
        self.env = env

        self.local_lib_store: str = ""

        self.global_origin: str = "default"

        self.packages: list[RefPackage] = []
        self.external_packages: list[RefPackage] = []

        self.cache: dict[str, Any] = {}
        self.cache_path: str = ""

        self._loadConfig()
        self._parseOrigin()
        self._parseLocalLibStore()
        self._loadCache()

        self._parseRefPackages()
        self._assembleRefPackages()

    def _loadConfig(self):
        json_path = os.path.join(self.path, "packages.json")
        if not os.path.exists(json_path):
            src = os.path.join(os.getenv("IMAKECORE_ROOT"), ".data", "packages.json")
            shutil.copyfile(src, json_path)

        self.json = Utils.loadJson(json_path)

    def _parseOrigin(self): 
        if "origin" in self.json:
            self.global_origin = self.json["origin"]
        elif self.json.get("forceLocal", False):
            print("WARNING: 'forceLocal' is deprecated, use 'origin: local'")
            self.global_origin = "local"

        if self.global_origin not in ("local", "default"):
            print(f"ERROR: Invalid global origin '{self.global_origin}'. Must be local or default.")
            exit(1)

    def _parseLocalLibStore(self):
        
        self.local_lib_store = self.json.get("localLibStore")
        if self.local_lib_store is None:
            self.local_lib_store = os.path.join(self.path, ".lib")
        elif not os.path.isabs(self.local_lib_store):
            self.local_lib_store = os.path.join(self.path, self.local_lib_store)
        self.local_lib_store = os.path.normpath(self.local_lib_store)

    def _parseRefPackages(self) -> None:
        raw = self.json.get("packages", {})
        if not raw:
            print("ERROR: packages.json does not contain 'packages' field.")
            exit(1)
        for name, value in raw.items():
            ref = RefPackage.from_package_json(name, value, self)
            if not ref.skip:
                self.packages.append(ref)
        
    def _loadCache(self) -> None:
        self.cache_path = os.path.join(self.path, ".data", "resolve-cache.json")
        if not os.path.exists(self.cache_path):
            return
        try:
            self.cache = Utils.loadJson(self.cache_path)
        except Exception:
            self.cache = {}

    def save_cache(self) -> None:
        data: dict[str, Any] = {"version": 1, "last_update": datetime.now().isoformat(), "resolved": {}}
        for ref in self.all_packages():
            if ref.real_package and ref.real_package.success:
                key = f"{ref.real_package.publisher}/{ref.real_package.name}"
                data["resolved"][key] = {
                    "ref_hash": self._compute_ref_hash(ref),
                    "publisher": ref.real_package.publisher,
                    "name": ref.real_package.name,
                    "version": ref.real_package.version,
                    "path": ref.real_package.path,
                }
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def get_cached(self, ref: RefPackage) -> LibPackage | None:
        key = f"{ref.publisher}/{ref.name}"
        entry = self.cache.get("resolved", {}).get(key)
        if not entry:
            return None
        if entry.get("ref_hash") != self._compute_ref_hash(ref):
            return None
        path = entry.get("path")
        if not path or not os.path.exists(path):
            return None
        return LibPackage.fromFolder(path)

    @staticmethod
    def _compute_ref_hash(ref: RefPackage) -> str:
        raw = json.dumps({"n": ref.name, 
                          "v": ref.version, 
                          "p": ref.publisher,
                            "o": ref.origin, 
                           "path": ref.path, 
                           "url": ref.url,
                           "g": ref.git.url if ref.git else None,
                           "r": ref.resolve}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def all_packages(self) -> list[RefPackage]:
        return self.packages + self.external_packages

    # ── Assemble: resolve suggestCandidate / forceCandidate ──────────────

    def _assembleRefPackages(self) -> None:
        for ref in self.packages:
            self._assemble_one(ref)

    def _assemble_one(self, ref: RefPackage) -> None:
        # Cache match → suggestCandidate
        cached = self.get_cached(ref)
        if cached is not None:
            from scripts.provider.ResolveLibProvider import Candidate
            ref.suggestCandidate = Candidate(cached)

        # Path → forceCandidate
        if ref.path:
            ref.forceCandidate = self._assemble_path(ref)
            return

        # URL → forceCandidate
        if ref.url:
            ref.forceCandidate = self._assemble_url(ref)
            return

        # Git → forceCandidate
        if ref.git:
            ref.forceCandidate = self._assemble_git(ref)

    # ── Path assembly ────────────────────────────────────────────────────

    def _assemble_path(self, ref: RefPackage):
        path = self._resolve_path(ref)
        if not path:
            print(f"ERROR: Package '{ref.name}' path '{ref.path}' is empty or does not exist.")
            exit(1)
        lp = LibPackage.fromFolder(path)
        if not lp.success:
            print(f"ERROR: Failed to load package '{ref.name}' from '{path}'.")
            exit(1)
        if not lp.isMatch(ref):
            print(f"ERROR: Package at '{path}' does not match '{ref.name}' version {ref.version}.")
            exit(1)
        from scripts.provider.ResolveLibProvider import Candidate
        return Candidate(lp)

    def _resolve_path(self, ref: RefPackage) -> str | None:
        if not ref.path or not ref.path.strip():
            return None
        if os.path.isabs(ref.path):
            resolved = os.path.normpath(ref.path)
        else:
            resolved = os.path.normpath(os.path.join(self.path, ref.path))
        if not os.path.exists(resolved) or not os.path.isdir(resolved):
            return None
        return resolved

    # ── URL / Git download ───────────────────────────────────────────────

    def _assemble_url(self, ref: RefPackage):
        return self._assemble_download(ref, ref.url)

    def _assemble_git(self, ref: RefPackage):
        git_info = f"git:{ref.git.url}"
        if ref.git.tag:
            git_info += f" tag={ref.git.tag}"
        elif ref.git.branch:
            git_info += f" branch={ref.git.branch}"
        elif ref.git.hash:
            git_info += f" hash={ref.git.hash}"
        return self._assemble_download(ref, [git_info], is_git=True)

    def _assemble_download(self, ref: RefPackage, sources: list[str],
                           is_git: bool = False):
        # Check for existing successful download
        session = get_session()
        try:
            for src in sources:
                existing = (session.query(LibPackageDownload)
                            .filter(LibPackageDownload.path_info == src)
                            .first())
                if existing and existing.success:
                    ver = Version(existing.version)
                    if ref.version_range.contains(ver):
                        lp = LibPackage.fromFolder(existing.target)
                        if lp.success:
                            from scripts.provider.ResolveLibProvider import Candidate
                            return Candidate(lp)

            # No existing download → download now
            target_dir = self._compute_download_target(ref)
            if not target_dir:
                print(f"ERROR: Could not determine target directory for '{ref.name}'.")
                exit(1)

            # Insert tracking record
            for src in sources:
                dl = LibPackageDownload(
                    path_info=src, success=False, target="",
                    name=ref.name, publisher=ref.publisher, version=ref.version,
                )
                session.add(dl)
            session.commit()

            # Download and extract
            downloaded = False
            cache_dir = self.env.sysCachePath if self.env else os.path.join(
                os.getenv("IMAKECORE_ROOT", ""), ".cache")
            os.makedirs(cache_dir, exist_ok=True)

            for src in sources:
                if self._download_single(src, cache_dir, target_dir, ref, is_git, session):
                    downloaded = True
                    break

            if not downloaded:
                print(f"ERROR: Failed to download package '{ref.name}' from all sources.")
                exit(1)

            # Build LibPackage from target
            from scripts.provider.ResolveLibProvider import Candidate
            lp = LibPackage.fromFolder(target_dir)
            if not lp.success:
                print(f"ERROR: Downloaded package '{ref.name}' is invalid.")
                exit(1)

            return Candidate(lp)
        finally:
            session.close()

    def _download_single(self, src: str, cache_dir: str, target_dir: str,
                         ref: RefPackage, is_git: bool, session) -> bool:
        """Download from a single source. Returns True on success."""
        import time

        if is_git:
            return self._download_git_source(src, target_dir, ref, session)

        # URL download
        cache_file = os.path.join(cache_dir,
                                  f"{ref.name}_{int(time.time())}.zip")
        try:
            # Download
            r = requests.get(src, timeout=60)
            if r.status_code != 200:
                return False
            with open(cache_file, "wb") as f:
                f.write(r.content)

            # Extract to temp, then move
            with tempfile.TemporaryDirectory() as tmpdir:
                with zipfile.ZipFile(cache_file, 'r') as zf:
                    zf.extractall(tmpdir)
                self._move_extracted(tmpdir, target_dir, ref, src, session)
            return True
        except Exception:
            return False
        finally:
            if os.path.exists(cache_file):
                os.remove(cache_file)

    def _download_git_source(self, src: str, target_dir: str,
                             ref: RefPackage, session) -> bool:
        """Git clone source. Returns True on success."""
        import subprocess
        try:
            # Parse git info from src string
            # Format: "git:<url> tag=<tag>" or "git:<url> branch=<branch>"
            git_url = ref.git.url
            os.makedirs(target_dir, exist_ok=True)

            # git clone
            cmd = ["git", "clone", "--depth", "1"]
            if ref.git.branch:
                cmd += ["--branch", ref.git.branch]
            cmd += [git_url, target_dir]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if result.returncode != 0:
                print(f"ERROR: git clone failed: {result.stderr}")
                return False

            if ref.git.tag:
                result = subprocess.run(
                    ["git", "checkout", ref.git.tag],
                    cwd=target_dir, capture_output=True, text=True, timeout=30)
                if result.returncode != 0:
                    print(f"ERROR: git checkout tag failed: {result.stderr}")
                    return False

            # Update download record
            self._update_download_record(src, target_dir, ref, session)
            return True
        except Exception:
            return False

    def _move_extracted(self, tmpdir: str, target_dir: str,
                        ref: RefPackage, src: str, session) -> None:
        """Move extracted files to target, handling nested dirs."""
        # Find the actual package root (might be nested one level)
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

        # Read package.json to determine target name
        pkg_json_path = os.path.join(src_dir, "package.json")
        if not os.path.exists(pkg_json_path):
            print(f"ERROR: Downloaded content does not contain package.json.")
            exit(1)

        pkg_data = Utils.loadJson(pkg_json_path)
        publisher = pkg_data.get("publisher", ref.publisher or "local")
        name = pkg_data.get("name", ref.name)
        version = pkg_data.get("version", ref.version)

        if not name or not version:
            print(f"ERROR: Invalid package.json in downloaded content.")
            exit(1)

        # Determine target directory
        dir_name = f"{publisher}@{name}@{version}"
        sys_lib = (self.env.sysLibStore if self.env
                   else os.path.join(os.getenv("IMAKECORE_ROOT", ""), ".lib"))
        final_target = os.path.join(sys_lib, dir_name)

        # Copy to target
        if os.path.exists(final_target):
            shutil.rmtree(final_target)
        shutil.copytree(src_dir, final_target)
        os.makedirs(final_target, exist_ok=True)

        # Register in DB
        self._register_in_db(publisher, name, version, final_target)

        # Update download record
        self._update_download_record(src, final_target, ref, session)

    def _register_in_db(self, publisher: str, name: str,
                        version: str, path: str) -> None:
        """Register the downloaded package in LibPackage + LibPackageDetail DB."""
        from scripts.data.models import get_engine
        from scripts.data.LibPackage import LibPackage as LP
        from scripts.data.LibPackageDetail import LibPackageDetail as LPD

        pkg_json_path = os.path.join(path, "package.json")
        if not os.path.exists(pkg_json_path):
            return

        pkg_data = Utils.loadJson(pkg_json_path)
        session_db = get_session()
        try:
            # Check if already registered
            existing = (session_db.query(LP)
                        .filter(LP.publisher == publisher, LP.name == name,
                                LP.version == version)
                        .first())
            if existing:
                session_db.close()
                return

            # Register LibPackage
            lp = LP(
                publisher=publisher, name=name, version=version,
                path=os.path.normpath(path), content=pkg_data,
                is_global=True, summary=pkg_data.get("summary", ""),
                mode=pkg_data.get("mode", "sources"),
            )
            session_db.add(lp)

            # Register LibPackageDetail (scan files)
            detail = LPD.from_(path)
            if detail is not None:
                session_db.add(detail)

            session_db.commit()
        finally:
            session_db.close()

    def _update_download_record(self, path_info: str, target: str,
                                ref: RefPackage, session) -> None:
        """Update LibPackageDownload record with success info."""
        dl = (session.query(LibPackageDownload)
              .filter(LibPackageDownload.path_info == path_info)
              .first())
        if dl:
            dl.success = True
            dl.target = target
            dl.name = ref.name
            dl.publisher = ref.publisher
            dl.version = ref.version
            session.commit()

    def _compute_download_target(self, ref: RefPackage) -> str | None:
        """Compute target directory for downloaded package."""
        publisher = ref.publisher or "local"
        ver = ref.version if ref.version not in ("*", "latest", "default", "") else "default"
        dir_name = f"{publisher}@{ref.name}@{ver}"
        base = (self.env.sysLibStore if self.env
                else os.path.join(os.getenv("IMAKECORE_ROOT", ""), ".lib"))
        return os.path.join(base, dir_name)
