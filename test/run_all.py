"""
run_all.py — Master test runner.

Runs each sub-test directory's test.py in sequence and reports results.

Usage:  python run_all.py       (from test/ directory)
"""

import subprocess
import sys
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
SUITES = ["basic_resolve", "static_propagation", "validation",
          "version_specifiers", "cmake_output", "local_origin", "advanced_resolve",
          "path_resolve", "static_chain"]


def main():
    passed = 0
    failed = 0

    for suite in SUITES:
        test_py = TEST_DIR / suite / "test.py"
        if not test_py.exists():
            print(f"[SKIP] {suite} — test.py not found")
            continue

        result = subprocess.run(
            [sys.executable, str(test_py)],
            cwd=str(test_py.parent),
            timeout=300,
        )
        if result.returncode == 0:
            passed += 1
        else:
            failed += 1

    print("\n" + "=" * 60)
    print(f"TOTAL: {passed} passed, {failed} failed out of {len(SUITES)} suites")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)
