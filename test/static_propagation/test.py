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
    for name in (".package.pri", ".package.cmake", ".package.xmake", ".data", ".lib", ".support", ".bin"):
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
    pri = project / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))
    _check(pri.exists(), f"{project.name}: output missing")
    if pri.exists():
        txt = pri.read_text()
        for pkg in expected: _check(pkg in txt, f"{project.name}: missing '{pkg}'")
        pattern = r'includes\(["\'](.+?)["\']\)' if _G_PACK_TYPE == "xmake" else r'include\((.+?)\)'
        for m in re.finditer(pattern, txt):
            _check(Path(m.group(1)).exists(), f"{project.name}: broken include: {m.group(1)}")

def _vfy_cache(project: Path, *names: str):
    cache = project / ".data" / "resolve-cache.json"
    _check(cache.exists(), f"{project.name}: resolve-cache missing")
    if cache.exists():
        data = json.loads(cache.read_text(encoding="utf-8"))
        for n in names: _check(n in data.get("resolved",{}), f"{project.name}: cache missing '{n}'")

def _vfy_absent(project: Path, *forbidden: str):
    pri = project / (".package.xmake" if _G_PACK_TYPE == "xmake" else (".package.cmake" if _G_PACK_TYPE == "cmake" else ".package.pri"))
    if pri.exists():
        txt = pri.read_text()
        for pkg in forbidden: _check(pkg not in txt, f"{project.name}: leaked '{pkg}'")

# -- Tests


def test_static_propagates():
    """world (static) → hello — resolution succeeds, both in output."""
    proj = _prepare(ROOT / "project_static",
                    {"test/world": {"version": "1.0.0", "mode": "static"}})
    r = _run(proj)
    _check(r.returncode == 0, f"rc={r.returncode}")

    _vfy_pri(proj, "hello", "world")
    _vfy_pri(proj)
    _vfy_cache(proj, "test/hello", "test/world")

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
        _vfy_pri(proj, "hello")
        _vfy_pri(proj)
        _vfy_cache(proj, "test/hello")


# ── Main ───────────────────────────────────────────────────────────────

def run(pack_type: str = "qmake"):
    global _PASSED, _FAILED, _G_PACK_TYPE
    _G_PACK_TYPE = pack_type
    print(f"{'='*60}\nstatic_propagation  (root={ROOT})\n{'='*60}")
    _setup()
    test_static_propagates()
    test_static_source_cpp()
    print(f"\n  {_PASSED} passed, {_FAILED} failed")
    return _FAILED == 0


if __name__ == "__main__":
    pt = sys.argv[1] if len(sys.argv) > 1 else "qmake"
    sys.exit(0 if run(pt) else 1)
