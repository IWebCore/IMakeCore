"""
static_propagation/test.py — Self-contained functional test.

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


def test_static_propagates():
    proj = _mkproj({"test/world": {"version": "1.0.0", "mode": "static"}})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _check((proj / ".package.pri").exists(), ".package.pri missing")
    shutil.rmtree(proj, ignore_errors=True)


def test_static_source_cpp():
    proj = _mkproj({"test/hello": {"version": "2.0.0", "mode": "static"}})
    r = _run(proj)
    out = (r.stdout + r.stderr).lower()
    if r.returncode != 0:
        _check(any(w in out for w in ("header-only", "source", "static")),
               f"missing msg: {out[:200]}")
    shutil.rmtree(proj, ignore_errors=True)


def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nstatic_propagation  (root={ROOT})\n{'='*60}")
    _setup()
    test_static_propagates()
    test_static_source_cpp()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
