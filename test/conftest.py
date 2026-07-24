"""
conftest.py — Pytest fixtures for IMakeCore functional testing.

Provides:
  test_env    (session)  — shared IMAKECORE_ROOT with .system/, .lib/, .data/, DB
  test_project (function) — isolated project directory per test
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import pytest

# Paths relative to this file
ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
SYSTEM_SRC = ROOT / ".system"
DATA_SRC = ROOT / ".data"


# ── Session-scoped: shared IMAKECORE environment ─────────────────────────

class TestEnv:
    """Holds the isolated IMAKECORE_ROOT and paths for all tests in a session."""

    def __init__(self, root: Path) -> None:
        self.root = root                          # IMAKECORE_ROOT
        self.system = root / ".system"            # .system/ (code copy)
        self.lib = root / ".lib"                  # .lib/   (fixture packages)
        self.data = root / ".data"                # .data/  (config.json, packages.json)
        self.db_path = self.system / "db" / "package.db"
        self.imakecore_py = self.system / "IMakeCore.py"
        self.update_db_py = self.system / "scripts" / "updateDb.py"

    def python_path(self) -> str:
        """Return the directory to add to sys.path (the .system/ dir)."""
        return str(self.system)


@pytest.fixture(scope="session")
def test_env(tmp_path_factory) -> TestEnv:
    """Create an isolated IMAKECORE_ROOT shared by all tests.

    1. Copy .system/  (real code under test)
    2. Copy fixtures/ → .lib/ (virtual test packages)
    3. Write .data/config.json (minimal config)
    4. Write .data/packages.json (empty template, fallback)
    5. Run update_db.py to index fixture packages into SQLite
    6. Set IMAKECORE_ROOT in os.environ for the session duration
    """
    root = tmp_path_factory.mktemp("imakecore_root")
    env = TestEnv(root)

    # (1) Copy the real .system/ code into the isolated root
    shutil.copytree(str(SYSTEM_SRC), str(env.system),
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))

    # (2) Copy fixture packages into .lib/
    env.lib.mkdir(parents=True, exist_ok=True)
    if FIXTURES_DIR.exists():
        for fixture_dir in FIXTURES_DIR.iterdir():
            if fixture_dir.is_dir():
                dest = env.lib / fixture_dir.name
                if not dest.exists():
                    shutil.copytree(str(fixture_dir), str(dest))

    # (3) Write .data/config.json
    env.data.mkdir(parents=True, exist_ok=True)
    config = {
        "globalLibStore": ".lib",
        "libstores": [],
        "servers": [],
        "user": "test"
    }
    (env.data / "config.json").write_text(
        json.dumps(config, indent=2), encoding="utf-8"
    )

    # (4) Write .data/packages.json (empty template — fallback)
    (env.data / "packages.json").write_text(
        json.dumps({"packages": {}}, indent=2), encoding="utf-8"
    )

    # (5) Run update_db.py to index packages
    _run_update_db(env)

    # (6) Override IMAKECORE_ROOT for the session duration
    _saved_root = os.environ.get("IMAKECORE_ROOT")
    os.environ["IMAKECORE_ROOT"] = str(env.root)

    yield env

    # Teardown
    if _saved_root is not None:
        os.environ["IMAKECORE_ROOT"] = _saved_root
    else:
        os.environ.pop("IMAKECORE_ROOT", None)


def _run_update_db(env: TestEnv) -> None:
    """Call update_db.py in the isolated environment."""
    sub_env = os.environ.copy()
    sub_env["IMAKECORE_ROOT"] = str(env.root)
    result = subprocess.run(
        [sys.executable, "-B", str(env.update_db_py)],
        capture_output=True,
        text=True,
        env=sub_env,
        timeout=60,
    )
    if result.returncode != 0:
        pytest.fail(f"update_db.py failed:\n{result.stderr}\n{result.stdout}")


# ── Function-scoped: isolated project per test ───────────────────────────

@pytest.fixture
def test_project(tmp_path, test_env: TestEnv) -> Path:
    """Create an empty project directory for a single test case.

    The test function writes its own packages.json and then calls
    run_imakecore() from helpers.py.
    """
    project = tmp_path / "project"
    project.mkdir()
    (project / ".data").mkdir()
    return project


# ── Sub-test packages.json loader ────────────────────────────────────────

def load_sub_test_config(request: pytest.FixtureRequest) -> dict[str, Any]:
    """Load the packages.json from the current sub-test directory.

    Use this inside a test function to get the pre-configured
    dependency declaration for the sub-test scenario.
    """
    test_dir = Path(request.fspath).parent
    pkg_json = test_dir / "packages.json"
    if pkg_json.exists():
        return json.loads(pkg_json.read_text(encoding="utf-8"))
    return {"packages": {}}
