"""
CompileInfo.py — Captures compile-time environment from qmake/cmake.

Populated from environment variables set by .IMakeCore.prf / .IMakeCore.cmake
before invoking IMakeCore.py.
"""
from __future__ import annotations

import os
from typing import Any


class CompileInfo:
    """Compile-time context passed from the build system to IMakeCore."""

    _instance: CompileInfo | None = None

    def __init__(self) -> None:
        self.executable_path: str = ""
        self.target_type: str = "executable"
        self.platform: str = ""
        self.arch: str = ""
        self.compiler: str = ""
        self.compiler_version: str = ""
        self.build_mode: str = "debug"
        self.runtimes: str = ""
        self.cpp_std: str = ""
        self.exception_enabled: bool = True
        self.rtti_enabled: bool = True

    @classmethod
    def init(cls) -> CompileInfo:
        """Read compile info from environment variables and initialize the singleton."""
        info = cls.instance()
        info.executable_path = os.getenv("IMAKECORE_EXECUTABLE_PATH", "").strip()
        info.target_type = os.getenv("IMAKECORE_TARGET_TYPE", "executable").strip()
        info.platform = os.getenv("IMAKECORE_PLATFORM", "").strip()
        info.arch = os.getenv("IMAKECORE_ARCH", "").strip()
        info.compiler = os.getenv("IMAKECORE_COMPILER", "").strip()
        info.compiler_version = os.getenv("IMAKECORE_COMPILER_VERSION", "").strip()
        info.build_mode = os.getenv("IMAKECORE_BUILD_MODE", "debug").strip()
        info.runtimes = os.getenv("IMAKECORE_RUNTIMES", "").strip()
        info.cpp_std = os.getenv("IMAKECORE_CPP_STD", "").strip()
        info.exception_enabled = os.getenv("IMAKECORE_EXCEPTION_ENABLED", "1").strip() == "1"
        info.rtti_enabled = os.getenv("IMAKECORE_RTTI_ENABLED", "1").strip() == "1"
        return info

    @classmethod
    def instance(cls) -> CompileInfo:
        """Return the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def to_dict(self) -> dict[str, Any]:
        return {
            "executable_path": self.executable_path,
            "target_type": self.target_type,
            "platform": self.platform,
            "arch": self.arch,
            "compiler": self.compiler,
            "compiler_version": self.compiler_version,
            "build_mode": self.build_mode,
            "runtimes": self.runtimes,
            "cpp_std": self.cpp_std,
            "exception_enabled": self.exception_enabled,
            "rtti_enabled": self.rtti_enabled,
        }

    def __repr__(self) -> str:
        return f"<CompileInfo platform={self.platform} compiler={self.compiler} mode={self.build_mode}>"
