"""
run_all.py — Master test runner.

Accepts optional pack type arguments: qmake, cmake, or both.
Defaults to both if none specified.

Usage:
    python run_all.py              # runs qmake + cmake
    python run_all.py qmake        # runs qmake only
    python run_all.py cmake        # runs cmake only
    python run_all.py qmake cmake  # runs both
"""

import subprocess
import sys
import os
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent

# Point to the real .system/ directory so test subdirectories don't need
# their own .system junctions.  The test.py subprocesses inherit this
# and forward it to IMakeCore.py via env.
os.environ.setdefault("IMAKECORE_SYSTEM", str(TEST_DIR.parent / ".system"))
SUITES = [
    "basic_resolve", "static_propagation", "validation",
    "version_specifiers", "cmake_output", "local_origin",
    "advanced_resolve", "path_resolve", "static_chain",
    "package_json", "compile_info",
]

VALID = {"qmake", "cmake"}


def main():
    args = sys.argv[1:]
    if not args:
        pack_types = ["qmake", "cmake"]
    else:
        for a in args:
            if a not in VALID:
                print(f"ERROR: Invalid pack type '{a}'. Use: qmake cmake")
                return False
        seen = set()
        pack_types = []
        for a in args:
            if a not in seen:
                seen.add(a)
                pack_types.append(a)

    passed = 0
    failed = 0

    for suite in SUITES:
        test_py = TEST_DIR / suite / "test.py"
        if not test_py.exists():
            print(f"[SKIP] {suite}")
            continue

        for pt in pack_types:
            r = subprocess.run(
                [sys.executable, str(test_py), pt],
                cwd=str(test_py.parent), timeout=300,
            )
            if r.returncode == 0:
                passed += 1
            else:
                failed += 1

    print(f"\n{'='*60}")
    print(f"TOTAL: {passed} passed, {failed} failed"
          f"  (types: {', '.join(pack_types)})")
    print(f"{'='*60}")
    return failed == 0


if __name__ == "__main__":
    sys.exit(0 if main() else 1)
