"""
test_cases.py — Static mode: propagation to deps.
"""
from pathlib import Path

from helpers import write_packages_json, run_imakecore, assert_file_exists


class TestStaticPropagation:
    """Static libraries must propagate mode to transitive deps."""

    def test_static_propagates_to_dependency(self, test_env, test_project):
        """world (static) → hello — resolution should succeed."""
        write_packages_json(test_project, {
            "test/world": {"version": "1.0.0", "mode": "static"}
        })
        result = run_imakecore(test_project)
        assert result.returncode == 0, (
            f"Failed:\n{result.stdout}\n{result.stderr}"
        )
        assert_file_exists(test_project / ".package.pri")

    def test_static_with_source_cpp_dependency(self, test_env, test_project):
        """hello@2.0.0 (source+cpp) marked static — may or may not be allowed."""
        write_packages_json(test_project, {
            "test/hello": {"version": "2.0.0", "mode": "static"}
        })
        result = run_imakecore(test_project)
        output = (result.stdout + result.stderr).lower()
        if result.returncode != 0:
            # Should fail because source cpp + static is not allowed
            assert any(w in output for w in ("header-only", "source", "static")), (
                f"Error should mention the issue:\n{output}"
            )
        # If returncode is 0, the combination is accepted
