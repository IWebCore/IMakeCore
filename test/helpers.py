"""
helpers.py — Utility functions for IMakeCore test authoring.

All functions are designed to be used inside pytest test functions
that receive the ``test_env`` and ``test_project`` fixtures from conftest.py.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any


FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


# ── Project configuration ────────────────────────────────────────────────

def write_packages_json(project: Path, packages: dict[str, Any]) -> None:
    """Write a packages.json into the test project directory.

    Args:
        project:  The test_project Path from the fixture.
        packages:  Either a simple dict {"name": "version", ...}
                   or a dict of dicts with full config.
    """
    content = {"packages": packages}
    pkg_path = project / "packages.json"
    pkg_path.write_text(json.dumps(content, indent=2), encoding="utf-8")


def write_project_config(project: Path, config: dict[str, Any]) -> None:
    """Write .data/config.json into the test project directory."""
    cfg_dir = project / ".data"
    cfg_dir.mkdir(exist_ok=True)
    (cfg_dir / "config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )


# ── Run IMakeCore ────────────────────────────────────────────────────────

def run_imakecore(project: Path, pack_type: str = "qmake",
                  imakecore_root: str | None = None) -> subprocess.CompletedProcess:
    """Execute IMakeCore.py in a subprocess with an isolated environment.

    Args:
        project:   The test_project directory.
        pack_type: "qmake" or "cmake".
        imakecore_root:
            Path to the isolated IMAKECORE_ROOT.  If None, reads
            from the current ``IMAKECORE_ROOT`` environment variable
            (set by conftest.py).

    Returns:
        A ``CompletedProcess`` with ``returncode``, ``stdout``, ``stderr``.
    """
    if imakecore_root is None:
        imakecore_root = os.environ.get("IMAKECORE_ROOT", "")
    if not imakecore_root:
        raise RuntimeError("IMAKECORE_ROOT is not set")

    imakecore_py = os.path.join(imakecore_root, ".system", "IMakeCore.py")

    env = os.environ.copy()
    env["IMAKECORE_ROOT"] = imakecore_root

    return subprocess.run(
        [sys.executable, "-B", imakecore_py, str(project), pack_type],
        capture_output=True,
        text=True,
        env=env,
        timeout=120,
    )


def run_update_db(imakecore_root: str) -> subprocess.CompletedProcess:
    """Execute update_db.py in a subprocess (for use outside conftest)."""
    update_py = os.path.join(imakecore_root, ".system", "scripts", "updateDb.py")
    env = os.environ.copy()
    env["IMAKECORE_ROOT"] = imakecore_root
    return subprocess.run(
        [sys.executable, "-B", update_py],
        capture_output=True,
        text=True,
        env=env,
        timeout=60,
    )


# ── Assertions ───────────────────────────────────────────────────────────

def assert_file_exists(path: Path, description: str = "") -> None:
    """Assert a file exists at the given path."""
    assert path.exists(), (
        f"Expected file not found: {path}" + (f" ({description})" if description else "")
    )


def assert_pri_contains(project: Path, text: str) -> None:
    """Assert that .package.pri contains the given text."""
    pri = project / ".package.pri"
    assert pri.exists(), f".package.pri not found in {project}"
    content = pri.read_text(encoding="utf-8")
    assert text in content, (
        f"Expected '{text}' in .package.pri, but not found.\n"
        f"--- .package.pri ---\n{content}\n---"
    )


def assert_cmake_contains(project: Path, text: str) -> None:
    """Assert that .package.cmake contains the given text."""
    cmake = project / ".package.cmake"
    assert cmake.exists(), f".package.cmake not found in {project}"
    content = cmake.read_text(encoding="utf-8")
    assert text in content, (
        f"Expected '{text}' in .package.cmake, but not found.\n"
        f"--- .package.cmake ---\n{content}\n---"
    )


def assert_include_order(project: Path, *names: str) -> None:
    """Assert that include directives appear in the given order."""
    pri = project / ".package.pri"
    assert pri.exists(), f".package.pri not found in {project}"
    content = pri.read_text(encoding="utf-8")
    positions = {}
    for name in names:
        idx = content.find(name)
        assert idx >= 0, f"'{name}' not found in .package.pri"
        positions[name] = idx
    for a, b in zip(names, names[1:]):
        assert positions[a] < positions[b], (
            f"Expected '{a}' before '{b}' in .package.pri"
        )


# ── HTTP download helpers ────────────────────────────────────────────────

def zip_fixture(fixture_name: str) -> Path:
    """Package a fixture directory into a .zip for HTTP download testing.

    Args:
        fixture_name: e.g. "hello@1.0.0"

    Returns:
        Path to the generated .zip file (in a temp directory).
    """
    src = FIXTURES_DIR / fixture_name
    if not src.exists():
        raise FileNotFoundError(f"Fixture not found: {src}")

    tmp_dir = Path(tempfile.mkdtemp(prefix="imakecore_test_zip_"))
    zip_base = tmp_dir / fixture_name
    shutil.make_archive(str(zip_base), "zip", str(src))
    return Path(str(zip_base) + ".zip")


@contextmanager
def http_serve(directory: str | Path) -> str:
    """Context manager that starts an HTTP server on a random port.

    Usage::

        with http_serve("/path/to/files") as url:
            # url = "http://127.0.0.1:PORT"
            # files in directory are served at url/filename

    The server runs in a daemon thread and shuts down on exit.
    """
    import http.server

    handler = http.server.SimpleHTTPRequestHandler
    # Change to the serving directory so URLs are relative
    saved_cwd = os.getcwd()
    server = http.server.HTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        os.chdir(str(directory))
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        os.chdir(saved_cwd)
        server.shutdown()
