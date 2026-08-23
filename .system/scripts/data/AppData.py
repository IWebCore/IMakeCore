from __future__ import annotations

import os
import json
import shutil
import hashlib
from typing import Any
from scripts.Utils import Utils
from scripts.data.RefPackage import RefPackage
from scripts.data.LibPackage import LibPackage
from scripts.data.CompileInfo import CompileInfo

class AppData:
    def __init__(self, project_path: str, env=None) -> None:
        self.path = project_path
        self.env = env
        self.json: dict[str, Any] = self._loadConfig()
        self.global_origin: str = self._parseOrigin()
        self.local_lib_store: str = self._parseLocalLibStore()

        self.cache_path: str = os.path.join(self.path, ".data", "resolve-cache.json")
        self.cache: dict[str, Any] = self._loadCache()

        self.packages: list[RefPackage] = self._loadPackage()

        # CompileInfo.init()
        # self.compile_info: CompileInfo = CompileInfo.instance()
        # print(self.compile_info.to_dict())


    def _loadConfig(self):
        json_path = os.path.join(self.path, "packages.json")
        if not os.path.exists(json_path):
            src = os.path.join(os.getenv("IMAKECORE_ROOT", "").strip(), ".data", "packages.json")
            shutil.copyfile(src, json_path)

        return Utils.loadJson(json_path)


    def _parseLocalLibStore(self):
        local_lib_store = self.json.get("localLibStore")
        if local_lib_store is None:
            local_lib_store = os.path.join(self.path, ".lib")
        elif not os.path.isabs(local_lib_store):
            local_lib_store = os.path.join(self.path, local_lib_store)
        local_lib_store = os.path.normpath(local_lib_store)
        return local_lib_store


    def _parseOrigin(self): 
        global_origin = "default"
        if "origin" in self.json:
            global_origin = self.json["origin"]
        elif self.json.get("forceLocal", False):
            print("WARNING: 'forceLocal' is deprecated, use 'origin: local'")
            global_origin = "local"

        if global_origin not in ("local", "default"):
            print(f"ERROR: Invalid global origin '{global_origin}'. Must be local or default.")
            exit(1)

        return global_origin

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
        if not os.path.exists(self.cache_path):
            return {}
        try:
            return Utils.loadJson(self.cache_path)
        except Exception:
            return {}

    def _loadPackage(self):
        self.packages = []
        self._parseRefPackages()
        self._parseOverride()
        self._assembleRefPackages()
        return self.packages

    def save_cache(self) -> None:
        data: dict[str, Any] = {"version": 1, "resolved": {}}
        for ref in self.packages:
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

    def _parseOverride(self) -> None:
        """Parse global and per-package override versions.

        Global override: { "override": { "pkg/name": "1.0.0" } }
        Per-package override: { "packages": { "pkg/name": { "override": "1.0.0" } } }

        Per-package override takes precedence over global.
        """
        global_override: dict[str, str] = self.json.get("override", {})

        for ref in self.packages:
            key = ref.lib_name.fullName()
            # Per-package override takes priority
            if ref.config and "override" in ref.config:
                ref.overrideVersion = ref.config["override"]
            elif key in global_override:
                ref.overrideVersion = global_override[key]

    def _assembleRefPackages(self) -> None:
        """Match resolve-cache to set suggestCandidate, and handle overrideVersion."""
        for ref in self.packages:
            # Check overrideVersion — pin to specific version
            if ref.overrideVersion and self.env:
                from scripts.provider.ResolveLibProvider import Candidate
                mgr = self.env.getProviderManager()
                pkgs = mgr.findPackages(ref.lib_name)
                for p in pkgs:
                    if p.version == ref.overrideVersion:
                        ref.forceCandidate = Candidate(p)
                        break
                continue

            cached = self.get_cached(ref)
            if cached is not None:
                from scripts.provider.ResolveLibProvider import Candidate
                ref.suggestCandidate = Candidate(cached)
