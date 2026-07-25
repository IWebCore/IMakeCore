"""
advanced_resolve/test.py — Multiple deps, publisher scope, mode:default.
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


def _vfy_pri(project: Path, *expected: str):
    pri = project / ".package.pri"
    _check(pri.exists(), f"{project.name}: missing .package.pri")
    if pri.exists():
        txt = pri.read_text()
        for pkg in expected:
            _check(pkg in txt, f"{project.name}: missing '{pkg}'")
        for m in re.finditer(r'include\((.+?)\)', txt):
            _check(Path(m.group(1)).exists(), f"{project.name}: broken include: {m.group(1)}")


def _vfy_cache(project: Path, *names: str):
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: missing resolve-cache.json")
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        for n in names:
            _check(n in data.get("resolved", {}), f"{project.name}: cache missing '{n}'")


# ── Tests ──────────────────────────────────────────────────────────────

def test_publisher_scope():
    """Using 'test/hello' with publisher prefix should resolve correctly."""
    proj = _prepare(ROOT / "project_publisher", {"test/hello": "1.0.0"})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello")
    _vfy_cache(proj, "test/hello")


def test_mode_default_explicit():
    """Explicit mode='default' should work like no mode specified."""
    proj = _prepare(ROOT / "project_default", {
        "test/hello": {"version": "1.0.0", "mode": "default"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello")


def test_two_independent_packages():
    """Two unrelated packages should both resolve."""
    proj = _prepare(ROOT / "project_two", {
        "test/hello": "1.0.0",
        "test/world": "1.0.0"
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello", "world")
    _vfy_cache(proj, "test/hello", "test/world")


def test_transitive_with_versions():
    """world depends on hello>=1.0 — with two hello versions, picks latest but resolves."""
    proj = _prepare(ROOT / "project_trans_ver", {
        "test/world": {"version": "1.0.0"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")
    _vfy_pri(proj, "hello", "world")
    _vfy_cache(proj, "test/hello", "test/world")


# ── Main ───────────────────────────────────────────────────────────────
def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nadvanced_resolve  (root={ROOT})\n{'='*60}")
    _setup()
    test_publisher_scope()
    test_mode_default_explicit()
    test_two_independent_packages()
    test_transitive_with_versions()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
