"""
basic_resolve/test.py — Self-contained functional test.

This directory IS the IMAKECORE_ROOT.
"""

import json, os, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = ROOT / ".system" / "IMakeCore.py"
UPDATE_DB_PY = ROOT / ".system" / "scripts" / "updateDb.py"
_PASSED = _FAILED = 0


def _setup():
    (ROOT / ".db").mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-B", str(UPDATE_DB_PY)],
                   env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                   capture_output=True, text=True, check=True, timeout=60)


def _run(project: Path):
    return subprocess.run([sys.executable, "-B", str(IMAKECORE_PY), str(project), "qmake"],
                          env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                          capture_output=True, text=True, timeout=120)


def _mkproj(packages: dict) -> Path:
    proj = Path(tempfile.mkdtemp(dir=ROOT, prefix="proj_"))
    (proj / ".data").mkdir()
    (proj / "packages.json").write_text(json.dumps({"packages": packages}), encoding="utf-8")
    return proj


def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")


def test_single_package_no_deps():
    proj = _mkproj({"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _check((proj / ".package.pri").exists(), ".package.pri missing")
    _check("hello" in (proj / ".package.pri").read_text(), "hello not found")
    shutil.rmtree(proj, ignore_errors=True)


def test_single_source_package():
    proj = _mkproj({"test/hello": "2.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _check("hello" in (proj / ".package.pri").read_text(), "hello not found")
    shutil.rmtree(proj, ignore_errors=True)


def test_transitive_dependency():
    proj = _mkproj({"test/world": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    pri = (proj / ".package.pri").read_text()
    _check("world" in pri, "world missing")
    _check("hello" in pri, "hello (transitive) missing")
    shutil.rmtree(proj, ignore_errors=True)


def test_version_selection_latest():
    proj = _mkproj({"test/hello": ">=2.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    pri = (proj / ".package.pri").read_text()
    _check("2.0.0" in pri, "2.0.0 not selected")
    _check("1.0.0" not in pri, "1.0.0 leaked")
    shutil.rmtree(proj, ignore_errors=True)


def test_version_skip():
    proj = _mkproj({"test/hello": "x"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _check("hello" not in (proj / ".package.pri").read_text(), "hello leaked")
    shutil.rmtree(proj, ignore_errors=True)


def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nbasic_resolve  (root={ROOT})\n{'='*60}")
    _setup()
    test_single_package_no_deps()
    test_single_source_package()
    test_transitive_dependency()
    test_version_selection_latest()
    test_version_skip()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
