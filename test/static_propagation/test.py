"""
static_propagation/test.py — Self-contained functional test.
"""
import json, os, re, shutil, subprocess, sys
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


def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")


# ── Verification helpers ───────────────────────────────────────────────
def _vfy_pri_exists(project: Path, *expected_packages: str):
    pri = project / ".package.pri"
    _check(pri.exists(), f"{project.name}: .package.pri not generated")
    if not pri.exists():
        return
    txt = pri.read_text()
    for pkg in expected_packages:
        _check(pkg in txt, f"{project.name}: .package.pri missing '{pkg}'")


def _vfy_pri_includes_exist(project: Path):
    pri = project / ".package.pri"
    if not pri.exists():
        return
    for m in re.finditer(r'include\((.+?)\)', pri.read_text()):
        _check(Path(m.group(1)).exists(),
               f"{project.name}: include target missing: {m.group(1)}")


def _vfy_resolve_cache(project: Path, *pkg_names: str):
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: resolve-cache.json not generated")
    if not cache.exists():
        return
    data = json.loads(cache.read_text(encoding="utf-8"))
    resolved = data.get("resolved", {})
    for name in pkg_names:
        _check(name in resolved, f"{project.name}: resolve-cache missing '{name}'")


# ── Test cases ─────────────────────────────────────────────────────────

def test_static_propagates():
    """world (static) → hello — resolution succeeds, both in output."""
    proj = _prepare(ROOT / "project_static",
                    {"test/world": {"version": "1.0.0", "mode": "static"}})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")

    _vfy_pri_exists(proj, "hello", "world")
    _vfy_pri_includes_exist(proj)
    _vfy_resolve_cache(proj, "test/hello", "test/world")


def test_static_source_cpp():
    """hello@2.0.0 (source+cpp) + static — validation varies."""
    proj = _prepare(ROOT / "project_static_cpp",
                    {"test/hello": {"version": "2.0.0", "mode": "static"}})
    r = _run(proj)
    out = (r.stdout + r.stderr).lower()
    if r.returncode != 0:
        _check(any(w in out for w in ("header-only", "source", "static")),
               f"missing validation msg: {out[:200]}")
    if r.returncode == 0:
        _vfy_pri_exists(proj, "hello")
        _vfy_pri_includes_exist(proj)
        _vfy_resolve_cache(proj, "test/hello")


# ── Main ───────────────────────────────────────────────────────────────
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
