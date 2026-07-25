"""
static_chain/test.py — Deep static chain and dynamic-in-static testing.
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


# ── Tests ──────────────────────────────────────────────────────────────

def test_static_propagates_to_dep():
    """world (static) → hello — both should resolve successfully."""
    proj = _prepare(ROOT / "project_static_chain", {
        "test/world": {"version": "1.0.0", "mode": "static"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "hello", "world")


def test_source_marked_static():
    """hello@2.0.0 (source with .cpp) explicitly marked static — should work."""
    proj = _prepare(ROOT / "project_source_static", {
        "test/hello": {"version": "2.0.0", "mode": "static"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "hello")


def test_static_skips_dynamic_dep():
    """Static world + explicit dynamic_lib — both should coexist."""
    proj = _prepare(ROOT / "project_static_dynamic", {
        "test/world": {"version": "1.0.0", "mode": "static"},
        "test/dynamic_lib": {"version": "1.0.0", "mode": "dynamic"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "world", "dynamic_lib")


def test_source_mode_explicit():
    """Package with explicit mode='source' should resolve normally."""
    proj = _prepare(ROOT / "project_source_explicit", {
        "test/hello": {"version": "2.0.0", "mode": "source"}
    })
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}\n{r.stdout[:300]}")
    _vfy_pri(proj, "hello")


# ── Main ───────────────────────────────────────────────────────────────
def run():
    global _PASSED, _FAILED
    print(f"{'='*60}\nstatic_chain  (root={ROOT})\n{'='*60}")
    _setup()
    test_static_propagates_to_dep()
    test_source_marked_static()
    test_static_skips_dynamic_dep()
    test_source_mode_explicit()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    sys.exit(0 if run() else 1)
