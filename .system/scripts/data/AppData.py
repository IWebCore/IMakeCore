from __future__ import annotations

import os
import json
import shutil
import hashlib
from typing import Any
from datetime import datetime
from scripts.Utils import Utils
from scripts.data.RefPackage import RefPackage
from scripts.data.LibPackage import LibPackage


class AppData:
    def __init__(self, project_path: str) -> None:
        self.path = project_path
        self.json: dict[str, Any] = {}
        self.local_lib_store: str = ""
        self.global_origin: str = "default"
        self.packages: list[RefPackage] = []
        self.external_packages: list[RefPackage] = []
        self.cache: dict[str, Any] = {}
        self.cache_path: str = ""

        json_path = os.path.join(self.path, "packages.json")
        if not os.path.exists(json_path):
            src = os.path.join(os.getenv("IMAKECORE_ROOT"), ".data", "packages.json")
            shutil.copyfile(src, json_path)

        self.json = Utils.loadJson(json_path)

        if "origin" in self.json:
            self.global_origin = self.json["origin"]
        elif self.json.get("forceLocal", False):
            print("WARNING: 'forceLocal' is deprecated, use 'origin: local'")
            self.global_origin = "local"

        if self.global_origin not in ("local", "system", "default"):
            print(f"ERROR: Invalid global origin '{self.global_origin}'. Must be local, system, or default.")
            exit(1)

        self.local_lib_store = self.json.get("localLibStore")
        if self.local_lib_store is None:
            self.local_lib_store = os.path.join(self.path, ".lib")
        elif not os.path.isabs(self.local_lib_store):
            self.local_lib_store = os.path.join(self.path, self.local_lib_store)
        self.local_lib_store = os.path.normpath(self.local_lib_store)

        self._parse_packages()

        self.cache_path = os.path.join(self.path, ".data", "resolve-cache.json")
        self._load_cache()

    def all_packages(self) -> list[RefPackage]:
        return self.packages + self.external_packages

    def _parse_packages(self) -> None:
        raw = self.json.get("packages", {})
        if not raw:
            print("ERROR: packages.json does not contain 'packages' field.")
            exit(1)
        for name, value in raw.items():
            ref = self._parse_one(name, value)
            if ref is not None:
                self.packages.append(ref)

    def _parse_one(self, name: str, value: str | dict[str, Any]) -> RefPackage | None:
        ref = RefPackage.from_package_json(name, value, self)
        return ref if not ref.skip else None

    def _load_cache(self) -> None:
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
        return LibPackage(path)

    @staticmethod
    def _compute_ref_hash(ref: RefPackage) -> str:
        raw = json.dumps({"n": ref.name, "v": ref.version, "p": ref.publisher,
                           "o": ref.origin, "path": ref.path, "url": ref.url,
                           "g": ref.git.url if ref.git else None,
                           "r": ref.resolve}, sort_keys=True)
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
