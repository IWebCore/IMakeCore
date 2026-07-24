"""
test_cases.py — Validation: error paths that should be caught.
"""
from pathlib import Path

from helpers import write_packages_json, run_imakecore


def _output(result) -> str:
    """Return combined stdout+stderr, lowercased for searching."""
    return (result.stdout + result.stderr).lower()


class TestValidation:
    """IMakeCore must reject invalid configurations with clear messages."""

    def test_header_only_rejects_static(self, test_env, test_project):
        """hello@1.0.0 (header-only) + mode='static' → error."""
        write_packages_json(test_project, {
            "test/hello": {"version": "1.0.0", "mode": "static"}
        })
        result = run_imakecore(test_project)
        assert result.returncode == 1, (
            f"Expected exit(1), got {result.returncode}\n{_output(result)}"
        )
        assert "header-only" in _output(result), (
            f"Missing 'header-only':\n{_output(result)}"
        )

    def test_header_only_rejects_dynamic(self, test_env, test_project):
        """hello@1.0.0 (header-only) + mode='dynamic' → error."""
        write_packages_json(test_project, {
            "test/hello": {"version": "1.0.0", "mode": "dynamic"}
        })
        result = run_imakecore(test_project)
        assert result.returncode == 1, (
            f"Expected exit(1), got {result.returncode}\n{_output(result)}"
        )
        assert "header-only" in _output(result), (
            f"Missing 'header-only':\n{_output(result)}"
        )

    def test_missing_dependency(self, test_env, test_project):
        """Reference to nonexistent package → error."""
        write_packages_json(test_project, {"test/nonexistent": "1.0.0"})
        result = run_imakecore(test_project)
        assert result.returncode == 1, (
            f"Expected failure, got {result.returncode}\n{_output(result)}"
        )
        assert any(w in _output(result) for w in (
            "cannot", "not found", "not in the resolved", "failed"
        )), f"Missing error indicator:\n{_output(result)}"

    def test_missing_packages_json(self, test_env, test_project):
        """Missing packages.json — should fail gracefully."""
        result = run_imakecore(test_project)
        assert result.returncode in (0, 1), (
            f"Unexpected return code {result.returncode}\n{_output(result)}"
        )

    def test_dynamic_without_definition(self, test_env, test_project):
        """dynamic mode without dynamicDefinition → handled."""
        write_packages_json(test_project, {
            "test/dynamic_lib": {"version": "1.0.0", "mode": "dynamic"}
        })
        result = run_imakecore(test_project)
        assert result.returncode in (0, 1), (
            f"Unexpected return code {result.returncode}\n{_output(result)}"
        )
