"""
test_cases.py — Basic resolution: single package, transitive deps, version constraints.
"""
import json
from pathlib import Path

from helpers import (
    write_packages_json,
    run_imakecore,
    assert_file_exists,
    assert_pri_contains,
)


class TestBasicResolve:
    """Core resolution scenarios — the happy path."""

    def test_single_package_no_deps(self, test_env, test_project):
        """Resolve a single header-only package with no dependencies."""
        write_packages_json(test_project, {"test/hello": "1.0.0"})
        result = run_imakecore(test_project)
        assert result.returncode == 0, f"Failed:\n{result.stdout}\n{result.stderr}"
        assert_file_exists(test_project / ".package.pri")
        assert_pri_contains(test_project, "hello")

    def test_single_source_package(self, test_env, test_project):
        """Resolve a source package (contains .cpp)."""
        write_packages_json(test_project, {"test/hello": "2.0.0"})
        result = run_imakecore(test_project)
        assert result.returncode == 0
        assert_pri_contains(test_project, "hello")

    def test_transitive_dependency(self, test_env, test_project):
        """Resolve a package that depends on another — both should be included."""
        write_packages_json(test_project, {"test/world": "1.0.0"})
        result = run_imakecore(test_project)
        assert result.returncode == 0, f"Failed:\n{result.stdout}\n{result.stderr}"
        pri = (test_project / ".package.pri").read_text()
        assert "world" in pri, f"world not found:\n{pri}"
        assert "hello" in pri, f"hello not found:\n{pri}"

    def test_version_selection_latest(self, test_env, test_project):
        """When multiple versions exist, the latest compatible is selected."""
        write_packages_json(test_project, {"test/hello": ">=2.0"})
        result = run_imakecore(test_project)
        assert result.returncode == 0
        pri = (test_project / ".package.pri").read_text()
        assert "2.0.0" in pri, f"Expected version 2.0.0:\n{pri}"
        assert "test@hello@1.0.0" not in pri, f"1.0.0 leaked:\n{pri}"

    def test_version_skip(self, test_env, test_project):
        """Version 'x' skips the package entirely."""
        write_packages_json(test_project, {"test/hello": "x"})
        result = run_imakecore(test_project)
        assert result.returncode == 0
        pri = (test_project / ".package.pri").read_text()
        assert "hello" not in pri, f"hello should be absent:\n{pri}"

    def test_imakecore_creates_package_pri(self, test_env, test_project):
        """IMakeCore generates the expected .package.pri include chain."""
        write_packages_json(test_project, {"test/hello": "1.0.0"})
        result = run_imakecore(test_project)
        assert result.returncode == 0
        pri = test_project / ".package.pri"
        assert pri.exists()
        assert len(pri.read_text().strip()) > 0, ".package.pri is empty"
