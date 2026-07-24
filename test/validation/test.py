"""
validation/test.py — Self-contained functional test.

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


def _out(r): return (r.stdout + r.stderr).lower()


def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")


def test_header_only_rejects_static():
    proj = _mkproj({"test/hello": {"version": "1.0.0", "mode": "static"}})
    r = _run(proj)
    _check(r.returncode == 1, f"expected 1, got {r.returncode}")
    _check("header-only" in _out(r), f"missing: {_out(r)[:200]}")
    shutil.rmtree(proj, ignore_errors=True)


def test_header_only_rejects_dynamic():
    proj = _mkproj({"test/hello": {"version": "1.0.0", "mode": "dynamic"}})
    r = _run(proj)
    _check(r.returncode == 1, f"expected 1, got {r.returncode}")
    _check("header-only" in _out(r), f"missing: {_out(r)[:200]}")
    shutil.rmtree(proj, ignore_errors=True)


def test_missing_dependency():
    proj = _mkproj({"test/nonexistent": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 1, f"expected 1, got {r.returncode}")
    _check(any(w in _out(r) for w in ("cannot", "not found", "not in the resolved", "failed")),
           f"missing: {_out(r)[:200]}")
    shutil.rmtree(proj, ignore_errors=True)


def test_missing_packages_json():
    proj = Path(tempfile.mkdtemp(dir=ROOT, prefix="proj_"))
    (proj / ".data").mkdir()
    r = _run(proj)
    _check(r.returncode in (0, 1), f"rc={r.returncode}")
    shutil.rmtree(proj, ignore_errors=True)


def test_dynamic_without_definition():
    proj = _mkproj({"test/dynamic_lib": {"version": "1.0.0", "mode": "dynamic"}})
    r = _run(proj)
    _check(r.returncode in (0, 1), f"rc={r.returncode}")
    shutil.rmtree(proj, ignore_errors=True)


def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nvalidation  (root={ROOT})\n{'='*60}")
    _setup()
    test_header_only_rejects_static()
    test_header_only_rejects_dynamic()
    test_missing_dependency()
    test_missing_packages_json()
    test_dynamic_without_definition()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
