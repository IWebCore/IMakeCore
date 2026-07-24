"""
validation/test.py — Self-contained functional test.
"""
import json, os, shutil, subprocess, sys
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


def _prepare(project: Path, packages: dict) -> Path:
    for name in (".package.pri", ".package.cmake", ".data", ".lib", ".support", ".bin"):
        p = project / name
        if p.exists():
            (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    project.mkdir(parents=True, exist_ok=True)
    (project / "packages.json").write_text(json.dumps({"packages": packages}), encoding="utf-8")
    return project


def _out(r): return (r.stdout + r.stderr).lower()


def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")


# ── Verification helpers (for error-path tests) ────────────────────────
def _vfy_no_pri(project: Path):
    """Verify .package.pri was NOT generated (expected on error)."""
    pri = project / ".package.pri"
    _check(not pri.exists(), f"{project.name}: .package.pri should NOT exist on error")


def _vfy_pri_exists(project: Path, *expected: str):
    pri = project / ".package.pri"
    if pri.exists():
        txt = pri.read_text()
        for pkg in expected:
            _check(pkg in txt, f"{project.name}: .package.pri missing '{pkg}'")


# ── Test cases ─────────────────────────────────────────────────────────

def test_header_only_rejects_static():
    """hello@1.0.0 (header-only) + static → error."""
    proj = _prepare(ROOT / "project_err_static",
                    {"test/hello": {"version": "1.0.0", "mode": "static"}})
    r = _run(proj)
    _check(r.returncode == 1, f"expected exit(1), got {r.returncode}")
    _check("header-only" in _out(r), f"missing 'header-only': {_out(r)[:200]}")
    _vfy_no_pri(proj)


def test_header_only_rejects_dynamic():
    """hello@1.0.0 (header-only) + dynamic → error."""
    proj = _prepare(ROOT / "project_err_dynamic",
                    {"test/hello": {"version": "1.0.0", "mode": "dynamic"}})
    r = _run(proj)
    _check(r.returncode == 1, f"expected exit(1), got {r.returncode}")
    _check("header-only" in _out(r), f"missing 'header-only': {_out(r)[:200]}")
    _vfy_no_pri(proj)


def test_missing_dependency():
    """Reference to nonexistent package → error, no .package.pri."""
    proj = _prepare(ROOT / "project_err_missing",
                    {"test/nonexistent": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 1, f"expected exit(1), got {r.returncode}")
    _check(any(w in _out(r) for w in ("cannot", "not found", "not in the resolved", "failed")),
           f"missing error indicator: {_out(r)[:200]}")
    _vfy_no_pri(proj)


def test_missing_packages_json():
    """No packages.json — should fail gracefully, no crash."""
    proj = ROOT / "project_no_pkg"
    for name in (".package.pri", ".package.cmake", ".data", ".lib", ".support", ".bin"):
        p = proj / name
        if p.exists():
            (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    proj.mkdir(parents=True, exist_ok=True)
    r = _run(proj)
    _check(r.returncode in (0, 1), f"unexpected rc={r.returncode}")
    # No .package.pri expected (either empty or error)
    _check(not (proj / ".package.pri").exists() or r.returncode != 0,
           ".package.pri should not be generated when packages.json is missing")


def test_dynamic_without_definition():
    """dynamic mode without dynamicDefinition in resolve."""
    proj = _prepare(ROOT / "project_err_dynamic",
                    {"test/dynamic_lib": {"version": "1.0.0", "mode": "dynamic"}})
    r = _run(proj)
    _check(r.returncode in (0, 1), f"unexpected rc={r.returncode}")
    if r.returncode == 1:
        _check("dynamic" in _out(r), f"missing 'dynamic' in error: {_out(r)[:200]}")


# ── Main ───────────────────────────────────────────────────────────────
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
