"""basic_resolve/test.py"""
import json, os, re, shutil, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
IMAKECORE_PY = Path(os.getenv("IMAKECORE_SYSTEM", "")) / "IMakeCore.py"
UPDATE_DB_PY = Path(os.getenv("IMAKECORE_SYSTEM", "")) / "updateDb.py"
_PASSED = _FAILED = 0
_G_PACK_TYPE = "qmake"

def _setup():
    (ROOT / ".db").mkdir(exist_ok=True)
    subprocess.run([sys.executable, "-B", str(UPDATE_DB_PY)],
                   env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                   capture_output=True, text=True, check=True, timeout=60)

def _run(project: Path):
    return subprocess.run([sys.executable, "-B", str(IMAKECORE_PY), str(project), _G_PACK_TYPE],
                          env={**os.environ, "IMAKECORE_ROOT": str(ROOT)},
                          capture_output=True, text=True, timeout=120)

def _prepare(project: Path, packages: dict) -> Path:
    for name in (".package.pri", ".package.cmake", ".data", ".lib", ".support", ".bin"):
        p = project / name
        if p.exists(): (shutil.rmtree if p.is_dir() else os.remove)(str(p))
    project.mkdir(parents=True, exist_ok=True)
    (project / "packages.json").write_text(json.dumps({"packages": packages}), encoding="utf-8")
    return project

def _check(c, msg):
    global _PASSED, _FAILED
    if c: _PASSED += 1
    else: _FAILED += 1; print(f"  FAIL: {msg}")

def _vfy_pri(project: Path, *expected: str):
    pri = project / (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri")
    _check(pri.exists(), f"{project.name}: output missing")
    if pri.exists():
        txt = pri.read_text()
        for pkg in expected: _check(pkg in txt, f"{project.name}: missing '{pkg}'")
        for m in re.finditer(r'include\((.+?)\)', txt):
            _check(Path(m.group(1)).exists(), f"{project.name}: broken include: {m.group(1)}")

def _vfy_cache(project: Path, *names: str):
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: resolve-cache missing")
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        for n in names: _check(n in data.get("resolved",{}), f"{project.name}: cache missing '{n}'")

def _vfy_absent(project: Path, *forbidden: str):
    pri = project / (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri")
    if pri.exists():
        txt = pri.read_text()
        for pkg in forbidden: _check(pkg not in txt, f"{project.name}: leaked '{pkg}'")

# -- Tests


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

def test_static_chain_rejects_source_dep():
    """world (static) → hello (source) — source dep in static chain is error."""
    proj = _prepare(ROOT / "project_static_source_dep", {
        "test/world": {"version": "1.0.0", "mode": "static"},
        "test/hello": {"version": "2.0.0", "mode": "source"}
    })
    r = _run(proj)
    _check(r.returncode == 1, f"expected exit(1) for source in static chain, got {r.returncode}")
    out = (r.stdout + r.stderr).lower()
    _check("source" in out, f"error should mention 'source': {out[:200]}")


# ── Main ───────────────────────────────────────────────────────────────

def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\nstatic_chain  (root={ROOT})\n{'='*60}")
    _setup()
    test_source_marked_static()
    test_source_mode_explicit()
    test_static_chain_rejects_source_dep()
    test_static_propagates_to_dep()
    test_static_skips_dynamic_dep()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
